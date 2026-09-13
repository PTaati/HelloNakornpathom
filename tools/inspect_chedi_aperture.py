"""Read-only source check: centerline visibility through the v004 prayer entrance."""
import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'art-source/HNP-ART-CHEDI-001/HNP_Chedi_Modular_ProductionStaging_v004.blend'))
trees=[]
for obj in bpy.data.objects:
    if obj.type!='MESH' or not any(c.name.startswith(('HNP_Chedi_M01','HNP_Chedi_M03','HNP_Chedi_M04')) for c in obj.users_collection): continue
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    trees.append((obj.name,BVHTree.FromPolygons(verts,[list(p.vertices) for p in obj.data.polygons])))
samples=[]
for z in (.7,1.65,3):
    for y in (-32,-29,-27,-24,-21):
        hits=[]
        for name,tree in trees:
            location,normal,index,distance=tree.ray_cast(Vector((0,y,z)),Vector((0,1,0)),40)
            if location is not None:hits.append({'object':name,'point':list(location),'distance':distance})
        samples.append({'origin':[0,y,z],'hits':sorted(hits,key=lambda x:x['distance'])[:3]})
report={'task':'HNP-RELEASE-20260913','source':'v004','readOnly':True,'samples':samples}
path=root/'reports/qa/HNP-RELEASE-20260913-source-aperture.json'
path.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
