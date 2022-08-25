import os

from time import time
from math import pi
from math import cos
from math import sin
from statistics import mean

import numpy as np

from compas.geometry import centroid_points

from compas.geometry import Translation

from compas.datastructures import mesh_dual

from compas_singular.datastructures import CoarseQuadMesh

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeParameter, DeviationEdgeParameter
from compas_cem.optimization import TrailEdgeForceConstraint, PlaneConstraint

from compas_plotters.plotter import Plotter

from compas_cem.viewers import Viewer


# ------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------

OPTIMIZE = True

EXPORT_JSON = False

VIEW = True
SHOW_EDGETEXT = False

STRIPS_DENSITY = 2  # only even numbers (2, 4, 6, ...) for best results

# ------------------------------------------------------------------------------
# Create a topology diagram
# ------------------------------------------------------------------------------

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'data/coarse_quad_mesh_6_2D_tower.json')
coarse = CoarseQuadMesh.from_json(FILE)
print('coarse quad mesh:', coarse)

coarse.collect_strips()
coarse.set_strips_density(STRIPS_DENSITY)
coarse.densification()
mesh = coarse.get_quad_mesh()
print('dense quad mesh:', mesh)

mesh = mesh_dual(mesh)
mesh.collect_polyedges()
print('dual quad mesh:', mesh)
FILE = os.path.join(HERE, 'data/arch_bridge_2D_topology.json')
mesh.to_json(FILE)

polyedge2height = {}
for pkey, polyedge in mesh.polyedges(data=True):
    if mesh.is_edge_on_boundary(polyedge[0], polyedge[1]):
        polyedge2height[pkey] = centroid_points([mesh.vertex_coordinates(vkey) for vkey in polyedge]
            )[2]
polyedge2height = sorted(polyedge2height.items(), key=lambda item: item[1])
supports = mesh.polyedge_vertices(polyedge2height[0][0]) + mesh.polyedge_vertices(polyedge2height[1][0])
loads = mesh.polyedge_vertices(polyedge2height[-1][0])
print(len(supports), 'supports')
print(len(loads), 'loads')

mean_length = mean([mesh.edge_length(*edge) for edge in mesh.edges()])

topology = TopologyDiagram.from_dualquadmesh(mesh,
                                             supports,
                                             trail_length=-mean_length,
                                             deviation_force=-1.0)

for key in loads:
    topology.add_load(NodeLoad(key, [0.0, 0.0, -0.1]))

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

topology.build_trails()
form = static_equilibrium(topology, eta=1e-6, tmax=100)

FILE = os.path.join(HERE, 'data/arch_bridge_2D_form_found.json')
form.to_json(FILE)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# # create optimizer
# opt = Optimizer()

# # parameters
# for edge in topology.trail_edges():
#     opt.add_parameter(TrailEdgeParameter(edge, -1.0, -1.0))

# for edge in topology.deviation_edges():
#     opt.add_parameter(DeviationEdgeParameter(edge, -1.0, -0.1))

# # constraints
# for edge in topology.trail_edges():
#     opt.add_constraint(TrailEdgeForceConstraint(edge, -1.0))

# for vkey in supports:
#     opt.add_constraint(PlaneConstraint(vkey, plane=((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))))

# # optimize
# start = time()
# form_opt = opt.solve_nlopt(topology, algorithm="LBFGS", iters=500, eps=1e-3)

# # print out results
# print("----------")
# print(f"Optimizer. # Parameters {opt.number_of_parameters()}, # Constraints {opt.number_of_constraints()}")
# print(f"Optimization elapsed time: {time() - start}")
# print(f"Final value of the objective function: {opt.penalty}")
# print(f"Norm of the gradient of the objective function: {opt.gradient_norm}")

# FILE = os.path.join(HERE, 'data/arch_bridge_2D_form_opt.json')
# form_opt.to_json(FILE)

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

# ns = 0.45
# shift = 1.0
# plotter = Plotter(figsize=(16.0, 9.0))

# # plot topology diagram
# plotter.add(topology, nodesize=ns)

# # plot translated form diagram
# T = Translation.from_vector([shift, 0.0, 0.0])
# plotter.add(form.transformed(T), nodesize=ns)

# # plot translated optimized form diagram
# T = Translation.from_vector([shift * 2.0, 0.0, 0.0])
# plotter.add(form_opt.transformed(T), nodesize=ns)

# # show scene
# plotter.zoom_extents(padding=-0.3)
# plotter.show()

# viewer = App(width=1600, height=900)
# viewer.view.camera.rx = -60
# viewer.view.camera.rz = 0
# viewer.view.camera.ty = -2
# viewer.view.camera.distance = 10

# viewer.add(form)
# viewer.show()

# ------------------------------------------------------------------------------
# Launch viewer
# ------------------------------------------------------------------------------

if VIEW:

    viewer = Viewer(width=1600, height=900, show_grid=False)

# ------------------------------------------------------------------------------
# Visualize starting mesh
# ------------------------------------------------------------------------------

    viewer.add(mesh)

# ------------------------------------------------------------------------------
# Visualize topology diagram
# ------------------------------------------------------------------------------

    topology = topology.transformed(Translation.from_vector([9.0, 0.0, 0.0]))
    viewer.add(topology,
               show_nodes=True,
               nodes=None,
               nodesize=15.0,
               show_edges=True,
               edges=None,
               edgewidth=2.0,
               show_loads=False,
               loadscale=2.5,
               show_edgetext=False,
               edgetext="key",
               show_nodetext=False,
               nodetext="key"
               )

# ------------------------------------------------------------------------------
# Visualize translated form diagram
# ------------------------------------------------------------------------------

    form = form.transformed(Translation.from_vector([18.0, 0.0, 0.0]))
    viewer.add(form,
               show_nodes=True,
               nodes=None,
               nodesize=15.0,
               show_edges=True,
               edges=None,
               edgewidth=2.0,
               show_loads=True,
               loadscale=1.0,
               loadtol=1e-1,
               show_residuals=False,
               residualscale=1.0,
               residualtol=1.5,
               show_edgetext=SHOW_EDGETEXT,
               edgetext="force",
               show_nodetext=False,
               nodetext="xyz"
               )

# ------------------------------------------------------------------------------
# Visualize translated constrained form diagram
# ------------------------------------------------------------------------------

    if OPTIMIZE:
        form_opt = form_opt.transformed(Translation.from_vector([18.0, -6.0, 0.0]))
        viewer.add(form_opt,
                   show_nodes=True,
                   nodes=None,
                   nodesize=15.0,
                   show_edges=True,
                   edges=None,
                   edgewidth=2.0,
                   show_loads=True,
                   loadscale=1.0,
                   loadtol=1e-1,
                   show_residuals=False,
                   residualscale=1.0,
                   residualtol=1.5,
                   show_edgetext=SHOW_EDGETEXT,
                   edgetext="force",
                   show_nodetext=False,
                   nodetext="xyz"
                   )

# ------------------------------------------------------------------------------
# Show scene
# -------------------------------------------------------------------------------

    viewer.show()