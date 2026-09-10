# HNP-WORLD-002 — independent traveller export review

**Asset:** `HNP_Traveller_Child_Rigged_v002`  
**Date:** 2026-09-10  
**Review scope:** isolated Blender export evidence only. Inspected all three supplied PNG previews plus manifest and Blender roundtrip report under `art-export/hnp-world-002-traveller/`. The artist's working `.blend` and Unity project were not changed.

## Result

| Check | Status | Evidence / finding |
|---|---|---|
| Cute silhouette and outfit readability | PASS | Three-quarter and gameplay-distance previews show a large-head child-like silhouette, cowboy hat, cream button shirt, dark shorts and sandals. The light/dark/skin palette remains legible without textures. This is a stylized art-direction proposal; character-specific reference is absent and therefore provisional. |
| Gameplay-distance readability | PASS | `HNP_Traveller_Child_Rigged_v002_preview_gameplay.png` retains recognizable hat, light shirt, dark shorts and limb separation at the supplied landscape framing. Actual in-game camera, lighting, outline/shadow contrast and mobile screen readability are NOT RUN. |
| Sampled walk pose | PASS | `HNP_Traveller_Child_Rigged_v002_preview_walk.png` shows a readable opposing arm/leg stride with no obvious detached part or self-intersection in this single sampled extreme. Playback continuity, foot planting, loop seam and stop transition are NOT RUN. |
| Geometry/material budget | PASS | Manifest reports 7,340 evaluated triangles (≤12,000), one mesh, three materials (at the stated player target), one UV layer, zero degenerate faces/loose vertices/non-manifold edges and no negative scale. |
| Export roundtrip evidence | PASS | `HNP_Traveller_Child_Rigged_v002.roundtrip.json` reports one mesh, one armature, both Idle/Walk actions, 7,340 triangles, three materials, bounds delta `3e-07 m`, and zero reported root location/rotation/scale movement for each clip. This validates the documented Blender roundtrip only. |
| Idle/Walk neutral-pose claim consistency | PASS — retest | Regenerated manifest now reports `idle_walk_neutral_pose_match: true` and `idle_walk_neutral_max_matrix_component_delta: 0.0`, consistent with its neutral stopping contract. Its per-clip endpoint deltas and root translation/rotation/scale metrics are also zero. The earlier conflicting values (`false`, `0.03489949554204941`) were superseded by this retest; this result verifies record consistency, not visual blending. |
| Required animation coverage | NOT RUN | Only Idle and Walk are exported. The manifest explicitly defers Jump, Sit, Dance, LieDown and Celebrate; G09's broader animation checklist is not accepted by this asset review. |
| Unity import, Avatar/Animator, scale and runtime rig | NOT RUN | Manifest itself marks Unity import/prefab not run. Its 1.64 m source height versus 2.15 m existing CharacterController and proposed 1.310976 wrapper scale require Unity-owner validation; no Editor/Play Mode access was taken. |

## Visual notes

The model is appealing and immediately legible as a youthful traveller. The large hat/head, light shirt and dark lower body give a strong mobile silhouette; the sampled stride is broad enough to read. The evidence is three stills, not an animation review. There is no basis here to claim stable idle, loop seams, locomotion speed matching, clipping under continuous motion, or performance in the world scene.

## Required follow-up

1. **Unity owner:** import the staged FBX in an isolated wrapper, bind both named clips, validate axis/scale/Avatar and CharacterController fit, then capture gameplay-camera Idle/Walk evidence.
2. **QA retest:** review continuous playback and stop transition after those artifacts exist. Physical mobile validation remains separate and NOT RUN.

## Neutral-pose reconciliation retest — 2026-09-10

**PASS.** This retest read the regenerated manifest and roundtrip JSON only. The manifest's Idle/Walk neutral-pose boolean is now `true` and its maximum matrix-component delta is `0.0`; the roundtrip report remains `PASS` with the documented two actions, `7,340` triangles and zero root transform metrics. No preview, Blender scene, Unity import, Play Mode, Web build, or mobile device test was performed for this retest.
