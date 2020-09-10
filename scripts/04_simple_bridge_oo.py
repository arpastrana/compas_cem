from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter
from compas_cem.viewers import TopologyViewer

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointGoal
from compas_cem.optimization import PlaneGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint

from compas.geometry import Plane
from compas.geometry import length_vector

from time import time

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = "/Users/arpj/code/libraries/compas_cem/data/json/w1_cem_2d_bridge.json"

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Store initial lines
# ------------------------------------------------------------------------------

keys = list(topology.deviation_edges())
deviation_force = 1.0
topology.edges_attribute(name="force", value=deviation_force, keys=keys)

load = [-2.0, 0.0, 0.0]
keys = list(topology.root_nodes()) 
for node in topology.root_nodes():
    topology.node_load(node, load)

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = topology.trails()
edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define goals / Targets
# ------------------------------------------------------------------------------

optimizer.add_goal(PointGoal(node=7, point=[29.13,22.20,0.00]))
optimizer.add_goal(PointGoal(node=2, point=[42.99,-14.17,0.00]))

plane = Plane(point=[32.0, 0.0, 0.0], normal=[0.0, 1.0, 0.0])
optimizer.add_goal(PlaneGoal(node=3, plane=plane))

plane = Plane(point=[32.0, 0.0, 0.0], normal=[1.0, 0.0, 0.0])
optimizer.add_goal(PlaneGoal(node=6, plane=plane))

# ------------------------------------------------------------------------------
# Define optimization parameters / constraints
# ------------------------------------------------------------------------------
bound_t = 20.0  # 10.0
bound_d = 20.0 # 10.0 

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
x_opt, l_opt = optimizer.solve_nlopt(topology, opt_algorithm, iters, stopval, step_size)

# print out results
print("Elapsed time: {}".format(time() - start))
print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Obtain residual forces
# ------------------------------------------------------------------------------

for node in topology.support_nodes():
    residual = length_vector(topology.residual_force(node))
    print("node: {} residual: {}".format(node, residual))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_nodes(radius=0.30, text="key")
plotter.draw_edges(text="force")
plotter.draw_loads(scale=-2.0)
plotter.draw_residuals(scale=-0.25)
plotter.draw_segments(edge_lines)

points = []
for key, goal in optimizer.goals.items():
    if not isinstance(goal, PointGoal):
        continue
    pt = goal.target_geometry()
    points.append({
        "pos": pt[:2],
        "radius": 0.15,
        "facecolor": (255, 153, 0)
    }
    )

plotter.draw_points(points)

plotter.show()

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

viewer = TopologyViewer(topology)
viewer.add_nodes(size=20)
viewer.add_edges(width=(1, 5))
viewer.add_loads(scale=-2, width=15)
viewer.add_residuals(scale=-0.25, width=15)

points = []
for key, goal in optimizer.goals.items():
    if not isinstance(goal, PointGoal):
        continue
    points.append(goal.target_geometry())

viewer.add_points(points, size=30)

viewer.show()
