from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter
from compas_cem.viewers import TopologyViewer

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointGoal
from compas_cem.optimization import TrimeshGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint

from compas.datastructures import Mesh
from compas.datastructures import network_transformed

from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Transformation

from trimesh import Trimesh

from numpy import array

from time import time

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN_MESH = "/Users/arpj/code/libraries/compas_cem/data/json/lightvault.json"
IN_ARCH = "/Users/arpj/code/libraries/compas_cem/data/json/arch.json"
OUT_ARCH = "/Users/arpj/code/libraries/compas_cem/data/json/arch_optimized.json"

ref_nodes = [7, 26]
target_points = [[0.002, 1.012, -0.020], [0.001, -1.019, 0.114]]

plot = False
view = True
export = True

# ------------------------------------------------------------------------------
# Target Mesh
# ------------------------------------------------------------------------------

mesh = Mesh.from_json(IN_MESH)

vertices, faces = mesh.to_vertices_and_faces()        
vertices = array(vertices).reshape((-1, 3))
faces = array(faces).reshape((-1, 3))
trimesh = Trimesh(vertices=vertices, faces=faces)

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN_ARCH)
force_equilibrium(topology)

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer(topology, verbose=True)

# ------------------------------------------------------------------------------
# Define goals / Targets
# ------------------------------------------------------------------------------

for node, point in zip(ref_nodes, target_points):
    optimizer.add_goal(PointGoal(node, point))

# record starting time
for node in topology.nodes():
    if topology.node_type(node) in {"root", "support"}:
        continue
    optimizer.add_goal(TrimeshGoal(node, trimesh))

# ------------------------------------------------------------------------------
# Define optimization parameters / constraints
# ------------------------------------------------------------------------------

bound_t = 0.025
bound_d = 0.07

for edge in topology.trail_edges():
    optimizer.add_constraint(TrailEdgeConstraint(edge, bound_t, bound_t))

for edge in topology.deviation_edges():
    optimizer.add_constraint(DeviationEdgeConstraint(edge, bound_d, bound_d))
        
# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# record starting time
start = time()

# optimization constants
opt_algorithm = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS
iters = 100  # 100
stopval = 1e-4  # 1e-4
step_size = 1e-6  # 1e-4

# optimize
print("Optimizing")
x_opt, l_opt = optimizer.solve_nlopt(opt_algorithm, iters, stopval, step_size)

# print out results
print("Elapsed time: {}".format(time() - start))
print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Export
# ------------------------------------------------------------------------------

if export:
    topology.to_json(OUT_ARCH)
    print("Exported json file to: {}".format(OUT_ARCH))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:
    T = Transformation.from_frame_to_frame(Frame.worldYZ(), Frame.worldXY())
    topology_transformed = network_transformed(topology, T)

    plotter = TopologyPlotter(topology_transformed, figsize=(16, 9))

    plotter.draw_nodes(radius=0.025, text="key")
    plotter.draw_edges(text="attr")
    plotter.draw_loads(scale=0.05)

    plotter.show()

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

if view:
    viewer = TopologyViewer(topology)
    viewer.add_nodes(size=20)
    viewer.add_edges(width=(1, 5))

    points = []
    for key, goal in optimizer.goals.items():
        if not isinstance(goal, PointGoal):
            continue
        points.append(goal.target_geometry())

    viewer.add_points(points, size=30)
    viewer.add_mesh(mesh, edges_width=1.0, faces_on=False)

    viewer.show()
