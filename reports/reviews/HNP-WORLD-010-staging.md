# HNP-WORLD-010 — final front-sanctuary staging review

**Evidence:** final `art-export/hnp-world-010/HNP_Chedi_v010_preview_{front,three-quarter,inside}.png`, `manifest.json`, `roundtrip.json`, and `ref/pra.jpg`. Staging only; Unity import and runtime were not performed by QA.

| Check | Status | Evidence / finding |
| --- | --- | --- |
| Actual photo orientation/content | **PASS** | The final inside preview now matches `pra.jpg`: the Buddha's raised hand is on viewer-left and the seated people/side details align. The prior mirrored preview is superseded. The image is complete, upright, unmirrored and visually undistorted. |
| Photo data / UV evidence | **PASS (manifest)** | Manifest records exact source-copy hash match, sRGB, full-frame UV0, no crop, 387×792 source at ratio 0.488636, and five front visibility rays hitting the photo mesh. |
| Connected chamber | **PASS (staging)** | Front and three-quarter previews show a roofed, side-walled projection connected into the Chedi. The plain rectangular dark recess frames the photo on a back wall; the primitive visible Buddha is absent. |
| Budget / export integrity | **PASS** | Visible geometry is 25,314 triangles (25,462 with colliders), under the 30k landmark budget; all 10 meshes report UV0. FBX round-trip PASS has no degenerate/loose geometry and maximum bounds delta 0.000004 m. |
| Route/collision/gameplay camera | **NOT RUN** | The manifest documents a 6.58 m central opening and sidewall collision intent, but Unity must rerun the four cardinal gate-deviation approaches and actual gameplay-camera review. |
| Unity/Web/mobile | **NOT RUN** | No import, runtime, browser, or physical-device evidence exists for this revision. |

## Decision

**PASS — corrected v010 staging asset is approved for targeted Unity import.** The first final preview was correctly held for a mirrored photo; the final rerender resolves it. Keep route/camera and device validation as separate post-import gates.
