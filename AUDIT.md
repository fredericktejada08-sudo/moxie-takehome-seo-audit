# Muse MedSpa (musemedspaaustin.com) — SEO Audit
Moxie Take-Home Exercise, Track B — AI-Enhanced SEO Audit

## Audit summary

**Target:** Muse MedSpa, an independent single-location medspa in Austin, TX (4201 Bee Caves Rd
#B200), established 2016. Publicly accessible, not part of a chain.

**What I looked at:**
- On-page/technical review of 4 pages (homepage, `/services` hub, `/services/laser-hair-removal`,
  `/about`) — title tags, meta descriptions, H1s, JSON-LD structured data, image alt text, canonicals,
  internal linking.
- Ahrefs API (Site Explorer) — domain rating and organic traffic/keyword metrics for Muse and 3 direct
  Austin competitors (Refine Aesthetics, Beaux MedSpa, Viva Day Spa).
- Live Google Business Profile / SERP check (via browser) — star rating, review count, category,
  NAP data as it actually displays in Google.
- Reputation scan across third-party review platforms (Yelp, Birdeye, Facebook, TrustAnalytica,
  ZipAppointments, RealSelf).
- An AI SEO specialist (Claude, prompted with a fixed audit method) independently re-verified the
  on-page claims below against the raw HTML rather than trusting my first-pass read — it caught one
  real mistake in my brief (see Reflection).
- A live follow-up (`LIVE_VERIFICATION_FOLLOWUP.md`) closing out every item the first pass flagged as
  "can't confirm from HTML": Wayback Machine capture history + direct redirect testing, Google's
  PageSpeed Insights API (hit a quota wall, logged honestly), a Playwright-measured real-browser
  LCP/CLS fallback, and real Ahrefs Keywords Explorer volume/difficulty numbers.

**Headline finding:** Muse's site is professionally built with no major indexability problems, but sits
at **Ahrefs Domain Rating 8, ~46 est. monthly organic visits, and only 5 ranking organic keywords** —
against direct local competitors at DR 21–50 and 107–2,240 ranking keywords. The on-page issues below
are real and worth fixing, but a live follow-up check (see `LIVE_VERIFICATION_FOLLOWUP.md`) found the
actual primary cause: **the site migrated from WordPress to Webflow in early-to-mid 2026, and every
tested legacy URL from the old site now 404s instead of redirecting** — a decade of accumulated
backlinks and rankings currently point at dead pages. That's recommendation #1 below, and it outranks
everything else in this audit.

## Top 6 prioritized recommendations

**1. Fix the broken legacy-URL redirects from the WordPress→Webflow migration. (Critical — confirmed root cause)**
Live-verified, not a hypothesis: the Wayback Machine shows the site was still on WordPress as of
2026-01-20 and on Webflow by 2026-05-15. Every one of 17 real legacy URLs pulled from the last
WordPress capture's own navigation (`/laser-hair-removal/`, `/injectable-treatments/`,
`/testimonials/`, `/meet-the-team/`, etc.) currently 301s only to strip its trailing slash, then
**404s** — none of them land on the equivalent new-site page. That's a decade of backlinks and cached
rankings pointing at dead pages, which is the far more likely explanation for DR 8 / 5 keywords than
any on-page issue below.
*Rationale: this is a bigger lever than every other recommendation in this audit combined — map the
full list of previously-indexed URLs (pull from Ahrefs' backlink report or GSC's legacy index, not
just the 17 sampled here) to their new-site equivalents and add real 301s.*

**2. Fix title tags to lead with the brand and the full service range, not one service. (Critical)**
The homepage `<title>` is *"Medical Spa in Austin, Texas | Laser Hair Removal"* — it drops the brand
name entirely and over-indexes on one of ~7 service categories, even though Muse also does
injectables, body treatments, and wellness. The laser-hair-removal service page has the same
brand-omission problem. This is a same-day fix with no downside.
*Rationale: title tags are the single highest-leverage on-page SEO element and directly drive
search-result CTR; omitting the brand also weakens entity/brand-search association.*

**3. Add structured data to the laser-hair-removal service page — it currently has none. (Critical)**
Home, `/services`, and `/about` all carry some JSON-LD; the actual service page (the highest
commercial-intent page type on the site) has zero. Add a `Service`/`MedicalProcedure` node plus
`BreadcrumbList`.
*Rationale: this is the page type most likely to be searched with transactional intent, and it's the
one with no structured data backing it at all — an inconsistency, not a deliberate choice.*

**4. Write real alt text for content-bearing images sitewide. (Critical)**
Every sampled image across all 4 pages (83 total) has `alt=""` — confirmed independently by two
separate passes. Team photos, service cards, and treatment imagery currently have zero alt text.
*Rationale: zero cost to accessibility, zero image-search visibility today. This is a pure gap, not a
trade-off — decorative/background images can stay empty, but content images shouldn't be.*

**5. Fix NAP and geo-data inconsistencies — found in both the site's own code and off-site. (High)**
Three separate, independently-confirmed issues: (a) the `/about` page's JSON-LD lists coordinates
~1.5 miles away from where the site's own footer Google Maps link points, and the `/services` page's
schema puts a Maps URL in a field meant for actual latitude/longitude; (b) live search turned up a
stale citation on CareCredit's directory still listing Muse's *old* address (5524 Bee Cave Rd) instead
of the current one (4201 Bee Caves Rd); (c) Google Business Profile categorizes the business under
"West Lake Hills, Texas" while every page of the *current* site optimizes for "Austin" — and this one
now has a confirmed mechanical cause, not just a coincidence: the old WordPress site's title
explicitly said *"Medical Spa Westlake"* (see `LIVE_VERIFICATION_FOLLOWUP.md`), and that geo term was
simply dropped in the Webflow rewrite. It's a regression from the migration, not a pre-existing gap.
*Rationale: NAP/geo consistency across the web is a direct local-ranking input, separate from
on-site content quality — and these are all verified sitting live today, not theoretical.*

**6. Once the redirects are fixed, close the content gap with real, verified demand.** (Medium — sequenced after #1)
The site's own blog already proves a working content pattern (a lip filler cost post) that hasn't been
applied to the laser-hair-removal page, which currently has zero pricing content. This is no longer a
directional guess — Ahrefs Keywords Explorer confirms **"laser hair removal austin cost" gets 100
real monthly US searches at a measured keyword difficulty of 0** (essentially no competition), against
the head term "laser hair removal austin" at 1,000/mo, difficulty 31. This is exactly the kind of
low-effort, high-confidence opportunity worth acting on — but sequenced behind #1, since new content
on a page whose historical link equity is currently 404ing elsewhere on the domain won't get the
crawl/ranking credit it deserves until that's fixed.
*Rationale: real, measured demand at zero difficulty is as close to a "just do this" as SEO
recommendations get — the only reason it's not #1 is that #1 is a prerequisite for it to matter.*

## AI-generated deliverable 1: rewritten meta titles & descriptions

| Page | Current | Rewritten |
|---|---|---|
| Homepage — title | `Medical Spa in Austin, Texas \| Laser Hair Removal` (49 chars) | `Muse MedSpa \| Austin Med Spa, Injectables & Laser Care` (56 chars) |
| Homepage — description | `Visit our medical spa in Austin, Texas for microneedling, laser hair removal, facials, and advanced skin treatments tailored to your aesthetic goals.` | `Muse MedSpa is Austin's boutique medical spa for injectables, laser hair removal, microneedling, and facials — real results, personalized care since 2016.` (154 chars) |
| Laser hair removal — title | `Laser Hair Removal in Austin, Texas \| Medical Spa Care` (56 chars) | `Laser Hair Removal in Austin, Texas \| Muse MedSpa` (49 chars) |
| Laser hair removal — description | `Experience laser hair removal at our medical spa in Austin, Texas for smooth, long-lasting results with advanced, safe, and effective treatments.` | `Laser hair removal at Muse MedSpa in Austin, TX — smooth, long-lasting results with advanced technology. See pricing, sessions needed, and book today.` (150 chars) |

Both rewrites keep the location + service keyword the originals already had right, add the brand name
back in, and — on the service page — plant the "pricing/sessions" hook that the content-gap finding
(recommendation 6) says is missing from the page entirely.

## AI-generated deliverable 2 (bonus): GBP / NAP consistency checklist

Built from the live GBP check + citation scan, not assumptions:

- [ ] Correct the stale address on CareCredit's directory listing (currently shows the old 5524 Bee
      Cave Rd address instead of the current 4201 Bee Caves Rd #B200)
- [ ] Decide and standardize the primary city: GBP currently surfaces as "West Lake Hills, Texas"
      while the entire website optimizes for "Austin" — either add Austin explicitly as a serviced
      area in GBP or align on-site copy, don't leave this to default categorization
- [ ] Pull the exact lat/long from the live GBP listing and apply it consistently in the site's own
      JSON-LD (currently two different coordinate sources on the site disagree by ~1.5 miles)
- [ ] Run a full citation audit (Yext, Moz Local, or a manual pass across the major directories) to
      catch other stale-address listings beyond the one found on CareCredit
- [ ] Redirect review-request effort specifically toward Google (currently 100 reviews/4.9★ on Google
      vs. 139 on Birdeye, 69 on Yelp) — Google reviews influence Local Pack ranking directly; the
      site's own on-page review schema does not (Google's review-rich-result policy explicitly
      excludes self-hosted reviews about your own business — sourced, not assumed)

## Reflection — raw material, not written for you

Per the exercise's own rule, the written reflection has to be in your voice, so I'm not drafting that
section — but here's what actually happened during the build, factually, in case it's useful raw
material:

- The AI audit agent **caught a real error in my own brief**: I told it the site had no blog (based on
  4 pages I'd manually fetched); it independently checked the sitemap, found `/blog` with 5 live posts,
  and flagged the correction before proceeding.
- It **verified my claims rather than trusting them** — re-derived the alt-text and schema findings
  from the raw HTML itself instead of accepting my summary, and it corrected the framing on one thing
  I'd assumed (that missing FAQ schema was a loss) by sourcing Google's actual current policy on
  self-hosted review rich results instead.
- Where it had to be reined in / where a human step was genuinely required: the agent could not access
  Search Console, the Wayback Machine, a live browser, or PageSpeed Insights itself — for *why is the
  keyword gap so large*, it gave ranked, hedged hypotheses instead of a confident single answer, which
  was the right call given its evidence, but it took a separate human-run follow-up (Wayback Machine
  capture history + directly curling 17 legacy URLs) to actually confirm which hypothesis was true.
  That follow-up found something the on-page audit alone never could: the site quietly migrated
  platforms in 2026 and every one of its old URLs now 404s — which turned out to be the real headline
  finding of the whole audit, bigger than anything the first pass surfaced.
- Google's own PageSpeed Insights API hit a quota wall (429) with no error budget left for the day —
  worth naming as a real "AI/tool-chain limitation," not a AI-reasoning one: had to fall back to
  measuring Core Web Vitals directly in a live browser instead of the tool built for the job.
- Ahrefs' domain-rating/metrics endpoint rejected `date=today` and required an actual past ISO date —
  a small but real integration gotcha, not something either of us anticipated going in.

## Files in this folder
- `home.html`, `services.html`, `services_laser-hair-removal.html`, `about.html` — raw fetched HTML,
  the actual evidence base for the on-page findings above
- `ahrefs_results.json` / `ahrefs_lookup.py` — the real Ahrefs API pull (DR + organic traffic/keywords)
  for Muse and 3 competitors
- `SCORPIO_INTEL_RAW_OUTPUT.md` — the AI agent's full, unedited on-page audit output
- `LIVE_VERIFICATION_FOLLOWUP.md` — closes out every "cannot confirm from HTML" item from the first
  pass with real tool evidence (Wayback Machine, redirect testing, PageSpeed API, Playwright, Ahrefs
  Keywords Explorer) — this is where the WordPress→Webflow migration finding actually surfaced
