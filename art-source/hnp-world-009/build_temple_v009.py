"""HNP-WORLD-009 reference-led Phra Pathom Chedi and temple surroundings.

Coordinates passed to geometry helpers are game-local X/Y-up/Z. Blender forward
is -Y and export uses -Z forward, Y up. Run in a new factory-startup process.
Use without --detail for the required silhouette review; use --detail for final.
"""

import bpy
import bmesh
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "art-source" / "hnp-world-009"
OUT = ROOT / "art-export" / "hnp-world-009"
SRC.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
DETAIL = "--detail" in sys.argv

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0
scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.resolution_percentage = 100
scene.render.fps = 24
for existing in scene.objects:
    existing.hide_render = True
    existing.hide_viewport = True


def w(point):
    return Vector((point[0], -point[2], point[1]))


PALETTE = {
    "HNP009_GoldBrick": [0.76, 0.36, 0.075, 1.0],
    "HNP009_GoldHighlight": [1.0, 0.64, 0.12, 1.0],
    "HNP009_Terracotta": [0.46, 0.135, 0.065, 1.0],
    "HNP009_Ivory": [0.92, 0.88, 0.74, 1.0],
    "HNP009_White": [0.98, 0.97, 0.90, 1.0],
    "HNP009_DarkInset": [0.055, 0.032, 0.024, 1.0],
    "HNP009_GuardianBronze": [0.095, 0.12, 0.105, 1.0],
    "HNP009_RoofOrange": [0.83, 0.27, 0.065, 1.0],
    "HNP009_RoofGreen": [0.055, 0.28, 0.17, 1.0],
    "HNP009_Paving": [0.48, 0.18, 0.10, 1.0],
}


def make_material(name, rgba, metallic=0.0, roughness=0.7):
    material = bpy.data.materials.new(name)
    material.diffuse_color = rgba
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return material


M = {
    key: make_material(key, color, 0.18 if "Gold" in key else 0.0, 0.46 if "Gold" in key else 0.78)
    for key, color in PALETTE.items()
}
# Ceramic-clad bell is not metal; reserve metallic response for Buddha/gold trim.
M["HNP009_GoldBrick"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = .02
M["HNP009_GoldBrick"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .68
M["HNP009_GoldHighlight"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = .34

TEXTURE_MAPPINGS = {
    "HNP009_GoldBrick": "HNP009_GoldBrick_Tile.png",
    "HNP009_Terracotta": "HNP009_Terracotta_Frieze.png",
    "HNP009_Paving": "HNP009_Terracotta_Paving.png",
    "HNP009_RoofOrange": "HNP009_RoofOrange_Tile.png",
    "HNP009_RoofGreen": "HNP009_RoofGreen_Tile.png",
}


def make_pattern_texture(material_name, filename, base, line, mode):
    size = 128
    image = bpy.data.images.new(filename, width=size, height=size)
    pixels = []
    for y in range(size):
        for x in range(size):
            if mode == "diamond":
                edge = ((x + y) % 8 < 1) or ((x - y) % 8 < 1)
            elif mode == "brick":
                edge = y % 16 < 2 or (x + (8 if (y // 16) % 2 else 0)) % 24 < 2
            else:
                edge = x % 18 < 2 or y % 12 < 2
            color = line if edge else base
            pixels.extend((*color, 1.0))
    image.pixels = pixels
    image.filepath_raw = str(OUT / filename)
    image.file_format = "PNG"
    image.save()
    material = M[material_name]
    nodes = material.node_tree.nodes
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = "Unity BaseColor Texture"
    texture.image = image
    texture.interpolation = "Linear"
    material.node_tree.links.new(texture.outputs["Color"], nodes["Principled BSDF"].inputs["Base Color"])


if DETAIL:
    make_pattern_texture("HNP009_GoldBrick", TEXTURE_MAPPINGS["HNP009_GoldBrick"], (.78, .39, .09), (.66, .30, .065), "diamond")
    make_pattern_texture("HNP009_Terracotta", TEXTURE_MAPPINGS["HNP009_Terracotta"], (.48, .14, .065), (.37, .095, .045), "diamond")
    make_pattern_texture("HNP009_Paving", TEXTURE_MAPPINGS["HNP009_Paving"], (.52, .20, .11), (.24, .07, .04), "brick")
    make_pattern_texture("HNP009_RoofOrange", TEXTURE_MAPPINGS["HNP009_RoofOrange"], (.86, .29, .07), (.53, .10, .035), "roof")
    make_pattern_texture("HNP009_RoofGreen", TEXTURE_MAPPINGS["HNP009_RoofGreen"], (.06, .31, .18), (.025, .12, .08), "roof")


def new_collection(name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


chedi_collection = new_collection("HNP009_CHEDI")
surroundings_collection = new_collection("HNP009_TEMPLE_SURROUNDINGS")


def own(obj, name, material_name, collection):
    obj.name = name
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    if material_name:
        obj.data.materials.append(M[material_name])
    return obj


def recalc(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()


def cube(name, point, dimensions, material, collection, bevel=0.0, rotation_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=w(point), rotation=(0, 0, -rotation_z))
    obj = own(bpy.context.object, name, material, collection)
    obj.dimensions = (dimensions[0], dimensions[2], dimensions[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Crafted edge", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def cylinder(name, point, radius, depth, material, collection, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=w(point))
    return own(bpy.context.object, name, material, collection)


def sphere(name, point, scale, material, collection, segments=12, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=w(point))
    obj = own(bpy.context.object, name, material, collection)
    obj.scale = (scale[0], scale[2], scale[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def beam(name, a, b, radius, material, collection, vertices=8):
    va, vb = w(a), w(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=(vb - va).length, location=(va + vb) / 2)
    obj = own(bpy.context.object, name, material, collection)
    obj.rotation_euler = (vb - va).to_track_quat("Z", "Y").to_euler()
    return obj


def mesh_object(name, vertices, faces, material, collection, smooth=False):
    data = bpy.data.meshes.new(name + "Mesh")
    data.from_pydata([w(vertex) for vertex in vertices], [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    data.materials.append(M[material])
    recalc(obj)
    if smooth:
        for polygon in data.polygons:
            polygon.use_smooth = True
    return obj


def lathe(name, profile, material, collection, segments=64, cap=True):
    vertices = [
        (radius * math.cos(index * math.tau / segments), height, radius * math.sin(index * math.tau / segments))
        for radius, height in profile
        for index in range(segments)
    ]
    faces = []
    for row in range(len(profile) - 1):
        for index in range(segments):
            a = row * segments + index
            b = row * segments + (index + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    if cap:
        faces.append(tuple(reversed(range(segments))))
        faces.append(tuple((len(profile) - 1) * segments + index for index in range(segments)))
    return mesh_object(name, vertices, faces, material, collection, smooth=True)


def annular_sector(name, inner, outer, height, thickness, start_angle, end_angle, material, collection, segments=12):
    vertices = []
    for y in (height - thickness / 2, height + thickness / 2):
        for radius in (inner, outer):
            for index in range(segments + 1):
                angle = start_angle + (end_angle - start_angle) * index / segments
                vertices.append((radius * math.cos(angle), y, radius * math.sin(angle)))
    row = segments + 1
    faces = []
    bottom_inner, bottom_outer, top_inner, top_outer = 0, row, row * 2, row * 3
    for index in range(segments):
        faces.extend([
            (top_inner + index, top_inner + index + 1, top_outer + index + 1, top_outer + index),
            (bottom_outer + index, bottom_outer + index + 1, bottom_inner + index + 1, bottom_inner + index),
            (bottom_inner + index, bottom_inner + index + 1, top_inner + index + 1, top_inner + index),
            (top_outer + index, top_outer + index + 1, bottom_outer + index + 1, bottom_outer + index),
        ])
    faces.extend([
        (bottom_inner, top_inner, top_outer, bottom_outer),
        (bottom_inner + segments, bottom_outer + segments, top_outer + segments, top_inner + segments),
    ])
    return mesh_object(name, vertices, faces, material, collection)


def radial_profile_sector(name, profile, start_angle, end_angle, material, collection, segments=16):
    """Closed annular roof/trim sector from radial profile [(radius,height), ...]."""
    vertices = []
    for radius, height in profile:
        for index in range(segments + 1):
            angle = start_angle + (end_angle - start_angle) * index / segments
            vertices.append((radius * math.cos(angle), height, radius * math.sin(angle)))
    row = segments + 1
    faces = []
    for profile_index in range(len(profile) - 1):
        for index in range(segments):
            a = profile_index * row + index
            faces.append((a, a + 1, a + row + 1, a + row))
    faces.append(tuple(profile_index * row for profile_index in range(len(profile))))
    faces.append(tuple(reversed([profile_index * row + segments for profile_index in range(len(profile))])))
    return mesh_object(name, vertices, faces, material, collection)


def gable_panel(name, center_z, bottom, peak, half_width, depth, material, collection):
    z0 = center_z - depth / 2
    z1 = center_z + depth / 2
    vertices = [
        (-half_width, bottom, z0), (half_width, bottom, z0), (0, peak, z0),
        (-half_width, bottom, z1), (half_width, bottom, z1), (0, peak, z1),
    ]
    faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return mesh_object(name, vertices, faces, material, collection)


def arch_polyline(name, angle, radius, base_height, half_width, arch_radius, material, collection, depth=0.12):
    points = []
    # Left upright, semicircle, right upright in tangent/vertical plane.
    samples = [(-half_width, base_height), (-half_width, base_height + arch_radius)]
    for index in range(9):
        theta = math.pi - math.pi * index / 8
        samples.append((arch_radius * math.cos(theta), base_height + arch_radius + arch_radius * math.sin(theta)))
    samples.extend([(half_width, base_height + arch_radius), (half_width, base_height)])
    tangent = Vector((-math.sin(angle), 0, math.cos(angle)))
    radial = Vector((math.cos(angle), 0, math.sin(angle)))
    for tangent_offset, y in samples:
        game = radial * radius + tangent * tangent_offset
        points.append((game.x, y, game.z))
    for index in range(len(points) - 1):
        beam(f"{name}_{index:02d}", points[index], points[index + 1], depth, material, collection, 8)


def arch_wall_bay(name, angle, radius, material, collection, depth=.35):
    """Solid arcade bay with a genuine semicircular opening, jambs and spandrel."""
    bay_half = 2.5
    opening_half = 1.45
    bottom = -2.76
    spring = -.55
    peak = .90
    wall_top = 1.10
    radial = Vector((math.cos(angle), 0, math.sin(angle)))
    tangent = Vector((-math.sin(angle), 0, math.cos(angle)))
    vertices = []
    faces = []

    def game_vertex(tangent_offset, height, radial_offset):
        point = radial * (radius + radial_offset) + tangent * tangent_offset
        return (point.x, height, point.z)

    def add_prism(polygon):
        start = len(vertices)
        for radial_offset in (-depth / 2, depth / 2):
            vertices.extend(game_vertex(x, y, radial_offset) for x, y in polygon)
        count = len(polygon)
        faces.append(tuple(start + index for index in reversed(range(count))))
        faces.append(tuple(start + count + index for index in range(count)))
        for index in range(count):
            next_index = (index + 1) % count
            faces.append((start + index, start + next_index, start + count + next_index, start + count + index))

    add_prism([(-bay_half, bottom), (-opening_half, bottom), (-opening_half, wall_top), (-bay_half, wall_top)])
    add_prism([(opening_half, bottom), (bay_half, bottom), (bay_half, wall_top), (opening_half, wall_top)])
    arch_radius = peak - spring
    for segment in range(8):
        x0 = -opening_half + 2 * opening_half * segment / 8
        x1 = -opening_half + 2 * opening_half * (segment + 1) / 8
        y0 = spring + math.sqrt(max(0, arch_radius * arch_radius - x0 * x0))
        y1 = spring + math.sqrt(max(0, arch_radius * arch_radius - x1 * x1))
        add_prism([(x0, y0), (x1, y1), (x1, wall_top), (x0, wall_top)])
    return mesh_object(name, vertices, faces, material, collection)


def standing_buddha(prefix, point, scale, material, collection, blessing_pose=False):
    x, y, z = point
    cylinder(prefix + "_Pedestal", (x, y + 0.25 * scale, z), 0.55 * scale, 0.5 * scale, material, collection, 16)
    # Robe is a tapered body with leg-length silhouette.
    lathe(prefix + "_Robe", [(0.42 * scale, y + 0.5 * scale), (0.36 * scale, y + 2.1 * scale),
                              (0.50 * scale, y + 3.2 * scale), (0.26 * scale, y + 3.65 * scale)], material, collection, 16)
    robe = collection.objects[prefix + "_Robe"]
    robe.location += w((x, 0, z))
    sphere(prefix + "_Head", (x, y + 4.05 * scale, z), (0.25 * scale, 0.32 * scale, 0.24 * scale), material, collection, 12, 8)
    sphere(prefix + "_Ushnisha", (x, y + 4.34 * scale, z), (0.10 * scale, 0.12 * scale, 0.10 * scale), material, collection, 10, 6)
    # Elongated ears and flared robe hem preserve the photographed standing silhouette.
    sphere(prefix + "_Ear_L", (x - .27 * scale, y + 4.0 * scale, z), (.055 * scale, .18 * scale, .045 * scale), material, collection, 8, 6)
    sphere(prefix + "_Ear_R", (x + .27 * scale, y + 4.0 * scale, z), (.055 * scale, .18 * scale, .045 * scale), material, collection, 8, 6)
    if blessing_pose:
        # Abhaya-like gesture from pra.jpg: statue-right/viewer-left palm raised.
        beam(prefix + "_RaisedUpperArm", (x - .32 * scale, y + 3.35 * scale, z), (x - .52 * scale, y + 2.98 * scale, z), .10 * scale, material, collection)
        beam(prefix + "_RaisedForearm", (x - .52 * scale, y + 2.98 * scale, z), (x - .52 * scale, y + 3.82 * scale, z - .03 * scale), .095 * scale, material, collection)
        sphere(prefix + "_RaisedPalm", (x - .52 * scale, y + 3.94 * scale, z - .035 * scale), (.13 * scale, .20 * scale, .055 * scale), material, collection, 8, 6)
        for finger in range(4):
            finger_x = x - (.60 - finger * .052) * scale
            beam(prefix + f"_RaisedFinger_{finger}", (finger_x, y + 3.98 * scale, z - .04 * scale), (finger_x, y + 4.19 * scale, z - .04 * scale), .018 * scale, material, collection, 6)
    else:
        beam(prefix + "_ArmChest", (x - 0.34 * scale, y + 3.25 * scale, z), (x + 0.05 * scale, y + 3.55 * scale, z - 0.05), 0.105 * scale, material, collection)
    beam(prefix + "_ArmDown", (x + 0.33 * scale, y + 3.25 * scale, z), (x + 0.36 * scale, y + 2.15 * scale, z), 0.105 * scale, material, collection)


def guardian(prefix, point, scale, collection):
    x, y, z = point
    cylinder(prefix + "_Base", (x, y + 0.18 * scale, z), 0.45 * scale, 0.36 * scale, "HNP009_Ivory", collection, 8)
    sphere(prefix + "_Body", (x, y + 1.15 * scale, z), (0.38 * scale, 0.34 * scale, 0.70 * scale), "HNP009_GuardianBronze", collection, 10, 6)
    sphere(prefix + "_Head", (x, y + 2.05 * scale, z), (0.28 * scale, 0.25 * scale, 0.32 * scale), "HNP009_GuardianBronze", collection, 10, 6)
    beam(prefix + "_Staff", (x + 0.30 * scale, y + 0.35 * scale, z), (x + 0.30 * scale, y + 2.65 * scale, z), 0.055 * scale, "HNP009_GoldHighlight", collection, 8)


# --- Chedi macro profile, approved contract radius 23 / height 44. ---
BASE_PROFILE = [
    (23.0, 0.0), (23.0, 0.55), (22.8, 0.70), (22.8, 1.20),
    (22.2, 1.35), (22.2, 1.90), (21.5, 2.05), (21.5, 2.65),
    (20.8, 2.82), (20.8, 3.45), (20.15, 3.62), (20.15, 4.28),
    (19.55, 4.46), (19.55, 5.18), (19.0, 5.38), (19.0, 6.15),
    (18.55, 6.38), (18.55, 7.25), (18.35, 7.80),
]
BELL_PROFILE = [
    (18.35, 7.80), (18.25, 8.35), (18.0, 9.05), (17.75, 9.75),
    (17.45, 10.55), (17.05, 11.6), (16.6, 12.8), (16.05, 14.2),
    (15.4, 15.8), (14.65, 17.55), (13.75, 19.3), (12.7, 20.95),
    (11.55, 22.35), (10.25, 23.45), (8.8, 24.25), (7.65, 24.65),
]
COLLAR_LOWER_PROFILE = [
    (7.65, 24.65), (7.65, 25.0), (7.15, 25.15), (7.15, 25.55), (6.30, 25.72),
]
COLLAR_UPPER_PROFILE = [(6.75, 26.82), (7.0, 26.96), (7.0, 27.25), (6.15, 27.45)]

lathe("Chedi_BaseTiers", BASE_PROFILE, "HNP009_GoldBrick", chedi_collection, 72)
lathe("Chedi_Bell", BELL_PROFILE, "HNP009_GoldBrick", chedi_collection, 72)
lathe("Chedi_CollarLower", COLLAR_LOWER_PROFILE, "HNP009_GoldHighlight", chedi_collection, 64)
lathe("Chedi_CollarUpper", COLLAR_UPPER_PROFILE, "HNP009_GoldHighlight", chedi_collection, 64)

# Strong readable lower-third ring courses, based on IMG_161058/161311.
BELL_MOULDINGS = ((18.45, 7.95), (18.35, 8.45), (18.20, 9.00), (18.0, 9.60), (17.72, 10.25))
for index, (radius, height) in enumerate(BELL_MOULDINGS):
    lathe(f"Bell_Moulding_{index:02d}", [(radius - .18, height - .12), (radius + .22, height), (radius - .15, height + .16)], "HNP009_GoldHighlight", chedi_collection, 72)

# Dark open gallery beneath spire and repeated gabled support rhythm.
lathe("Gallery_DarkRecess", [(6.18, 25.72), (6.18, 26.84)], "HNP009_DarkInset", chedi_collection, 64)
for index in range(24):
    angle = index * math.tau / 24
    x, z = 6.83 * math.cos(angle), 6.83 * math.sin(angle)
    cylinder(f"Gallery_Column_{index:02d}", (x, 26.27, z), 0.18, 1.08, "HNP009_GoldHighlight", chedi_collection, 10)
    if DETAIL:
        # Small triangular support/leaf rhythm visible against the dark gallery.
        tangent = Vector((-math.sin(angle), 0, math.cos(angle)))
        radial = Vector((math.cos(angle), 0, math.sin(angle)))
        p = radial * 7.05
        verts = [
            (p.x + tangent.x * .24, 27.0, p.z + tangent.z * .24),
            (p.x - tangent.x * .24, 27.0, p.z - tangent.z * .24),
            (p.x, 27.55, p.z),
        ]
        mesh_object(f"Gallery_Gable_{index:02d}", verts, [(0, 1, 2)], "HNP009_Terracotta", chedi_collection)

# Shortened ringed spire: ~37.6% including gallery, but visible needle above gallery is 16.55m.
SPIRE_PROFILE = []
ring_samples = []
ring_count = 29 if DETAIL else 18
for index in range(ring_count):
    t = index / (ring_count - 1)
    height = 27.45 + 15.75 * t
    radius = 6.05 * ((1.0 - t) ** 0.98) + 0.08
    SPIRE_PROFILE.extend([(radius, height), (radius + 0.11, height + 0.15), (max(.08, radius - .10), height + .34)])
    ring_samples.append({"x": round(radius + .11, 4), "y": round(height + .15, 4)})
SPIRE_PROFILE.extend([(0.16, 43.45), (0.20, 43.65), (0.055, 44.0)])
lathe("Chedi_RingedSpire", SPIRE_PROFILE, "HNP009_GoldBrick", chedi_collection, 48)

# Dark terracotta frieze and leaf finials at the bell base.
lathe("Chedi_TerracottaFrieze", [(18.75, 6.85), (19.15, 7.05), (19.15, 7.65), (18.55, 7.8)], "HNP009_Terracotta", chedi_collection, 72)
if DETAIL:
    for index in range(40):
        angle = index * math.tau / 40
        radial = Vector((math.cos(angle), 0, math.sin(angle)))
        tangent = Vector((-math.sin(angle), 0, math.cos(angle)))
        center = radial * 19.22
        half = 0.25
        verts = [
            (center.x + tangent.x * half, 7.58, center.z + tangent.z * half),
            (center.x - tangent.x * half, 7.58, center.z - tangent.z * half),
            (center.x, 8.25, center.z),
        ]
        mesh_object(f"Frieze_Leaf_{index:02d}", verts, [(0, 1, 2)], "HNP009_Terracotta", chedi_collection)

    # White articulated perimeter façades with pilasters and grille apertures.
    # Near-continuous white perimeter facade; only the monumental -Z shrine opening is omitted.
    facade_gap = .22
    radial_profile_sector(
        "Chedi_WhitePerimeterBand",
        [(22.68, 0), (23.08, 0), (23.08, 2.62), (22.68, 2.62)],
        -math.pi / 2 + facade_gap, 3 * math.pi / 2 - facade_gap,
        "HNP009_White", chedi_collection, 92,
    )
    radial_profile_sector(
        "Chedi_WhiteCornice",
        [(22.62, 2.34), (23.22, 2.34), (23.22, 2.62), (22.62, 2.62)],
        -math.pi / 2 + facade_gap, 3 * math.pi / 2 - facade_gap,
        "HNP009_Ivory", chedi_collection, 92,
    )
    for facade_index in range(36):
        angle = facade_index * math.tau / 36
        front_delta = abs(math.atan2(math.sin(angle + math.pi / 2), math.cos(angle + math.pi / 2)))
        if front_delta < facade_gap:
            continue
        radial = Vector((math.cos(angle), 0, math.sin(angle)))
        center = radial * 23.16
        if facade_index % 2 == 0:
            cube(f"BaseGrille_{facade_index}", (center.x, 1.34, center.z), (1.02, .58, .08), "HNP009_DarkInset", chedi_collection, .02, angle + math.pi / 2)
        else:
            cube(f"BasePilaster_{facade_index}", (center.x, 1.18, center.z), (.26, 2.18, .20), "HNP009_Ivory", chedi_collection, .025, angle + math.pi / 2)

# Integrated monumental front worship portico, local front -Z.
front_z = -23.55
cube("Portico_DarkNiche", (0, 5.3, front_z - .38), (6.5, 9.8, .45), "HNP009_DarkInset", chedi_collection, .08)
cube("Portico_WhiteDais", (0, .7, front_z - 1.15), (7.6, 1.4, 2.3), "HNP009_White", chedi_collection, .10)
for step in range(4):
    cube(f"Portico_Step_{step}", (0, .16 + step * .32, -27.15 + step * .58), (9.8 - step * .7, .32, 1.15), "HNP009_White", chedi_collection, .05)
for side in (-1, 1):
    cube(f"Portico_Pilaster_{side}", (side * 3.55, 5.0, front_z - .75), (.72, 10.0, 1.25), "HNP009_White", chedi_collection, .08)
    for h in (1.0, 8.8, 9.5):
        cube(f"Portico_Capital_{side}_{h}", (side * 3.55, h, front_z - .75), (1.15, .28, 1.55), "HNP009_Ivory", chedi_collection, .04)
gable_panel("Portico_GableWhite", front_z - .72, 9.45, 15.6, 5.0, 1.35, "HNP009_White", chedi_collection)
gable_panel("Portico_GableTerracotta", front_z - 1.45, 10.1, 14.8, 4.15, .30, "HNP009_Terracotta", chedi_collection)
for side in (-1, 1):
    beam(f"Portico_GoldGable_{side}", (side * 4.2, 9.9, front_z - 1.65), (0, 15.25, front_z - 1.65), .13, "HNP009_GoldHighlight", chedi_collection, 10)
    beam(f"Portico_InnerArch_{side}", (side * 2.0, 4.0, front_z - 1.70), (0, 10.3, front_z - 1.70), .16, "HNP009_GoldHighlight", chedi_collection, 10)
standing_buddha("FrontStandingBuddha", (0, 1.15, front_z - 1.72), 1.65, "HNP009_GoldHighlight", chedi_collection, blessing_pose=True)
if DETAIL:
    # Deep layered pointed sanctuary arch, based on pra.jpg rather than a flat A-frame.
    arch_shape = [(-2.65, 2.1), (-2.65, 7.1), (-2.45, 8.5), (-1.8, 10.2),
                  (0, 12.25), (1.8, 10.2), (2.45, 8.5), (2.65, 7.1), (2.65, 2.1)]
    for layer, (scale, depth_z, mat) in enumerate(((1.0, -1.95, "HNP009_GoldHighlight"), (.82, -2.08, "HNP009_Terracotta"), (.67, -2.18, "HNP009_GoldHighlight"))):
        points = [(x * scale, 1.2 + (y - 1.2) * scale, front_z + depth_z) for x, y in arch_shape]
        for index in range(len(points) - 1):
            beam(f"SanctuaryArch_{layer}_{index}", points[index], points[index + 1], .16 - layer * .025, mat, chedi_collection, 10)
    guardian("FrontGuardian_L", (-5.0, .35, -23.2), .95, chedi_collection)
    guardian("FrontGuardian_R", (5.0, .35, -23.2), .95, chedi_collection)
    for side in (-1, 1):
        # Small gold finials/chofah on the front gable silhouette.
        for index in range(6):
            t = (index + 1) / 7
            x = side * 4.2 * (1 - t)
            y = 9.9 + (15.25 - 9.9) * t
            beam(f"GableFlame_{side}_{index}", (x, y, front_z - 1.78), (x + side * .22, y + .48, front_z - 1.82), .055, "HNP009_GoldHighlight", chedi_collection, 8)

# Simplified collision intent: monument body only; stairs/dais remain separate architecture.
cylinder("COLL_ChediBase", (0, 3.9, 0), 22.85, 7.8, "HNP009_DarkInset", chedi_collection, 32)

# --- Temple surroundings: correct two elevations and open cardinal stairs. ---
# Upper ring sits on current terrace top (world Y 2.9); lower court sits on plaza world Y .12.
annular_sector("UpperTerracottaWalk", 23.4, 28.9, .015, .03, 0, math.tau, "HNP009_Paving", surroundings_collection, 96)

gate_half_angle = math.asin(4.0 / 33.0)
# Wall bays are 5m wide, so their centers need extra angular clearance beyond
# the 8m cardinal stair opening. Pillars retain the original rhythm.
wall_gate_clearance = gate_half_angle + math.asin(2.5 / 33.1)
for quadrant in range(4):
    center = quadrant * math.pi / 2
    start = center + gate_half_angle
    end = (quadrant + 1) * math.pi / 2 - gate_half_angle
    annular_sector(f"LowerCourt_{quadrant}", 29.2, 37.0, -2.76, .10, start, end, "HNP009_Paving", surroundings_collection, 18)

# Continuous cloister quadrants with genuine arch rhythm and cardinal openings.
bay_angles = []
for index in range(40):
    angle = index * math.tau / 40
    if min((angle % (math.pi / 2)), (math.pi / 2) - (angle % (math.pi / 2))) < gate_half_angle:
        continue
    bay_angles.append(angle)

wall_bay_count = 0
side_niche_count = 0
for index, angle in enumerate(bay_angles):
    radial = Vector((math.cos(angle), 0, math.sin(angle)))
    tangent = Vector((-math.sin(angle), 0, math.cos(angle)))
    center = radial * 33.1
    # White fluted-looking pilaster built as shaft/cap, not one stretched box.
    cube(f"Arcade_Pillar_{index:02d}", (center.x, -1.25, center.z), (.48, 3.30, .48), "HNP009_White", surroundings_collection, .04, angle)
    cube(f"Arcade_Base_{index:02d}", (center.x, -2.72, center.z), (.78, .36, .72), "HNP009_Ivory", surroundings_collection, .04, angle)
    cube(f"Arcade_Capital_{index:02d}", (center.x, .38, center.z), (.78, .28, .72), "HNP009_Ivory", surroundings_collection, .04, angle)
    if DETAIL:
        bay_center_angle = angle + math.tau / 80
        center_mod = bay_center_angle % (math.pi / 2)
        center_gate_distance = min(center_mod, math.pi / 2 - center_mod)
        wall_clears_cardinal_gate = center_gate_distance >= wall_gate_clearance
        if wall_clears_cardinal_gate:
            arch_wall_bay(f"Arcade_WallBay_{index:02d}", bay_center_angle, 33.1, "HNP009_White", surroundings_collection)
            wall_bay_count += 1
        if wall_clears_cardinal_gate and index % 8 == 1:
            bay_radial = Vector((math.cos(bay_center_angle), 0, math.sin(bay_center_angle)))
            statue_center = bay_radial * 33.38
            standing_buddha(f"SideBuddha_{index:02d}", (statue_center.x, -2.25, statue_center.z), .62, "HNP009_GoldHighlight", surroundings_collection)
            side_niche_count += 1

# Pitched orange/green roof, segmented to keep stairs open.
for quadrant in range(4):
    center = quadrant * math.pi / 2
    start = center + gate_half_angle
    end = (quadrant + 1) * math.pi / 2 - gate_half_angle
    radial_profile_sector(f"RoofOrange_{quadrant}", [(30.9,1.15),(33.1,2.05),(35.65,1.15),(35.65,1.02),(33.1,1.85),(30.9,1.02)], start, end, "HNP009_RoofOrange", surroundings_collection, 20)
    radial_profile_sector(f"RoofGreenInner_{quadrant}", [(30.82,1.08),(31.28,1.29),(31.28,1.15),(30.82,.95)], start, end, "HNP009_RoofGreen", surroundings_collection, 20)
    radial_profile_sector(f"RoofGreenOuter_{quadrant}", [(35.20,1.30),(35.73,1.08),(35.73,.95),(35.20,1.16)], start, end, "HNP009_RoofGreen", surroundings_collection, 20)

if DETAIL:
    # Low white outer balustrade and lamps, respecting all four stair gaps.
    for quadrant in range(4):
        center = quadrant * math.pi / 2
        start = center + gate_half_angle
        end = (quadrant + 1) * math.pi / 2 - gate_half_angle
        annular_sector(f"OuterBalustrade_{quadrant}", 36.72, 37.0, -1.92, 1.55, start, end, "HNP009_White", surroundings_collection, 20)
    for index, angle in enumerate((math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4)):
        x, z = 36.0 * math.cos(angle), 36.0 * math.sin(angle)
        cylinder(f"CourtLampPost_{index}", (x, -.75, z), .10, 4.2, "HNP009_GuardianBronze", surroundings_collection, 10)
        sphere(f"CourtLamp_{index}", (x, 1.42, z), (.30, .36, .30), "HNP009_GoldHighlight", surroundings_collection, 12, 8)

# Explicit simple colliders; arches themselves stay open.
annular_sector("COLL_UpperWalk", 23.4, 28.9, -.04, .08, 0, math.tau, "HNP009_DarkInset", surroundings_collection, 64)
for quadrant in range(4):
    center = quadrant * math.pi / 2
    start = center + gate_half_angle
    end = (quadrant + 1) * math.pi / 2 - gate_half_angle
    annular_sector(f"COLL_LowerCourt_{quadrant}", 29.2, 37.0, -2.84, .12, start, end, "HNP009_DarkInset", surroundings_collection, 12)
for index, angle in enumerate(bay_angles):
    x, z = 33.1 * math.cos(angle), 33.1 * math.sin(angle)
    cube(f"COLL_ArcadeColumn_{index:02d}", (x, -1.25, z), (.55, 3.35, .55), "HNP009_DarkInset", surroundings_collection, 0, angle)


def collection_meshes(collection, include_colliders=True):
    return [obj for obj in collection.objects if obj.type == "MESH" and (include_colliders or not obj.name.startswith("COLL_"))]


def ensure_uv(obj):
    if obj.type != "MESH":
        return
    uv = obj.data.uv_layers.active or obj.data.uv_layers.new(name="UVMap")
    uv.name = "UVMap"
    for polygon in obj.data.polygons:
        raw = []
        for loop_index in polygon.loop_indices:
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            raw.append((loop_index, (math.atan2(vertex.y, vertex.x) / math.tau) % 1.0, vertex))
        angles = [entry[1] for entry in raw]
        crosses_seam = max(angles, default=0) - min(angles, default=0) > .5
        for loop_index, angle, vertex in raw:
            if crosses_seam and angle < .5:
                angle += 1.0
            uv.data[loop_index].uv = (angle * 8.0, vertex.z * .35 + math.hypot(vertex.x, vertex.y) * .04)


for obj in collection_meshes(chedi_collection) + collection_meshes(surroundings_collection):
    ensure_uv(obj)


def join_objects(objects, output_name):
    objects = [obj for obj in objects if obj and obj.type == "MESH"]
    if not objects:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    if len(objects) > 1:
        bpy.ops.object.join()
    result = bpy.context.object
    result.name = output_name
    return result


def batch_collection(collection, asset_prefix):
    # Preserve three explicit collision interfaces, batch all visible statics by material.
    join_objects([obj for obj in collection.objects if obj.name.startswith("COLL_LowerCourt")], "COLL_LowerCourt")
    join_objects([obj for obj in collection.objects if obj.name.startswith("COLL_ArcadeColumn")], "COLL_ArcadeColumns")
    visible = [obj for obj in collection_meshes(collection) if not obj.name.startswith("COLL_")]
    by_material = {}
    for obj in visible:
        material_name = obj.data.materials[0].name if obj.data.materials else "NoMaterial"
        by_material.setdefault(material_name, []).append(obj)
    for material_name, objects in by_material.items():
        join_objects(objects, f"{asset_prefix}_{material_name}")


batch_collection(chedi_collection, "HNP_Chedi_v009")
batch_collection(surroundings_collection, "HNP_TempleSurroundings_v009")


def bounds_and_metrics(objects):
    # Exact post-batch measurements; rotated joined-object AABBs over-report extents.
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    triangles = 0
    vertices = 0
    degenerate = 0
    loose = 0
    for obj in objects:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
        vertices += len(obj.data.vertices)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        degenerate += sum(1 for face in bm.faces if face.calc_area() < 1e-10)
        loose += sum(1 for vertex in bm.verts if not vertex.link_edges)
        bm.free()
    return {
        "min": [round(value, 6) for value in minimum],
        "max": [round(value, 6) for value in maximum],
        "dimensions": [round(value, 6) for value in (maximum - minimum)],
        "triangles": triangles,
        "vertices": vertices,
        "degenerate_faces": degenerate,
        "loose_vertices": loose,
    }


def camera_and_lights(location, target, ortho_scale, resolution, filepath):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = "PREVIEW_Camera"
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho_scale
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 55))
    sun = bpy.context.object
    sun.name = "PREVIEW_Sun"
    sun.rotation_euler = (math.radians(28), math.radians(-18), math.radians(-42))
    sun.data.energy = 2.2
    sun.data.color = (1.0, .78, .52)
    sun.data.angle = math.radians(9)
    bpy.ops.object.light_add(type="AREA", location=(-24, 62, 48))
    area = bpy.context.object
    area.name = "PREVIEW_Fill"
    area.data.energy = 2600
    area.data.size = 35
    area.data.color = (.50, .68, 1.0)
    area.rotation_euler = (Vector(target) - area.location).to_track_quat("-Z", "Y").to_euler()
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs[0].default_value = (.24, .32, .42, 1)
    background.inputs[1].default_value = .65
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(filepath)
    bpy.ops.render.render(write_still=True)
    for obj in (camera, sun, area):
        bpy.data.objects.remove(obj, do_unlink=True)


chedi_metrics = bounds_and_metrics(collection_meshes(chedi_collection, False))
surroundings_metrics = bounds_and_metrics(collection_meshes(surroundings_collection, False))

# Collision meshes are export-only evidence and never part of beauty previews.
for obj in collection_meshes(chedi_collection) + collection_meshes(surroundings_collection):
    if obj.name.startswith("COLL_"):
        obj.hide_render = True

if not DETAIL:
    for obj in surroundings_collection.objects:
        obj.hide_render = True
    camera_and_lights((0, 120, 23), (0, 0, 21), 59, (1100, 900), OUT / "HNP009_Chedi_silhouette-blockout.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(SRC / "HNP_Chedi_Blockout_v009.blend"))
    print("HNP009_BLOCKOUT_PASS", json.dumps({"chedi": chedi_metrics, "profile": BELL_PROFILE}))
    raise SystemExit(0)

# Final master source before preview objects.
bpy.ops.wm.save_as_mainfile(filepath=str(SRC / "HNP_TempleArt_v009.blend"))


def export_collection(collection, filename):
    objects = collection_meshes(collection)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    path = OUT / filename
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"MESH"},
        axis_forward="-Z", axis_up="Y", add_leaf_bones=False, bake_anim=False,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
    )
    return path


chedi_fbx = export_collection(chedi_collection, "HNP_Chedi_v009.fbx")
surroundings_fbx = export_collection(surroundings_collection, "HNP_TempleSurroundings_v009.fbx")

# Three required visual views.
for obj in surroundings_collection.objects:
    obj.hide_render = True
camera_and_lights((0, 105, 24), (0, 0, 20), 62, (1100, 900), OUT / "HNP_Chedi_v009_preview_front.png")
for obj in surroundings_collection.objects:
    obj.hide_render = False
for obj in surroundings_collection.objects:
    if obj.name.startswith("COLL_"):
        obj.hide_render = True
for obj in chedi_collection.objects:
    if obj.name.startswith("COLL_"):
        obj.hide_render = True
camera_and_lights((55, 92, 35), (0, 0, 17), 94, (1280, 900), OUT / "HNP_Temple_v009_preview_three-quarter.png")
camera_and_lights((22, 46, 4.5), (0, 0, 3.2), 35, (1280, 720), OUT / "HNP_Temple_v009_preview_courtyard.png")
camera_and_lights((17, -17, 1.8), (24, -24, -.6), 11, (1280, 720), OUT / "HNP_Temple_v009_preview_arcade-detail.png")


def roundtrip(path, source_metrics):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path), automatic_bone_orientation=False)
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    metrics = bounds_and_metrics(imported)
    dimension_delta = max(abs(a - b) for a, b in zip(source_metrics["dimensions"], metrics["dimensions"]))
    result = {
        "status": "PASS" if dimension_delta < .001 and metrics["triangles"] == source_metrics["triangles"] else "FAIL",
        "mesh_count": len(imported),
        "triangles": metrics["triangles"],
        "bounds": metrics,
        "max_dimension_delta_m": round(dimension_delta, 8),
    }
    for obj in imported:
        bpy.data.objects.remove(obj, do_unlink=True)
    return result


chedi_roundtrip = roundtrip(chedi_fbx, bounds_and_metrics(collection_meshes(chedi_collection)))
surroundings_roundtrip = roundtrip(surroundings_fbx, bounds_and_metrics(collection_meshes(surroundings_collection)))
(OUT / "roundtrip.json").write_text(json.dumps({
    "blender_version": bpy.app.version_string,
    "HNP_Chedi_v009.fbx": chedi_roundtrip,
    "HNP_TempleSurroundings_v009.fbx": surroundings_roundtrip,
}, indent=2), encoding="utf-8")


def uv_report(collection):
    objects = collection_meshes(collection)
    with_uv0 = sum(1 for obj in objects if len(obj.data.uv_layers) > 0)
    return {"mesh_count": len(objects), "meshes_with_uv0": with_uv0, "status": "PASS" if with_uv0 == len(objects) else "FAIL"}

light_profile = {
    "coordinate_system": "game-local XYZ; Y up; Chedi local front -Z; apply same root transform as Chedi",
    "bell": [{"x": radius, "y": height} for radius, height in BELL_PROFILE],
    "rings": (
        [{"x": r, "y": h} for r, h in ((22.9,.62),(22.3,1.30),(21.6,2.0),(20.9,2.78),(20.25,3.58),(19.65,4.42),(19.1,5.34),(18.65,6.34))]
        + [{"x": round(r + .22, 4), "y": h} for r, h in BELL_MOULDINGS]
        + [{"x": 7.15, "y": 25.15}, {"x": 7.0, "y": 26.96}, {"x": 7.0, "y": 27.25}]
        + ring_samples
    ),
    "shrine": [
        {
            "name": "FrontGableOuter",
            "points": [
                {"x": -4.2, "y": 9.9, "z": -25.2},
                {"x": 0.0, "y": 15.25, "z": -25.2},
                {"x": 4.2, "y": 9.9, "z": -25.2},
            ],
            "width": 0.13,
        },
        {
            "name": "FrontNicheInner",
            "points": [
                {"x": -2.0, "y": 4.0, "z": -25.25},
                {"x": 0.0, "y": 10.3, "z": -25.25},
                {"x": 2.0, "y": 4.0, "z": -25.25},
            ],
            "width": 0.16,
        },
    ],
}
(OUT / "light-profile.json").write_text(json.dumps(light_profile, indent=2), encoding="utf-8")

manifest = {
    "task_id": "HNP-WORLD-009",
    "revision": "v009",
    "status": {
        "blender_source": "PASS" if chedi_metrics["degenerate_faces"] == 0 and surroundings_metrics["degenerate_faces"] == 0 else "FAIL",
        "chedi_fbx_roundtrip": chedi_roundtrip["status"],
        "surroundings_fbx_roundtrip": surroundings_roundtrip["status"],
        "designer_visual_review": "PASS",
        "unity_import": "NOT RUN",
    },
    "references": {
        "macro": ["ref/jd.jpg", "ref/pra.jpg"],
        "bell_frieze": ["ref/IMG_20211023_161058.jpg", "ref/IMG_20211023_161311.jpg"],
        "spire_collar": ["ref/IMG_20211023_161037.jpg"],
        "side_shrines": ["ref/IMG_20211023_160743.jpg", "ref/IMG_20211023_160959.jpg", "ref/IMG_20211023_161603.jpg", "ref/IMG_20211023_162201.jpg"],
        "arcade": ["ref/IMG_20211023_161118.jpg", "ref/IMG_20211023_161227.jpg"],
        "stairs_paving": ["ref/IMG_20211023_160436.jpg", "ref/IMG_20211023_161207.jpg", "ref/IMG_20211023_161403.jpg"],
        "style": ["ref/style.jpg"],
    },
    "designer_review": "reports/reviews/HNP-WORLD-009-detail.md (corrected second-detail PASS)",
    "provisional": [
        "All dimensions are gameplay-scale reconstructions; photographs are not survey measurements.",
        "Repeated bay count, guardian forms, lamp design and exact tile/frieze ornament are stylized reductions for mobile Web.",
        "Front portico depth is held within the previous approximately 50 m footprint for integration safety.",
    ],
    "integration_fix": {
        "issue": "Arcade wall bay half-width intruded into cardinal stair openings in first Web integration.",
        "resolution": "Wall and niche bay centers require gate_half_angle + asin(2.5/33.1); pillar placement is unchanged.",
        "cardinal_stair_clear_width_m": 8.0,
        "arcade_wall_half_width_m": 2.5,
        "wall_gate_clearance_radians": round(wall_gate_clearance, 8),
        "pillar_count_unchanged": len(bay_angles),
        "wall_bay_count_after_clearance": wall_bay_count,
        "side_niche_count_after_clearance": side_niche_count,
    },
    "units": "metres",
    "axis": {"blender_forward": "-Y", "fbx_forward": "-Z", "fbx_up": "Y"},
    "pivot": "both FBXs share ground origin; Unity root position (53,2.9,0), Y rotation 90 degrees",
    "palette": PALETTE,
    "texture_mappings": {
        material: {"file": filename, "color_space": "sRGB", "uv_set": "UV0", "wrap": "Repeat"}
        for material, filename in TEXTURE_MAPPINGS.items()
    },
    "assets": {
        "HNP_Chedi_v009.fbx": {
            "source": "art-source/hnp-world-009/HNP_TempleArt_v009.blend",
            "metrics_visible": chedi_metrics,
            "metrics_export_with_colliders": bounds_and_metrics(collection_meshes(chedi_collection)),
            "uv": uv_report(chedi_collection),
            "materials": sorted({material.name for obj in collection_meshes(chedi_collection) for material in obj.data.materials}),
            "collision": ["COLL_ChediBase"],
            "roundtrip": chedi_roundtrip,
        },
        "HNP_TempleSurroundings_v009.fbx": {
            "source": "art-source/hnp-world-009/HNP_TempleArt_v009.blend",
            "metrics_visible": surroundings_metrics,
            "metrics_export_with_colliders": bounds_and_metrics(collection_meshes(surroundings_collection)),
            "uv": uv_report(surroundings_collection),
            "materials": sorted({material.name for obj in collection_meshes(surroundings_collection) for material in obj.data.materials}),
            "collision": {
                "meshes": [obj.name for obj in collection_meshes(surroundings_collection) if obj.name.startswith("COLL_")],
                "intent": "Renderer off in Unity; upper/lower paving and columns only. Cardinal stair openings and arches remain traversable.",
            },
            "roundtrip": surroundings_roundtrip,
            "elevation_contract": {
                "upper_paving": "r23.4-28.9 at local Y 0.015 (world 2.915)",
                "lower_paving": "r29.2-37 at local Y -2.76 (world 0.14), four 8m cardinal gaps",
                "cloister_base": "local Y -2.9; same Chedi root transform",
            },
        },
    },
    "light_profile": "art-export/hnp-world-009/light-profile.json",
    "previews": [
        "art-export/hnp-world-009/HNP_Chedi_v009_preview_front.png",
        "art-export/hnp-world-009/HNP_Temple_v009_preview_three-quarter.png",
        "art-export/hnp-world-009/HNP_Temple_v009_preview_courtyard.png",
        "art-export/hnp-world-009/HNP_Temple_v009_preview_arcade-detail.png",
    ],
}
manifest["source_sha256"] = {
    "HNP_TempleArt_v009.blend": hashlib.sha256((SRC / "HNP_TempleArt_v009.blend").read_bytes()).hexdigest(),
    "build_temple_v009.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
for filename in (
    "HNP_Chedi_v009.fbx", "HNP_TempleSurroundings_v009.fbx", "light-profile.json", "roundtrip.json",
    "HNP_Chedi_v009_preview_front.png", "HNP_Temple_v009_preview_three-quarter.png", "HNP_Temple_v009_preview_courtyard.png",
    "HNP_Temple_v009_preview_arcade-detail.png",
    *TEXTURE_MAPPINGS.values(),
):
    manifest.setdefault("sha256", {})[filename] = hashlib.sha256((OUT / filename).read_bytes()).hexdigest()
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

if any(value == "FAIL" for value in manifest["status"].values()):
    raise RuntimeError(json.dumps(manifest["status"]))
print("HNP009_DETAIL_PASS", json.dumps(manifest["status"]))
