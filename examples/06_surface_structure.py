import os

from statistics import mean

from compas.datastructures import mesh_dual

from compas.geometry import add_vectors
from compas.geometry import Translation

from compas_singular.datastructures import CoarseQuadMesh

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeParameter
from compas_cem.optimization import DeviationEdgeParameter
from compas_cem.optimization import OriginNodeXParameter
from compas_cem.optimization import OriginNodeYParameter
from compas_cem.optimization import OriginNodeZParameter
from compas_cem.optimization import PlaneConstraint
from compas_cem.optimization import LineConstraint
from compas_cem.optimization import PointConstraint

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
FILE = os.path.join(HERE, 'data/coarse_quad_mesh_66.json')
coarse = CoarseQuadMesh.from_json(FILE)
print('coarse quad mesh:', coarse)

coarse.collect_strips()
coarse.set_strips_density(STRIPS_DENSITY)
coarse.densification()
mesh = coarse.get_quad_mesh()
print('dense quad mesh:', mesh)

mesh = mesh_dual(mesh)
print('dual quad mesh:', mesh)

supports = []
boundary_vertices = mesh.vertices_on_boundary()[:-1]
for i in range(len(boundary_vertices)):
    u, v = boundary_vertices[0:2]
    polyedge = mesh.collect_polyedge(u, v)
    if i % 2 == 0:
        supports += polyedge
        for _ in range(len(polyedge)):
            del boundary_vertices[0]
    else:
        for _ in range(len(polyedge) - 2):
            del boundary_vertices[0]
    if len(boundary_vertices) == 0:
        break
print(len(supports), 'supports')

mean_length = mean([mesh.edge_length(*edge) for edge in mesh.edges()])

topology = TopologyDiagram.from_dualquadmesh(mesh,
                                             supports,
                                             trail_length=-mean_length,
                                             deviation_force=-1.0)
topology.build_trails()

# for key in topology.nodes():
#     if topology.is_node_support(key):
#         continue
#     topology.add_load(NodeLoad(key, [0.0, 0.0, -0.5]))

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
        opt.add_parameter(TrailEdgeParameter(edge, bound_low=10, bound_up=mean_length))

    for edge in topology.deviation_edges():
        opt.add_parameter(DeviationEdgeParameter(edge, bound_low=10, bound_up=1.0))

    for node in topology.origin_nodes():
        opt.add_parameter(OriginNodeXParameter(node, bound_low=1.0, bound_up=1.0))
        opt.add_parameter(OriginNodeYParameter(node, bound_low=1.0, bound_up=1.0))
        # opt.add_parameter(OriginNodeZParameter(node, bound_low=None, bound_up=0.0))

    # # constraints
    # for edge in topology.trail_edges():
    #     opt.add_constraint(TrailEdgeForceConstraint(edge, -1.0))

    # plane = ([0.0, 0.0, -1.0], [0.0, 0.0, 1.0])
    # for node in supports:
    #     opt.add_constraint(PlaneConstraint(node, plane=plane))

    for node in topology.nodes():
        point = topology.node_coordinates(node)
        # line = [add_vectors(point, (0.0, 0.0, zcoord)) for zcoord in (1.0, -1.0)]
        # opt.add_constraint(LineConstraint(node, line=line))
        opt.add_constraint(PointConstraint(node, point=point))

    # optimize
    form_opt = opt.solve(topology.copy(),
                         algorithm="LBFGS",
                         iters=200,
                         eps=1e-1,
                         verbose=True)

# ------------------------------------------------------------------------------
# Export to JSON
# ------------------------------------------------------------------------------

if EXPORT_JSON:
    datastructures = [mesh, form]
    names = ["shell_topology", "shell_form_found"]

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
