# Moxie Take-Home — AI-Enhanced SEO Audit (Track B)

An SEO audit of [Muse MedSpa](https://www.musemedspaaustin.com/), an independent single-location
medspa in Austin, TX, combining real tool data (Ahrefs API, live Google Business Profile check) with
an AI SEO-audit agent for synthesis, verification, and prioritization.

## Run it again, on a different site

This isn't a one-off script — the whole method is packaged as a reusable command
(`.claude/skills/seo-audit/`, a [Claude Code](https://claude.com/claude-code) skill), in two forms.

**For a non-technical user — a local dashboard, no command line:**
```bash
python3 .claude/skills/seo-audit/dashboard.py
```
Opens a browser at `http://localhost:8799` with a plain form: website URL, optional competitor sites,
optional search terms to check demand for, optional business name/address. Click "Run audit," get back
a plain-English report — a clear banner on whether a broken site migration was found, real Google
Business Profile data, real Core Web Vitals (once enabled — see below), a competitive table, and a
numbered list of what to fix first. It calls the Anthropic API directly to write the plain-English
part; if no API key is configured it still shows all the real evidence, just without the narrative.

**APIs actually wired in, not just described:** Ahrefs (competitive benchmark + keyword volume/
difficulty), Google Places API (real Business Profile rating/reviews/category — verified to match a
live Google Search knowledge panel exactly, 4.9★/100 reviews, using a Google Maps Platform key already
provisioned for a separate project on this machine rather than a new one), and PageSpeed Insights
(real Core Web Vitals) — that last one currently returns a `403 blocked` error until the PageSpeed
Insights API is enabled for that key's Google Cloud project; both scripts report that honestly instead
of faking a score.

**For a technical user:**
```bash
python3 .claude/skills/seo-audit/gather_evidence.py \
  --url https://some-other-medspa.com \
  --competitors competitor1.com,competitor2.com \
  --pages "/,/about,/services" \
  --out ~/projects/seo-audits/some-other-medspa
```

Both share the same underlying evidence-gathering: page fetch, robots.txt, real Ahrefs competitive
data, and — the important one — a Wayback Machine platform-migration check that automatically tests
real legacy URLs against the live site if it detects one. That detection deliberately binary-searches
*backward from the live site's current platform* through capture history, not forward from the site's
very first capture — comparing only the two endpoints gives a false negative once Wayback re-crawls the
new platform, and comparing against the first-ever capture finds the *earliest* migration a site ever
made rather than the most recent one. Verified against `musemedspaaustin.com` itself, which turns out
to have migrated twice (Squarespace→WordPress in 2019, then WordPress→Webflow in 2026) — the tool
correctly finds the recent one, not the older one. Also re-run against a second, unrelated Austin
medspa (`beauxmedspa.com`, no migration) while building this, specifically to confirm it generalizes
and doesn't produce a false positive.

`SKILL.md` documents the one step that's still manual (a third-party reputation scan — Yelp/Birdeye/
etc. — since no general-purpose search API is configured here) and how to synthesize everything into a
report. See `.claude/skills/seo-audit/SKILL.md` for the full procedure.

- **`AUDIT.md`** — the final deliverable: audit summary, top 6 prioritized recommendations, two
  AI-generated deliverables (rewritten meta titles/descriptions, a GBP/NAP consistency checklist), and
  reflection notes.
- **`SCORPIO_INTEL_RAW_OUTPUT.md`** — the AI agent's full, unedited output, given the prompt described
  in that file (raw HTML + real Ahrefs numbers + live GBP findings as evidence, with instructions to
  verify independently rather than trust the input at face value).
- **`LIVE_VERIFICATION_FOLLOWUP.md`** — closes out every item the first-pass audit flagged as
  "cannot confirm from HTML." This is where the headline finding of the whole audit turned up: a live
  redirect test proves the site's 2026 WordPress→Webflow migration left every legacy URL 404ing
  instead of redirecting.
- **`home.html`, `services.html`, `services_laser-hair-removal.html`, `about.html`** — the raw fetched
  HTML that is the actual evidence base for the on-page findings (title tags, JSON-LD, alt text, etc).
- **`wordpress_last_capture_2026-01-20.html`, `webflow_first_capture_2026-05-15.html`, `thank-you.html`,
  `wayback_history.json`** — supporting evidence for the migration finding: the last archived
  WordPress capture, the first archived Webflow capture, the site's thin/unindexed thank-you page, and
  the raw Wayback Machine capture history.
- **`ahrefs_results.json`, `ahrefs_lookup.py`** — the real Ahrefs API pull (domain rating, organic
  traffic, ranking keywords) for Muse and three direct Austin competitors.
