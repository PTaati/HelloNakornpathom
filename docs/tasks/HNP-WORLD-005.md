# HNP-WORLD-005 — still pose, fast walk, vertical sky

Status: VERIFIED desktop Web. Root owns Unity exclusively; no art or scene regeneration.
Input: latest request supersedes authored Run and breathing Idle.
Write scope: world game and animation bridge; editor motion-only update; generated constant-pose animation/controller via Unity; fresh Web build; targeted tests/reports and local preview script.
Acceptance: no bottom Tip object/text; stopped skeleton remains identical across samples; Run references the exact Walk clip at 9/5.4 playback speed; camera pitch reaches -90 with forward.y=1 through pointer input, returns normally; build/browser errors absent. Physical device NOT RUN.

## Delivery / evidence

- Build `builds/world005/web`: PASS in `reports/world/world005-build.log`, including `HNP005_MOTION_PASS idle=constant run=Walk speed=1.666667` and successful build.
- Browser PASS: `reports/world/world005-camera-20260910-205937/report.json`, Chrome 152 desktop software WebGL. Test uses WASD, Run icon and pointer drag, not direct state setters.
- No Tip object, identical Walk clip in normal/fast states, playback multiplier 1.666667, static Idle clip after release, bone pose delta below 0.000001 after 1.5 seconds.
- 3.25 m camera distance preserved; pitch reaches -90 degrees and sky-facing direction on landscape and portrait; reverse drag returns normally. Zero page/console errors.
- Screenshot `still.png` inspected: bottom hint absent, standing pose visible. Other captures and numeric skeleton samples are in the same evidence directory.
- Local preview http://localhost:8081 updated; restart via `tools/serve-world003.ps1`. Hard-refresh older browser tabs.
- Physical-phone, full gameplay and performance regression NOT RUN; this is targeted motion/camera validation. No internet deployment.
- Rebuild via `HNP.Editor.HnpWorld003Integrator.BuildMotion005`: generates a constant pose from the existing Idle clip and binds Run to Walk in Unity while preserving existing controller GUID. Original authored art clips are retained, not deleted.
