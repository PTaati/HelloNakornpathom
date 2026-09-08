import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(r/'art-source/world/Nakornpathom.blend'))
o=bpy.data.objects['Town_HNPW_Teal']
print('TEAL_TRANSFORM',o.matrix_world)
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if -108<p.x<-85 and abs(p.y)<1 and p.z>0:print('CENTRAL_VERTEX',tuple(p))
