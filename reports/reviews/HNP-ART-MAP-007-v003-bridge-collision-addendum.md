# HNP-ART-MAP-007 v003 — bridge/collision correction addendum

**Task:** HNP-RELEASE-20260913 / HNP-ART-MAP-007  
**Decision:** **PASS — revised Blender export and visual handoff only.**  
**Not a Unity/gameplay approval:** collision traversal and the final integrated scene remain **NOT RUN** here.

## Evidence independently inspected

- `art-export/HNP-ART-MAP-007/production-v003-previews/HNP_Map007_v003_route-02-bridge-crossing.png` (11:12:33, 13 Sep 2026)
- `art-export/HNP-ART-MAP-007/manifest-v003.json` (11:13:10)
- `art-export/HNP-ART-MAP-007/roundtrip-v003.json`
- FBX hashes recomputed locally:
  - `HNP_Map007_BridgeCanal_LOD0_v003.fbx`: `d067c2a4142bcbd7deb88b8fd0f0808c14cb3299fb9cd2a6692701573f00b682`
  - `HNP_Map007_BridgeCanal_Collision_v003.fbx`: `4a0d28c51bd33e94b39e4702030900fa4708dfe77e6e09e101ce8844685d9d58`

## Gate results

| Gate | Status | Result |
|---|---|---|
| Direct bridge visual | **PASS** | The player-height render now reads as a usable road bridge: foreground lead-in reaches the deck, rails define the sides, guardian-pavilion columns frame the crossing, and the road exits toward the temple. It is a stylised/reference-led rendition, not a survey or photoreal claim. |
| Revised export integrity | **PASS** | The manifest and round-trip report declare 55,492 LOD0 / 30,674 LOD1 bridge triangles and 312 collision triangles, with zero degenerate faces and matching dimensions. The two revised FBX hashes above match the manifest. |
| Collision/gameplay surface | **NOT RUN** | An exported collision mesh and a render cannot demonstrate that the Unity CharacterController is above the visible deck, can enter/leave both ramps, or avoids canal-bank blockers. This directly addresses the prior integrated-scene FAIL; Unity must provide fresh player-height screenshots and a no-teleport route run. |
| Mobile Web budget | **NOT RUN** | No final integrated Web profiling/sector-LOD evidence was supplied. Bridge LOD0 is 55,492 triangles, so budget acceptance must use the final build rather than this source-only review. |

## Required integration retest

Unity owner: import these exact hashes, remove/disable the legacy flat bridge collider, and capture a player-height approach, on-deck, and exit frame plus the final Web route traversal. A source art PASS must not be used to close the earlier Unity physical-path failure.
