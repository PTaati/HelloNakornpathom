"""Read-only Blender inspection helper for the task source file."""

import bpy
import bmesh

obj = bpy.data.objects["HNP_CHR_Traveller_Child_v002"]
mesh = obj.data
print("OBJECT", tuple(obj.location), tuple(obj.dimensions), tuple(obj.scale))

def inspect_components(mesh_to_check, label):
    parents = list(range(len(mesh_to_check.vertices)))

    def find(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(a, b):
        a = find(a)
        b = find(b)
        parents[b] = a

    for edge in mesh_to_check.edges:
        union(*edge.vertices)
    components = {}
    for vertex in mesh_to_check.vertices:
        components.setdefault(find(vertex.index), []).append(vertex)
    items = []
    for vertices in components.values():
        minimum = [min(vertex.co[axis] for vertex in vertices) for axis in range(3)]
        maximum = [max(vertex.co[axis] for vertex in vertices) for axis in range(3)]
        dimensions = [maximum[axis] - minimum[axis] for axis in range(3)]
        items.append((len(vertices), dimensions, minimum, maximum))
    print(label, "TOTAL_COMPONENTS", len(items))
    for item in sorted(items, key=lambda value: max(value[1]), reverse=True)[:25]:
        print(label, "COMPONENT", item)


inspect_components(mesh, "REST")
evaluated_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
evaluated_mesh = evaluated_obj.to_mesh()
inspect_components(evaluated_mesh, "EVALUATED")
evaluated_obj.to_mesh_clear()

bm = bmesh.new()
bm.from_mesh(mesh)
degenerate = [face for face in bm.faces if face.calc_area() < 1e-10]
print("DEGENERATE_COUNT", len(degenerate))
for face in degenerate:
    print("DEGENERATE", face.index, tuple(face.calc_center_median()), [tuple(vertex.co) for vertex in face.verts])
bm.free()
