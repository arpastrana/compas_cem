from compas.geometry import closest_point_on_plane

__all__ = [
    "pull_point_to_plane",
    "pull_point_to_mesh"
]

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def pull_point_to_plane(point, plane):
    """
    """
    return closest_point_on_plane(point, plane)


def pull_point_to_mesh(point, mesh):
    """
    """
    # closest_points, distances, triangle_id =
    # trimesh.proximity.closest_point(mesh, TEST_POINTS)
    from trimesh import Trimesh
    from trimesh.proximity import closest_point

    vertices, faces = mesh.to_vertices_and_faces()
    trimesh = Trimesh(vertices, faces)
    closest_point, distance, triangle_id = closest_point(mesh, point)

    return 

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
