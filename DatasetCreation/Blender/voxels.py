import bpy  # import blender python
import bmesh    # import blender mesh
import itertools

# Reset the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Get the scene
scene = bpy.context.scene

# Empty mesh
mesh = bpy.data.meshes.new("My Cube")

# Make the cube object
cube = bpy.data.objects.new("My Cube", mesh)

# Add object to a collection in the scene
# scene.collection.objects.link(cube)

# Build a cube mesh using bmesh, Blender's mesh editing system
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)

# Store the bmesh inside the mesh
bm.to_mesh(mesh)

cube.location = (0,0,0)

for i,j,k in itertools.product(range(10), repeat=3):
    new_cube = cube.copy()
    scene.collection.objects.link(new_cube)
    new_cube.location = (i,j,k)

