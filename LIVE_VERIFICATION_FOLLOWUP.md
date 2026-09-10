# Live verification follow-up

The original audit (`SCORPIO_INTEL_RAW_OUTPUT.md`) flagged six items as "cannot be confirmed from
HTML — needs a live check." This follow-up closes out all six using live tools: the Wayback Machine's
public API, direct HTTP redirect testing, Google's PageSpeed Insights API, Playwright (real-browser
performance measurement), and the Ahrefs Keywords Explorer endpoint. Every number below is a real
tool output, not an estimate — commands/timestamps included so it's independently reproducible.

## 1. Google Business Profile rating/review count — CONFIRMED (Playwright, live Google search)
4.9 stars, 100 Google reviews, categorized "Medical spa in West Lake Hills, Texas." Directly visible
in Google's own SERP knowledge panel for "Muse MedSpa Austin Bee Caves Road" — captured live via
browser automation. This is what's behind the AUDIT.md GBP checklist.

## 2. Was there a recent platform migration that reset backlink/authority history? — CONFIRMED, and it's worse than "reset history"
This is the most important finding in the entire audit, and it upgrades recommendation 5 from a
ranked hypothesis to a proven root cause.

**Wayback Machine capture history** (`http://web.archive.org/cdx/search/cdx?url=musemedspaaustin.com...`):
- The site ran on **WordPress** continuously from at least 2017 through **2026-01-20** (confirmed:
  that capture contains 105 `wordpress`/`wp-content` references, 0 Webflow references, title
  `"Med Spa Austin | Medical Spa Westlake | Muse Med Spa"`).
- By **2026-05-15**, the site is on **Webflow** (0 WordPress references, 5 Webflow references, title
  `"Medical Spa in Austin, Texas | Laser Hair Removal"`).
- So the WordPress -> Webflow migration happened in a roughly 4-month window in early-to-mid 2026 —
  recent, not historical.
- **The old WordPress title explicitly included "Westlake."** The new Webflow site drops it entirely.
  This is the direct, mechanical explanation for the GBP mismatch in finding #1 above (GBP still
  categorizes the business under "West Lake Hills," but the current site no longer reinforces that
  geo term anywhere) — it's a regression from the migration, not a pre-existing inconsistency.

**Legacy URL redirect test** (direct `curl` against 17 real URLs pulled from the last WordPress
capture's own internal navigation):
```
/laser-hair-removal/          -> 301 -> /laser-hair-removal          -> 404
/injectable-treatments/       -> 301 -> /injectable-treatments       -> 404
/facial-skin-treatments/      -> 301 -> /facial-skin-treatments      -> 404
/meet-the-team/               -> 301 -> /meet-the-team               -> 404
/male-aesthetics/             -> 301 -> /male-aesthetics             -> 404
/testimonials/                -> 301 -> /testimonials                -> 404
/coolpeel/, /profound/, /attiva/, /truflex/, /ultherapy/,
/sclerotherapy/, /microblading-brow-treatment/, /prf-hair-growth/,
/body-contouringfat-reduction/, /monthly-specials/, /muse-gallery/  -> 301 -> (trailing slash stripped) -> 404
```
**All 17 tested legacy URLs return a genuine 404** ("Not Found" title, not a soft-404 redirect to the
homepage). The 301 that fires is just Webflow's default trailing-slash normalization — it is not an
intentional URL-mapping redirect from the old site structure to the new one. **A decade of accumulated
backlinks, cached rankings, and direct/bookmarked traffic pointing at any of these old URLs currently
lands on a dead page.** This is almost certainly the primary driver of the DR 8 / 5-ranking-keywords
collapse identified in the original Ahrefs pull — not the on-page/schema issues, which are real but
secondary.

**Action, and it should now be recommendation #1, above the on-page fixes:** map every indexed legacy
URL (start with the ~17+ found in the last WordPress capture, but pull the full list from Ahrefs'
backlink report or Search Console's legacy index) to its correct new-site equivalent and add real
301s. This is a bigger lever than any single on-page fix in this audit.

## 3. robots.txt — CONFIRMED clean
`curl https://www.musemedspaaustin.com/robots.txt` returns only `Sitemap: https://www.musemedspaaustin.com/sitemap.xml`
— no Disallow rules. Not blocking crawlers.

## 4. Does /thank-you (and similar utility pages) carry noindex? — CONFIRMED: it does NOT, and it should
`curl` of `/thank-you` returns HTTP 200, no `<meta name="robots">` tag at all, and ~156 words of content
that's just nav boilerplate plus a generic "Success!" message. It's indexable today. Minor relative to
finding #2, but a genuine, free fix: add `noindex, follow`.

## 5. Core Web Vitals (LCP/CLS) — PARTIALLY CONFIRMED
Google's PageSpeed Insights API (`pagespeedonline.googleapis.com`) returned `429 RESOURCE_EXHAUSTED`
against the shared daily quota (no dedicated API key configured) — logging the attempt honestly rather
than skipping it. Fell back to Playwright, measuring real `PerformanceObserver` LCP/CLS/FCP directly in
a live Chromium session:

| Page | LCP | CLS | FCP |
|---|---|---|---|
| Homepage | 2,492 ms | 0.025 | 968 ms |
| Laser hair removal | 432 ms | 0.025 | 204 ms |

CLS is comfortably in the "good" range (<0.1) on both pages — a real, repeatable signal since layout
shift isn't cache-sensitive. LCP/FCP are directionally fine (homepage's 2,492ms sits right at the "good"
threshold) but **this is a single unthrottled lab sample on a fast connection, not CrUX real-user field
data or a simulated-mobile-network Lighthouse run** — treat as "no red flag visible," not as a
verified pass/fail against Google's actual CWV thresholds.

## 6. Keyword difficulty/volume for the content-gap recommendation — CONFIRMED (Ahrefs Keywords Explorer)
| Keyword | Volume/mo (US) | Difficulty | CPC |
|---|---|---|---|
| laser hair removal austin | 1,000 | 31 (medium) | $8.00 |
| laser hair removal austin cost | 100 | 0 (effectively no competition) | $8.00 |
| medical spa austin | 250 | 47 (medium-high) | $1.80 |

This confirms the specific content-gap recommendation in AUDIT.md with real numbers instead of a
directional estimate: "laser hair removal austin cost" has genuine monthly demand and zero measured
difficulty — a concrete, low-effort, high-confidence content target once the redirect issue (finding
#2) is fixed enough for the site to be crawled/ranked at all again.
