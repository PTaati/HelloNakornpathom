---
name: hnp-unity-web
description: Implement Unity gameplay and integrate art for Hello Nakornpathom on mobile landscape Web, including touch input, scene and prefab integration, Web builds and targeted validation.
---

# Unity and mobile Web production

Use the project root containing `AGENTS.md` and `hnp-game/`. Read `docs/agents/TEAM.md` for ownership, `GAME_AGENT_SYSTEM.md` for G/P requirements and system contracts, and the relevant sections of `GAME_PRODUCTION_PLAN.md`. Inspect current code before designing a replacement system.

## Tool and Editor preflight

Read `hnp-game/ProjectSettings/ProjectVersion.txt` and package files. Discover tools in the current session. If Unity MCP is absent, inspect `tools/unity_mcp.py` and verify its installed relay executable before using it. Its default invocation lists capabilities; inspect returned schemas before any tools/call. `--code-file` currently hardcodes Unity_RunCommand, so use it only after that tool and its schema have actually been discovered. Do not fabricate MCP server addresses.

Obtain exclusive Editor ownership from root before import/build/Play Mode/scene mutations. Query active project, play/compile state and dirty scenes; `tools/unity_preflight.cs` is an existing read-only inspection candidate, to be inspected before use. Preserve pending user work with a checkpoint. Do not start a second Unity process on the same open project.

## Integration and gameplay

- Accept actual FBX/texture/manifest files with a revision. Preserve `.meta` and GUID. Check meter scale, orientation, bounds/pivot, URP material appearance, rig/clip import, wrapper prefab and collider against gameplay use. Confirm missing script/material/reference counts and camera views.
- Keep runtime state separate from data assets. Money/item transactions must commit once across repeated taps or minigame callbacks. A zero wallet must not enter GameOver and a minigame concurrently. Restore input/camera/state on cancel, scene change and failure.
- Touch needs independent pointer IDs for movement/camera/buttons and cancellation when focus or orientation changes. Input over UI must not leak into gameplay. Pause timers with the page/rotation overlay and clear held input before resuming.
- Test save consistency after committed transactions, corrupt/unavailable storage, repeat entry and retry paths only where the task affects them. Use existing test structure; avoid tests that only copy implementation details.
- Read `.github/workflows/deploy-pages.yml` when changing delivery: the existing workflow must be inspected to determine whether it builds Unity or only publishes a prebuilt directory. Build success is separate from browser gameplay success.
- Serve Web output over HTTP(S), verify loader/error handling and relevant response headers/cache behavior. Fullscreen/audio require user interaction and orientation/fullscreen fallbacks must remain playable. A generated build does not authorize an unrelated deployment.

## Handoff

Deliver feature/build revision, affected paths, how to play, expected behavior, console/test/build logs and unresolved issues. Assign PASS/FAIL/BLOCKED/NOT RUN separately for compile, asset validation, EditMode/PlayMode, Web browser and physical mobile checks. Transfer Editor ownership through root for QA, identifying active scene, checkpoint and play state. Raise difficult architectural/debugging issues to root with reproduction and attempted fixes instead of spending repeated broad retries.
