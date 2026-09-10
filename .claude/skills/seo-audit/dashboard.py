#!/usr/bin/env python3
"""Local, no-install SEO audit dashboard for non-technical users.

Run it:
    python3 dashboard.py

Then open http://localhost:8799 in a browser, fill in a website URL (and
optionally 1-3 competitor websites), and click "Run audit". No command-line
flags, no JSON, no separate steps — one form, one report.

Stdlib only (http.server + urllib), except it calls the Anthropic API over
plain HTTPS (no SDK needed) to turn the raw evidence into a plain-English,
prioritized report. Reuses the same evidence-gathering code as
gather_evidence.py in this folder (page fetch, robots.txt, real Ahrefs
competitive data, Wayback Machine platform-migration check).
"""
import datetime
import html
import json
import os
import re
import socketserver
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gather_evidence as ge  # noqa: E402  (reuses fetch/wayback/ahrefs helpers)

PORT = 8799
ANTHROPIC_ENV_PATH = "/home/fredericktejada/projects/dialpad-mcp/.env"
ANTHROPIC_MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """You are an SEO audit specialist writing for a small-business owner who is not \
technical. You are given REAL evidence already gathered by automated tools: on-page facts (title, \
meta description, headings, structured-data types found, image alt-text coverage) for one or more \
pages, real Ahrefs competitive benchmark numbers, and a Wayback Machine platform-migration check that \
may have found broken legacy URLs after a site redesign.

Rules:
- Only state things the evidence actually shows. Do not invent metrics, rankings, or claims you \
were not given.
- If the migration check found broken legacy URLs, treat that as the single most important finding \
and explain simply why it matters (old links and search history pointing at dead pages).
- Avoid SEO jargon where possible; where a technical term is unavoidable (e.g. "schema markup"), \
define it in one short clause the first time you use it.
- Explicitly say what could NOT be checked automatically (e.g. the business's real Google Business \
Profile rating, real-user page speed) rather than guessing or ignoring it.
- End with a short numbered list: the top 3-5 things to fix, in priority order, each with a one-line \
plain-English reason "why it matters", written so a non-technical owner could hand it to a web \
developer as-is.

Write in plain paragraphs and simple numbered/bulleted lists. No code blocks."""


def load_anthropic_key():
    env = ge.load_env(ANTHROPIC_ENV_PATH)
    return env.get("ANTHROPIC_API_KEY", "")


def call_claude(user_content):
    key = load_anthropic_key()
    if not key:
        return None, "ANTHROPIC_API_KEY not found — showing raw evidence only (see below)."
    payload = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": 2000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
            text = "".join(b.get("text", "") for b in data.get("content", []))
            return text, None
    except urllib.error.HTTPError as e:
        return None, f"Anthropic API error {e.code}: {e.read().decode()[:300]}"
    except Exception as e:
        return None, f"Anthropic API call failed: {e}"


def extract_onpage_facts(url, html_text):
    if not html_text:
        return {"url": url, "error": "could not fetch page"}
    title_m = re.search(r"<title>(.*?)</title>", html_text, re.I | re.S)
    desc_m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html_text, re.I)
    if not desc_m:
        desc_m = re.search(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', html_text, re.I)
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html_text, re.I | re.S)
    h1s = [re.sub(r"<[^>]+>", "", h).strip() for h in h1s]
    jsonld_types = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S):
        try:
            data = json.loads(block)
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type") if isinstance(item, dict) else None
                if t:
                    jsonld_types.append(t)
        except Exception:
            jsonld_types.append("(unparseable JSON-LD)")
    imgs = re.findall(r"<img\b[^>]*>", html_text)
    empty_alt = sum(1 for i in imgs if re.search(r'alt=""', i))
    no_alt = sum(1 for i in imgs if "alt=" not in i)
    text_only = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", html_text, flags=re.S))
    word_count = len(text_only.split())
    return {
        "url": url,
        "title": html.unescape(title_m.group(1)).strip() if title_m else None,
        "meta_description": html.unescape(desc_m.group(1)).strip() if desc_m else None,
        "h1s": h1s,
        "jsonld_types": jsonld_types,
        "images_total": len(imgs),
        "images_empty_alt": empty_alt,
        "images_no_alt_attr": no_alt,
        "word_count": word_count,
    }


def discover_pages(base_url, home_html):
    """Homepage plus up to 2 auto-discovered internal pages (services/about/contact-style)."""
    domain = urllib.parse.urlparse(base_url).netloc
    candidates = re.findall(rf'href="https?://(?:www\.)?{re.escape(domain)}/([a-z0-9/_-]+)"', home_html or "", re.I)
    keywords = ["service", "about", "location", "treatment", "product", "contact"]
    picked = []
    for path in candidates:
        if any(k in path.lower() for k in keywords) and path not in picked:
            picked.append(path)
        if len(picked) >= 2:
            break
    return [""] + picked  # "" = homepage itself


def run_audit(url, competitors, keywords):
    result = {"url": url, "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    domain = urllib.parse.urlparse(url).netloc

    status, home_html = ge.fetch(url)
    if status != 200 or not home_html:
        result["fetch_error"] = f"Could not fetch {url} (status {status})"
        return result

    pages_to_check = discover_pages(url, home_html)
    page_facts = []
    for path in pages_to_check:
        full = urllib.parse.urljoin(url, path)
        if path == "":
            page_html = home_html
        else:
            _, page_html = ge.fetch(full)
        page_facts.append(extract_onpage_facts(full, page_html))
    result["pages"] = page_facts

    _, robots = ge.fetch(urllib.parse.urljoin(url, "/robots.txt"))
    result["robots_has_disallow"] = bool(robots and "disallow" in robots.lower() and
                                          re.search(r"disallow:\s*\S", robots, re.I))

    history = ge.wayback_history(domain)
    live_platform = ge.detect_platform(home_html)
    migration = ge.find_platform_transition(domain, history, live_platform)
    if migration["detected"]:
        last_old_ts = migration["last_old_capture"]
        _, last_old_html = ge.wayback_capture_html(domain, last_old_ts)
        legacy_paths = ge.extract_internal_links(last_old_html, domain)[:15]
        tests = [ge.test_redirect(domain, p) for p in legacy_paths]
        broken = [t for t in tests if str(t["final_status"]).startswith("4")]
        migration["legacy_urls_tested"] = len(tests)
        migration["legacy_urls_broken"] = len(broken)
    result["migration"] = migration

    ahrefs = {}
    token = ge.load_env(ge.DEFAULT_AHREFS_ENV).get("AHREFS_API_TOKEN", "")
    if token:
        as_of = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        domains = [domain] + [c.strip() for c in competitors if c.strip()]
        for d in domains:
            ahrefs[d] = ge.ahrefs_domain_data(d, token, "us", as_of)
    result["ahrefs"] = ahrefs

    kw_results = []
    kw_terms = [k.strip() for k in keywords if k.strip()]
    if kw_terms and token:
        r = ge.ahrefs_get("/keywords-explorer/overview",
                           {"country": "us", "select": "keyword,volume,difficulty,cpc,clicks,global_volume",
                            "keywords": ",".join(kw_terms)}, token)
        if r:
            kw_results = r.get("keywords", [])
    result["keywords"] = kw_results

    # Ask Claude to turn the raw evidence into a plain-English, prioritized report.
    evidence_for_claude = {k: v for k, v in result.items() if k != "generated_at"}
    ai_text, ai_error = call_claude(
        "Here is the automated evidence for a website SEO audit:\n\n" +
        json.dumps(evidence_for_claude, indent=2))
    result["ai_summary"] = ai_text
    result["ai_error"] = ai_error
    return result


# ---------- minimal, safe rendering (everything derived from fetched sites is HTML-escaped) ----------

def esc(v):
    return html.escape(str(v)) if v is not None else ""


def markdown_lite_to_html(text):
    if not text:
        return ""
    lines = text.split("\n")
    out, in_list = [], False
    for line in lines:
        line = esc(line.strip())
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        if line.startswith("### ") or line.startswith("## ") or line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h4>{line.lstrip('#').strip()}</h4>")
        elif re.match(r"^(\d+\.|-|\*)\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item_text = re.sub(r"^(\d+\.|-|\*)\s+", "", line)
            out.append(f"<li>{item_text}</li>")
        elif line == "":
            if in_list:
                out.append("</ul>")
                in_list = False
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{line}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


PAGE_HEAD = """<!doctype html>
<html><head><meta charset="utf-8"><title>SEO Audit Dashboard</title>
<style>
body { font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; max-width: 900px;
       margin: 40px auto; padding: 0 20px; color: #1a1a2e; background: #fafafa; }
h1 { font-size: 1.6em; } h2 { font-size: 1.25em; margin-top: 2em; border-bottom: 2px solid #eee; padding-bottom: 6px; }
h4 { margin-bottom: 4px; }
label { display: block; margin-top: 14px; font-weight: 600; }
input[type=text] { width: 100%; padding: 10px; font-size: 1em; margin-top: 4px; border: 1px solid #ccc; border-radius: 6px; }
button { margin-top: 20px; padding: 12px 24px; font-size: 1.05em; background: #4f46e5; color: white;
         border: none; border-radius: 6px; cursor: pointer; }
button:hover { background: #4338ca; }
.hint { color: #666; font-size: 0.9em; margin-top: 2px; }
.banner { padding: 14px 18px; border-radius: 8px; margin: 16px 0; font-weight: 600; }
.banner.bad { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.banner.good { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.banner.neutral { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 0.95em; }
th { background: #f3f4f6; }
.card { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px 20px; margin: 12px 0; }
.small { color: #666; font-size: 0.85em; }
a.back { display: inline-block; margin-top: 24px; }
</style></head><body>
"""
PAGE_TAIL = "</body></html>"


def render_form(error=None):
    err_html = f'<div class="banner bad">{esc(error)}</div>' if error else ""
    return PAGE_HEAD + f"""
<h1>SEO Audit Dashboard</h1>
<p class="small">Enter a website below. This checks the page itself, compares it to competitors using
real Ahrefs data, and checks whether a past site redesign broke any old links — then writes up a
plain-English report of what to fix first.</p>
{err_html}
<form method="POST" action="/audit">
  <label for="url">Website to audit</label>
  <input type="text" id="url" name="url" placeholder="https://example.com" required>
  <div class="hint">The homepage URL of the business you want to check.</div>

  <label for="competitors">Competitor websites (optional)</label>
  <input type="text" id="competitors" name="competitors" placeholder="competitor1.com, competitor2.com">
  <div class="hint">Comma-separated. Used to show how this site compares.</div>

  <label for="keywords">Search terms to check demand for (optional)</label>
  <input type="text" id="keywords" name="keywords" placeholder="laser hair removal austin">
  <div class="hint">Comma-separated. Real monthly search volume will be looked up for each.</div>

  <button type="submit">Run audit</button>
</form>
""" + PAGE_TAIL


def render_results(r):
    if r.get("fetch_error"):
        return PAGE_HEAD + f'<div class="banner bad">{esc(r["fetch_error"])}</div><a class="back" href="/">&larr; Try again</a>' + PAGE_TAIL

    parts = [f"<h1>SEO Audit — {esc(urllib.parse.urlparse(r['url']).netloc)}</h1>"]
    parts.append(f'<p class="small">Generated {esc(r["generated_at"])}</p>')

    m = r["migration"]
    if m.get("detected"):
        broken, total = m.get("legacy_urls_broken", 0), m.get("legacy_urls_tested", 0)
        parts.append(f'<div class="banner bad">⚠ This site changed platforms recently '
                      f'(around the site\'s archived history), and {broken} of {total} old page '
                      f'links tested now lead to a broken page instead of redirecting properly. '
                      f'Any past Google ranking or links pointing at those old pages are likely being '
                      f'wasted.</div>')
    elif m.get("checked"):
        parts.append('<div class="banner good">✓ No sign of a broken site migration — old page links '
                      'still resolve correctly.</div>')
    else:
        parts.append('<div class="banner neutral">Could not check site history (no archive data '
                      'found for this domain).</div>')

    if r.get("ai_summary"):
        parts.append("<h2>Plain-English summary &amp; what to fix first</h2>")
        parts.append(f'<div class="card">{markdown_lite_to_html(r["ai_summary"])}</div>')
    elif r.get("ai_error"):
        parts.append(f'<div class="banner neutral">{esc(r["ai_error"])}</div>')

    parts.append("<h2>Pages checked</h2>")
    for p in r["pages"]:
        parts.append('<div class="card">')
        parts.append(f'<strong>{esc(p.get("url"))}</strong><br>')
        if p.get("error"):
            parts.append(f'<span class="small">{esc(p["error"])}</span>')
        else:
            parts.append(f'Title: {esc(p.get("title") or "(missing)")}<br>')
            parts.append(f'Meta description: {esc(p.get("meta_description") or "(missing)")}<br>')
            parts.append(f'Headings (H1): {esc(", ".join(p.get("h1s") or []) or "(none found)")}<br>')
            parts.append(f'Structured data found: {esc(", ".join(p.get("jsonld_types") or []) or "none")}<br>')
            alt_total = p.get("images_total", 0)
            alt_empty = p.get("images_empty_alt", 0)
            parts.append(f'Images: {alt_total} total, {alt_empty} with no descriptive text (alt text)<br>')
            parts.append(f'<span class="small">~{p.get("word_count", 0)} words on this page</span>')
        parts.append("</div>")

    if r.get("ahrefs"):
        parts.append("<h2>Competitive benchmark (real Ahrefs data)</h2>")
        parts.append("<table><tr><th>Site</th><th>Authority score (DR)</th><th>Est. monthly visitors from search</th><th># of search terms it ranks for</th></tr>")
        for d, v in r["ahrefs"].items():
            parts.append(f"<tr><td>{esc(d)}</td><td>{esc(v.get('dr','?'))}</td>"
                          f"<td>{esc(v.get('org_traffic','?'))}</td><td>{esc(v.get('org_keywords','?'))}</td></tr>")
        parts.append("</table>")

    if r.get("keywords"):
        parts.append("<h2>Search demand for your terms</h2>")
        parts.append("<table><tr><th>Search term</th><th>Monthly searches (US)</th><th>Difficulty</th></tr>")
        for k in r["keywords"]:
            parts.append(f"<tr><td>{esc(k.get('keyword'))}</td><td>{esc(k.get('volume','?'))}</td>"
                          f"<td>{esc(k.get('difficulty','?'))}</td></tr>")
        parts.append("</table>")

    parts.append('<a class="back" href="/">&larr; Run another audit</a>')
    return PAGE_HEAD + "\n".join(parts) + PAGE_TAIL


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet for a non-technical user

    def do_GET(self):
        if self.path == "/":
            body = render_form().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/audit":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        fields = parse_qs(self.rfile.read(length).decode())
        url = (fields.get("url", [""])[0] or "").strip()
        competitors = (fields.get("competitors", [""])[0] or "").split(",")
        keywords = (fields.get("keywords", [""])[0] or "").split(",")

        if not re.match(r"^https?://", url):
            url = "https://" + url
        if not url or "." not in url:
            body = render_form(error="Please enter a valid website address.").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        try:
            result = run_audit(url, competitors, keywords)
            body = render_results(result).encode()
        except Exception as e:
            body = render_form(error=f"Something went wrong running the audit: {e}").encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), Handler)
    url = f"http://localhost:{PORT}"
    print(f"SEO Audit Dashboard running at {url}")
    print("Press Ctrl+C to stop.")
    threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
