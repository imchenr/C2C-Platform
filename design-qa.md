# Design QA

## Comparison target

- Source visual truth: `/Users/eddy/.codex/generated_images/019ff16b-5a34-7211-bb1d-0f1fe295f0b4/exec-97cebf46-5a8a-4f01-99a5-6afcfce45399.png`
- Rendered implementation: `/Users/eddy/Codes/design-platform/implementation-home-final.png`
- Full-view combined evidence: `/Users/eddy/Codes/design-platform/design-qa-comparison-final.png`
- Focused header/hero/category evidence: `/Users/eddy/Codes/design-platform/design-qa-focused-final.png`
- Admin evidence: `/Users/eddy/Codes/design-platform/implementation-admin.png`
- Mobile evidence: `/Users/eddy/Codes/design-platform/implementation-mobile.png`

## Normalization

- State: C-end homepage, logged-in verified student, 同济大学, default recommendation state.
- CSS viewport: `1440 x 1024`.
- Browser density: `deviceScaleFactor = 1`.
- Source pixels: `1487 x 1058`, normalized with high-quality downsampling to `1440 x 1024`.
- Implementation pixels: `1440 x 1024`.
- The full comparison places normalized source and implementation side by side at identical pixel dimensions. The focused comparison stacks their first `520px` regions for detailed header, hero and category inspection.

## Findings

No actionable P0, P1 or P2 findings remain.

- Fonts and typography: the implementation uses the available PingFang SC / Noto Sans SC / Microsoft YaHei system stack with matching heavy dark-green display type and readable 12–16px utility type. Heading scale, single-line hero composition and product typography now preserve the source hierarchy. Exact glyph metrics vary slightly with the host system font; this is acceptable P3 drift.
- Spacing and layout rhythm: header is `74px`, hero ends at `383px`, category strip ends at `505px`, and the six-card product row begins at `553.8px`, closely matching the source composition. Section density, dividers, small radii and low elevation are aligned.
- Colors and visual tokens: ivory, forest green, leaf green, sunflower yellow and price orange map consistently to the source. State colors preserve accessible contrast and no unrelated purple/blue brand system was introduced.
- Image quality and asset fidelity: the campus hero, six visible product photos and visible avatars are raster assets with correct subjects and crops. All 13 visible homepage images loaded successfully; none are placeholders, CSS drawings or broken remote assets.
- Copy and content: product name, campus, primary headline, search language, product labels, prices, trust cues and safety copy are coherent and realistic. The additional “逛市场” navigation item and notification affordance are intentional functional extensions that do not change the source hierarchy.
- Icons: Element Plus line icons form one consistent icon family and visually match the source’s light-outline treatment. No handcrafted SVG or text-glyph icon substitutes are present.
- Responsiveness: at `390 x 844`, the C-end has no horizontal overflow (`scrollWidth === clientWidth === 390`), categories become a 4-column grid, products become a 2-column grid and persistent controls remain reachable. The admin remains intentionally desktop-oriented.
- Accessibility: all visible images have alt text, core controls are keyboard-reachable, search and favorite controls have accessible names, and semantic headings/navigation are present.

## Interaction and runtime verification

- Search button navigated to `/market?keyword=台灯` and returned “米家台灯 Lite”.
- Category filtering updated the market heading and result state.
- C-end demo login succeeded and routed to the homepage.
- Message center loaded 3 conversations and a functional composer.
- Orders loaded 3 user orders with lifecycle controls.
- Publish page loaded the authenticated form, image uploader and product fields.
- Admin login succeeded and loaded the dashboard.
- Admin product audit showed 12 products and one pending approval action.
- Admin reports showed 2 reports and one immediate handling action.
- Operations loaded all 8 seeded categories.
- Clean final browser tab produced zero console errors or warnings.
- Frontend production build passed; Python modules compiled; API health, home, user and admin endpoints passed live smoke checks.

## Comparison history

### Pass 1 — blocked

- Evidence: `implementation-home.png`.
- P2: hero was `470px` tall instead of the source’s approximately `308px`, which pushed product discovery below the first viewport.
- P2: homepage used four cards per row instead of the source’s six-card marketplace rhythm.
- P2: `PageHeader` and one safety icon were unresolved Vue components on secondary routes.
- Fixes: reduced hero height, restored a single-line headline, aligned category and section boundaries, moved to a six-column home grid, globally registered `PageHeader`, and replaced the unavailable icon.

### Pass 2 — blocked

- Evidence: `implementation-home-v2.png` and the earlier `design-qa-comparison.png`.
- P2: vertical spacing still delayed the product row and safety bar by roughly 40–60px.
- P2: category icons had unnecessary tinted containers, and visible avatars were initial-based fallbacks rather than raster assets.
- Fixes: measured DOM bounds and aligned hero/category/product boundaries to `383px / 505px / 553.8px`; reduced section padding; removed icon containers; added local raster avatars and bound them throughout the main marketplace surfaces.

### Pass 3 — passed

- Evidence: `design-qa-comparison-final.png` and `design-qa-focused-final.png`.
- Post-fix result: source and implementation preserve the same information hierarchy, first-viewport density, six-item product row, safety treatment, imagery, typography and primary actions. No actionable P0/P1/P2 mismatch remains.

## Follow-up polish

- P3: add a dedicated close-up photo for the seeded mouse listing instead of reusing the keyboard desk scene.
- P3: load a bundled Noto Sans SC webfont if pixel-identical font metrics are required across operating systems.
- P3: split the ECharts admin bundle further if initial-load performance becomes a production target.

final result: passed

