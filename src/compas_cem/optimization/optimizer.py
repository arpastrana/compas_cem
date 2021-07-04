import autograd.numpy as np

from functools import partial

from compas_cem.equilibrium import static_equilibrium

from compas_cem.equilibrium.force_numpy import equilibrium_state_numpy

from compas_cem.optimization import nlopt_solver
from compas_cem.optimization import grad_autograd
from compas_cem.optimization import objective_function_numpy


__all__ = ["Optimizer"]


# ------------------------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------------------------

class Optimizer():
    """
    An object that modifies a form diagram to meet multiple constraints.
    """
    def __init__(self):
        self.parameters = {}
        self.constraints = {}
        self.x_opt = None
        self.penalty = None
        self.evals = None

# ------------------------------------------------------------------------------
# Counters
# ------------------------------------------------------------------------------

    def number_of_parameters(self):
        """
        The number of optimization parameters.
        """
        return len(self.parameters)

    def number_of_constraints(self):
        """
        The number of constraints added to the optimizer.
        """
        return len(self.constraints)

# ------------------------------------------------------------------------------
# Mappings
# ------------------------------------------------------------------------------

    def index_parameter(self):
        """
        A dictionary that maps indices to parameter keys.
        """
        return {idx: key for idx, key in enumerate(self.parameters.keys())}

    def parameter_index(self):
        """
        A dictionary that maps parameter keys to indices.
        """
        return {key: idx for key, idx in self.index_parameter()}

# ------------------------------------------------------------------------------
# Additions
# ------------------------------------------------------------------------------

    def add_parameter(self, parameter):
        """
        Adds a parameter to the optimization problem.
        """
        key = (parameter.key(), parameter.attr_name())
        self.parameters[key] = parameter

    def add_constraint(self, constraint):
        """
        Adds a goal constraint.
        """
        key = constraint.key()
        self.constraints[key] = constraint

# ------------------------------------------------------------------------------
# Removals
# ------------------------------------------------------------------------------

    def remove_parameter(self, key):
        """
        Removes an optimization parameter.
        """
        if key not in self.parameters:
            raise KeyError("Parameter not found at object key: {}".format(key))
        del self.parameters[key]

    def remove_constraint(self, key):
        """
        Removes a goal constraint from the optimizer.
        """
        if key not in self.constraints:
            raise KeyError("Constraints not found on object key: {}".format(key))
        del self.constraints[key]

# ------------------------------------------------------------------------------
# Objective Function
# ------------------------------------------------------------------------------

    def objective_func(self, topology, grad_func):
        """
        Test with autodiff.
        """
        obj_func = objective_function_numpy
        func = partial(self._optimize_form, topology=topology)
        return partial(obj_func, x_func=func, grad_func=grad_func)

# ------------------------------------------------------------------------------
# Gradient Function
# ------------------------------------------------------------------------------

    def gradient_func(self, topology):
        """
        """
        x_func = partial(self._optimize_form, topology=topology)
        return partial(grad_autograd, grad_func=x_func)

# ------------------------------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------
#
    def solve_nlopt(self, topology, algorithm, iters, eps=None):
        """
        Solve an optimization problem with NLOpt.
        """
        # test for bad stuff before going any further
        self.check_optimization_sanity()

        # compose gradient and objective functions
        grad_func = self.gradient_func(topology.copy())
        penalty_func = self.objective_func(topology, grad_func)

        # generate optimization variables
        x = self.optimization_parameters(topology)

        # extract the lower and upper bounds to optimization variables
        bounds_low, bounds_up = self.optimization_bounds(topology)

        # stack keyword arguments
        hyper_parameters = {"f": penalty_func,
                            "algorithm": algorithm,
                            "dims": self.number_of_parameters(),
                            "bounds_low": bounds_low,
                            "bounds_up": bounds_up,
                            "iters": iters,
                            "stopval": eps,
                            "ftol": None}

        # assemble optimization solver
        solver = nlopt_solver(**hyper_parameters)

        # solve optimization problem
        try:
            x_opt = solver.optimize(x)
            evals = solver.get_numevals()
            print("Optimization ended correctly!")
            print("Number of evaluations incurred: {}".format(evals))
        except RuntimeError:
            evals = solver.get_numevals()
            print("Tol unreached and max iters exhausted! Try increasing them.")
            print("Number of evaluations incurred: {}".format(evals))
            x_opt = None

        # fetch last optimum value of loss function
        loss_opt = solver.last_optimum_value()

        # set optimizer attributes
        self.x_opt = x_opt
        self.penalty = loss_opt
        self.evals = evals

        # exit like a champion
        return static_equilibrium(topology)

# ------------------------------------------------------------------------------
# Optimization parameters
# ------------------------------------------------------------------------------

    def optimization_parameters(self, form):
        """
        Creates optimization paremeters array.
        Only one entry in the array per constraint.
        Takes care of keeping the ordering.
        """
        # TODO: This can become an (n, 3) array to acount for root nodes variables?
        x = np.zeros(self.number_of_parameters())

        for index, ckey in self.index_parameter().items():
            constraint = self.parameters[ckey]
            x[index] = constraint.start_value(form)

        return x

    def optimization_bounds(self, form):
        """
        Creates optimization bounds array.
        Only one entry in the array per constraint.
        """
        bounds_low = np.zeros(self.number_of_parameters())
        bounds_up = np.zeros(self.number_of_parameters())

        for index, ckey in self.index_parameter().items():
            parameter = self.parameters[ckey]
            bounds_low[index] = parameter.bound_low(form)
            bounds_up[index] = parameter.bound_up(form)

        return bounds_low, bounds_up

# ------------------------------------------------------------------------------
# Updates
# ------------------------------------------------------------------------------

    def _update_topology_origin_nodes(self, x, topology):
        """
        """
        map_xyz_index = {"x": 0, "y": 1, "z": 2}

        for index, ckey in self.index_parameter().items():

            node = self.parameters[ckey].key()

            # TODO: weak check, needs to be handled differently
            if not isinstance(node, int):
                continue

            # TODO: this check should happen upon assembly, not at calculation?
            if not topology.is_node_origin(node):
                msg = "{} is not a root node. Assigned constraint is invalid!"
                raise ValueError(msg.format(node))

            # TODO: refactor to handle xyz more transparently
            xyz = topology.node_xyz(key=node)
            parameter = self.parameters[ckey]
            j = map_xyz_index[parameter.attr_name()]
            xyz[j] = x[index]

            # self.form.node_xyz(key=node, xyz=xyz)  # form.node_xyz(node, y=x[])?
            topology.node_attributes(key=node, names="xyz", values=xyz)

    def _update_topology_edges(self, x, topology):
        """
        """
        for index, ckey in self.index_parameter().items():

            edge = self.parameters[ckey].key()

            # TODO: weak check, needs to be handled differently
            if isinstance(edge, int):
                continue

            if topology.is_trail_edge(edge):
                name = "length"
            elif topology.is_deviation_edge(edge):
                name = "force"

            value = x[index]

            topology.edge_attribute(key=edge, name=name, value=value)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

    def _calculate_penalty(self, eq_state):
        """
        """
        error = 0.0
        for goal in self.constraints.values():
            error += goal.error(eq_state)

        return error

    def _optimize_form(self, parameters, topology):
        """
        """
        self._update_topology_origin_nodes(parameters, topology)
        self._update_topology_edges(parameters, topology)

        eq_state = equilibrium_state_numpy(topology, tmax=100, eta=1e-5)

        return self._calculate_penalty(eq_state)

# ------------------------------------------------------------------------------
# Sanity Check
# ------------------------------------------------------------------------------

    def check_optimization_sanity(self):
        """
        Verify the optimization problem is in its sane mind.
        """
        if len(self.parameters) == 0:
            msg = "No parameters defined. Optimization not possible."
            raise ValueError(msg)

        if len(self.constraints) == 0:
            msg = "No constraints defined. Optimization not possible."
            raise ValueError(msg)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
