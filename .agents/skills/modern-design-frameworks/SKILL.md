---
name: modern-design-frameworks
description: Use when building or styling web applications to ensure they use the best modern design frameworks, component architectures, and premium aesthetics.
---

# Modern Design Frameworks & Aesthetics

When tasked with building or styling a web application, follow these guidelines to ensure a premium, modern user experience.

## Frameworks & Architecture
- **Framework Selection:** Prioritize Next.js for full-stack applications, Vite + React for Single Page Applications (SPAs), and Astro for content-heavy or static sites.
- **Component-Driven:** Build strict, reusable component hierarchies. Prefer using accessible headless UI primitives (like Radix UI) as the base layer for complex interactive components.

## Styling & CSS Rules
- **Vanilla CSS by Default:** Use modern Vanilla CSS (custom properties, CSS Grid/Flexbox, native nesting) for maximum control and flexibility, as required by the repository baseline.
- **Tailwind CSS / shadcn/ui:** Do NOT use Tailwind CSS or Tailwind-based component libraries (like shadcn/ui) unless the user explicitly requests them. If requested, confirm the preferred version and setup.

## Premium Aesthetics
Achieving a "wow" factor is critical. Apply these modern design principles:
- **Typography:** Avoid system defaults. Use modern, highly legible typefaces (e.g., Inter, Roboto, Outfit). Ensure strong typographic hierarchy.
- **Colors:** Avoid generic primary colors (e.g., plain `#FF0000`). Use curated HSL palettes (e.g., sleek dark modes, vibrant but harmonious accents).
- **Depth & Materials:** Utilize modern styling techniques like glassmorphism (translucency + background blur), subtle drop shadows, and soft gradients.
- **Micro-animations:** Make the interface feel alive. Use smooth transitions on hover states, subtle scale effects on active elements, and layout animations to provide feedback and guide the user's attention.

## Registry / WaaS Design Reads

When working in the Registry repo, read `TASTE.md` before a meaningful public UI or template change. Use the design read and dials there to decide whether the surface is:

- **Authority mode:** dense Registry discovery, rankings, maps, profile facts, pSEO links, and trust evidence.
- **Light product mode:** curriculum, onboarding, education, or product explanation that benefits from an off-white enterprise canvas.
- **Gallery-forward conversion mode:** WaaS, contractor, studio, trades, or portfolio-led pages where real visual proof is the product.

For gallery-forward contractor or studio templates:

- Use an airy light canvas, generous whitespace, off-black text, low-contrast gray borders, muted gold/ink accents, and a deep-ink footer.
- Use a spaced wordmark treatment only when the actual brand can carry it.
- Use existing sans fonts for body and most headings; a system serif italic accent is acceptable for one or two editorial words without adding an external font.
- Build framed/bracketed or bento galleries from real project categories and real images. Do not invent marquee clients, license facts, founding years, owner stories, portraits, or portfolio categories.
- Preserve conversion tools that prove value, such as calculators, estimate forms, contact paths, license/bond proof, owner story, and project captions.
- Keep hero media LCP-safe: explicit dimensions, eager loading when it is the LCP asset, and no opacity/reveal animation on the hero media or critical hero text.
- Prefer CSS transform/opacity for hover polish. If scroll reveal is needed, use one small IntersectionObserver client island with `prefers-reduced-motion` support.
- Do not hide essential captions, CTAs, or project facts behind hover-only behavior.
