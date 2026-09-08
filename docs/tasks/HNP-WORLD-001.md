# HNP-WORLD-001 — Reference-based town and character

Status: COMPLETE — playable reference world; physical mobile QA NOT RUN

Inputs: `ref/game-document/image2.png` (layout), `ref/jd.jpg` (chedi form), `ref/style.jpg` (warm stylized art), `docs/design/MAP_LAYOUT.md`.
Scope: new `NakornpathomWorld.unity`, Blender world/chedi/traveller sources and FBX, exploration controller/UI, Web build, traversal and screenshot evidence. Existing station test scene stays available.

Acceptance:

- Station left, canal/bridge, central approach, chedi right; top-down comparison recorded.
- Original Blender chedi has stepped circular base, bell body, collar and segmented tapering spire, plus gabled entrance.
- Warm sunset, faceted foliage, streets, canal, shops, festival stalls and a dressed character with walking limb movement.
- Character can walk from station over bridge to temple, around upper terrace and across north/south public areas; solid buildings and canal edges block unsafe entry.
- Web build renders correctly and keyboard/touch controls remain available. Physical mobile performance explicitly untested without hardware.

Scale is compressed and provisional, not a surveyed digital twin. No new minigame rules are introduced in this map/art task.

Delivered: Blender sources and three FBX models, Unity scene and prefabs, free exploration with animated traveller, minimap/full map and landscape controls, WebGL build. Traversal passed through station, market, stairs, full upper terrace and all three bridges; jump/landing passed. Chrome browser and visual checks passed. Evidence and limitations: `reports/world/validation.md`. Launch instructions: `START_PROTOTYPE.md`.
