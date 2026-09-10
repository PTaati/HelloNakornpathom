# HNP-WORLD-004 — closer camera and sky look

Status: VERIFIED desktop Web; physical mobile NOT RUN. Owner: root, exclusive Unity writer. Requirement: G07.
Input: current r3 world and user's request for half camera distance and sky-facing look.
Write scope: HnpWorldGame.cs camera logic/diagnostics, editor build entry point, tools camera test/server, fresh builds/world004/web, this task and reports/world camera evidence.
Acceptance: unobstructed follow radius 3.25 m (was 6.5); pitch reaches -85 degrees through drag; camera forward points skyward without placing the camera below ground; return to normal look works; portrait works; Unity build and desktop Web checks PASS. Physical mobile separately NOT RUN.
Implementation: keep positional orbit pitch above -18 degrees while allowing viewing pitch to -85 degrees, avoiding a below-ground orbit at maximum sky look. Existing wall spherecast remains intact. No scene/art regeneration.

## Results

- Unity compile/build PASS: `reports/world/world004-build.log`, `Build Finished, Result: Success`.
- Browser pointer-drag tests PASS: `reports/world/world004-camera-20260910-204711/report.json`; Chrome 152.0.7977.83 desktop software WebGL, landscape 1280×720 and portrait 390×844. Zero console/page errors.
- Initial radius measured 3.2499995 m; maximum upward pitch -85°, forward.y 0.99619; camera y 0.52069 above the station ground. Reverse drag returned pitch to +40.18°. Portrait reached -85° as well.
- Actual screenshots inspected: `close.png`, `sky.png` in that evidence folder; camera changes are visible, not merely configured values.
- Build: `builds/world004/web`; WASM SHA-256 `b5be753123d6be0e218d288723f3a237bf7ba0ed5f2e7c92a6efe227389860b5`.
- Local preview updated to http://localhost:8081 ; restart via existing `tools/serve-world003.ps1`, now pointing at world004. Prior r3 artifacts preserved.
- Reproduce: start game; drag upward on the right-side open screen repeatedly to look skyward, downward to return. WASD/joystick behavior is unchanged.
- Physical-phone and full-world regression NOT RUN for this camera-only revision. No internet deployment performed.
