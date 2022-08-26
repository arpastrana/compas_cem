import os

from compas.geometry import scale_vector
from compas.geometry import Point
from compas.geometry import Translation

from compas.datastructures import mesh_dual

from compas_singular.datastructures import CoarseQuadMesh

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeParameter
from compas_cem.optimization import DeviationEdgeParameter
from compas_cem.optimization import PointConstraint

from compas_cem.viewers import Viewer

# ------------------------------------------------------------------------------
# Controls
# ------------------------------------------------------------------------------

SELF_STRESSED = True
OPTIMIZE = True

EXPORT_JSON = False

VIEW = True
SHOW_EDGETEXT = True

STRIPS_DENSITY = 2  # only even numbers (2, 4, 6, ...) for best results

deviation_force = 1.0

# ------------------------------------------------------------------------------
# Create a topology diagram
# ------------------------------------------------------------------------------

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'data/coarse_quad_mesh_666_3D_tower.json')
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

supports, loads = [], []
for pkey, polyedge in mesh.polyedges(data=True):
    if mesh.is_edge_on_boundary(polyedge[0], polyedge[1]):
        if len(polyedge) == 3 * STRIPS_DENSITY:
            supports += polyedge
        elif len(polyedge) == 3 * STRIPS_DENSITY + 1:
            loads += polyedge
print(len(supports), 'supports')

topology = TopologyDiagram.from_dualquadmesh(mesh,
                                             supports,
                                             trail_state=-1,
                                             deviation_force=deviation_force,
                                             deviation_state=-1)

topology.build_trails()

if not SELF_STRESSED:
    print(len(loads), 'loads')
    for key in loads:
        if topology.is_node_support(key):
            continue
        topology.add_load(NodeLoad(key, [0.0, 0.0, -0.1]))

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-6, tmax=100)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if OPTIMIZE:
    # create optimizer
    opt = Optimizer()

    # parameters
    for edge in topology.trail_edges():
        opt.add_parameter(TrailEdgeParameter(edge))

    for edge in topology.deviation_edges():
        opt.add_parameter(DeviationEdgeParameter(edge, bound_up=deviation_force))

    # constraints
    points = []
    for node in topology.nodes():
        if topology.is_node_origin(node):
            continue
        xyz = Point(*topology.node_coordinates(node))
        opt.add_constraint(PointConstraint(node, xyz))

    # optimize
    form_opt = opt.solve(topology,
                         algorithm="SLSQP",
                         iters=500,
                         eps=1e-6,
                         verbose=True)

# ------------------------------------------------------------------------------
# Export to JSON
# ------------------------------------------------------------------------------

if EXPORT_JSON:
    datastructures = [mesh, topology, form]
    names = ["archtower_mesh", "archtower_topology", "archtower_form", "archtower_form_opt"]

    if OPTIMIZE:
        datastructures.append(form_opt)
        names.append("shell_form_opt")

    for ds, name in zip(datastructures, names):
        path = os.path.join(HERE, f"data/{name}.json")
        ds.to_json(path)
        print(f"Exported datastructure to {path}")

# ------------------------------------------------------------------------------
# Launch viewer
# ------------------------------------------------------------------------------

if VIEW:

    viewer = Viewer(width=1600, height=900, show_grid=False)
    shift_vector = [20.0, 0.0, 0.0]

# ------------------------------------------------------------------------------
# Visualize starting mesh
# ------------------------------------------------------------------------------

    viewer.add(mesh)

# ------------------------------------------------------------------------------
# Visualize topology diagram
# ------------------------------------------------------------------------------

    topology = topology.transformed(Translation.from_vector(scale_vector(shift_vector, 1.)))
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

    form = form.transformed(Translation.from_vector(scale_vector(shift_vector, 2.)))
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
        T = Translation.from_vector(scale_vector(shift_vector, 3.))
        form_opt = form_opt.transformed(T)
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

        pointcolor = (255, 0, 0)
        for point in points:
            viewer.add(point.transformed(T), color=pointcolor, facecolor=facecolor, pointcolor=pointcolor, pointsize=40)

# ------------------------------------------------------------------------------
# Show scene
# -------------------------------------------------------------------------------

    viewer.show()
