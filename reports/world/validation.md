# Reference world validation — HNP-WORLD-001

Build: `NakornpathomWorld.unity`, Unity 6000.6.0f1, WebGL2 / Mobile URP. Date: 2026-09-08.

| Check | Result | Evidence |
|---|---|---|
| Original Blender town, chedi and traveller export/import | PASS | `art-source/world/`, `art-export/world/*manifest.json`, Unity FBX assets |
| Station left, canal, central avenue, chedi right and fair below | PASS — relative layout only | `aerial.png`, Unity `WorldMap.png`, reference `image2.png` |
| Golden bell, stepped base, collar, ringed spire and gabled entrances | PASS — stylized interpretation | `approach.png`, reference `jd.jpg` |
| Continuous walking: station, bridge, market, stairs, complete upper terrace, outer plaza, north/south bridges, station return | PASS | `traversal.txt`, `traversal.json`, `tools/unity_test_world.cs` |
| Jump and landing without falling through terrain | PASS | Same traversal test |
| Web build | PASS — 0 errors, 357 warnings, 52,132,717 bytes | `build.txt`; build completed despite MCP warning/error envelope |
| Desktop Chrome WebGL startup, keyboard movement, jump, map, landscape/portrait restoration | PASS | `web-smoke.json`, `web-desktop.png`, `web-landscape.png`, `web-map.png` |
| Physical Android/iOS device, multitouch and sustained FPS | NOT RUN | Desktop browser is not hardware mobile QA |

Traversal drives the actual CharacterController in Play Mode at 1/60-second steps; only initial setup resets position. It checks arrival, terrace elevation, descent, ground bounds and jumping. Failed direct routes encountered a tree and parked car; the final route uses the perimeter road and passes beside the car. Solid obstacles remain in the world.

FBX import mirrored X. Corrected model roots with X scale -1, keeping +Z aligned to the top of the reference. Welded and triangulated the chedi tip before export to remove invalid cap polygons.

Sources are original procedural Blender models. Blender ran through its CLI; Unity scene operations and gameplay tests ran through Unity MCP. Traveller uses separate pivoted limbs for procedural walking, not a skinned animation rig. Layout distances and unpictured station details are provisional, compressed for exploration. This delivery adds the explorable map/art; Word minigames remain future work.

Browser: Chrome 152.0.7977.76, Windows desktop, headless SwiftShader WebGL, 1280×720 and 844×390; portrait overlay checked at 390×844. Visual inspection confirmed dressed traveller, animated walking pose, temple visible along the avenue, material colors, UI and map. No JavaScript page errors or console errors. Runtime logs still mention stripped/unsupported optional URP postprocessing shaders; this scene disables postprocessing. Build warnings also include Unity Web toolchain compatibility/deprecation warnings. No clean-warning or mobile-performance claim is made.
