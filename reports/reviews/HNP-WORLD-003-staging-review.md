# HNP-WORLD-003 — independent Blender staging review

**Date:** 2026-09-10. **Scope:** isolated preview/manifest review of `art-export/hnp-world-003/` against `ref/jd.jpg`, `ref/style.jpg`, and `docs/art/HNP-WORLD-003-brief.md`. No source, FBX, Unity, scene, or browser mutation was made.

## Visual staging result

| Asset/check | Status | Evidence and actionable feedback |
|---|---|---|
| Chedi silhouette/proportions | PASS | `HNP_Chedi_v003-preview.png` now reads as wide stepped base → smooth broad bell → narrow dark ring/collar → ribbed spire. Manifest reports 46 m base width and 44 m height, matching the provisional correction target. This is materially closer to `jd.jpg` than the rejected world capture. |
| Chedi front portico/niche | FAIL | The white portico and standing figure are present but too small/thin against the bell at the supplied camera angle. Enlarge its white gable/side columns and stair-axis contrast approximately 1.5–2× in screen footprint, with the dark niche retained, so it reads before fine geometry. Exact ornament stays provisional. |
| Chedi production budget | FAIL | Manifest lists 45,012 triangles, exceeding the production-plan landmark target of ≤30,000. Do not remove the validated silhouette; provide a measured LOD/profile exception or reduce unseen/ring/step tessellation and report the new count. Four materials are credible for this landmark only with batching/profile evidence. |
| Sedan/hatchback/pickup/minibus form | PASS | The previews show recognisable individual wheels, windows, lights/grille/bumper read, sloped cabins and distinct pickup bed/minibus volume. Each vehicle is 2,472–3,132 triangles, within the ≤6,000 vehicle target. |
| Vehicle visual variety | FAIL | Sedan and hatchback previews are near-identical salmon, front-three-quarter forms except for the taxi roof sign; the manifest exposes one body palette. Supply actual green/yellow taxi, blue/teal, coral/red, cream/white variants and a rear/side comparison so four body families remain distinguishable at gameplay distance. |
| Vehicle material budget | FAIL | Each vehicle lists seven material slots, not the brief/plan target of ≤2 shared materials. Consolidate to a shared atlas/material strategy or provide profiling evidence for an exception before multiplying moving instances. |
| Pigeon silhouette | PASS | `HNP_Pigeon_v003-preview.png` has a visible body, head, beak, tail and spread wing silhouette; it no longer reads as a black pixel. |
| Pigeon flight / budget | FAIL | The still does not establish wing-pivot animation or recognisable flight phases. Manifest lists 1,147 triangles, exceeding the brief's ≤300/billboard bird target. Provide 2–3 wing-phase previews/clip evidence and a lower-LOD/billboard or a measured exception. |
| Run asset/staging | FAIL | `traveller-manifest.json` documents a distinct root-in-place Run (17 frames, 24 fps, 48° thigh swing, torso lean and negligible loop delta), which is a source-level PASS. But `HNP_Traveller_Run-preview.png` is extremely under-lit and tiny on black, so the pose cannot be independently judged at useful scale; rerender a lit three-quarter run frame at the same scale as the other traveller previews. |
| Unity / runtime road loops / UI | NOT RUN | The manifest says Unity validation is NOT RUN. Previews cannot prove all traffic instances drive loops, bird random flight, UI removal/Thai menu/minimap behavior, clip binding, collider safety, or mobile performance. |

## Staging decision

**FAIL for Unity integration as-is.** The high-level chedi and vehicle/pigeon forms are promising, but the portico readability, chedi/bird budgets, vehicle material slots and variant proof must be addressed or explicitly profiled/approved. The run preview must be rerendered before visual animation acceptance. These findings do not reject the underlying Chedi silhouette correction.

## Required next evidence

1. Revised chedi preview with enlarged front portico plus updated triangle/LOD report.
2. Variant sheet showing all four vehicle families in their actual palette variants; shared-material/atlas or profiling report.
3. Pigeon wing-up/mid/down previews and lower LOD/budget evidence.
4. Lit, close three-quarter Run preview; then Unity Animator/gameplay-camera capture.
5. After approved import, a 30–60 s gameplay capture proving all visible cars move road loops and birds fly, followed by Thai UI/minimap review.

## Regenerated staging retest — 2026-09-10

**Evidence freshness:** re-read regenerated `manifest.json` and `traveller-manifest.json`; SHA-256 values were recalculated for current preview files before visual inspection. This section supersedes the earlier staging failures where noted.

| Retest check | Status | Current evidence / limitation |
|---|---|---|
| Chedi form and front portico | PASS | The current `HNP_Chedi_v003-preview.png` retains the reference hierarchy—broad layered base, smooth bell, narrow dark open ring/collar and ribbed spire—and the ivory front portico/niche is now visibly enlarged and readable at the supplied framing. It meets the brief's staged silhouette/contrast gate against `ref/jd.jpg`; exact architectural ornament remains provisional. |
| Chedi budget and roundtrip | PASS | Current manifest reports 27,172 triangles (within the ≤30,000 landmark target), 46 m base width, 44 m height and `roundtrip: PASS`. Unity material/rendering/camera validation remains NOT RUN. |
| Four vehicle families, palette and budget | PASS | Current sedan/taxi (yellow), hatchback (blue), pickup (coral/red) and minibus (green/teal) previews are visibly distinct in color and body purpose. Manifest reports 2,472–3,132 triangles each, two material slots (`HNP3_Atlas`, `HNP3_Body`) and roundtrip PASS. Gameplay loop motion/spacing remains NOT RUN. |
| Pigeon silhouette and budget | PASS | Current pigeon preview retains a readable body/head/beak/tail/wing silhouette. Manifest reports 267 triangles, one atlas material and roundtrip PASS, satisfying the stated staging budget. Wing-up/mid/down playback and random-flight behavior remain NOT RUN. |
| Train staging | PASS | New `HNP_Train_v003-preview.png` clearly reads as a two-car passenger train with windows, lights and wheel read. Manifest reports 4,476 triangles, two materials and roundtrip PASS, within the ≤20,000 visible-train target. Station fit, arrival/departure, collision and G01 handoff are NOT RUN. |
| Run preview and sampled clipping | PASS | The relit, close `HNP_Traveller_Run-preview.png` is large enough to inspect. Its bent knees/elbows, torso lean and opposing limbs read as a run rather than sped-up walk; no obvious body/hat/sandal clipping is visible in this sampled frame. Traveller manifest records `HNP_Traveller_Run`, root motion false and loop delta `2.0519153448064732e-16`. Continuous clip playback, transition and Unity Animator binding remain NOT RUN. |

### Retest staging decision

**PASS for staged asset handoff to Unity.** This is not Unity visual approval and does not pass road loops, bird flight, UI, animation playback, WebGL or mobile acceptance. The next independent gate is Unity gameplay-camera evidence at golden hour/night with all actor systems running.
