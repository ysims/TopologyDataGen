import os
import sys
import numpy as np
import bpy  # import blender python
import bmesh  # import blender mesh

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

# Get the scene
scene = bpy.context.scene

# Empty mesh
mesh = bpy.data.meshes.new("Voxel")

# Make the cube object
cube = bpy.data.objects.new("Voxel", mesh)

# Build a cube mesh using bmesh, Blender's mesh editing system
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)

# Store the bmesh inside the mesh
bm.to_mesh(mesh)

grid = np.load("objects.npy")

# Create a numpy array from the voxel grid so we can turn it into an open3d geometry
# numpy_point_cloud = None
for point in grid:
    # Create the Blender cubes
    new_cube = cube.copy()
    new_cube.location = (point[0], point[1], point[2])
    scene.collection.objects.link(new_cube)
