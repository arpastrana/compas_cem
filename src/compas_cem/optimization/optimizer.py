import numpy as np

from functools import partial

from compas_cem.optimization import nlopt_solver

from compas_cem.optimization import grad_finite_difference_numpy
from compas_cem.optimization import objective_function_numpy

from compas_cem.diagrams import TopologyDiagram

from compas_cem.equilibrium import force_equilibrium


__all__ = [
    "Optimizer"
]

# ------------------------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------------------------

class Optimizer():
    def __init__(self, **kwargs):
        self.topology = None
        self.constraints = {}
        self.goals = {}

# ------------------------------------------------------------------------------
# Counters
# ------------------------------------------------------------------------------

    def number_of_constraints(self):
        """
        """
        return len(self.constraints)

    def number_of_goals(self):
        """
        """
        return len(self.goals)

# ------------------------------------------------------------------------------
# Mappings
# ------------------------------------------------------------------------------

    def index_constraint(self):
        """
        A dictionary that maps indices to constraint keys.
        """
        return {idx: key for idx, key in enumerate(self.constraints.keys())}

    def constraint_index(self):
        """
        A dictionary that maps indices to constraint keys.
        """
        return {key: idx for key, idx in self.index_constraint()}

# ------------------------------------------------------------------------------
# Additions
# ------------------------------------------------------------------------------

    def add_constraint(self, constraint):
        """
        Adds an edge constraint.
        """
        key = constraint.key()
        self.constraints[key] = constraint

    def add_goal(self, goal):
        """
        Adds an target/goal.
        """
        key = goal.key()
        self.goals[key] = goal

# ------------------------------------------------------------------------------
# Removals
# ------------------------------------------------------------------------------

    def remove_constraint(self, key):
        """
        Removes an edge constraint from the optimizer.
        """
        if key not in self.constraints:
            raise KeyError("Constraint not found at object key: {}".format(key))
        del self.constraints[key]

    def remove_goal(self, key):
        """
        Removes an target/goal from the optimizer.
        """
        if key not in self.goals:
            raise KeyError("Goal not found at object key: {}".format(key))
        del self.goals[key]

# ------------------------------------------------------------------------------
# Objective Function
# ------------------------------------------------------------------------------

    def objective_func(self, grad_func, verbose):
        """
        """
        obj_func = objective_function_numpy
        func = self._optimize_topology
        v = verbose
        return partial(obj_func, x_func=func, grad_func=grad_func, verbose=v) 
    
# ------------------------------------------------------------------------------
# Gradient Function
# ------------------------------------------------------------------------------

    def gradient_func(self, step_size, verbose):
        """
        """
        grad_func = grad_finite_difference_numpy
        func = self._optimize_topology
        v = verbose
        return partial(grad_func, x_func=func, step_size=step_size, verbose=v)

# ------------------------------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------

    def solve_nlopt(self, topology, algorithm, iters, stopval, step_size, verbose=False):
        """
        """
        self.topology = topology  # TODO: this should not happen here!

        self.check_optimization_sanity()

        grad_f = self.gradient_func(step_size, verbose)
        f = self.objective_func(grad_f, verbose)

        x = self.optimization_parameters() 
        bounds_low, bounds_up = self.optimization_bounds()

        hyper_parameters = {
            "f": f,
            "algorithm": algorithm,
            "dims": self.number_of_constraints(),
            "bounds_low": bounds_low,
            "bounds_up": bounds_up,
            "iters": iters,
            "stopval": stopval
        }

        solver = nlopt_solver(**hyper_parameters)

        try:
            x_opt = solver.optimize(x)
        except RuntimeError:
            print("Tol unreached and max iters exhausted! Try increasing them.")
            x_opt = None

        loss_opt = solver.last_optimum_value()
        return x_opt, loss_opt

# ------------------------------------------------------------------------------
# Optimization parameters
# ------------------------------------------------------------------------------

    def optimization_parameters(self):
        """
        """
        x = np.zeros(self.number_of_constraints())

        for index, ckey in self.index_constraint().items():
            constraint = self.constraints[ckey]
            x[index] = constraint.start_value(self.topology)

        return x

    def optimization_bounds(self):
        """
        """
        bounds_low = np.zeros(self.number_of_constraints())
        bounds_up = np.zeros(self.number_of_constraints())

        for index, ckey in self.index_constraint().items():
            constraint = self.constraints[ckey]
            bounds_low[index] = constraint.bound_low(self.topology)
            bounds_up[index] = constraint.bound_up(self.topology)

        return bounds_low, bounds_up
    
# ------------------------------------------------------------------------------
# Updates
# ------------------------------------------------------------------------------

    def _update_topology_edges(self, x):
        """
        """
        x = np.squeeze(x).tolist()

        for index, ckey in self.index_constraint().items():
            edge = ckey
            if self.topology.is_trail_edge(edge):
                name = "length"
            elif self.topology.is_deviation_edge(edge):
                name = "force"    
            self.topology.edge_attribute(key=edge, name=name, value=x[index])

    def _compute_error(self):
        """
        """
        error = 0.0
        for goal in self.goals.values():
            goal.update(self.topology)
            error += goal.error()

        return error

# ------------------------------------------------------------------------------
# Equilibrium
# ------------------------------------------------------------------------------

    def _update_topology_equilibrium(self):
        """
        """
        force_equilibrium(self.topology, kmax=100, eps=1e-5)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

    def _optimize_topology(self, parameters):
        """
        """
        self._update_topology_edges(parameters)
        self._update_topology_equilibrium()
        return self._compute_error()

# ------------------------------------------------------------------------------
# Sanity Check
# ------------------------------------------------------------------------------

    def check_optimization_sanity(self):
        """
        """
        if len(self.constraints) == 0:
            msg = "No constraints defined. Optimization not possible."
            raise ValueError(msg)
        
        if len(self.goals) == 0:
            msg = "No goals defined. Optimization not possible."
            raise ValueError(msg)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
