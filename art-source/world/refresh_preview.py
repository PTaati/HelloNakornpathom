"""Reframe existing source to include the taller finial, without regenerating geometry."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'art-source/world/Nakornpathom.blend'))
bpy.context.scene.camera.data.lens=32
bpy.context.scene.render.filepath=str(root/'art-export/world/world-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'art-source/world/Nakornpathom.blend'))
bpy.ops.render.render(write_still=True)
