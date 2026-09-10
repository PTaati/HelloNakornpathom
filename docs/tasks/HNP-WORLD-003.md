# HNP-WORLD-003 — Reference art and Thai mobile UI correction

Status: IMPLEMENTED / WEB REGRESSION AND INDEPENDENT VISUAL REVIEW PASS; physical-phone acceptance NOT RUN. Editor owner: root (all team Unity writers stopped).

Inputs: latest user corrections; `ref/style.jpg`, `ref/jd.jpg`; existing world and traveller sources; `docs/art/HNP-WORLD-003-brief.md`.

Goal: broad photo-referenced Phra Pathom Chedi; detailed varied moving traffic; recognizable flapping random-flight birds; distinct Run animation; warm golden sky/lighting; Thai UI, no HOME/fullscreen/MAP buttons, settings hidden at top left, tappable minimap and icon-only jump/run. Keep portrait and landscape playable.

Write scope: `art-source/hnp-world-003/`, `art-export/hnp-world-003/`; world Unity scripts/shader/editor integration, corresponding FBX/material/font/prefab/scene assets; Web template and build; targeted test tooling and reports.

Acceptance: independent model reference review and export budgets; correct imports and no missing meshes/materials; browser proof of UI/map/menu/run and actor movement; build success. Physical-phone tests reported separately, never inferred from desktop viewport emulation.

Reference research: Tourism Authority of Thailand describes the front standing Buddha niche: https://www.tourismthailand.org/Articles/10-things-to-do-in-nakhon-pathom . Actual geometry comparison uses supplied `ref/jd.jpg`; no online photo copied into game assets. Thai Sarabun font is from Google Fonts with OFL license alongside the font.

History: artist agent unavailable from usage limit, root produced Blender assets; Unity agent staged initial UI/life code, then root took ownership and replaced incomplete adapters. QA remains an independent reviewer. See `reports/reviews/HNP-WORLD-003-*.md`.

Delivery: `reports/world/HNP-WORLD-003-web-delivery.md`. Final build `builds/world003-r3/web`, served locally at http://localhost:8081 . Unity import/build PASS in `reports/world/world003-build4.log`; browser regression PASS in `reports/world/world003-web-20260910-203824/report.json`. This includes Thai UI/menu/map, portrait/landscape, actual Run/Idle states with stable idle root, moving cars/birds/wing poses and 32 additional seconds of sampled road bounds. Physical phones, listening-quality review and full train/minigame integration remain NOT RUN.
