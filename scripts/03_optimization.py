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
# force_equilibrium(topology, kmax=100, verbose=False)

# ------------------------------------------------------------------------------
# Optimization? - Numpy!
# ------------------------------------------------------------------------------

def loss_numpy(y, y_hat):
    """
    Returned values hould be positive
    """
    # distance to points
    sq = np.square(y - y_hat)
    error = np.sum(sq)
    return error


def f(x, grad, func, lr=1e-3):
    """
    Finite differences
    """
    if grad.size > 0:
        # finite difference
        
        # fx 0
        fx0 = func(x, topology, y_hat)
    
        for i in range(len(x)):  # vectorize with numpy?

            x = np.copy(x)
            x[i] += lr

            # fx 1
            fx1 = func(x, topology, y_hat)

            delta_fx = (fx1 - fx0) / lr
            grad[i] = delta_fx

    # fx
    fx = func(x, topology, y_hat)
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
    
    # what happens when a variable is "unbounded"?
    # is it just not part of the optimization parameters?
    solver.set_lower_bounds(bounds_low)
    solver.set_upper_bounds(bounds_up)

    solver.set_min_objective(fx)

    solver.set_xtol_rel(tol)  # or set_ftol_rel
    solver.set_maxeval(maxeval)

    xopt = solver.optimize(x)

    opt_val = solver.last_optimum_value()  # loss
    result = solver.last_optimize_result()

    print("xopt", xopt)
    print("opt val", opt_val)

    return result


def update_topology_edges(topology, x, t_edges, d_edges):
    num_t_edges = len(t_edges)
    num_d_edges = len(d_edges)

    # new_lengths = np.squeeze(x[0:num_t_edges]).tolist()
    # new_forces = np.squeeze(x[num_t_edges:]).tolist()

    new_forces = np.squeeze(x[0:num_d_edges]).tolist()
    new_lengths = np.squeeze(x[num_d_edges:]).tolist()

    for edge, length in zip(t_edges, new_lengths):
        topology.edge_attribute(key=edge, name="length", value=length)

    for edge, force in zip(d_edges, new_forces):
        topology.edge_attribute(key=edge, name="force", value=force)


def generate_goals(topology, target_nodes):
    xyz = np.array([topology.node_coordinates(node) for node in target_nodes])
    y = np.reshape(np.array(xyz), (-1, 3))
    return y


def main(x, topology, y_hat, t_edges, d_edges, target_nodes):
    """
    Combo breaker.
    """
    update_topology_edges(topology, x, t_edges, d_edges)
    force_equilibrium(topology, kmax=100)
    y = generate_goals(topology, target_nodes)
    return loss_numpy(y, y_hat) 


# ------------------------------------------------------------------------------
# Work
# ------------------------------------------------------------------------------

# algorithms
from nlopt import LD_MMA
from nlopt import LN_COBYLA
from nlopt import LN_BOBYQA
from nlopt import LD_LBFGS


# optimization constants
opt_algorithm = LN_BOBYQA  # LN_BOBYQA / LD_LBFGS
relative_tol = 1e-4  # 1e-4
max_iterations = 100
learning_rate = 1e-4  # 1e-4

# bounds
bound_trail = 50.0
bound_deviation = 30.0

# targets
goal_points = [[65.33, -8.84, 0.00]]
target_nodes = [2]

target_points = {k: target for k, target in zip(target_nodes, goal_points)}
uv_target = {index: k for index, k in enumerate(target_points.keys())}

# topology stuff
num_edges = topology.number_of_edges()

# parameters to optimize - x
# all edges are optimizable here
# later consider only optimizable

t_edges = list(topology.trail_edges())  
d_edges = list(topology.deviation_edges())
print("t_edges", t_edges)
print("d_edges", d_edges)

num_t_edges = len(t_edges)
num_d_edges = len(d_edges)

trail_lengths = topology.edges_attribute(name="length", keys=t_edges)
deviation_forces = topology.edges_attribute(name="force", keys=d_edges)

# x = (np.array(trail_lengths + deviation_forces))
x = (np.array(deviation_forces + trail_lengths))
print("x", x)

# bounds up
# all edges are optimizable
bounds_up = np.ones(num_edges, dtype=np.float)
# bounds_up[:num_t_edges] *= bound_trail
# bounds_up[num_t_edges:] *= bound_deviation
bounds_up[:num_d_edges] *= bound_deviation
bounds_up[num_d_edges:] *= bound_trail
bounds_up += x
print("bounds_up", bounds_up)

# bounds low
# all edges are optimizable
bounds_low = np.ones(num_edges, dtype=np.float)
bounds_low[:num_d_edges] *= -bound_deviation
bounds_low[num_d_edges:] *= -bound_trail
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
update_topology_edges(topology, x, t_edges, d_edges)

# test loss
error = loss_numpy(y, y_hat)
print("error", error)

# create partial functions
main_partial = partial(main, t_edges=t_edges, d_edges=d_edges, target_nodes=target_nodes)

fx_partial = partial(f, func=main_partial, lr=learning_rate)

# optimization numpy

out = optimization_numpy(x, fx_partial, opt_algorithm, bounds_up, bounds_low, relative_tol, max_iterations)


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


print("okay!")

# ------------------------------------------------------------------------------
# Visualization
# ------------------------------------------------------------------------------

from compas.utilities import geometric_key
from compas.datastructures import network_transformed
from compas.geometry import Rotation
from math import radians

edge_text = None
node_text = "key"

edge_text = {}
for e, attr in topology.edges(True):
    msg = "{} / f: {}".format(e, round(attr["state"] * attr["force"], 3))
    edge_text[e] = msg

# edge_text = {e: attr["type"] for e, attr in topology.edges(True)}

node_text = {n: geometric_key(topology.node_coordinates(n), precision="3f") for n in topology.nodes()}

# transformation = Rotation.from_axis_and_angle([1, 0, 0], radians(-90))
# topology = network_transformed(topology, transformation)

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_nodes(radius=0.25, text=node_text)
plotter.draw_edges(text=edge_text)

plotter.draw_loads(scale=2.0)
plotter.draw_segments(edge_lines)
plotter.show()

