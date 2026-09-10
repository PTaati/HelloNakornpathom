---
name: hnp-design-qa
description: Design gameplay and art briefs, independently review Blender models, and validate Hello Nakornpathom mobile Web gameplay with reproducible evidence. Use for feature acceptance, visual review, playtesting and regression reports.
---

# Design and independent QA

Use the project root containing `AGENTS.md` and `hnp-game/`. Read `docs/agents/TEAM.md`, the relevant G/P requirements in `GAME_AGENT_SYSTEM.md` and test/budget sections in `GAME_PRODUCTION_PLAN.md`. For level layout, read the extracted Word text, `docs/design/MAP_LAYOUT.md` and actual source references.

## Design mode

Turn the assigned feature into observable acceptance: start conditions, player actions, success/failure/retry, exit state and edge cases. Link requirement IDs and identify provisional decisions. Preserve the mobile landscape target and route station-left → central road/bridge → temple. Do not silently include deferred minigames or treat prototype behavior as a final design decision.

For art briefs specify source references and uncertainty, gameplay purpose, silhouette, palette, dimensions/pivot, viewing distance, collider clearance, rig/animation/attachments and the applicable production budget. Separate a desired artistic outcome from a prescribed modeling technique.

## Blender review mode

Inspect actual reference and preview images with available image tools. Compare silhouette, proportions, palette and cultural/architectural details; image generation is not a substitute for mesh review. Inspect source/export reports for UV, normals, dimensions, triangles after modifiers, material/texture counts, rig/clips and clipping. Check a gameplay-camera view in Unity when available.

Use staging exports, previews or isolated copies; do not change the artist's live file. Missing visual access means visual review is NOT RUN or BLOCKED, not PASS based on a filename or manifest. Route mesh/UV/rig defects to Blender and import/material/prefab defects to Unity. Budget exceptions need evidence, not automatic rejection of the intended silhouette.

## Gameplay QA mode

Identify the exact build/hash, save/preconditions and device/OS/browser before execution. Review existing `tools/test_web.py` or `tools/test_world_web.py` before reuse, including target URL and side effects. Discover browser tooling rather than assume a browser is connected.

Choose relevant cases from the production plan: win/lose/retry, duplicate transactions, reload/save, simultaneous movement/camera/jump, pointer cancellation, UI hit blocking, safe area, rotation/fullscreen fallback, background/resume, audio and loading/cache failures. Obtain Editor ownership through root before Play Mode or scene changes; report-only work may run in parallel.

Record expected and actual behavior, frequency, evidence and bug owner/severity. A screenshot alone cannot prove input/flow correctness. Separate viewport emulation and physical Android/iPhone results; absent physical device access is NOT RUN. Historical PASS applies only to its recorded revision/device, not the current task. Do not repair implementation during independent review; send actionable defects to its owner and retest the correction.

## Report

Write task-assigned design files or `reports/reviews/` and `reports/qa/`. Include requirement/task IDs, revision/build, device/browser, steps, expected/actual, evidence paths, severity/owner and retest status. Use one of PASS, FAIL, BLOCKED or NOT RUN per check; split mixed outcomes into separate checks rather than invent PARTIAL PASS. NOT RUN means no execution evidence; BLOCKED means an attempted required check cannot proceed, with the concrete prerequisite recorded. A release gate can FAIL while constituent device tests remain NOT RUN. State remaining release-gate gaps separately from a completed documentation or setup task.
