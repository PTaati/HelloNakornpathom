# HNP-WORLD-010 — front sanctuary blockout review

**Evidence:** `art-export/hnp-world-010/HNP_Chedi_v010_blockout_front.png` and `HNP_Chedi_v010_blockout_three-quarter.png`, compared with `ref/pra.jpg`. No source, Unity or export asset was modified.

| Check | Status | Finding |
| --- | --- | --- |
| Photo facing and primitive replacement | **PASS (blockout)** | The supplied portrait appears upright/front-facing in the recess and the prior primitive visible Buddha is gone. At this distance no mirroring is evident. |
| Connected chamber form | **PASS (blockout)** | Three-quarter evidence shows a roofed, side-walled projection physically connected to the Chedi, with the portrait on the back wall of a rectangular recess; it is not an unbacked image plane. |
| Full-photo/aspect verification | **NOT RUN** | The preview is insufficient to prove pixel-exact uncropped `.4886` aspect or image hash. Final manifest and closer interior preview are required. |
| Route/collision and gameplay-camera occlusion | **NOT RUN** | No Unity or runtime route evidence exists for the new projection. Re-run four cardinal `gateDeviation: 0` stair approaches and inspect the actual gameplay camera after integration. |
| Final materials/UV/bounds/export | **NOT RUN** | Final staging manifest, FBX round-trip, material/UV and bounds evidence has not been supplied. |

**Decision: PASS for blockout form; proceed to final artist staging.** This is not a Unity, route, or Web acceptance.
