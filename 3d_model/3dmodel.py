import open3d as o3d
import numpy as np
import os

MODEL_PATH = r"C:\Users\Abzal_\Desktop\data_vis\ass5\shark.obj"
POISSON_DEPTH = 9
VOXEL_SIZE = 0.05
PLANE_SIZE = 3.0
PLANE_HEIGHT = 0.0
window_width, window_height = 1200, 800

def print_header(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def load_mesh_any(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    try:
        mesh = o3d.io.read_triangle_mesh(path)
        if mesh and len(mesh.vertices) > 0:
            return mesh, None
    except: pass
    pcd = o3d.io.read_point_cloud(path)
    if pcd is None or len(pcd.points) == 0:
        raise RuntimeError("Can't read model as mesh or point cloud.")
    return None, pcd

def mesh_info(mesh):
    return len(mesh.vertices), len(mesh.triangles), mesh.has_vertex_colors(), mesh.has_vertex_normals()

def pcd_info(pcd):
    return len(pcd.points), pcd.has_colors()

def step1_load_and_show(path):
    print_header("STEP 1 — Loading model")
    mesh, pcd = load_mesh_any(path)
    if mesh:
        if not mesh.has_vertex_normals(): mesh.compute_vertex_normals()
        v, t, has_color, has_normals = mesh_info(mesh)
        print(f"Vertices: {v}, Triangles: {t}, Colors: {has_color}, Normals: {has_normals}")
        o3d.visualization.draw_geometries([mesh], window_name="Original Mesh",
                                          width=window_width, height=window_height)
        return mesh, None
    else:
        v, has_color = pcd_info(pcd)
        print(f"Points: {v}, Colors: {has_color}")
        o3d.visualization.draw_geometries([pcd], window_name="Original PointCloud",
                                          width=window_width, height=window_height)
        return None, pcd

def step2_mesh_to_pcd(mesh, pcd):
    print_header("STEP 2 — Convert to Point Cloud")
    if pcd is not None:
        source_pcd = pcd
    else:
        source_pcd = mesh.sample_points_uniformly(number_of_points=50000)
    v, has_color = pcd_info(source_pcd)
    print(f"Points: {v}, Colors: {has_color}")
    o3d.visualization.draw_geometries([source_pcd], window_name="Point Cloud",
                                      width=window_width, height=window_height)
    return source_pcd

def step3_poisson_reconstruct(pcd, depth=9, density_threshold=0.05):
    print_header("STEP 3 — Poisson Reconstruction")
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=depth)
    densities = np.asarray(densities)
    threshold = np.quantile(densities, density_threshold)
    mesh.remove_vertices_by_mask(densities <= threshold)
    mesh.compute_vertex_normals()
    print(f"Vertices: {len(mesh.vertices)}, Triangles: {len(mesh.triangles)}, Colors: {mesh.has_vertex_colors()}")
    o3d.visualization.draw_geometries([mesh], window_name="Poisson Mesh",
                                      width=window_width, height=window_height)
    return mesh

def step4_voxelize(pcd, voxel_size=0.05):
    print_header("STEP 4 — Voxelization")
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size)
    print(f"Voxels: {len(voxel_grid.get_voxels())}, Colors: {pcd.has_colors()}")
    o3d.visualization.draw_geometries([voxel_grid], window_name="Voxel Grid",
                                      width=window_width, height=window_height)
    return voxel_grid

def step5_create_plane_near_object(mesh_or_pcd):
    print_header("STEP 5 — Add Plane")
    plane = o3d.geometry.TriangleMesh.create_box(width=PLANE_SIZE, height=0.01, depth=PLANE_SIZE)
    plane.translate(-plane.get_center())
    plane.translate((0.0, PLANE_HEIGHT - 0.005, 0.0))
    plane.paint_uniform_color([0.2,0.2,0.8])
    plane.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh_or_pcd, plane], window_name="Object + Plane",
                                      width=window_width, height=window_height)
    return plane

def clip_pcd_by_plane(pcd, plane_point, plane_normal, keep_positive=False):
    pts = np.asarray(pcd.points)
    mask = np.dot(pts - plane_point, plane_normal) >= 0 if keep_positive else np.dot(pts - plane_point, plane_normal) <= 0
    new_pcd = o3d.geometry.PointCloud()
    new_pcd.points = o3d.utility.Vector3dVector(pts[mask])
    if pcd.has_colors(): new_pcd.colors = o3d.utility.Vector3dVector(np.asarray(pcd.colors)[mask])
    return new_pcd, mask.sum()

def clip_mesh_by_plane(mesh, plane_point, plane_normal, keep_positive=False):
    verts = np.asarray(mesh.vertices)
    tris = np.asarray(mesh.triangles)
    centroids = verts[tris].mean(axis=1)
    keep_tri = tris[np.dot(centroids - plane_point, plane_normal) >= 0 if keep_positive else np.dot(centroids - plane_point, plane_normal) <= 0]
    if len(keep_tri)==0: return o3d.geometry.TriangleMesh(), 0
    unique_vids, new_indices = np.unique(keep_tri.flatten(), return_inverse=True)
    new_mesh = o3d.geometry.TriangleMesh()
    new_mesh.vertices = o3d.utility.Vector3dVector(verts[unique_vids])
    new_mesh.triangles = o3d.utility.Vector3iVector(new_indices.reshape(-1,3))
    if mesh.has_vertex_colors(): new_mesh.vertex_colors = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_colors)[unique_vids])
    if mesh.has_vertex_normals(): new_mesh.vertex_normals = o3d.utility.Vector3dVector(np.asarray(mesh.vertex_normals)[unique_vids])
    return new_mesh, len(new_mesh.vertices)

def step6_clip_and_show(mesh_or_pcd, plane_mesh):
    print("\n=== STEP 6 — Clip object by plane ===")
    verts = np.asarray(plane_mesh.vertices)
    p0, p1, p2 = verts[0], verts[1], verts[2]
    normal = np.cross(p1 - p0, p2 - p0)
    normal /= np.linalg.norm(normal)
    point = p0

    if isinstance(mesh_or_pcd, o3d.geometry.PointCloud):
        clipped, remaining = clip_pcd_by_plane(mesh_or_pcd, point, normal, keep_positive=False)
        print(f"Points after clipping: {remaining}")
        print(f"Has colors: {clipped.has_colors()}")
        o3d.visualization.draw_geometries([clipped], window_name="Clipped PointCloud",
                                          width=window_width, height=window_height)
        return clipped
    elif isinstance(mesh_or_pcd, o3d.geometry.TriangleMesh):
        clipped, remaining_vertices = clip_mesh_by_plane(mesh_or_pcd, point, normal, keep_positive=False)
        v, t, has_color, has_normals = mesh_info(clipped)
        print(f"Vertices after clipping: {v}, Triangles: {t}, Has colors: {has_color}, Has normals: {has_normals}")
        o3d.visualization.draw_geometries([clipped], window_name="Clipped Mesh",
                                          width=window_width, height=window_height)
        return clipped



def step7_color_and_extremes(obj, axis="z", marker_size=0.03):
    if isinstance(obj, o3d.geometry.PointCloud):
        pts = np.asarray(obj.points)
        colors = np.zeros((len(pts),3))
    elif isinstance(obj, o3d.geometry.TriangleMesh):
        pts = np.asarray(obj.vertices)
        colors = np.zeros((len(pts),3))
        obj.vertex_colors = o3d.utility.Vector3dVector(colors)
    else:
        raise TypeError("Object must be PointCloud or TriangleMesh")
    axis = axis.lower()
    idx = {"x":0, "y":1, "z":2}[axis]
    values = pts[:, idx]
    norm = (values - values.min()) / (values.max() - values.min() + 1e-9)
    colors[:, 0] = norm   # R
    colors[:, 1] = 0      # G
    colors[:, 2] = 1 - norm # B
    if isinstance(obj, o3d.geometry.PointCloud):
        obj.colors = o3d.utility.Vector3dVector(colors)
    else:
        obj.vertex_colors = o3d.utility.Vector3dVector(colors)
    min_idx, max_idx = np.argmin(values), np.argmax(values)
    min_point, max_point = pts[min_idx], pts[max_idx]
    print(f"Extremes along {axis.upper()}:")
    print(f"  MIN: {min_point}")
    print(f"  MAX: {max_point}")
    sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=marker_size)
    sphere_min.paint_uniform_color([0,0,1])  # синий
    sphere_min.translate(min_point)
    sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=marker_size)
    sphere_max.paint_uniform_color([1,0,0])  # красный
    sphere_max.translate(max_point)

    o3d.visualization.draw_geometries([obj, sphere_min, sphere_max],
                                      window_name=f"Gradient + Extremes",
                                      width=1200, height=800)

    return min_point, max_point


if __name__=="__main__":
    mesh, pcd = step1_load_and_show(MODEL_PATH)
    source_pcd = step2_mesh_to_pcd(mesh, pcd)
    reconstructed_mesh = step3_poisson_reconstruct(source_pcd)
    voxel_grid = step4_voxelize(source_pcd)
    
    plane_mesh = step5_create_plane_near_object(source_pcd)
    
    clipped_pcd = step6_clip_and_show(source_pcd, plane_mesh)
    
    extrema = step7_color_and_extremes(source_pcd, axis="z", marker_size=0.03)


