# HNP-WORLD-007 — sprint duration and circular cooldown

Status: VERIFIED targeted desktop Web. Root exclusive Unity owner. Inputs: latest world006 and user request.
Scope: HnpWorldGame sprint state/UI, vector ring graphic, Animator bridge keyboard bypass removal, build entry point, targeted tests/reports/local preview.
Acceptance: icon/Shift starts one 5-second sprint at existing 5x speed; expiry automatically restores walking, disables button for 5 more seconds, draws a filling circular ring; spam/held Shift cannot reset or bypass; ready restores button/hides ring; menu/focus pause follows existing active game clock. Desktop Web/build PASS; real-phone NOT RUN.
Timing starts on activation, including time standing still. Active sprint cannot be extended or toggled off by repeated taps. Requires a new press after cooldown, never auto-restarts from held Shift.

## Delivery and evidence

- Unity compile/build PASS: `reports/world/world007-build.log`, `Build Finished, Result: Success`. Existing motion controller/art and world clock preserved.
- Browser PASS: `reports/world/world007-sprint-20260910-212018/report.json`, Chrome 152 desktop software WebGL; 1280×720 and 390×844 viewports. Zero page/console errors.
- Run state playback 5 automatically changed to Walk playback 1 with movement held. Sprint deadline 5.324 active seconds; cooldown observed at 5.368; cooldown deadline 10.324. First ready observation at 10.513 (sampling latency). Repeated clicks did not alter deadlines.
- Disabled button and Shift presses during cooldown could not start running. Held Shift did not restart on ready; a fresh Shift press did. In-game menu pause preserved active time/progress for 1.3 real seconds.
- Filling ring visibly inspected in `portrait-ring.png`; portrait cooldown disables the button, recovery hides the ring, then tapping the portrait Run button starts the next sprint. Landscape capture `cooldown-ring.png` also retained.
- Build `builds/world007/web`; WASM SHA-256 `cbb4c73aca73062532d8d3832fe7d075eedc03347f4bf7264eee8d05381aa1e8`. Local preview http://localhost:8081 updated. Restart with `tools/serve-world003.ps1`; hard-refresh older tabs.
- Reproduce test: `python tools/test_world007_sprint.py`; build entry `HNP.Editor.HnpWorld003Integrator.BuildSprint007`.
- Earlier test failure `world007-sprint-20260910-211919` sampled the Idle-to-Walk-to-Run transition before completion. Retest waits for rendered state; production code/build unchanged between tests.
- Physical phones, background-resume and full gameplay regression NOT RUN. No public deployment performed.
