from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "art-export" / "HNP-ART-MAP-007" / "production-v003-previews"
OUT.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

camera = bpy.data.objects.get("GameplayCamera_1p65m")
if camera is None:
    raise RuntimeError("GameplayCamera_1p65m is missing")
scene.camera = camera

collections = {
    "station": bpy.data.collections.get("MAP007_HERO_STATION"),
    "street": bpy.data.collections.get("MAP007_HERO_STREET_CORNER"),
    "bridge": bpy.data.collections.get("MAP007_HERO_BRIDGE_CANAL"),
    "temple": bpy.data.collections.get("MAP007_HERO_TEMPLE_APPROACH"),
    "route": bpy.data.collections.get("MAP007_DIRECT_ROUTE_PREVIEW_ONLY"),
    "chedi": bpy.data.collections.get("MAP007_AUTHORITATIVE_CHEDI_PREVIEW_ONLY"),
}
if any(value is None for value in collections.values()):
    raise RuntimeError("One or more MAP007 preview collections are missing")


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


shots = {
    "route-01-station-exit": (
        {"station", "street", "bridge", "route", "chedi"},
        (25, 0, 1.65),
        (150, 0, 4),
        34,
    ),
    "route-02-bridge-crossing": (
        {"street", "bridge", "route", "chedi"},
        (108, 0, 3.35),
        (160, 0, 3.5),
        36,
    ),
    "route-03-exterior-approach": (
        {"route", "chedi"},
        (410, 0, 1.65),
        (519, 0, 38),
        23,
    ),
}

for name, (active, position, target, lens) in shots.items():
    for key, collection in collections.items():
        collection.hide_render = key not in active
    camera.location = position
    camera.data.lens = lens
    aim(camera, target)
    scene.render.filepath = str(OUT / f"HNP_Map007_v003_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED {name}")

print("HNP_MAP007_V003_ROUTE_PROOFS_DONE")
