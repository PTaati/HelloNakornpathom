# HNP-PROTOTYPE-001 — MCP / Blender / station prototype

Status: REVIEW — playable station trial delivered; physical mobile and Blender MCP verification remain open. Requirements: G01 (station only), G07 (basic controls), P01.

Input: root design documents, existing Unity URP project. Visuals are provisional original low-poly blockouts.
Write scope: `tools/`, `art-source/station/`, `art-export/station/`, `hnp-game/Assets/_HNP/`, `hnp-game/Assets/WebGLTemplates/HNP/`, `reports/`, `builds/web/`.

Acceptance:

- Discover and exercise Unity MCP using the installed relay, report Blender MCP availability separately.
- Create a Blender bench with source, FBX, preview and geometry manifest; verify imported scale/material/collider.
- Create a saved station prototype scene with movement, camera, jump and one interaction.
- Compile and exercise Play Mode; build Web when available. Real mobile tests remain NOT RUN without a device.

No existing scene is overwritten. Full train intro and full journey are outside this first trial.

## Handoff

- PASS: Unity MCP discovery and read-only preflight; Blender CLI bench generation/export/preview.
- Prepared: station builder, runtime movement/camera/jump/pickup/ending UI, touch controls and Web template.
- RESOLVED: user clarified accidental deny and authorized continuation. Unity MCP reconnected; transient discovery failure during script reload recovered on retry.
- PASS: saved scene, prefab material/collider/height verification, Play Mode movement/jump/landing, collection idempotency, ending gates and restart.
- Corrected mirrored 3D signs after screenshot review and saved the scene.
- BLOCKED: Blender MCP details unavailable; Blender CLI path is verified.
- PASS: revised Web build and Chrome startup/input/orientation smoke test; scene visuals verified from screenshots after explicitly configuring Mobile URP / WebGL2. Physical mobile tests NOT RUN.
- Evidence: `reports/environment.md`, `reports/unity-preflight.json`, `reports/unity-refresh.json`, `art-export/station/bench-manifest.json`.
- Additional evidence: `reports/unity-preflight-resume.json`, `reports/unity-create-station.json`, `reports/unity-play-tests.json`, `reports/unity-fix-signs.json`.
- Evidence: `reports/web-build.txt`, `reports/web-build-hashes.json`, `reports/web-smoke.json`, `reports/web-desktop.png`, `reports/web-landscape.png`, `reports/prototype-validation.md`.
- Next: physical mobile input/fullscreen/performance verification and Blender MCP connection details, then extend the station intro toward the bridge route. Do not mark the full production-plan milestones complete from this trial alone.
