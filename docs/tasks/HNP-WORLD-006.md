# HNP-WORLD-006 — accelerated world clock and 5x running

Status: VERIFIED targeted desktop Web. Root exclusive Unity owner. Scope: world clock/lighting/sky shader, run constants/Animator state, targeted Web build/tests and local preview. Inputs: world005 and latest user request.

Acceptance: 10 game minutes per active real second (144 real seconds/day); automatic day/night transition; visible sun and directional light use same moving direction; paused menus/focus do not advance time; run movement 27 m/s and Walk playback 5x, stopped pose unchanged. Build and targeted desktop Web PASS; physical phones NOT RUN.

Implementation uses monotonic realtime differences while actively playing, resetting baseline on focus/pause. Sunrise around 06:00, noon 12:00, sunset 18:00; stylized trajectory, not astronomical ephemeris. Existing manual day/night menu remains, displaying HH:mm in Thai.

## Results / delivery

- Unity build PASS: `reports/world/world006-build.log`, run multiplier 5, move speed 27, Build Finished Success. No scene/art regeneration.
- Desktop Web PASS: `reports/world/world006-camera-20260910-210914/report.json`, Chrome 152.0.7977.83 software WebGL. Automated WASD/button input measured walking 5.4000023 m/s and running 27.0000028 m/s; Run uses the same Walk clip at state speed 5. Static stopped pose remains stable and bottom hint remains absent.
- Active cycle observed for 81.097 seconds: minutes 585.58014 → 1396.54858, measured 9.999981 game minutes/real second. Day and automatic night both reached. Thirteen samples verify rendered sky sun direction equals directional-light direction; menu pause holds game minutes unchanged for 2.2 seconds. Zero console/page errors.
- Inspected actual cycle-0/cycle-6/cycle-12 screenshots in that report directory: changing illumination/shadows and night sky are visible.
- Build `builds/world006/web`, WASM SHA-256 `07d28292af0f69e89183e216f2a001a79ebdadbd4983166ad5a90c5a23abdf03`. Preview http://localhost:8081 now serves this build. Restart with `tools/serve-world003.ps1`; hard-refresh older tabs.
- Rebuild entry point `HNP.Editor.HnpWorld003Integrator.BuildTime006`. Reproduce with `python tools/test_world006_time.py`.
- Physical phones, full 24-hour wrap/endurance, and background-resume browser regression NOT RUN for this revision. Clock/focus reset is implemented; tested pause case is the in-game menu. No internet deployment performed.
