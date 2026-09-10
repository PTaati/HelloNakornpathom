# HNP-WORLD-002 — design/QA readiness review

**Date:** 2026-09-10  
**Reviewer scope:** read-only review of references, current previews, scene/code and prior evidence. No Unity Editor, Play Mode, scene, Blender source or implementation change was performed.

## Result

| Check | Status | Evidence / finding |
|---|---|---|
| Brief completeness | PASS | `docs/design/HNP-WORLD-002.md` specifies scope, budgets, interaction, acceptance, ownership, provisional items and requirement trace. |
| Current world baseline | PASS | HNP-WORLD-001 evidence records station-left → road → chedi-right, traversal and desktop Chrome smoke: `reports/world/validation.md`, `reports/world/traversal.json`. |
| Traveller visual review | PASS | `art-export/world/traveller-preview.png` was visually inspected: cute readable silhouette and G10 clothing are present. Existing 7,384-triangle manifest: `art-export/world/traveller-manifest.json`. |
| Chedi/town visual review | PASS | `art-export/world/world-preview.png` was visually inspected: chedi silhouette is readable and warm stylized palette is coherent; detail beyond cited references remains provisional. Manifest: `art-export/world/world-manifest.json`. |
| Stable idle/walk/run/jump acceptance | NOT RUN | Current `HnpTravellerPose.cs` provides only movement-driven procedural limbs/head motion; no idle/run/jump state contract or new build evidence. |
| Traffic, birds, train, day/night, music | NOT RUN | Read-only code/scene review found no corresponding runtime systems or audio assets in the world scene. |
| Current physical mobile acceptance | NOT RUN | Prior evidence is Windows desktop Chrome/headless SwiftShader and explicitly excludes Android/iPhone testing. |
| HNP-WORLD-002 release gate | FAIL | Required feature implementation and physical device evidence are absent; NOT RUN items cannot be counted as passed. |

## Handoff findings

- Existing HNP-WORLD-001 is a valid exploration-art baseline, not proof of G01 arrival, G02 crossing/retry, full G07 view modes, G09 animation set, or P01 physical-mobile behavior.
- `HnpWorldGame.cs` currently gives touch pads/map/portrait pause and free movement; it has no audio lifetime management or time-of-day/ambient lifecycle. `HnpTravellerPose.cs` has no idle state, so stability must be proven after implementation.
- The road preview contains simple parked/static-looking cars; this does not satisfy safe moving traffic. StationPrototype contains train geometry, but the world scene has no train system.
- No reproducible defect is filed because the missing items are planned scope, not a regression in a claimed implementation. Producer confirmation is required on vehicle collision semantics and G07 alternate view before implementation.

## Required evidence for retest

Build hash and launch URL; source/export manifests; Android Chrome and iPhone Safari device records; gameplay video for W2-01–W2-05; console log; profiler/frame-time and tracked-memory captures; cold-cache download/start measurement; audio gesture/blocked/focus/rotation test results. See the acceptance matrix in `docs/design/HNP-WORLD-002.md`.
