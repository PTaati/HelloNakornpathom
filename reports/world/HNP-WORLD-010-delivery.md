# HNP-WORLD-010 — photo shrine delivery

Build: `builds/world010-r1/web`, Unity 6000.6.0f1.

## Change

The primary front Buddha primitive and ornate open niche are replaced by a projecting gabled chamber joined to the Chedi. Its interior has plain rectangular walls, ceiling, floor and an upright, full-frame `ref/pra.jpg` display. This is a photograph on a 3D recess wall, not a newly sculpted or scanned 3D Buddha. Chamber dimensions and unseen construction remain provisional gameplay adaptations.

The exact original JPEG is retained (387 × 792); UVs preserve aspect and correct orientation. A separate unlit Unity material keeps it readable at night without applying the monument emission tint. Other Chedi body details, Town, surrounding cloister, traffic, player and gameplay settings remain in place. Chedi FBX/prefab asset GUIDs are retained.

## Files

- Blender source/generator: `art-source/hnp-world-010/HNP_Chedi_v010.blend`, `build_chedi_v010.py`.
- Staging FBX/photo/light profile/UV/material/bounds reports: `art-export/hnp-world-010/`.
- Unity: `Assets/_HNP/Editor/HnpWorld010Integrator.cs`, `Scripts/World/HnpShrine010Diagnostics.cs`, emission-property guard in `HnpNightLighting.cs`, World010 materials/textures, existing Chedi FBX/prefab, world scene and minimap.
- Web test: `tools/test_world010_shrine.py`; reference regression retains explicit build argument.

## Evidence

- PASS corrected independent staging review: `reports/reviews/HNP-WORLD-010-staging.md`. Initial mirrored UVs were rejected and regenerated; original photo was never edited.
- PASS Blender: 25,314 visible triangles / 25,462 including collision; front extent 27.700001 m, dimensions 46.43327 × 50.96 × 44 m in Blender XYZ; 10 meshes with UV0, zero degenerate faces/loose vertices, FBX round-trip delta 0.000004 m.
- PASS Unity import: `reports/world/world010-integration/scene-validation.json`, 47 static meshes / 74,848 static triangles, missing references 0. Counts exclude runtime traffic/birds and skinned player.
- PASS exact photo hash/aspect/GUID and five unoccluded front mesh rays: `world010-integration/photo-validation.json`.
- PASS 16 solid-core collision cases, four cardinal gate centerlines with zero lateral deviation and two upper courtyard arcs: `world010-integration/collision.json`, `temple-routes.json`.
- Unity front/oblique evidence: `world010-integration/shrine-front.png`, `shrine-oblique.png`.
- Build log: `reports/world/world010-build1.log`.
- PASS real Web shrine day/night and portrait controls: `world010-shrine-20260910-232325/report.json` and screenshots. The close third-person avatar can partially cover the lower photo; the unobstructed Unity view separately verifies the complete image.
- PASS Web night/traffic and inward movement/jump collision plus retreat: `world008-night-20260910-232426/report.json`.
- Tested Web WASM SHA256: `7222c7d2919792cf35531f027501c720f3fb6d5ec48042e14437684863047369`.
- PASS clock/map/static idle/overhead camera/portrait regression: `world009-reference-20260910-232520/report.json`.
- PASS independent scoped final visual review: `reports/reviews/HNP-WORLD-010-final.md`.

## Replay / limitations

Open the local Web game, start in Thai, follow the main road to the Chedi and inspect the projecting front sanctuary from straight ahead and obliquely. The portrait must remain upright, with the raised hand on the viewer's left as in `pra.jpg`. Open the upper-left menu and toggle night; the image should remain visible. Check portrait orientation and all stair approaches. The opaque Chedi remains solid.

Physical mobile and hardware performance: NOT RUN. Browser viewport tests do not establish phone performance. Original references and previous builds are retained; no public deployment was performed.
