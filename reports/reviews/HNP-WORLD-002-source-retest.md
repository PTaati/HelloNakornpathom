# HNP-WORLD-002 — independent source-only retest

**Date:** 2026-09-10  
**Scope:** Static review only of `HnpWorldGame.cs`, `HnpTravellerPose.cs`, the task brief, and `reports/world/HNP-WORLD-002-runtime-source-report.md`. No Editor, Play Mode, scene, asset, build, browser, or device action was performed.

## Outcome

| Check | Status | Static evidence / limitation |
|---|---|---|
| Gesture-gated music start | PASS | The only in-script call to `StartMusic()` is `Begin()`; the shipped UI wires `START` to `Begin()`. The `AudioSource` and generated clip are created after that path, not in `Awake`. Static evidence cannot prove browser autoplay acceptance. |
| Mute control | PASS | `SOUND` invokes `ToggleMusic()`, toggling `AudioSource.mute` and its text. Actual tap, persistence/reload and audio output are NOT RUN. |
| Audio/focus/portrait lifecycle | FAIL | `OnApplicationFocus`/`OnApplicationPause` only reset input. `TickLife(Time.unscaledDeltaTime)` runs before the focus/portrait/map early-return. Therefore actors/time continue and music is neither paused nor faded/muted behind focus loss, portrait overlay, or map—contrary to the brief's portrait pause requirement. Owner: Unity runtime. |
| Fullscreen/autoplay fallback | FAIL | No fullscreen request or `Tap for sound` fallback path is present in reviewed source. This fails the specified implementation contract; browser behavior is also NOT RUN. Owner: Unity/Web runtime. |
| Non-blocking actors | PASS | All ambience originates through `Box`, which destroys each primitive collider. Cars/train/birds therefore have no source-created physics collider; actor movement uses deterministic waypoint loops. G02 collision/retry remains absent (ambience-only), as disclosed. Visual clearance and traversal are NOT RUN. |
| Time loop and birds | PASS | `TickLife` increments a 240-second repeating `worldTime`, updates ambient/fog/sun, advances actors, and deactivates six of eight birds below daylight threshold. It does not write player/collider geometry. Runtime continuity, night readability, lighting pop, shader validity and performance are NOT RUN. |
| UI safe-area anchoring | PASS | HUD and controls parent to the runtime `safe` rect, whose anchors use `Screen.safeArea`. Actual safe-area rendering is NOT RUN. |
| UI touch target/layout | FAIL | At 1280×720 reference resolution, TIME/SOUND are 66×31/72×31, MAP 144×21, RUN 66×34 and HOME 66×30: each has a dimension below the brief’s 44 CSS-px minimum. TIME/SOUND also overlap the top portion of the 154×112 minimap: their y spans reach about -40.5 while the minimap begins at -30 relative to the top-right anchor. Owner: Unity UI. |
| Animation/root contract | PASS | `HnpTravellerPose` only writes limb/head local rotations; it does not write the character root. It smooths controller-derived speed and blends limbs toward idle, which supports the no-root-drift design intent. Visual foot planting, clipping, pop, stable 60-second idle, run distinction and landing recovery are NOT RUN. |
| Traversal API/regression contract | PASS | `Begin`, `Step`, `ReturnToStation`, and `SetHeading` remain public; `Step` retains safe-position/fall recovery and calls pose after controller movement. Existing route/collider success at day/night is NOT RUN for this revision. |

## Acceptance interpretation

The source demonstrates that W2 ambience and time-of-day were added and are intentionally non-blocking. It does **not** establish UI visual polish, lighting quality, animation quality, Play Mode traversal, WebGL behavior, or real mobile performance. The source-level failures above mean the delivered code does not yet fully meet the HNP-WORLD-002 UI/audio contract; they should be corrected before a feature retest.

## Required retest evidence

After the Unity owner corrects the two source failures: compile log; Play Mode video for idle/walk/run/jump and route at day/night; traversal test at day/night; served WebGL test covering Start, blocked audio, mute, focus/background, map, portrait and fullscreen fallback; and Android Chrome plus iPhone Safari records with build hash, OS/browser, safe area and frame-time/memory evidence.

## Corrective source retest — 2026-09-10

**Scope:** final `HnpWorldGame.cs` only; no compilation or execution. This section supersedes the earlier lifecycle and UI findings where noted.

| Corrected check | Status | Static evidence / limitation |
|---|---|---|
| Focus, portrait and map suspend world life | PASS | `Update` derives `suspended` from not-started, focus, portrait, and map state; it calls `SetMusicPaused(suspended)` and returns before `TickLife`. Thus this source path does not advance actors/time while suspended. `OnApplicationFocus`, `OnApplicationPause`, and `ToggleMap` also reset input and pause music when entering their respective suspended states. Runtime verification is NOT RUN. |
| Resume music after suspension | PASS | `SetMusicPaused(false)` calls `UnPause` only when started, focused, landscape, map closed, unmuted, and not already playing. This is static control-flow evidence only; audible resume/browser lifecycle behavior is NOT RUN. |
| 44 px minimum touch target | PASS | `Btn` clamps both dimensions through `Mathf.Max(44, ...)`; TIME, SOUND, MAP, RUN and HOME therefore meet the minimum in reference-canvas units. Actual CSS/device size and safe-area rendering are NOT RUN. |
| TIME/SOUND versus minimap | PASS | TIME/SOUND are repositioned to y=`-172` (44 px high), below the minimap frame's y span of `-142..-30`; their controls do not overlap that frame by source geometry. Visual rendering is NOT RUN. |
| All control non-overlap | FAIL | RUN and HOME share x=`-135`. After the universal 44 px height clamp, RUN spans y=`48..92` and HOME y=`12..56` from the bottom-right anchor, overlapping by 8 reference pixels. Owner: Unity UI. This is a source-geometry finding; actual rendered layout remains NOT RUN. |
| Fullscreen/autoplay fallback | NOT RUN | No served WebGL/browser test was run. This review does not convert source inspection into browser acceptance. |
