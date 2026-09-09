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

**Headline finding:** Muse's site is professionally built with no major indexability problems, but sits
at **Ahrefs Domain Rating 8, ~46 est. monthly organic visits, and only 5 ranking organic keywords** —
against direct local competitors at DR 21–50 and 107–2,240 ranking keywords. On-page issues (below)
are real and worth fixing, but they don't explain a gap that size on their own — domain
authority/backlink history is the more likely primary driver, with a secondary "Local Pack blind spot"
in the Ahrefs metric itself (see recommendation 5).

## Top 5 prioritized recommendations

**1. Fix title tags to lead with the brand and the full service range, not one service. (Critical)**
The homepage `<title>` is *"Medical Spa in Austin, Texas | Laser Hair Removal"* — it drops the brand
name entirely and over-indexes on one of ~7 service categories, even though Muse also does
injectables, body treatments, and wellness. The laser-hair-removal service page has the same
brand-omission problem. This is a same-day fix with no downside.
*Rationale: title tags are the single highest-leverage on-page SEO element and directly drive
search-result CTR; omitting the brand also weakens entity/brand-search association.*

**2. Add structured data to the laser-hair-removal service page — it currently has none. (Critical)**
Home, `/services`, and `/about` all carry some JSON-LD; the actual service page (the highest
commercial-intent page type on the site) has zero. Add a `Service`/`MedicalProcedure` node plus
`BreadcrumbList`.
*Rationale: this is the page type most likely to be searched with transactional intent, and it's the
one with no structured data backing it at all — an inconsistency, not a deliberate choice.*

**3. Write real alt text for content-bearing images sitewide. (Critical)**
Every sampled image across all 4 pages (83 total) has `alt=""` — confirmed independently by two
separate passes. Team photos, service cards, and treatment imagery currently have zero alt text.
*Rationale: zero cost to accessibility, zero image-search visibility today. This is a pure gap, not a
trade-off — decorative/background images can stay empty, but content images shouldn't be.*

**4. Fix NAP and geo-data inconsistencies — found in both the site's own code and off-site. (High)**
Two separate, independently-confirmed issues: (a) the `/about` page's JSON-LD lists coordinates
~1.5 miles away from where the site's own footer Google Maps link points, and the `/services` page's
schema puts a Maps URL in a field meant for actual latitude/longitude; (b) live search turned up a
stale citation on CareCredit's directory still listing Muse's *old* address (5524 Bee Cave Rd) instead
of the current one (4201 Bee Caves Rd). Google Business Profile itself categorizes the business under
"West Lake Hills, Texas" while every page of the site optimizes for "Austin" — worth a deliberate
decision (not an accident) on which city framing to lead with.
*Rationale: NAP/geo consistency across the web is a direct local-ranking input, separate from
on-site content quality — and this one is verified sitting live on a real third-party site today, not
theoretical.*

**5. Treat the keyword gap as a domain-authority problem first, not an on-page problem — and reuse
the blog's own proven content pattern.** (High, and the most consequential if true)
5 ranking keywords vs. competitors' 100–2,000+ is too large a gap to be explained by title tags and
alt text. Two things worth checking that the on-page audit can't confirm: whether this Webflow site
recently replaced an older platform without full redirects (which would reset backlink equity for a
business that's actually been open since 2016), and whether Ahrefs' organic-keyword count is simply
blind to Local Pack/Maps visibility that the strong review count (100 Google reviews, 4.9★, confirmed
live) may already be winning. Separately: the site's own blog already has posts that answer
cost/pricing questions (e.g., a lip filler cost post) — that exact pattern doesn't yet exist for laser
hair removal, and it's the highest-value, lowest-effort content gap given the template already works.
*Rationale: fixing on-page issues is necessary but likely insufficient; this is the one recommendation
that, if confirmed, would change the whole prioritization.*

## AI-generated deliverable 1: rewritten meta titles & descriptions

| Page | Current | Rewritten |
|---|---|---|
| Homepage — title | `Medical Spa in Austin, Texas \| Laser Hair Removal` (49 chars) | `Muse MedSpa \| Austin Med Spa, Injectables & Laser Care` (56 chars) |
| Homepage — description | `Visit our medical spa in Austin, Texas for microneedling, laser hair removal, facials, and advanced skin treatments tailored to your aesthetic goals.` | `Muse MedSpa is Austin's boutique medical spa for injectables, laser hair removal, microneedling, and facials — real results, personalized care since 2016.` (154 chars) |
| Laser hair removal — title | `Laser Hair Removal in Austin, Texas \| Medical Spa Care` (56 chars) | `Laser Hair Removal in Austin, Texas \| Muse MedSpa` (49 chars) |
| Laser hair removal — description | `Experience laser hair removal at our medical spa in Austin, Texas for smooth, long-lasting results with advanced, safe, and effective treatments.` | `Laser hair removal at Muse MedSpa in Austin, TX — smooth, long-lasting results with advanced technology. See pricing, sessions needed, and book today.` (150 chars) |

Both rewrites keep the location + service keyword the originals already had right, add the brand name
back in, and — on the service page — plant the "pricing/sessions" hook that the content-gap finding
(recommendation 5) says is missing from the page entirely.

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
  and flagged the correction before proceeding — which changed part of the causal analysis on
  recommendation 5.
- It **verified my claims rather than trusting them** — re-derived the alt-text and schema findings
  from the raw HTML itself instead of accepting my summary, and it corrected the framing on one thing
  I'd assumed (that missing FAQ schema was a loss) by sourcing Google's actual current policy on
  self-hosted review rich results instead.
- Where it had to be reined in / where a human call was still needed: the *why is the keyword gap so
  large* question doesn't have a single clean answer from on-page evidence alone — the agent was
  explicit about that and ranked multiple plausible explanations by likelihood rather than picking one
  confidently, which is the correct call but does mean a human (or a follow-up Ahrefs/GSC pull) has to
  actually resolve it before recommendation 5 can be acted on.
- Ahrefs' domain-rating/metrics endpoint rejected `date=today` and required an actual past ISO date —
  a small but real integration gotcha, not something either of us anticipated going in.

## Files in this folder
- `home.html`, `services.html`, `services_laser-hair-removal.html`, `about.html` — raw fetched HTML,
  the actual evidence base for the on-page findings above
- `ahrefs_results.json` / `ahrefs_lookup.py` — the real Ahrefs API pull (DR + organic traffic/keywords)
  for Muse and 3 competitors
