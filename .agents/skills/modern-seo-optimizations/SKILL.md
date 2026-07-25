---
name: modern-seo-optimizations
description: Use when building, auditing, or optimizing web applications to ensure they meet strict technical SEO standards, including dynamic metadata injections, link attributions, Core Web Vitals (CWV), and structured data.
---

# Modern SEO & Performance Optimizations

When tasked with building or auditing web applications, follow these strict guidelines to ensure maximum technical SEO compliance and performance.

## 1. Metadata & Dynamic Injections
- **Framework APIs:** Utilize modern framework APIs (e.g., Next.js Metadata API or App Router `generateMetadata`) to dynamically inject `<head>` tags.
- **Canonicalization:** Always inject self-referencing `<link rel="canonical">` tags on every page. Ensure query parameters that do not change content are stripped from the canonical URL to prevent duplicate content indexing.
- **Social Graph:** Inject rigorous Open Graph (`og:title`, `og:image`, `og:url`) and Twitter Card metadata for all shareable routes.

## 2. Link Attributions & Equity (Project Standards)
- **Registry & Editorial Links:** First-party verification, citation, and editorial links must pass authority. Use `rel="noopener noreferrer"` without `nofollow`. Do not blanket-nofollow these links.
- **External & Sponsored Links:** Paid ads, sponsorships, native endorsements, and affiliate links must strictly use `rel="nofollow sponsored"`.
- **User-Generated Content:** Arbitrary outbound links submitted by users must use `rel="nofollow ugc"`.
- **Widget Rendering:** Render SEO authority widgets in the host page's Light DOM (not Shadow DOM or iframes) to ensure link equity transfers properly. Widget attribution must point to the most specific canonical Registry URL (gym profile first, then blog/state). Avoid duplicate hidden `display:none` SEO copy.

## 3. Structured Data (JSON-LD)
- **Injection Method:** Always inject `Schema.org` markup via `<script type="application/ld+json">` rather than inline microdata.
- **Entity Types:** Mandate specific schemas based on content type: `LocalBusiness` for directory profiles, `BreadcrumbList` for hierarchical navigation, and `Article` for blogs/news.

## 4. Core Web Vitals & Technical Crawlability
- **INP & LCP:** Enforce strict limits for LCP (< 2.5s) via priority image loading (`fetchpriority="high"`) and INP (< 200ms) by minimizing main-thread blocking JS.
- **Robots & Sitemaps:** Ensure dynamic `sitemap.xml` and `robots.txt` generation that accurately reflects the `index`/`noindex` rules of the current deployment environment.
