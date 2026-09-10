# HNP-WORLD-009 — Reference-led Chedi and temple refinement

status: COMPLETE
requirement_ids: G02, G03, G04, P01
editor_owner: root

## Goal and inputs

Inspect the user-supplied photographs in `ref/`, especially the newly added
`IMG_20211023*.jpg` and `pra.jpg`, and refine the Chedi and surrounding temple
scene. Real photographs govern architecture and material identity; `style.jpg`
governs stylization, and `jd-night.jpg` governs night illumination. Distances
remain gameplay-compressed, not surveyed dimensions.

Baseline: HNP-WORLD-008, `builds/world008-r4/web`.

## Ownership and writes

- Blender artist: `art-source/hnp-world-009/`, `art-export/hnp-world-009/`.
- Designer/QA: `docs/art/HNP-WORLD-009-reference-brief.md`, task-specific review evidence.
- Root: Unity integration, night-light fit, task record, build and targeted tests. Town-only cleanup ownership transferred from artist to root: `clean_town_v009.py`, `HNP_Town_v009.blend/.fbx`, `town-cleanup-manifest.json`.
- Preserve original references, existing asset GUIDs, and all unrelated work.

## Acceptance

- Reference inventory and explicit photo-to-feature mapping; unconfirmed details marked provisional.
- Reviewed silhouette before detail; Blender source, FBX, UV/material/bounds/triangle report and round-trip evidence.
- Chedi bell, rings, spire, front shrine and surrounding architectural details visibly match supplied photographs better than baseline.
- Unity import has no missing meshes/materials/scripts; night lights fit revised geometry.
- Station-left route, movement, portrait/landscape UI, five-second sprint/cooldown and accelerated clock remain intact.
- No traversal through the solid Chedi; intended paths remain usable.
- Fresh Web build, browser functional and visual checks with exact revision/evidence.
- Physical mobile testing remains NOT RUN unless an actual device is available.

## Results

Reference review: PASS inventory/brief, all 75 field photos inspected alongside `jd.jpg`, `pra.jpg`, style/night and map references. Brief: `docs/art/HNP-WORLD-009-reference-brief.md`.

Integration scripts compile: PASS, `reports/world/world009-compile.log`.
Baseline (v008 geometry only) route checks: PASS four cardinal stair approaches and two upper court arcs, `reports/world/world009-integration/baseline-temple-routes.json`; an initial JSON test-report serialization error was corrected and rerun.

Macro silhouette: PASS after corrected full-body neutral-light preview; independent review `reports/reviews/HNP-WORLD-009-silhouette.md`. First preview cropped the finial and showed a collider; corrected before approval. This is not final-detail approval.

Web regression harness baseline: PASS on explicitly recorded v008 build, `reports/world/world009-reference-20260910-221116/report.json`; corrected screen-coordinate drag direction after first test attempt.

Blender detailed revision: PASS independent corrected-detail review (`reports/reviews/HNP-WORLD-009-detail.md`). Source/export and material UV round-trip evidence retained in `art-export/hnp-world-009/`.

First detailed export round-trip: PASS (Chedi 27,388 triangles including collider; surroundings 42,260). Root visual gate: FAIL, held out of Unity pending fixes to final framing, excessively strong tile pattern, discontinuous lower white base, poorly readable arcade arch walls and front-gable crossbar. Designer independent review requested. This export is not the delivered build.

Town cleanup: PASS; removed exactly 34 old cloister roofs and 34 pillars by original component coordinates, retaining every other island. Existing `COLL_Town` geometry hash unchanged. FBX round-trip 22 meshes / 21,778 triangles matches source. Evidence: `art-export/hnp-world-009/town-cleanup-manifest.json`. Blender thumbnail-cache warning did not prevent source/export save or round-trip.

Revision r1 held after actual Web screenshot review: an arcade jamb encroached on cardinal stair gaps. Corrected wall-center clearance to include the bay half-width; 36 pillars preserved, wall bays reduced from 36 to 32. Final surroundings 24,184 triangles including colliders; round-trip maximum delta 0.000008 m. r1 is not the delivery build.

Revision r2 Unity integration: PASS, 45 static meshes / 77,130 triangles, zero missing references. All four stair centerline probes have zero lateral deviation through the gate; two upper courtyard arcs pass. Evidence: `reports/world/world009-integration/scene-validation.json`, `temple-routes.json`, `collision.json`, `asset-identity.json`. Existing Chedi/Town asset GUIDs preserved. Build: `builds/world009-r2/web`, log `reports/world/world009-build2.log`.

Final r2 verification: PASS desktop Web reference/clock/camera/map/portrait checks (`world009-reference-20260910-225000`), night/collision (`world008-night-20260910-225051`) and sprint/cooldown (`world007-sprint-20260910-225153`), all under `reports/world/`. Independent final visual verdict PASS, `reports/reviews/HNP-WORLD-009-final.md`. Physical mobile/performance NOT RUN. Delivery details and replay steps: `reports/world/HNP-WORLD-009-delivery.md`. Local test server updated to r2 at `http://localhost:8081`; old builds retained.
