# HNP-ART-MAP-007 v003 — Final export handoff independent review

**Decision:** **PASS — art/export handoff for Unity staging.**  
**Scope:** MAP007 station, street, Saphan Yak bridge/canal, temple-approach kit and collision FBXs only. The Chedi remains the separate authoritative asset; Unity integration, simultaneous LOD/draw-call evidence, Web and physical mobile are **NOT RUN**.

## Evidence reviewed

- `art-export/HNP-ART-MAP-007/manifest-v003.json`
- `art-export/HNP-ART-MAP-007/roundtrip-v003.json`
- current route previews `route-01-station-exit`, `route-02-bridge-crossing`, `route-03-exterior-approach`, plus current bridge/station/town previews.

All twelve declared FBXs report roundtrip `PASS`, matching dimensions/triangle counts and zero degenerate faces. This replaces the v003 candidate's 219,988-triangle / 16-degenerate bridge finding.

| Gate | Status | Finding |
|---|---|---|
| Station/platform/town | **PASS** | The kit retains the meaningful light-roofed station, rail platform, Thai signboard, town frontage, utilities and direct road context; it no longer reads as the rejected box corridor. |
| Saphan Yak identity/scale | **PASS** | The bridge is compact, located at stated route stationing X=130, has four readable guardian-pavilion positions, 34.5m × 8.5m reference-led dimensions and real deck/rail/water context. It is stylised/reference-led, not claimed photoreal or survey-exact. |
| Player-height bridge proof | **PASS (visual)** | The corrected `route-02` now visibly places the player on the deck with pavement, rails, guardian frames and both road exits—resolving the prior black-under-mesh proof failure. |
| Direct route / temple approach | **PASS (visual)** | Route-01 and route-03 communicate a continuous direct road from station direction through bridge to exterior temple approach without invented zigzags/forced reveal tests. |
| Export/roundtrip integrity | **PASS (reported)** | 0 degenerate faces and matching expected/observed metrics across all 12 exports; collision exports are included. |
| Scale integration caution | **NOT RUN** | Manifest preview lists Chedi scale `2.7375`; current published-height integration must instead use the scene-owner's aggregate-visible-bounds scale/grade decision. Do not blindly apply preview scale. |
| Performance / colliders / game path | **NOT RUN** | LOD0 family totals are high (Station 41,956; Street 52,104; Bridge 52,308; Approach 26,892); sector/LOD behaviour and Chedi overlap must be profiled in Unity. Collision FBXs are not proof of player movement or entrance-seam clearance. |

## Unity handoff

Import only the final v003 exports/atlas/collision files. Preserve direct +X placement, use visible-surface-aligned collision, and run actual route traversal before release. Treat all public-place exact access/current architectural details as provisional, not a block on the user-authorized reference-led game simulation.
