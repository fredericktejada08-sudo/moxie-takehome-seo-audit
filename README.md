# Moxie Take-Home — AI-Enhanced SEO Audit (Track B)

An SEO audit of [Muse MedSpa](https://www.musemedspaaustin.com/), an independent single-location
medspa in Austin, TX, combining real tool data (Ahrefs API, live Google Business Profile check) with
an AI SEO-audit agent for synthesis, verification, and prioritization.

## Run it again, on a different site

This isn't a one-off script — the whole method is packaged as a reusable command
(`.claude/skills/seo-audit/`, a [Claude Code](https://claude.com/claude-code) skill). Starting point:

```bash
python3 .claude/skills/seo-audit/gather_evidence.py \
  --url https://some-other-medspa.com \
  --competitors competitor1.com,competitor2.com \
  --pages "/,/about,/services" \
  --out ~/projects/seo-audits/some-other-medspa
```

That handles every scriptable part: page fetch, robots.txt, real Ahrefs competitive data, and —
the important one — a Wayback Machine platform-fingerprint check that automatically tests real legacy
URLs against the live site if it detects a migration. It was re-run against a second, unrelated Austin
medspa (`beauxmedspa.com`) while building this to confirm it actually generalizes, not just works once.
`SKILL.md` documents the two steps that still need a live tool (Google Business Profile, Core Web
Vitals) and how to synthesize everything into a report. See `.claude/skills/seo-audit/SKILL.md` for
the full procedure.

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
