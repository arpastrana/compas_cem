import os

from compas.geometry import centroid_points
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import dot_vectors
from compas.geometry import subtract_vectors
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

from compas_cem.plotters import Plotter
from compas_cem.viewers import Viewer

# ------------------------------------------------------------------------------
# Controls
# ------------------------------------------------------------------------------

STRIPS_DENSITY = 3  # only even numbers (2, 4, ...) for best results
DEVIATION_FORCE = 0.1  # starting force in all deviation edges

SHIFT_TRAILS = True
LOADS_VERTICAL = False

KMAX = None

OPTIMIZE = True
OPTIMIZER = "SLSQP"
ITERS = 300
EPS = 1.

PLOT = True
VIEW = True
SHOW_EDGETEXT = False

EXPORT_JSON = False

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
                                             trail_state=1.,
                                             deviation_force=DEVIATION_FORCE,
                                             deviation_state=1.)

topology.build_trails()


# assign in-plane loads for numerical stability
# hole is the boundary with fewer vertices
hole = sorted(mesh.vertices_on_boundaries(), key=lambda x: len(x))[0]
hole_centroid = centroid_points([mesh.vertex_coordinates(key) for key in hole])
for key in hole:
    trail_edge = topology.connected_trail_edges(key)[0]
    vector = normalize_vector(topology.edge_vector(*trail_edge))
    vector_hole = subtract_vectors(mesh.vertex_coordinates(key), hole_centroid)
    if dot_vectors(vector, vector_hole) < 0.:
        vector = scale_vector(vector, -1.)
    topology.add_load(NodeLoad(key, scale_vector(vector, -1.0)))


if LOADS_VERTICAL:
    print(len(loads), 'loads')
    for key in loads:
        if not topology.is_node_support(key):
            topology.add_load(NodeLoad(key, [0.0, 0.0, -0.1]))

# ------------------------------------------------------------------------------
# Shift trail sequences to avoid having indirect deviation edges
# ------------------------------------------------------------------------------

if SHIFT_TRAILS:
    print("Shifting sequences, baby!")

    while topology.number_of_indirect_deviation_edges() > 0:
        for node_origin in topology.origin_nodes():

            for edge in topology.connected_edges(node_origin):

                if topology.is_indirect_deviation_edge(edge):
                    u, v = edge
                    node_other = u if node_origin != u else v
                    sequence = topology.node_sequence(node_origin)
                    sequence_other = topology.node_sequence(node_other)

                    if sequence_other > sequence:
                        topology.shift_trail(node_origin, sequence_other)

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, kmax=KMAX)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if OPTIMIZE:
    # create optimizer
    opt = Optimizer()

    for edge in topology.trail_edges():
        opt.add_parameter(TrailEdgeParameter(edge))

    for edge in topology.deviation_edges():
        opt.add_parameter(DeviationEdgeParameter(edge, bound_low=DEVIATION_FORCE-0.1))

    # constraints
    points = []
    for node in topology.nodes():
        if topology.is_node_origin(node):
            continue
        xyz = Point(*topology.node_coordinates(node))
        opt.add_constraint(PointConstraint(node, xyz))

    # optimize
    tmax = 1
    if topology.number_of_indirect_deviation_edges() > 0:
        tmax = 100
    form_opt = opt.solve(topology,
                         algorithm=OPTIMIZER,
                         iters=ITERS,
                         eps=EPS,
                         tmax=tmax,
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
# Visualization
# ------------------------------------------------------------------------------

if PLOT or VIEW:
    shift_vector = [22.0, 0.0, 0.0]
    topology = topology.transformed(Translation.from_vector(scale_vector(shift_vector, 1.)))
    form = form.transformed(Translation.from_vector(scale_vector(shift_vector, 2.)))
    forms = [form]

    if OPTIMIZE:
        form_opt = form_opt.transformed(Translation.from_vector(scale_vector(shift_vector, 3.)))
        forms.append(form_opt)

# ------------------------------------------------------------------------------
# Plot
# ------------------------------------------------------------------------------

if PLOT:

    ns = 12
    form_edgewidth = (0.75, 3.0)

    plotter = Plotter(figsize=(18, 9))

    plotter.add(topology,
                nodesize=ns,
                edgecolor="type",
                nodetext="sequence",
                nodecolor="type",
                show_nodetext=True)

    for form in forms:
        plotter.add(form,
                    edgewidth=form_edgewidth,
                    nodesize=ns,
                    edgetext="force",
                    show_loads=False,
                    show_reactions=False,
                    show_edgetext=SHOW_EDGETEXT)

    plotter.zoom_extents(padding=-2)
    plotter.show()

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

    viewer.add(topology,
               edgewidth=0.03,
               show_loads=False)

# ------------------------------------------------------------------------------
# Visualize translated form diagram
# ------------------------------------------------------------------------------

    for form in forms:
        viewer.add(form,
                   edgewidth=(0.03, 0.15),
                   edgetext="force",
                   show_edgetext=SHOW_EDGETEXT)

# ------------------------------------------------------------------------------
# Show scene
# -------------------------------------------------------------------------------

    viewer.show()
