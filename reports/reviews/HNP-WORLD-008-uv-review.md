# HNP-WORLD-008 — vehicle UV repair staging review

**Date:** 2026-09-10  
**Scope:** isolated repair exports in `art-export/hnp-world-008/`; the original v003 Blender source was not opened or modified by QA.

## Result

| Check | Status | Evidence |
| --- | --- | --- |
| Glass visual separation | **PASS** | All four actual previews (`HNP_{Sedan,Hatchback,Pickup,Minibus}_v003-preview.png`) show consistently dark, readable windscreen/side-window regions against their yellow, blue, red, and teal bodies. |
| UV0 repair evidence | **PASS (staging)** | `vehicle-uv-manifest.json` records matching repaired and FBX-roundtrip glass-loop counts: Sedan/Hatchback/Pickup 24 each; Minibus 48. Each entry is `status: PASS` and identifies a UV-layer-only repair. |
| Geometry/material budget preservation | **PASS (manifest)** | Manifest reports unchanged v003-style small-vehicle budgets: 2,472–3,132 triangles, two material slots each, metre units, and `-Z` forward / `Y` up. |
| Unity import into existing GUIDs and runtime cabin emission | **NOT RUN** | Static previews and manifest do not establish Unity's UV channel selection, material assignment, existing-GUID import, or night emission in the current build. Retest on the r4 night capture is required. |

## Handoff

**Staging approval: PASS.** The repaired exports are suitable for Unity's targeted reimport. Verify the final r4 capture has a subtle, correctly mapped warm cabin/window cue; it must not be inferred from these neutral-light previews.

**Known limitation, outside this repair:** close third-person vehicle occlusion is pre-existing world003 traffic behavior and is not evaluated as a new HNP-WORLD-008 UV/night-light release gate.
