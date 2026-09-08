"""Original provisional station bench, generated with Blender, metres, Z up."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'art-export/station'
OUT.mkdir(parents=True, exist_ok=True)
# This script runs in a separate factory-startup background process.
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1

def material(name, color, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = .65
    bsdf.inputs['Metallic'].default_value = metallic
    return m

wood = material('HNP_Teak', (.42,.19,.065))
metal = material('HNP_DeepTeal', (.035,.16,.17), .3)
parts = []
def box(name, position, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object; obj.name = name; obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft edges', 'BEVEL'); bevel.width=.012; bevel.segments=1
    bpy.context.view_layer.objects.active=obj; bpy.ops.object.modifier_apply(modifier=bevel.name)
    parts.append(obj)
    return obj

for i in range(4): box('SeatSlat', (0,-.225+i*.15,.48), (1.8,.13,.065), wood)
for z in [.72,.90,1.08]: box('BackSlat',(0,.29,z),(1.8,.055,.13),wood)
for x in [-.69,.69]:
    for y in [-.21,.23]: box('Leg',(x,y,.225),(.065,.065,.45),metal)
    box('SeatSupport',(x,0,.42),(.075,.62,.07),metal)
    box('BackSupport',(x,.32,.78),(.06,.065,.67),metal)
    box('Armrest',(x,0,.73),(.09,.62,.055),wood)
    box('ArmSupport',(x,-.23,.60),(.05,.05,.26),metal)
bpy.ops.object.select_all(action='DESELECT')
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
bench = bpy.context.object; bench.name='HNP_Prop_StationBench_A'
scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(); bpy.ops.object.mode_set(mode='OBJECT')
bench.data.calc_loop_triangles()
report=dict(asset_id=bench.name, status='provisional', source='Original procedural design; station reference pending',
            unit='metres', dimensions=list(bench.dimensions), triangles=len(bench.data.loop_triangles),
            materials=[m.name for m in bench.data.materials], textures=[], clips=[],
            pivot='ground centre', collision='Unity compound boxes', blender_version=bpy.app.version_string)
(OUT/'bench-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.export_scene.fbx(filepath=str(OUT/'HNP_Prop_StationBench_A.fbx'),use_selection=True,
                        object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,
                        bake_anim=False,apply_unit_scale=True)
# Save an isolated art source with a camera suitable for preview.
bpy.ops.object.camera_add(location=(3.1,-3.6,2.5))
camera=bpy.context.object; camera.rotation_euler=(Vector((0,0,.55))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO'; camera.data.ortho_scale=2.9; scene.camera=camera
bpy.ops.object.light_add(type='AREA', location=(1,-2,4)); bpy.context.object.data.energy=450; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=4
scene.world.color=(.22,.22,.22)
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=1000; scene.render.resolution_y=760; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
scene.render.filepath=str(OUT/'bench-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/station/HNP_Prop_StationBench_A.blend'))
bpy.ops.render.render(write_still=True)
print('HNP_BENCH_PASS',json.dumps(report))
