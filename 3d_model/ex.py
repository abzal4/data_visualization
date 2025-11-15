import open3d as o3d

# Загрузка модели
mesh = o3d.io.read_triangle_mesh(r"C:\Users\Abzal_\Desktop\data_vis\ass5\shark.obj")   # можно STL/PLY
mesh.compute_vertex_normals()

print(mesh)

# Визуализация
o3d.visualization.draw_geometries([mesh])
