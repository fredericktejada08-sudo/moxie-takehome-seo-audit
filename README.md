# Moxie Take-Home — AI-Enhanced SEO Audit (Track B)

An SEO audit of [Muse MedSpa](https://www.musemedspaaustin.com/), an independent single-location
medspa in Austin, TX, combining real tool data (Ahrefs API, live Google Business Profile check) with
an AI SEO-audit agent for synthesis, verification, and prioritization.

- **`AUDIT.md`** — the final deliverable: audit summary, top 5 prioritized recommendations, two
  AI-generated deliverables (rewritten meta titles/descriptions, a GBP/NAP consistency checklist), and
  reflection notes.
- **`SCORPIO_INTEL_RAW_OUTPUT.md`** — the AI agent's full, unedited output, given the prompt described
  in that file (raw HTML + real Ahrefs numbers + live GBP findings as evidence, with instructions to
  verify independently rather than trust the input at face value).
- **`home.html`, `services.html`, `services_laser-hair-removal.html`, `about.html`** — the raw fetched
  HTML that is the actual evidence base for the on-page findings (title tags, JSON-LD, alt text, etc).
- **`ahrefs_results.json`, `ahrefs_lookup.py`** — the real Ahrefs API pull (domain rating, organic
  traffic, ranking keywords) for Muse and three direct Austin competitors.
