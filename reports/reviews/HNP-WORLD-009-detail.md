# HNP-WORLD-009 — final art staging detail review

**Date:** 2026-09-10  
**Scope:** independent staging review only. Evidence: `art-export/hnp-world-009/HNP_Chedi_v009_preview_front.png`, `HNP_Temple_v009_preview_three-quarter.png`, `HNP_Temple_v009_preview_courtyard.png`, `manifest.json`, and `town-cleanup-manifest.json`; compared with `ref/jd.jpg`, `ref/pra.jpg`, `ref/jd-night.jpg`, and the HNP-WORLD-009 reference brief. No Blender source, Unity project, or FBX was modified by QA.

## Result

| Check | Status | Evidence / finding |
| --- | --- | --- |
| Landmark silhouette and cultural read | **PASS (stylized staging)** | The broad brick/terracotta bell, subordinate ribbed spire, low repeated-bay collar, lower moulding courses and pointed frieze now give a materially more recognisable Chedi hierarchy than v003. This is a mobile-scale interpretation of `jd.jpg`, not an exact measured reconstruction. |
| Primary front sanctuary | **PASS (stylized staging)** | The front preview has a tall, deep dark-red/gold pointed sanctuary, standing Buddha, white structural frame and stairs. It correctly distinguishes the primary `pra.jpg`-informed sanctuary from the smaller repeated side openings. Fine gold carving and the real interior ceiling remain intentionally simplified. |
| Perimeter / courtyard architecture | **PASS (stylized staging)** | The three-quarter view reads the orange tiled ring roof, white arcade wall, opening rhythm, dark guardian accents, radial court and cardinal entry breaks. These use the photographed white/terracotta/dark-inset language rather than the previous plain houses surrounding the landmark. |
| Materials, UV and shading | **PASS (preview + manifest)** | The previews show continuous repeat patterns across bell, frieze, roof and paving without an obvious seam or stretched patch. `manifest.json` maps all five repeating textures to UV0 and records two FBX round-trip PASS results with no degenerate faces or loose vertices. This is not a substitute for Unity material/shader inspection. |
| Chedi budget / export integrity | **PASS** | Visible Chedi geometry is 27,264 triangles (27,388 with collider), within the ≤30,000 main-landmark LOD0 budget; seven material slots; bounds 46.84 × 51.145 × 44 m; round-trip delta ≤0.000008 m. |
| Surroundings budget | **NOT RUN (profile gate)** | Surroundings are 40,912 visible triangles (42,260 with colliders) across an 84.6 m diameter set. The production plan has no separate measured allocation for this landmark-adjacent assembly. It is an explicit integration/performance profiling item, not evidence of a mobile-Web pass. |
| Town cleanup scope | **PASS (manifest)** | Cleanup manifest records exactly 34 roofs and 34 pillars removed, preserves source/round-trip 21,778 triangles, and has identical before/after collision hashes. There is no town beauty preview, so visual town cleanup is not claimed. |
| Preview completeness | **NOT RUN for finial close inspection** | Front and three-quarter detail frames crop the extreme spire tip; the macro silhouette blockout previously provided the full-body evidence. This does not block staging import, but final in-game distance/finial readability still needs Unity evidence. |
| Unity import, collider behavior, night lighting, Web/mobile | **NOT RUN** | Manifest explicitly records Unity import NOT RUN. No current Unity/gameplay camera, Web build, browser, or physical-device evidence was supplied. |

## Staging decision

**PASS — approve the v009 FBX staging assets for targeted Unity integration.** The model fixes the architectural identity deficiencies of v003 and supplies credible UV/round-trip evidence. The integration owner must retain the manifest's renderer-off collider intent, profile the 40.9k-triangle surroundings assembly in the actual scene, and provide game-camera day/night evidence before any runtime or mobile claim.

## Root-held visual gate correction

**Status update:** the preceding scoped staging PASS is **superseded; do not import this first-detail revision.** On a closer architectural read of the same three-quarter/courtyard evidence, the surrounding arcade is not yet a credible photo-faithful façade: it reads as a flat fence, with floating dark oval/guardian shapes and exposed arch-pipe forms. The arch peak sits visibly above its low eave and the filled spandrel/crossbar treatment is especially distracting across the front gable. The large high-contrast basket-weave tile pattern also overstates surface scale, while the white articulated façade is isolated rather than continuous.

| Corrective gate | Status | Required correction |
| --- | --- | --- |
| Arcade / façade construction | **FAIL** | Replace the fence/pipe read with real wall-and-arch meshes, continuous white base/facade mass, coherent eave-to-arch relationship, and integrated guardian details. |
| Surface scale / front-gable read | **FAIL** | Reduce tile contrast/scale so it supports rather than grids the bell and court; remove or redesign the thick dark crossbar/spandrel across the sanctuary gable. |
| Bounds / integration fit | **BLOCKED** | Manifest surroundings bounds reach ±42.312 m despite the stated r37 lower paving contract. Artist must reconcile actual bounds/intent before integration. |
| Corrected staging review | **NOT RUN** | Await corrected previews and revised manifest. Unity/Web/mobile remain NOT RUN. |

Root is holding the first-detail import. The earlier macro-silhouette PASS remains valid only for the previously reviewed blockout; it is not final visual approval.

## Corrected second-detail retest

**Evidence:** replaced v009 previews plus revised `manifest.json`, including `HNP_Temple_v009_preview_arcade-detail.png`; reviewed 2026-09-10. The arcade-detail camera deliberately cuts through the Chedi on its left and is a mesh diagnostic, not a beauty/gameplay view.

| Retest check | Status | Finding |
| --- | --- | --- |
| Bell, base and front sanctuary | **PASS (staging)** | The full framed front now has a smaller/lower-contrast brick treatment, continuous white circular lower band, resolved front-gable treatment and full finial. The broad terracotta bell, subordinate ribbed spire, ring courses and primary Buddha sanctuary maintain the intended photo-informed hierarchy. |
| Arcade/façade mesh | **PASS (staging geometry)** | The new detail diagnostic visibly shows a true open arch silhouette with jamb/wall geometry rather than the previous pipe/fence construction. The outer three-quarter view correctly lets the continuous base occlude much of the arcade at that camera height. Final gameplay-camera visibility/traversal is still **NOT RUN**. |
| Surface scale and readability | **PASS (staging)** | Reduced tile contrast no longer produces the dominating basket-weave grid of the held revision; white/terracotta/dark-inset separation is coherent at preview distance. |
| Bounds, UV and export | **PASS** | Revised surroundings visible bounds are ±36.727 m, consistent with the r37 contract; visible triangles are 23,984 (25,332 with colliders), with all 10 meshes reporting UV0. Chedi is 27,620 visible triangles (27,744 with collider), all 8 meshes UV0; both FBX round-trips PASS without degenerate or loose geometry. |
| Runtime integration / navigation / mobile | **NOT RUN** | No Unity import, gameplay camera, collider traversal, Web profile, browser or physical-device evidence has yet been supplied. |

**Updated integration gate: PASS for corrected v009 staging assets.** The root-held first-detail visual FAIL is resolved. Proceed with targeted Unity integration; retain the manifest's renderer-off collision intent and collect the separate runtime/gameplay-camera evidence before any Unity/Web/mobile acceptance.
