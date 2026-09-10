#!/usr/bin/env python3
"""Gather deterministic SEO-audit evidence for one URL: raw page HTML, robots.txt,
Wayback Machine capture history (with a platform-migration heuristic), a legacy-URL
redirect test, and real Ahrefs API competitive data.

This does the mechanical, scriptable half of the seo-audit skill. The parts that
need a live browser (Google Business Profile check, Core Web Vitals) or judgment
(prioritizing findings, writing the report) are NOT here — see SKILL.md.

Usage:
    python3 gather_evidence.py --url https://example.com \
        --competitors comp1.com,comp2.com \
        --pages /,/about,/services \
        --keywords "target keyword,another keyword" \
        --out ~/projects/seo-audits/example-com

Stdlib only, except Ahrefs calls (also stdlib urllib). Reads AHREFS_API_TOKEN from
the same .env this machine's other Ahrefs scripts use, unless --ahrefs-env is given.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_AHREFS_ENV = "/home/fredericktejada/TMC/Ahrefs API/.env"
AHREFS_BASE = "https://api.ahrefs.com/v3"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PLATFORM_MARKERS = {
    "webflow": ["webflow", "website-files.com"],
    "wordpress": ["wp-content", "wp-json", "wordpress"],
    "squarespace": ["squarespace"],
    "wix": ["wix.com", "wixstatic"],
    "shopify": ["cdn.shopify.com", "shopify"],
}


def fetch(url, out_path=None, timeout=20, retries=1):
    last_err = None
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                status = resp.status
                break
        except urllib.error.HTTPError as e:
            body = e.read()
            status = e.code
            break
        except Exception as e:
            last_err = e
            continue
    else:
        return None, f"failed after {retries + 1} attempts: {last_err}"
    if out_path:
        with open(out_path, "wb") as f:
            f.write(body)
    return status, body.decode("utf-8", errors="replace")


def detect_platform(html):
    html_l = (html or "").lower()
    for platform, markers in PLATFORM_MARKERS.items():
        if any(m in html_l for m in markers):
            return platform
    return "unknown"


def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def ahrefs_get(path, params, token):
    url = f"{AHREFS_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"[ahrefs {e.code}] {path} {params.get('target', params.get('keywords',''))}: {e.read().decode()[:300]}\n")
        return None


def ahrefs_domain_data(domain, token, country, as_of_date):
    out = {}
    dr = ahrefs_get("/site-explorer/domain-rating", {"target": domain, "date": as_of_date, "protocol": "both"}, token)
    time.sleep(1.1)
    if dr and "domain_rating" in dr:
        out["dr"] = dr["domain_rating"].get("domain_rating")
        out["ahrefs_rank"] = dr["domain_rating"].get("ahrefs_rank")
    m = ahrefs_get("/site-explorer/metrics", {"target": domain, "date": as_of_date, "country": country,
                                               "mode": "subdomains", "protocol": "both", "volume_mode": "monthly"}, token)
    time.sleep(1.1)
    if m and "metrics" in m:
        out["org_traffic"] = m["metrics"].get("org_traffic")
        out["org_keywords"] = m["metrics"].get("org_keywords")
        out["org_cost"] = m["metrics"].get("org_cost")
    return out


def wayback_history(domain):
    url = f"http://web.archive.org/cdx/search/cdx?url={urllib.parse.quote(domain)}&output=json&collapse=timestamp:6&limit=200"
    # The CDX API is noticeably slower than a normal page fetch, especially with a
    # wide collapse window on a domain with a long capture history — 20s timed out
    # here on a real test run (beauxmedspa.com) that completed fine at 45s on retry.
    status, body = fetch(url, timeout=45, retries=1)
    if status is None or not body:
        print(f"    [warn] Wayback CDX lookup failed for {domain}: {body}")
        return []
    try:
        rows = json.loads(body)
    except Exception as e:
        print(f"    [warn] Wayback CDX returned unparseable JSON for {domain}: {e}")
        return []
    return rows[1:] if rows else []


def wayback_capture_html(domain, timestamp):
    url = f"https://web.archive.org/web/{timestamp}id_/https://{domain}/"
    status, html = fetch(url, timeout=45, retries=1)
    return status, html


def extract_internal_links(html, domain):
    if not html:
        return []
    pattern = rf'href="https?://(?:www\.)?{re.escape(domain)}/([a-z0-9/_-]*)"'
    paths = set(re.findall(pattern, html, re.I))
    return sorted(p for p in paths if p and not p.startswith("wp-json"))


def test_redirect(domain, path):
    url = f"https://{domain}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        # Follow redirects manually to report the final status honestly.
        current = url
        for _ in range(5):
            req = urllib.request.Request(current, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return {"path": path, "final_status": resp.status, "final_url": resp.geturl()}
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    loc = e.headers.get("Location")
                    if not loc:
                        return {"path": path, "final_status": e.code, "final_url": current}
                    current = urllib.parse.urljoin(current, loc)
                    continue
                return {"path": path, "final_status": e.code, "final_url": current}
        return {"path": path, "final_status": "too_many_redirects", "final_url": current}
    except Exception as e:
        return {"path": path, "final_status": f"error: {e}", "final_url": url}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Target homepage URL")
    ap.add_argument("--competitors", default="", help="Comma-separated competitor domains")
    ap.add_argument("--pages", default="/", help="Comma-separated paths to fetch (e.g. /,/about,/services)")
    ap.add_argument("--keywords", default="", help="Comma-separated keywords for Ahrefs Keywords Explorer")
    ap.add_argument("--country", default="us")
    ap.add_argument("--ahrefs-env", default=DEFAULT_AHREFS_ENV)
    ap.add_argument("--out", required=True)
    ap.add_argument("--legacy-redirect-sample", type=int, default=15,
                     help="Max legacy URLs to test if a platform migration is detected")
    args = ap.parse_args()

    domain = urllib.parse.urlparse(args.url).netloc or args.url
    out_dir = os.path.expanduser(args.out)
    os.makedirs(out_dir, exist_ok=True)

    result = {"target_url": args.url, "domain": domain, "generated_at": datetime.datetime.utcnow().isoformat() + "Z"}

    # 1. Fetch target pages
    print(f"[1/6] Fetching {args.pages} from {domain}...")
    pages = {}
    for path in [p.strip() for p in args.pages.split(",") if p.strip()]:
        fname = re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_") or "home"
        full_url = urllib.parse.urljoin(args.url, path)
        status, html = fetch(full_url, os.path.join(out_dir, f"{fname}.html"))
        pages[path] = {"status": status, "file": f"{fname}.html", "bytes": len(html) if html else 0}
    result["pages_fetched"] = pages

    # 2. robots.txt
    print("[2/6] robots.txt...")
    status, robots = fetch(urllib.parse.urljoin(args.url, "/robots.txt"), os.path.join(out_dir, "robots.txt"))
    result["robots_txt"] = {"status": status, "has_disallow": bool(robots and "disallow" in robots.lower())}

    # 3. Wayback history + migration heuristic
    print("[3/6] Wayback Machine capture history...")
    history = wayback_history(domain)
    with open(os.path.join(out_dir, "wayback_history.json"), "w") as f:
        json.dump(history, f, indent=2)
    migration = {"detected": False}
    if history:
        first_ts = history[0][1]
        last_ts = history[-1][1]
        _, first_html = wayback_capture_html(domain, first_ts)
        _, last_html = wayback_capture_html(domain, last_ts)
        first_platform = detect_platform(first_html)
        last_platform = detect_platform(last_html)
        # also check live site's current platform
        live_status, live_html = pages.get("/") and fetch(args.url)
        live_platform = detect_platform(live_html)
        migration = {
            "first_capture": first_ts, "first_platform": first_platform,
            "last_wayback_capture": last_ts, "last_wayback_platform": last_platform,
            "live_platform": live_platform,
            "detected": last_platform != live_platform and last_platform != "unknown",
        }
        if migration["detected"]:
            print(f"    -> platform change detected: {last_platform} (archived {last_ts[:8]}) -> {live_platform} (live)")
            legacy_paths = extract_internal_links(last_html, domain)[: args.legacy_redirect_sample]
            print(f"[3b/6] Testing {len(legacy_paths)} legacy URLs from the last {last_platform} capture against the live site...")
            redirect_tests = [test_redirect(domain, p) for p in legacy_paths]
            broken = [r for r in redirect_tests if str(r["final_status"]).startswith("4")]
            migration["legacy_urls_tested"] = len(redirect_tests)
            migration["legacy_urls_broken"] = len(broken)
            migration["redirect_test_detail"] = redirect_tests
        else:
            print("    -> no platform change detected between last archived capture and live site")
    result["migration_check"] = migration

    # 4. Ahrefs competitive data
    env = load_env(args.ahrefs_env)
    token = env.get("AHREFS_API_TOKEN", "")
    ahrefs = {}
    if token:
        as_of = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        domains_to_check = [domain] + [c.strip() for c in args.competitors.split(",") if c.strip()]
        print(f"[4/6] Ahrefs domain data for {len(domains_to_check)} domain(s)...")
        for d in domains_to_check:
            ahrefs[d] = ahrefs_domain_data(d, token, args.country, as_of)
    else:
        print("[4/6] Skipped Ahrefs domain data: AHREFS_API_TOKEN not found at", args.ahrefs_env)
    result["ahrefs_domains"] = ahrefs

    # 5. Ahrefs keywords
    kw_terms = [k.strip() for k in args.keywords.split(",") if k.strip()]
    kw_results = {}
    if kw_terms and token:
        print(f"[5/6] Ahrefs Keywords Explorer for {len(kw_terms)} term(s)...")
        params = {"country": args.country, "select": "keyword,volume,difficulty,cpc,clicks,global_volume",
                  "keywords": ",".join(kw_terms)}
        r = ahrefs_get("/keywords-explorer/overview", params, token)
        if r:
            kw_results = r.get("keywords", [])
    elif kw_terms:
        print("[5/6] Skipped keyword pull: no Ahrefs token")
    result["ahrefs_keywords"] = kw_results

    print("[6/6] Writing evidence.json + SUMMARY.md...")
    with open(os.path.join(out_dir, "evidence.json"), "w") as f:
        json.dump(result, f, indent=2)

    with open(os.path.join(out_dir, "SUMMARY.md"), "w") as f:
        f.write(f"# Evidence summary — {domain}\n\nGenerated {result['generated_at']}\n\n")
        f.write("## Pages fetched\n")
        for p, info in pages.items():
            f.write(f"- `{p}` -> {info['file']} (HTTP {info['status']}, {info['bytes']} bytes)\n")
        f.write(f"\n## robots.txt\nHTTP {result['robots_txt']['status']}, has Disallow: {result['robots_txt']['has_disallow']}\n")
        f.write("\n## Migration check\n")
        f.write("```\n" + json.dumps({k: v for k, v in migration.items() if k != "redirect_test_detail"}, indent=2) + "\n```\n")
        if migration.get("detected"):
            f.write(f"\n**{migration.get('legacy_urls_broken', 0)}/{migration.get('legacy_urls_tested', 0)} sampled legacy URLs are broken (4xx) after migration.**\n")
        if ahrefs:
            f.write("\n## Ahrefs domain data\n| Domain | DR | Org. traffic/mo | Org. keywords |\n|---|---|---|---|\n")
            for d, v in ahrefs.items():
                f.write(f"| {d} | {v.get('dr','?')} | {v.get('org_traffic','?')} | {v.get('org_keywords','?')} |\n")
        if kw_results:
            f.write("\n## Ahrefs keywords\n| Keyword | Volume/mo | Difficulty | CPC (cents) |\n|---|---|---|---|\n")
            for k in kw_results:
                f.write(f"| {k['keyword']} | {k.get('volume','?')} | {k.get('difficulty','?')} | {k.get('cpc','?')} |\n")

    print(f"\nDone. Evidence written to {out_dir}/")
    print("Still needed (not scriptable here): a live Google Business Profile check and, if useful, a")
    print("Playwright-measured LCP/CLS fallback if PageSpeed Insights is rate-limited. See SKILL.md.")


if __name__ == "__main__":
    main()
