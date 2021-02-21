import numpy as np

from functools import partial

from compas_cem.optimization import nlopt_solver

from compas_cem.optimization import grad_finite_difference_numpy
from compas_cem.optimization import objective_function_numpy

from compas_cem.optimization import grad_autograd

from compas_cem.equilibrium import force_equilibrium

from compas_cem.equilibrium import form_equilibrate
from compas_cem.equilibrium import form_update

from compas_cem.equilibrium.force_numpy import form_equilibrate_numpy


__all__ = ["Optimizer"]

# profiling stuff
import atexit
import line_profiler
profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)

# ------------------------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------------------------

class Optimizer():
    """
    An object that modifies a form diagram to accomplish geometric goals.
    """
    def __init__(self, **kwargs):
        self.form = None
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
        Adds a constraint.
        """
        key = (constraint.key(), constraint.attr_name())
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

    def objective_func_2(self, form, grad_func, verbose):
        """
        Test with autodiff.
        """
        v = verbose
        obj_func = objective_function_numpy
        func = partial(self._optimize_form, form=form)

        return partial(obj_func, x_func=func, grad_func=grad_func, verbose=v)

    def objective_func(self, form, step_size, verbose):
        """
        """
        v = verbose
        func = partial(self._optimize_form, form=form)
        grad_func = grad_finite_difference_numpy
        grad_func = partial(grad_func, x_func=func, step_size=step_size, verbose=v)
        obj_func = objective_function_numpy

        return partial(obj_func, x_func=func, grad_func=grad_func, verbose=v)
    
# ------------------------------------------------------------------------------
# Gradient Function
# ------------------------------------------------------------------------------

    def gradient_func(self, step_size, verbose):
        """
        """
        grad_func = grad_finite_difference_numpy
        func = self._grad_optimize_form
        v = verbose

        return partial(grad_func, x_func=func, step_size=step_size, verbose=v)

    def gradient_func_2(self, form, verbose):
        """
        """
        x_func = partial(self._grad_optimize_form, form=form)

        return partial(grad_autograd, grad_func=x_func, verbose=verbose)

# ------------------------------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------
#
    def solve_nlopt(self, form, algorithm, iters, step_size, stopval=None, ftol=None, mode=None, verbose=False):
        """
        Solve an optimization problem with NLOpt.
        """
        # test for bad stuff before going any further
        self.check_optimization_sanity()

        # build trails
        form.trails()

        # compose gradient and objective functions
        if mode == "autodiff":
            print("*** Doing automatic differentiation! ***")
            gf = self.gradient_func_2(form.copy(), verbose)
            f = self.objective_func_2(form, gf, verbose)
        else:
            print("*** Doing finite differences! ***")
            grad_f = self.gradient_func(step_size, verbose)
            f = self.objective_func(form, step_size, verbose)

        # generate optimization variables
        x = self.optimization_parameters(form)

        # extract the lower and upper bounds to optimization variables
        bounds_low, bounds_up = self.optimization_bounds(form)

        # stack keyword arguments
        hyper_parameters = {
            "f": f,
            "algorithm": algorithm,
            "dims": self.number_of_constraints(),
            "bounds_low": bounds_low,
            "bounds_up": bounds_up,
            "iters": iters,
            "stopval": stopval,
            "ftol": ftol
        }

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

        # TODO: before exiting function, update form here!

        # exit like a champion
        return x_opt, loss_opt

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
        x = np.zeros(self.number_of_constraints())

        for index, ckey in self.index_constraint().items():
            constraint = self.constraints[ckey]
            x[index] = constraint.start_value(form)

        # print("x numpy", x, type(x))
        # print("x[0]", x[0], type(x[0]))

        # x = jnp.array(x, float)

        # print("x jax", x, type(x))
        # print("x[0]", x[0], type(x[0]))
        return x

    def optimization_bounds(self, form):
        """
        Creates optimization bounds array.
        Only one entry in the array per constraint.
        """
        bounds_low = np.zeros(self.number_of_constraints())
        bounds_up = np.zeros(self.number_of_constraints())

        for index, ckey in self.index_constraint().items():
            constraint = self.constraints[ckey]
            bounds_low[index] = constraint.bound_low(form)
            bounds_up[index] = constraint.bound_up(form)

        return bounds_low, bounds_up


# ------------------------------------------------------------------------------
# Updates
# ------------------------------------------------------------------------------

    def _update_form_root_nodes(self, x):
        """
        """
        map_xyz_index = {
            "x": 0,
            "y": 1,
            "z": 2
        }

        # print("x shape and size", x.shape, x.size)
        # x = np.squeeze(x).tolist()
        # if not isinstance(x, list):
        #     x = [x]

        for index, ckey in self.index_constraint().items():

            node = self.constraints[ckey].key()

            # TODO: weak check, needs to be handled differently
            if not isinstance(node, int):
                continue

            # TODO: this check should happen upon assembly, not at calculation?
            if not self.form.is_node_root(node):
                msg = "{} is not a root node. Assigned constraint is invalid!"
                raise ValueError(msg.format(node))

            # TODO: refactor to handle xyz more transparently
            xyz = self.form.node_xyz(key=node)
            constraint = self.constraints[ckey]
            j = map_xyz_index[constraint.attr_name()]
            xyz[j] = x[index]

            # self.form.node_xyz(key=node, xyz=xyz)  # form.node_xyz(node, y=x[])?
            self.form.node_attributes(key=node, names="xyz", values=xyz)

    def _update_form_edges(self, x):
        """
        """
        # TODO: this is duplicated
        # x = np.squeeze(x).tolist()
        # if not isinstance(x, list):
        #     x = [x]

        # breakpoint()

        for index, ckey in self.index_constraint().items():

            edge = self.constraints[ckey].key()

            # TODO: weak check, needs to be handled differently
            if isinstance(edge, int):
                continue

            if self.form.is_trail_edge(edge):
                name = "length"
            elif self.form.is_deviation_edge(edge):
                name = "force"

            value = x[index]

            self.form.edge_attribute(key=edge, name=name, value=value)


# ------------------------------------------------------------------------------
# Equilibrium
# ------------------------------------------------------------------------------

    def _update_form_equilibrium(self):
        """
        """
        force_equilibrium(self.form, kmax=100, eps=1e-5)


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

    def _compute_error(self, eq_state):
        """
        """
        error = 0.0
        for goal in self.goals.values():
            error += goal.error(eq_state)

        return error

    def _optimize_form(self, parameters, form):
        """
        """
        self.form = form

        self._update_form_root_nodes(parameters)
        self._update_form_edges(parameters)

        eq_state = form_equilibrate(form, kmax=100, eps=1e-5)
        error = self._compute_error(eq_state)

        form_update(self.form, **eq_state)

        self.form = None

        return error

    def _grad_optimize_form(self, parameters, form):
        """
        """
        self.form = form

        self._update_form_root_nodes(parameters)
        self._update_form_edges(parameters)

        eq_state = form_equilibrate_numpy(form, kmax=100, eps=1e-5)

        error = self._compute_error(eq_state)

        self.form = None

        return error

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
