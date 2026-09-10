---
name: seo-audit
description: Run a full AI-enhanced SEO audit for one URL — on-page technical read, real Ahrefs competitive benchmark, live Google Business Profile check, and a platform-migration/redirect integrity check — then synthesize into a prioritized report. Use when asked to audit a website's SEO, benchmark it against competitors, or investigate why a site's organic search performance seems weak.
---

# SEO audit

Built from a real Moxie take-home exercise (Track B): an audit of an independent Austin medspa that
found the technical/on-page issues were real but secondary — the actual root cause was a recent
platform migration that broke every legacy URL. That live-verification step is not optional here; it
is what caught the real finding the on-page read alone missed.

## Usage

Two ways to run this, depending on the audience:

**Non-technical user — local dashboard, no command-line flags:**
```
python3 ~/.claude/skills/seo-audit/dashboard.py
```
Opens a browser at `http://localhost:8799` with a plain form (website URL, optional competitor
sites, optional search terms, optional business name/address). Fill it in, click "Run audit," get a
plain-English report with a clear red/green banner for the migration check, real Google Business
Profile data, real Core Web Vitals (when the API is enabled — see Step 2), a competitive table, and a
numbered priority list — no JSON, no code. It calls the Anthropic API directly (key loaded the same way
the rest of this machine's scripts do — see `call_claude()` in `dashboard.py`) to write the
plain-English synthesis; if that key isn't available it still shows all the raw evidence, just without
the write-up.

**Technical user / inside Claude Code:**
```
/seo-audit <url> [competitor1.com,competitor2.com,...]
```
Example: `/seo-audit https://example-medspa.com refineaesthetics.com,vivadayspa.com`

If no competitors are given, either skip the competitive-benchmark step or ask the user for 1-3 real
local competitors — don't invent them.

## Step 1 — Gather deterministic evidence (scripted)

```bash
python3 ~/.claude/skills/seo-audit/gather_evidence.py \
  --url <url> \
  --competitors <comma-separated domains, optional> \
  --pages "/,/about,/services" \
  --keywords "<1-3 target keywords, optional>" \
  --out ~/projects/seo-audits/<domain-slug>
```

This fetches the given pages' raw HTML, robots.txt, real Ahrefs domain-rating/traffic/keyword data for
the target + competitors, real Google Business Profile data (rating/reviews/category/address via the
Places API), real Core Web Vitals (PageSpeed Insights API), and — the important part — Wayback Machine
capture history with a platform-fingerprint check (Webflow/WordPress/Squarespace/Wix/Shopify markers).
If it detects the live platform differs from its capture history, it automatically extracts real
internal links from the last pre-migration capture and tests each one against the live site for a
broken (4xx) landing, reporting `legacy_urls_broken / legacy_urls_tested` in `SUMMARY.md`. Read that
file first — it's the deterministic ground truth everything else builds on.

Add `--business-query "Business Name, street address, city ST"` for a reliable Google Business Profile
match; without it, the script falls back to the fetched homepage's `<title>` + domain, which usually
works but is less precise for a common business name.

Known limitations, already handled but worth knowing about:
- The Wayback CDX API is slower than a normal page fetch and can take 30-45s on a domain with a long
  capture history — the script uses a longer timeout with one retry for Wayback calls specifically.
  If `wayback_history.json` still comes back empty, say so plainly rather than assuming "no migration."
- Some archived pages (and the live site itself, on some hosts) are served gzip-compressed; `fetch()`
  now decompresses based on `Content-Encoding` — without this it silently reads binary noise as "empty"
  HTML rather than erroring, which is worse than a loud failure. If a page's on-page facts look
  suspiciously empty, check this before assuming the page has no content.
- Migration detection (`find_platform_transition`) binary-searches BACKWARD from the live site's
  current platform through capture history, not forward from the first capture. Comparing only the
  last archived capture to live gives a false negative once Wayback re-crawls the new platform (can
  happen within days); comparing against the *first* capture finds whichever migration happened
  earliest in the site's history, not the most recent one, on a site that's changed platforms more than
  once. Verified against a real case (`musemedspaaustin.com`) that had switched Squarespace→WordPress in
  2019 and WordPress→Webflow in 2026 — the correct, recent answer is the second one.

## Step 2 — Google Business Profile + Core Web Vitals (now real APIs, not manual)

Both `gather_evidence.py` and `dashboard.py` call these automatically via `google_maps_key()`, reusing
a Google Maps Platform key already provisioned for a separate lead-gen project on this machine
(`~/projects/leadgen-starter/leadgen/.env`) rather than a new one:

- **Google Business Profile** (`places_text_search` + `places_details`, Places API New): real star
  rating, review count, category, formatted address, phone, hours, business status, Maps link. No
  browser needed. Verified against a live Playwright SERP check on the same business — numbers matched
  exactly (4.9★/100 reviews). Note: the Places API's structured `addressComponents.locality` can
  disagree with what a Google Search knowledge-panel label shows (seen in testing: Places API said
  "Austin," the SERP panel said "West Lake Hills," a real neighboring incorporated city near this
  particular address) — don't treat either source as automatically more authoritative than the other;
  flag the discrepancy for a human to resolve rather than picking one.
- **Core Web Vitals** (`pagespeed_insights`, PageSpeed Insights API with the same key): performance
  score, LCP, CLS, FCP, and real-user CrUX field data if Google has enough traffic data for the URL.
  **Known live issue**: this key's Google Cloud project currently returns `403 ... requests to this API
  ... are blocked` — the PageSpeed Insights API needs to be enabled for that project in Google Cloud
  Console (APIs & Services → Enable APIs → "PageSpeed Insights API"). This is an account-configuration
  step, not a code fix — both scripts already degrade gracefully (report the real error, don't fabricate
  a score) until it's enabled.
- **Reputation scan** (Yelp/Birdeye/etc.) is still a manual WebSearch step — no general-purpose search
  API is configured on this machine, so don't claim this one is automated.

## Step 3 — Synthesize

Dispatch to the `scorpio-intel` agent if available (Read/Grep/Glob/WebSearch/WebFetch, no Bash — it
should read the fetched HTML files directly rather than trust a summary of them), giving it:
- The raw HTML file paths from step 1's `--out` directory
- The real Ahrefs numbers from `SUMMARY.md`/`evidence.json` (not re-derived by the agent — it doesn't
  have API access)
- The live GBP/CWV findings from step 2
- Explicit instructions to verify claims independently against the HTML rather than trust the input,
  and to flag anything it can't confirm rather than guess

If `scorpio-intel` isn't available in this environment, follow its method directly: check
indexability, on-page (title/meta/H1/schema), content depth vs. competitors, and always separate
FACTS (sourced) from assumptions (flagged for a live check) before returning anything.

Structure the final report as: audit summary, prioritized recommendations (put a confirmed
platform-migration/redirect problem above on-page fixes if one was found — it is a bigger lever), at
least one AI-generated deliverable (rewritten meta tags, a GBP checklist, or a content brief), and an
honest note on what needed a live tool vs. what the AI could determine on its own.

## Reference implementation

`~/projects/moxie-takehome/` has a full worked example (Muse MedSpa, Austin) including the raw agent
output, the live-verification follow-up that found a real WordPress→Webflow migration with broken
redirects, and the final report — use it as the template for report structure and depth.
