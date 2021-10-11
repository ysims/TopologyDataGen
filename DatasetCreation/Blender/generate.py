import itertools
import os
import numpy as np
import sys
import bpy  # import blender python
import bmesh  # import blender mesh
import mathutils

# Give it a path so we can open the numpy voxel grid file
dir = os.path.dirname(
    "C:/Users/c3256711/Documents/Uni/Honours Project/TopologyCollection/DatasetCreation/Blender/"
)
if not dir in sys.path:
    sys.path.append(dir)

# Reset the scene, we don't want anything hanging around
bpy.ops.wm.read_factory_settings(use_empty=True)

# Get the scene, for ease
scene = bpy.context.scene

# Create an empty mesh

# Make a cube/voxel object
# Requires creating an empty mesh and attaching a cube object to it
mesh = bpy.data.meshes.new("Voxel")
cube = bpy.data.objects.new("Voxel", mesh)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bm.to_mesh(mesh)

# Load the voxel grid
grid = (np.load(os.path.join(dir, "31_inverted_cube.npy"))).tolist()

# Make a new collection, which will contain everything we will union
union_collection = bpy.data.collections.new("UnionCollection")
scene.collection.children.link(union_collection)

# Make one cube outside of the collection
# this will have the union modifier applied to it
first_point = grid[0]
first_cube = cube.copy()
first_cube.location = (first_point[0], first_point[1], first_point[2])
scene.collection.objects.link(first_cube)
grid.remove(first_point)

# Read all the points and make cubes from them
# and put those cube in our collection that will contain
# everything that will be unioned with first_cube
for point in grid:
    new_cube = cube.copy()
    new_cube.location = (point[0], point[1], point[2])
    union_collection.objects.link(new_cube)

# Deselect everything and select the first_cube
# so that we can do things to it
bpy.ops.object.select_all(action="DESELECT")
first_cube.select_set(True)
bpy.context.view_layer.objects.active = first_cube

# Create a boolean modifier on first_cube
# and set the fields so it unions with the collection
bool = first_cube.modifiers.new(type="BOOLEAN", name="booly")
bool.operand_type = "COLLECTION"
bool.collection = union_collection
bool.operation = "UNION"
bool.solver = "FAST"
bool.double_threshold = 0.0

# It becomes owned by all the other cubes it's unioned by or something like that
# so we got to just make it its own user
bpy.ops.object.make_single_user(object=True, obdata=True)

# Apply the boolean modifier to the cube, so it's not dependent on the other cubes anymore
bpy.ops.object.modifier_apply({"object": first_cube}, modifier=bool.name)

# Select all the other cubes and delete them
# and delete the collection since we don't need it anymore
for obj in union_collection.objects:
    bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.collections.remove(union_collection)

# Add a modifier to smooth it out
smooth = first_cube.modifiers.new(type="REMESH", name="remesh-smooth")
smooth.mode = "SMOOTH"
smooth.octree_depth = 7
smooth.scale = 0.4
smooth.use_remove_disconnected = False
smooth.threshold = 0.0
smooth.use_smooth_shade = True

# # Apply the remesh modifier to the cube, so we're sure we have the right vertices
# bpy.ops.object.modifier_apply({"object": first_cube}, modifier=smooth.name)
