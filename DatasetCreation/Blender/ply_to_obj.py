import bpy
import time
import os
import open3d as o3d
import numpy as np

convert_ply_source = "/home/ysi/code/TopologyDataGen/DatasetCreation/Voxels/all_data/01-05-2022/"
convert_ply_destination = "/home/ysi/code/TopologyDataGen/DatasetCreation/Voxels/all_data/01-05-2022/ply/"

for file in os.listdir(convert_ply_source):
    if os.path.splitext(file)[1] == ".npy" and not ("grid" in os.path.splitext(file)[0]):
        path = convert_ply_source + file
        print("Converting: " + path)
        xyz = np.load(path)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        o3d.io.write_point_cloud(os.path.splitext(convert_ply_destination + file)[0] + ".ply", pcd)
        print("Converted: " + file)



start = time.time()



source_folder = convert_ply_destination
destination_folder = "/home/ysi/code/TopologyDataGen/DatasetCreation/Voxels/all_data/mesh/"



texture1 = bpy.data.textures.new("texture1", 'VORONOI')
texture1.noise_intensity = 1
texture1.noise_scale = 1.1



for file in os.listdir(source_folder):
    object_name = os.path.splitext(file)[0]
    if os.path.splitext(file)[1] == ".ply" and (os.path.exists(destination_folder + object_name + ".stl") == False):

        print("Augmenting: " + file)



        path = source_folder + file
        bpy.ops.import_mesh.ply(filepath=path)
        shape = bpy.context.active_object



        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        cube.scale[0] = 0.5
        cube.scale[1] = 0.5
        cube.scale[2] = 0.5
        cube.location[0] = 0
        cube.location[1] = 0
        cube.location[2] = 0



        cube.parent = shape



        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        shape.instance_type = 'VERTS'
        bpy.context.view_layer.objects.active = cube.parent
        bpy.data.objects[object_name].select_set(True)
        bpy.ops.object.duplicates_make_real()



        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[object_name].select_set(True)
        bpy.ops.object.delete()
        bpy.data.objects['Cube'].select_set(True)
        bpy.ops.object.delete()



        bpy.ops.object.select_all(action='DESELECT')
        MSH_OBJS = [m for m in bpy.context.scene.objects if m.type == 'MESH']



        for OBJS in MSH_OBJS:
            OBJS.select_set(state=True)
            bpy.context.view_layer.objects.active = OBJS



        bpy.ops.object.join()
        bpy.ops.object.modifier_add(type='REMESH')



        current = bpy.context.active_object

        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'UNSUBDIV'
        bpy.context.object.modifiers["Decimate"].iterations = 5



        bpy.ops.object.modifier_add(type='TRIANGULATE')
        output_destination = destination_folder + object_name + ".obj"
        bpy.ops.export_scene.obj(filepath=output_destination)

        bpy.ops.object.delete()



end = time.time()
print("TIME TAKEN: ")
print(end - start)