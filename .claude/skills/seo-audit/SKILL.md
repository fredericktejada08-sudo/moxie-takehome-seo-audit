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
the target + competitors, and — the important part — Wayback Machine capture history with a
platform-fingerprint check (Webflow/WordPress/Squarespace/Wix/Shopify markers). If it detects the
live platform differs from the last archived capture, it automatically extracts real internal links
from that last capture and tests each one against the live site for a broken (4xx) landing, reporting
`legacy_urls_broken / legacy_urls_tested` in `SUMMARY.md`. Read that file first — it's the deterministic
ground truth everything else builds on.

Known limitation, already handled but worth knowing about: the Wayback CDX API is slower than a normal
page fetch and can take 30-45s on a domain with a long capture history — the script uses a longer
timeout with one retry for Wayback calls specifically. If `wayback_history.json` still comes back
empty, say so plainly rather than assuming "no migration."

## Step 2 — Live checks that can't be scripted (do these directly)

- **Google Business Profile**: navigate to a Google search for `"<business name>" <city> <street>` via
  Playwright, snapshot the knowledge panel, and record the actual star rating, review count, and
  category as Google displays them — this is frequently NOT the same as what general web search
  results show, and cannot be inferred from HTML.
- **Core Web Vitals**: try Google's PageSpeed Insights API first
  (`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile&category=performance`).
  It shares a public quota and can return `429`. If it does, fall back to measuring real LCP/CLS/FCP
  directly in a live Playwright session via `PerformanceObserver` (see
  `~/projects/moxie-takehome/AUDIT.md` for the exact snippet used) — say explicitly that this is
  single-sample, unthrottled lab data, not CrUX field data, if you use the fallback.
- **Reputation scan**: WebSearch across Yelp/Birdeye/Facebook/etc. for review counts, and note if the
  native Google count (from the step above) is meaningfully different from third-party platforms.

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
