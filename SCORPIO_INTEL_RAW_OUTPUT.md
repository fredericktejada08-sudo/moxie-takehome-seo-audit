# Raw AI agent output — unedited

This is the verbatim response from the Claude sub-agent ("scorpio-intel," configured with a fixed
SEO-audit method: verify claims independently against source evidence, cite file/line, separate fact
from assumption, self-correct before returning) given the prompt below. Nothing in this file has been
edited — `AUDIT.md` is the synthesized/prioritized version built from this output plus the Ahrefs and
live GBP evidence gathered separately.

## The prompt given to the agent

Target: Muse MedSpa (musemedspaaustin.com), an independent Austin, TX medspa. Provided: 4 raw HTML
files (home, services, laser-hair-removal, about), real Ahrefs API competitive data (DR/traffic/keyword
counts for Muse + 3 competitors), reputation data from third-party review platforms, and my own
first-pass technical findings (alt text, schema, title tags) — with an explicit instruction to verify
those findings independently rather than trust them, and to flag anything that needed a live check
(e.g., Google Business Profile data) rather than guess at it.

## The agent's full response

## SEO Audit: Muse MedSpa (musemedspaaustin.com) — Homepage, /services, /services/laser-hair-removal, /about

**Scope confirmed from your brief:** independent single-location Austin medspa, standalone personal exercise (not a TMC client). Primary conversion goal on all four pages is booking a consultation (every page repeats a "Book a Free consultation" / "Book Your Appointment" CTA to `/contact-us`). Target audience: Austin-area (skews Westlake/West Austin given the 78746 zip) women and men, mid-to-upper income, seeking non-surgical aesthetic and wellness treatments — informational-to-commercial intent for most service queries, transactional intent near "book"/"cost"/"near me" terms. I answered these myself from the HTML/business context rather than blocking on a question.

One correction to your brief before the findings: **the site does have a blog** (`/blog`, in the sitemap, last modified 2026-07-09), with at least 5 published posts (lip filler cost in Austin, men's aesthetics, CoolPeel/sun damage, facial types, lip injections — confirmed via live fetch, not in your 4 supplied HTML files). This materially changes the "why only 5 ranking keywords" analysis below — flagging it up front rather than burying it.

### Critical (fix first)

- **`services_laser-hair-removal.html` — zero JSON-LD anywhere on the page (confirmed: 0 matches for `application/ld+json`).** This is your highest-traffic-intent page type (a specific paid service) and it has no `Service`/`MedicalProcedure` structured data at all, while home, /services, and /about all have some. Add a `Service` (or `MedicalProcedure`, given it's performed by clinical staff) node referencing the business as `provider`, plus a `BreadcrumbList` (Home > Services > Laser Hair Removal — the real nav hierarchy already exists via `/services` -> `/services/laser-hair-removal`). Note: I am **not** recommending `FAQPage` schema as an SEO win — Google deprecated FAQ rich results (per internal reference, retired 2026-05-07); do not add FAQ markup expecting a rich-result CTR bump.

- **Sitewide: alt text confirmed empty on every sampled `<img>` — I independently verified this, your claim holds.** Grep across all four files found every `alt=` attribute set to `alt=""` (home.html, services.html, services_laser-hair-removal.html, about.html — multiple clusters each). This includes content-bearing images (team member photos, before/after-adjacent imagery, service cards) where alt text is directly useful for image search and accessibility, not just decorative background images where empty alt is arguably correct. Fix priority: team member photos (`/about`), service card thumbnails (`/services`), and any hero/treatment images on service pages. Do not blanket-fill logos/decorative background `img.bg_img` — those can legitimately stay `alt=""`.

- **Homepage `<title>` omits the brand name entirely.** `<title>Medical Spa in Austin, Texas | Laser Hair Removal</title>`. It also leads with one of ~7 service categories despite Muse offering injectables, body, wellness (semaglutide), and male aesthetics. Compare `/about` (`About Muse Med Spa | Medical Spa in Austin, Texas`) and `/services` (`Microneedling & Facials in Austin, Texas | Muse`) — both correctly include the brand. Recommended replacement (49 chars currently -> keep under 60): `Muse MedSpa | Medical Spa in Austin, Texas` (43 chars) or `Muse MedSpa | Austin Med Spa, Injectables & Laser Care` (56 chars) — the second signals topical breadth for the treatments the business actually wants to rank for. The laser-hair-removal page has the same brand-omission problem (`Laser Hair Removal in Austin, Texas | Medical Spa Care`) — swap "Medical Spa Care" for "Muse MedSpa".

### High

- **The `geo` property on the nested `MedicalBusiness` node (services.html) only populates `url`, not `latitude`/`longitude`.** `GeoCoordinates` conveys no actual coordinates here — `url` is a generic `Thing` property, not what `GeoCoordinates` is for. Compare about.html, which correctly uses real latitude/longitude. Fix: either replace with real lat/long, or move the Maps link to `hasMap` on the parent `MedicalBusiness` node instead.

- **Geo coordinate mismatch between two sources on the site.** /about's JSON-LD gives one set of coordinates. The footer's Google Maps share link (present on all 4 pages) resolves to a location roughly 1.5 miles apart. One of these is wrong. Verify the correct pin against the actual Google Business Profile and fix whichever is stale (likely the JSON-LD, since GBP is presumably the source of truth).

- **Self-serving review schema — will not produce star rich snippets, and you should stop expecting it to.** Home and /services both mark up `MedicalBusiness`/`Organization` with reviews about Muse, hosted on Muse's own site. Per Google's Review Snippet structured-data guidelines (confirmed via search, not assumption): since the 2019 update, Google does not show review rich results for `LocalBusiness`/`Organization` types when the entity being reviewed controls the reviews on its own site — this is explicitly the "self-serving reviews" case. Positive note, since I should call out what's actually fine and not manufacture severity: the 15 reviews in the JSON-LD do genuinely match the 15 testimonials visibly rendered in the homepage slider (cross-checked names) — that's honest, non-fabricated markup — the only issue is that it can't do what it may have been added to do (win star snippets). The actual lever for star visibility is the Google Business Profile itself.

- **Homepage H1 carries no service/location keyword.** `<h1>We Celebrate Real Skin & Real Results</h1>`. This is a single, correctly-structured H1 (good — no duplicate-H1 issue on any of the 4 pages), but it's pure brand voice with zero topical signal, while the title over-indexes on one service.

### Medium / nice-to-have

- /services and /about MedicalBusiness nodes have no `@id`, so Google can't reliably merge them into one entity graph with the homepage's version.
- Minor NAP formatting inconsistency between two pages (comma difference in the address string) — trivial for schema parsing, worth a 30-second fix.
- Footer social icon mislabeled `aria-label="tiktok link"` but actually links to the Google Maps place page.
- Sitemap includes `/thank-you` (form-confirmation page) — worth confirming it carries noindex; couldn't verify without fetching that page's HTML.
- No hreflang anywhere — correctly not needed; single-location US business, single language.
- No noindex/nofollow meta robots found on the homepage — correct default, indexable as expected.

### Why only 5 ranking keywords vs. competitors' 100-2,000+? (causal analysis)

Given what I can see in the markup, the technical/content issues above are real and worth fixing, but they are not sufficient on their own to explain a gap this large. Ranked by how much of the gap each plausibly explains:

1. **Backlink/domain authority (most likely dominant factor, not fixable via on-page work).** DR 8 vs. 21-50 is the single biggest divergence in the Ahrefs data, and domain authority correlates far more strongly with breadth of keyword rankings than on-page/schema quality does.
2. **Local Pack vs. organic pack — flag this explicitly as unverified.** Ahrefs' organic keyword count measures the traditional 10-blue-links index, not Local Pack/Maps visibility, which is driven by GBP signals Ahrefs' web crawler doesn't measure at all. Given the strong third-party review evidence, it's entirely plausible Muse is getting real visibility through the Map Pack that this metric is structurally blind to. This needs a live Google Search Console / Maps check, not something confirmable from HTML.
3. **Possible recent site rebuild resetting authority — flag as unverified, worth checking.** If this Webflow build replaced an older website without full URL-for-URL 301 redirects, that would reset historical backlink equity and directly explain a low DR despite a decade-old business. Check Ahrefs' backlink history graph and the Wayback Machine.
4. **The technical/content issues are real secondary contributors, mainly to CTR and image search, not raw indexability.** Canonicals are all correct, robots.txt doesn't appear to block crawlers, and the sitemap is populated with 137 URLs including the blog. Indexability itself looks fine; the ceiling here is topical authority and off-page signals, not crawl/index blockers.

Net honest read: fix the on-page items because they're free wins — but don't expect them to close a 20x+ keyword-count gap. That gap is almost certainly backlinks/domain history first, Local Pack measurement blind-spot second.

### Keyword & content notes — laser-hair-removal page

| Primary keyword | Intent | Rough difficulty* | Supporting / long-tail terms |
|---|---|---|---|
| laser hair removal austin | Commercial (near-transactional, local) | Medium-High — national chains and multi-location competitors already rank here | laser hair removal austin tx cost; best laser hair removal austin; laser hair removal near me 78746; laser hair removal underarms/legs/brazilian austin; how many sessions for permanent laser hair removal |

*Directional estimate based on SERP composition, not pulled from Ahrefs Keywords Explorer for this specific term — confirm actual KD/volume before committing content resources.

Single term this page should target: laser hair removal austin (head term) with laser hair removal cost austin as the priority long-tail gap — the page currently has zero pricing information anywhere in its content, while the site's own blog already runs this exact pattern successfully on other services.

### FACTS / assumptions

**Confirmed directly from the HTML:**
- Zero descriptive alt text sitewide in the sampled markup.
- /services/laser-hair-removal has no JSON-LD at all.
- Home, /services, and /about use three structurally different schema representations of the same entity, with no consistent @id except /about.
- One H1 per page, correctly structured, no duplicates. Canonicals correct and self-referencing on all 4 pages.
- Sitemap has 137 URLs, includes /blog with at least 5 published posts (contradicts the "no blog" assumption in the original brief).
- Google's review-snippet policy: self-hosted reviews about your own business do not produce star rich results in web search, regardless of markup quality.

**Cannot be confirmed and need a live check — do not treat these as established:**
- Google Business Profile star rating and review count — must be checked directly in Google Maps, not inferred from general search results or HTML.
- Whether the current Webflow build is a recent migration from a prior platform — check Ahrefs' historical DR/backlink graph and Wayback Machine.
- Exact robots.txt directives beyond the sitemap line.
- Core Web Vitals / LCP / CLS — not assessed here.
- Whether /thank-you and other utility pages carry noindex.
- Rough keyword difficulty for "laser hair removal austin" — directional only.
