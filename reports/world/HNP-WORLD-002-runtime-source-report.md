# HNP-WORLD-002 runtime source handoff

Date: 2026-09-10.  Build identity: **not generated**; intended scene is `Assets/_HNP/Scenes/NakornpathomWorld.unity` on Unity 6000.6.0f1 / WebGL Mobile URP.

## Change scope

- `Assets/_HNP/Scripts/World/HnpWorldGame.cs`
  - Replaces oversized persistent cards with compact warm-gold/dark-teal landscape HUD controls. The shared button builder now enforces a 44px minimum width and height at the 1280x720 reference resolution. TIME/SOUND sit below the minimap with their state labels directly beneath; MAP is also placed below its map image. HOME is relocated to y=0, leaving a 26px gap from RUN after target-size clamping.
  - Removes the broken encoded arrow label strings in runtime UI and uses ASCII route separators.
  - Adds a manual `TIME` control and a runtime, 240-second visual day/night loop. It changes existing directional light, ambient light, fog, and the time label; it does not modify walkable geometry or colliders.
  - Adds original runtime-synthesized eight-second chime-loop music, created with `AudioClip.Create`. It is started only by the existing Start button gesture. `SOUND` mutes it; focus loss, portrait overlay, and map overlay pause it, and it resumes only after Start while focused in landscape. No downloaded or third-party audio is used.
  - Creates non-colliding runtime ambience under `HNP Runtime Living World`: five colored road vehicles on a deterministic loop, a station train loop that stays clear of the exit, eight distant birds (two remain at night), and repeated market canopies/lanterns. These use only Unity primitives and runtime URP materials.
  - Keeps station-left -> canal/central road -> chedi-right route, map, touch pads, and third-person camera unchanged.
- `Assets/_HNP/Scripts/World/HnpTravellerPose.cs`
  - Smooths controller-derived speed and walk/idle blend to reduce limb pop/stutter when a movement frame is temporarily blocked. It does not move the player root.

## Play/reproduction once Editor ownership is transferred

1. Open `NakornpathomWorld.unity` and enter Play Mode.
2. Tap/click `START`: music should start after this gesture only, the small `TIME` and `SOUND` controls appear at top right, and HUD remains minimal.
3. Wait or use `TIME` to observe the 240-second sunset/night/day loop. Open the map, rotate portrait, and background/resume: time, actors, and music should pause while suspended. Walk station -> bridge/canal -> market -> chedi; cars/train/birds are visual ambience and must not block traversal.
4. Walk/run/stop/jump repeatedly on flat ground and stairs. The traveller should settle from walk to idle without the old abrupt visual snapping.
5. Use `SOUND` to mute/unmute. Test map, portrait overlay, focus loss/resume, and a Web build/browser session after a safe Editor handoff.

## Validation status

| Check | Result | Evidence / limitation |
|---|---|---|
| Source scope / diff review | PASS | Only the two assigned world runtime scripts and this report changed. No art-source, art-export, scene, prefab, settings, package, or meta file was changed. |
| Static source inspection | PASS | `Box` destroys every primitive `BoxCollider` immediately, including traffic, train, birds, lanterns, and canopies, so ambience has no physics collision. `Update` now returns before `TickLife` for focus/portrait/map suspension and calls `SetMusicPaused`; `Btn` clamps both dimensions to 44px and gives TIME/SOUND/MAP non-overlapping below-minimap positions. Required namespaces cover UI, Input System, Event System, and the existing touch-pad contract. Audio is created in memory after `Begin`, not imported/downloaded. Existing public `Step`, `Begin`, `ReturnToStation`, and `SetHeading` contracts are retained for the world traversal command. |
| Unity compile | NOT RUN | Multiple Unity.exe processes were active; relay `tools/list` timed out and dirty/play/compile state could not be verified. |
| EditMode / PlayMode | NOT RUN | Blocked by unverified shared Editor state; no Play Mode was entered. |
| Asset/scene/prefab validation | NOT RUN | No import or scene mutation was authorized. |
| WebGL build | NOT RUN | No build was authorized while the active Editor state is unknown. |
| Desktop browser | NOT RUN | Requires a new build. |
| Physical Android/iOS | NOT RUN | No physical-device test was available or claimed. |

## Open issues / next owner checklist

- The intended UI/lighting/traffic result must be compiled and visually inspected in Unity before claiming feature acceptance. In particular, confirm mobile touch target sizing and that the runtime URP shader lookup succeeds with the project’s pipeline asset.
- Re-test the existing `tools/unity_test_world.cs` traversal at day and night. Cars/train intentionally remain ambience-only for this increment; G02 collision/retry is not implemented.
- Validate audio lifecycle in a served WebGL build: Start-only audio, mute behavior, focus loss, portrait overlay, and browser autoplay behavior. Browser autoplay rejection/fallback is **NOT RUN**: this code intentionally does not fake a `Tap for sound` outcome, because only an actual browser test can establish it. This source pass cannot establish a physical-mobile result.
- The project uses no runtime asset manifest for the synthesized sound because the clip is generated in memory. Its provenance is original procedural synthesis in `HnpWorldGame.Loop`.
