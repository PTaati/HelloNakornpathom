# HNP-WORLD-010 — Attached front sanctuary with actual Buddha photograph

status: COMPLETE
requirement_ids: G03, G04, P01
editor_owner: root

## Goal / inputs

Latest user request: attach the projecting front gable to the Chedi, simplify its interior to a plain rectangular chamber and show `ref/pra.jpg` as the actual Buddha image. The photo replaces the primitive front statue; this is a photographic display in a 3D architectural recess, not a claim of a newly scanned 3D Buddha.

Baseline: HNP-WORLD-009 r2. Original references and previous art revisions remain unchanged.

## Ownership

- Artist: new `art-source/hnp-world-010/`, `art-export/hnp-world-010/` only.
- Unity engineer: sole Editor/Unity writer; new integrator, affected Chedi materials/model/prefab/scene and build. Preserve Chedi GUID, Town and surroundings.
- Ownership handoff: engineer draft completed without import; root resumed sole Unity ownership for corrected integration/build.
- Designer/QA: `docs/art/HNP-WORLD-010-brief.md`, `reports/reviews/HNP-WORLD-010*.md`.
- Root: task record, Web tests, local server and final evidence.

## Acceptance

- Front gabled roof/walls visibly join the Chedi with a projecting rectangular chamber; no floating gap.
- Plain rectangular interior, unobstructed photo, full original aspect ratio and correct facing. No old primitive front statue.
- Exact user image retained without edits, copied texture provenance/hash recorded.
- Blender source/export/UV/material/bounds/round-trip checks and independent visual review.
- Unity missing-reference and photo/material checks, front and oblique views; existing four stair entrances and upper court traversal preserved.
- Fresh Web build plus day/night, collision and portrait/landscape targeted regression.
- Physical mobile NOT RUN unless a real device becomes available.

## Results

Preflight: root read all three role skills and production/team instructions; inspected actual `pra.jpg`, current generator and Unity integrator/tests. Unity 6000.6.0f1/package versions unchanged; no active Unity process at initial check. Engineer prepared a draft without import or Editor launch. Root review found path/validation defects and took ownership before integration, replacing the draft with a scoped version based on the proven v009 importer.

Compile: PASS, `reports/world/world010-compile.log`. No new model imported during this check.

Blockout form: PASS independent `reports/reviews/HNP-WORLD-010-blockout.md`. Full photo hash/aspect and final materials/export still require final staging/Unity validation. Root requested photo move forward to z=-23.82 to avoid opaque Chedi occlusion and roof rear extension to z=-13 to join the bell at ridge height.

First detailed photo view: FAIL, horizontally mirrored despite an initial manifest claim; root caught raised-hand/seated-person reversal against actual `pra.jpg`. Artist reversed mesh U coordinates, kept JPEG unchanged, regenerated source/FBX/previews and tightened front extents to the existing envelope. Root corrected close-preview orientation check: PASS; final independent staging review pending.

Final staging: PASS `reports/reviews/HNP-WORLD-010-staging.md`. Unity import/photo/rays/collision/routes: PASS `reports/world/world010-integration/`. Build: PASS `builds/world010-r1/web`, `reports/world/world010-build1.log`.

Web: PASS actual shrine photo day/night/portrait (`world010-shrine-20260910-232325`), night/collision/retreat (`world008-night-20260910-232426`), clock/static idle/map/camera/portrait regression (`world009-reference-20260910-232520`), all under `reports/world/`. Independent scoped final visual review PASS `reports/reviews/HNP-WORLD-010-final.md`. Physical mobile/performance NOT RUN. Delivery and replay: `reports/world/HNP-WORLD-010-delivery.md`. Local server target: `http://localhost:8081`, world010-r1; old builds retained.
