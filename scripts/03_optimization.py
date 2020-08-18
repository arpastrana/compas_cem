from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter

from compas_cem.equilibrium import force_equilibrium
from compas_cem.optimization import optimize_topology

from nlopt import opt

import numpy as np

from functools import partial

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = "/Users/arpj/code/libraries/compas_cem/data/json/w1_cem_2d_bridge.json"

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

keys = list(topology.deviation_edges())
deviation_force = 1.0
topology.edges_attribute(name="force", value=deviation_force, keys=keys)


# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = topology.trails()
edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Initial Force Equilibrium
# ------------------------------------------------------------------------------

# should we do this before optimization?
force_equilibrium(topology, kmax=100, verbose=False)

# ------------------------------------------------------------------------------
# Optimization? - Numpy!
# ------------------------------------------------------------------------------

def loss_numpy(y, y_hat):
    """
    Returned values hould be positive
    """
    # distance to points
    diff = y - y_hat
    rownorms = np.linalg.norm(diff, axis=1)
    rownorms = np.square(rownorms)
    error = np.sum(rownorms)
    
    # print("y", y)
    # print("y hat", y_hat)
    # print("diff", diff)
    # print("norm rows", rownorms)
    # print("sq", sq)
    # print("error", error)
    return error


def f(x, grad, func, lr):
    """
    Gradient
    """
    if grad.size > 0:
        # finite difference
        
        # fx 0
        fx0 = func(x, topology, y_hat)
        _x = np.copy(x)
        _x += lr

        # fx 1
        fx1 = func(_x, topology, y_hat)

        delta_fx = (fx1 - fx0) / lr
        print("delta fx", delta_fx)
        print("grad pre", grad)
        grad[:] = delta_fx
        print("grad post", grad)

    # fx
    print("====== Computing Loss ======")
    fx = func(x, topology, y_hat)
    print("Loss: {}".format(fx))
    return fx


def f_fd(x, grad, func, lr):
    """
    Finite differences
    """
    if grad.size > 0:
        # finite difference
        print("====== Computing Gradient ======")
        
        # fx 0
        fx0 = func(x, topology, y_hat)
    
        for i in range(len(x)):  # vectorize with numpy?

            _x = np.copy(x)
            _x[i] += lr

            # fx 1
            fx1 = func(_x, topology, y_hat)

            delta_fx = (fx1 - fx0) / lr
            grad[i] = delta_fx
        
        print("Gradient: {}".format(grad))

    # fx
    print("====== Computing Loss ======")
    fx = func(x, topology, y_hat)
    print("Loss: {}".format(fx))
    return fx


def optimization_numpy(x, fx, algorithm, bounds_up, bounds_low, tol, maxeval):
    """
    Depends on NLopt's python wrapper.
    """
    n = x.size
    solver = opt(algorithm, n)

    # to specify an unbounded dimension, use +- float('inf') or numpy.inf
    # bounds_up and bounds_low are np arrays with dimension n (x.size)
    # initial values for bounds are force or length in deviation edges
    # then, for bounds up, add defined bounds up value
    # for bounds down, the same
    # if no bound is specified, bounds up and low are equal
    # and should not be run through gradient descent in f()! artificially, 
    # the gradient is set to zero (as if variable was a constant)
    
    solver.set_maxeval(maxeval)
    # solver.set_ftol_rel(tol)  # or set_ftol_rel

    # what happens when a variable is "unbounded"?
    # is it just not part of the optimization parameters?
    solver.set_lower_bounds(bounds_low)
    solver.set_upper_bounds(bounds_up)

    solver.set_min_objective(fx)

    try:
        x_opt = solver.optimize(x)
    except RuntimeError:
        print("Runtime error! Max iters exhausted or tol rel not reached?")
        x_opt = None

    loss_opt = solver.last_optimum_value()  # loss
    return x_opt, loss_opt


def update_topology_edges(topology, x, t_edges, dd_edges, di_edges):
    num_t_edges = len(t_edges)
    num_dd_edges = len(dd_edges)

    new_dd_forces = np.squeeze(x[0:num_dd_edges]).tolist()
    new_t_lengths = np.squeeze(x[num_dd_edges:num_t_edges+num_dd_edges]).tolist()

    new_di_forces = np.squeeze(x[num_t_edges+num_dd_edges:]).tolist()

    if not isinstance(new_di_forces, list):
        new_di_forces = [new_di_forces]

    for edge, length in zip(t_edges, new_t_lengths):
        topology.edge_attribute(key=edge, name="length", value=length)

    for edge, force in zip(dd_edges, new_dd_forces):
        topology.edge_attribute(key=edge, name="force", value=force)
    
    for edge, force in zip(di_edges, new_di_forces):
        topology.edge_attribute(key=edge, name="force", value=force)


def generate_goals(topology, target_nodes):
    xyz = np.array([topology.node_coordinates(node) for node in target_nodes])
    y = np.reshape(np.array(xyz), (-1, 3))
    return y


def main(x, topology, y_hat, t_edges, dd_edges, di_edges, target_nodes):
    """
    Combo breaker.
    """
    update_topology_edges(topology, x, t_edges, dd_edges, di_edges)
    force_equilibrium(topology, kmax=100, verbose=False)  # need to change?
    y = generate_goals(topology, target_nodes)
    loss = loss_numpy(y, y_hat)
    return loss


# ------------------------------------------------------------------------------
# Work
# ------------------------------------------------------------------------------

from time import time

start = time()

# algorithms
from nlopt import LD_MMA
from nlopt import LN_COBYLA
from nlopt import LN_BOBYQA
from nlopt import LD_LBFGS
from nlopt import LD_SLSQP


# optimization constants
opt_algorithm = LD_LBFGS  # LN_BOBYQA / LD_LBFGS
max_iterations = 100  # 100
relative_tol = 1e-4  # 1e-4
learning_rate = 1e-4  # 1e-4

# bounds
bound_trail = 10.0  # 10.0
bound_deviation = 5.0 # 10.0 

# targets
goal_points = [[65.33, -8.84, 0.00], [65.33, 8.84, 0.00]]
target_nodes = [2, 7]

target_points = {k: target for k, target in zip(target_nodes, goal_points)}
uv_target = {index: k for index, k in enumerate(target_points.keys())}

# topology stuff
num_edges = topology.number_of_edges()

# parameters to optimize - x
# all edges are optimizable here
# later consider only optimizable

t_edges = list(topology.trail_edges())  
d_edges = list(topology.deviation_edges())

dd_edges = [uv for uv in d_edges if topology._is_direct_deviation_edge(uv)]
di_edges = [uv for uv in d_edges if topology._is_indirect_deviation_edge(uv)]

print("t_edges", t_edges)
print("d_edges", d_edges)
print("dd_edges", dd_edges)
print("di_edges", di_edges)

num_t_edges = len(t_edges)
num_d_edges = len(d_edges)
num_dd_edges = len(dd_edges)
num_di_edges = len(di_edges)

assert num_dd_edges + num_di_edges == num_d_edges, "Edges don't match!"

trail_lengths = topology.edges_attribute(name="length", keys=t_edges)
deviation_forces = topology.edges_attribute(name="force", keys=d_edges)
dd_forces = topology.edges_attribute(name="force", keys=dd_edges)
di_forces = topology.edges_attribute(name="force", keys=di_edges)

x = (np.array(dd_forces + trail_lengths + di_forces))
print("x", x)

# bounds up
# all edges are optimizable
bounds_up = np.ones(num_edges, dtype=np.float)
bounds_up[:num_dd_edges] *= bound_deviation
bounds_up[num_dd_edges:num_dd_edges+num_t_edges] *= bound_trail
bounds_up[num_dd_edges+num_t_edges:] *= bound_deviation
bounds_up += x
print("bounds_up", bounds_up)

# bounds low
# all edges are optimizable
bounds_low = np.ones(num_edges, dtype=np.float)
bounds_low[:num_dd_edges] *= -bound_deviation
bounds_low[num_dd_edges:num_dd_edges+num_t_edges] *= -bound_trail
bounds_low[num_dd_edges+num_t_edges:] *= -bound_deviation
bounds_low += x
print("bounds_low", bounds_low)

# generate goal array
y = generate_goals(topology, target_nodes)
print("y", y)

# generate target array
xyz = np.array([gp for gp in goal_points])
y_hat = np.reshape(xyz, (-1, 3))
print("y_hat", y_hat)

# update topology
# update_topology_edges(topology, x, t_edges, d_edges)
update_topology_edges(topology, x, t_edges, dd_edges, di_edges)

# test loss
error = loss_numpy(y, y_hat)
print("error", error)

# create partial functions
main_partial = partial(main, t_edges=t_edges, dd_edges=dd_edges, di_edges=di_edges, target_nodes=target_nodes)

fx_partial = partial(f_fd, func=main_partial, lr=learning_rate)

# optimization numpy
x_opt, l_opt = optimization_numpy(x, fx_partial, opt_algorithm, bounds_up, bounds_low, relative_tol, max_iterations)

print("Optimized weights: {}".format(x_opt))
print("Optimized loss: {}".format(l_opt))

# doing equilibrium once more after optimization
# can origin nodes be optimized?
# in the script doesn't look like it
# or maybe that's why they are part of the x parameter vector?
# what happens if there is a target defined at an edge, but then no
# corresponding bound? overconstrained, some default?
# does the ordering of parameters in x matter? do they need to follow the trails
# sequencing (layers)? ARPJ: looks like it!!
# ordering in CEM: direct deviation, trails, indirect deviations, origin nodes
# could you walk me over the almighty Main() function? What's happening inside?
# do we need to change force_equilibrium internally to consider a while loop?
# if no origin nodes, are the entries empty?
# does doing equilibrium after optimization changes anything at all?

print("okay!")
print("Elapsed time: {}".format(time() - start))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

from compas.utilities import geometric_key

edge_text = None
node_text = "key"

node_text = {}
for n in topology.nodes():
    msg = "{} / {}".format(n, geometric_key(topology.node_coordinates(n)))
    node_text[n] = msg

edge_text = {}
for e, attr in topology.edges(True):
    msg = "{} / f: {}".format(e, round(attr["force"], 3))
    edge_text[e] = msg

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_nodes(radius=0.25, text=node_text)
plotter.draw_edges(text=edge_text)

plotter.draw_loads(scale=2.0)
plotter.draw_segments(edge_lines)
plotter.show()

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

from math import copysign

from compas.utilities import rgb_to_hex
from compas.geometry import Point
from compas.geometry import Line
from compas.geometry import Polyline
from compas.geometry import Plane
from compas.geometry import Circle

from compas.utilities import rgb_to_hex

from compas_viewers.objectviewer import ObjectViewer


viewer = ObjectViewer()

forces = topology.edges_attribute(name="force")
minforce = min(forces)
maxforce = max(forces) - minforce
maxwidth = 10.0
minwidth = 1.0

cmap = {-1: (0, 0, 255), 1: (255, 0, 0)}
for edge, attr in topology.edges(True):
    start, end = topology.edge_coordinates(*edge)
    f = attr["force"]
    f = (f - minforce) / maxforce

    s = {}
    s["edges.color"] = rgb_to_hex(cmap[copysign(1.0, attr["force"])])
    s["edges.width"] = f * maxwidth + minwidth
    viewer.add(Line(start, end), settings=s)

# viewer.show()
