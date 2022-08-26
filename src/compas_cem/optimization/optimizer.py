from time import time

from functools import partial

import autograd.numpy as np

from autograd import grad as agrad

from compas_cem.data import Data

from compas_cem.equilibrium import static_equilibrium
from compas_cem.equilibrium.force_numpy import equilibrium_state_numpy

from compas_cem.optimization import grad_autograd
from compas_cem.optimization import grad_finite_differences
from compas_cem.optimization import objective_function_numpy
from compas_cem.optimization import nlopt_solver
from compas_cem.optimization import nlopt_status

from compas_cem.optimization.parameters import EdgeParameter
from compas_cem.optimization.parameters import NodeParameter

from nlopt import RoundoffLimited


__all__ = ["Optimizer"]

# ------------------------------------------------------------------------------
# Optimizer
# ------------------------------------------------------------------------------


class Optimizer(Data):
    """
    An object that modifies a form diagram to meet multiple constraints.
    """
    def __init__(self, **kwargs):
        super(Optimizer, self).__init__(**kwargs)

        self.parameters = dict()
        self.constraints = dict()

        self.x_opt = None
        self.time_opt = None
        self.penalty = None
        self.evals = None
        self.gradient_norm = None
        self.status = None

        self._ckey = -1
        self._pkey = -1

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
# Parameters
# ------------------------------------------------------------------------------

    def add_parameter(self, parameter):
        """
        Adds a parameter to the optimization problem.
        """
        self._pkey += 1
        self.parameters[self._pkey] = parameter

    def remove_parameter(self, pkey):
        """
        Removes an optimization parameter.
        """
        if pkey not in self.parameters:
            raise KeyError("Parameter not found at object key: {}".format(pkey))
        del self.parameters[pkey]

# ------------------------------------------------------------------------------
# Constraints
# ------------------------------------------------------------------------------

    def add_constraint(self, constraint):
        """
        Adds a goal constraint.
        """
        self._ckey += 1
        self.constraints[self._ckey] = constraint

    def remove_constraint(self, ckey):
        """
        Removes a constraint from the optimizer.
        """
        if ckey not in self.constraints:
            raise KeyError("Constraints not found on object key: {}".format(ckey))
        del self.constraints[ckey]

# ------------------------------------------------------------------------------
# Objective Function
# ------------------------------------------------------------------------------

    def objective_func(self, topology, grad_func, tmax, eta):
        """
        The objective function to minimize.
        """
        f = objective_function_numpy
        x_func = partial(self._optimize_form, topology=topology, tmax=tmax, eta=eta)
        return partial(f, x_func=x_func, grad_func=grad_func)

# ------------------------------------------------------------------------------
# Gradient Function
# ------------------------------------------------------------------------------

    def gradient_func(self, grad_f, topology, tmax, eta, step_size):
        """
        The objective function to calculate gradients from.
        """
        x_func = partial(self._optimize_form, topology=topology, tmax=tmax, eta=eta)
        return partial(grad_f, x_func=x_func, step_size=step_size)

# ---------------------- --------------------------------------------------------
# Solver
# ------------------------------------------------------------------------------

    def solve(self, topology, algorithm="SLSQP", grad="AD", step_size=1e-6, iters=100, eps=1e-6, kappa=1e-8, tmax=100, eta=1e-6, verbose=False):
        """
        Solve a constrained form-finding problem using gradient-based optimization.

        Parameters
        ----------
        topology : :class:`compas_cem.diagrams.TopologyDiagram`
            A topology diagram.
        algorithm : ``str``, optional
            The name of the gradient-based local optimization algorithm to use.
            Only the following local gradient-based optimization algorithms are supported:

            - SLSQP: Sequential Least Squares Programming
            - LBFGS: Low-Storage Broyden-Fletcher-Goldfarb-Shanno
            - MMA: Method of Moving Asymptotes
            - TNEWTON: Preconditioned Truncated Newton
            - AUGLAG: Augmented Lagrangian
            - VAR: Limited-Memory Variable-Metric Algorithm

            Defaults to "SLSQP".
            Refer to the NLopt `documentation <https://nlopt.readthedocs.io/en/latest/>`_ for more details on their theoretical underpinnings.
        grad : ``str``, optional
            The method to compute the gradient of the objective function.
            The currently available methods are:

            - AD: Automatic differentiation
            - FD: Finite differences

            Defaults to "AD".
        iters : ``int``, optional
            The maximum number of iterations to run the optimization algorithm for.
            Defaults to ``100``.
        eps : ``float``, optional
            The convergence threshold for the output value of the objective function.
            Defaults to ``1e-6``.
        kappa : ``float``, optional
            The convergence threshold for the norm of the gradient of the objective function.
            Defaults to ``1e-8``.
        step_size : ``float``, optional
            The step size to calculate the gradient of the objective function via finite differences.
            It becomes active only if ``grad="FD"``. It is otherwise ignored by this function.
            Defaults to ``1e-3``.
        tmax : ``int``, optional
            The maximum number of iterations the CEM form-finding algorithm will run for.
            If ``eta`` is hit first, the form-finding algorithm will stop early.
            Defaults to ``100``.
        eta : ``float``, optional
            The numerical converge threshold of the CEM form-finding algorithm.
            If ``tmax`` is hit first, the form-finding algorithm will stop early.
            Defaults to ``1e-6``.
        verbose : ``bool``, optional
            A flag to prints statistics of the optimization process.
            Defaults to ``True``.

        Returns
        -------
        form : :class:`compas_cem.diagrams.FormDiagram`
            A form diagram.
        """
        if verbose:
            print("----------")
            print("Optimization with {} started!".format(algorithm))
            print(f"# Parameters: {self.number_of_parameters()}, # Constraints {self.number_of_constraints()}")

        # test for bad stuff before going any further
        self.check_optimization_sanity()

        # compose gradient and objective functions
        if grad not in ("AD", "FD"):
            raise ValueError(f"Gradient method {grad} is not supported!")
        if grad == "AD":
            if verbose:
                print("Computing gradients using automatic differentiation!")
            x_func = partial(self._optimize_form, topology=topology.copy(), tmax=tmax, eta=eta)
            grad_func = partial(grad_autograd, grad_func=agrad(x_func))  # x, grad, x_func

        elif grad == "FD":
            if verbose:
                print(f"Warning: Calculating gradients using finite differences with step size {step_size}. This may take a while...")
            grad_func = self.gradient_func(grad_finite_differences, topology.copy(), tmax, eta, step_size)

        # grad_func = self.gradient_func(grad_func, topology.copy(), tmax, eta, step_size)
        obj_func = self.objective_func(topology, grad_func, tmax, eta)

        # generate optimization variables
        x = self.optimization_parameters(topology)

        # extract the lower and upper bounds to optimization variables
        bounds_low, bounds_up = self.optimization_bounds(topology)

        # stack keyword arguments
        hyper_parameters = {"f": obj_func,
                            "algorithm": algorithm,
                            "dims": self.number_of_parameters(),
                            "bounds_low": bounds_low,
                            "bounds_up": bounds_up,
                            "iters": iters,
                            "eps": eps,
                            "ftol": kappa}

        # assemble optimization solver
        solver = nlopt_solver(**hyper_parameters)

        # solve optimization problem
        x_opt = None
        start = time()
        try:
            x_opt = solver.optimize(x)
            if verbose:
                print("Optimization ended correctly!")
        except RoundoffLimited:
            print("Optimization was halted because roundoff errors limited progress")
            print("Results may still be useful though!")
            x_opt = self.optimization_parameters(topology)
        except RuntimeError:
            print("Optimization failed for reasons I do not understand yet...")
            print(f"Optimization total runtime: {round(time() - start, 4)} seconds")
            return static_equilibrium(topology)

        # fetch last optimum value of loss function
        time_opt = time() - start
        loss_opt = solver.last_optimum_value()
        evals = solver.get_numevals()
        status = nlopt_status(solver.last_optimize_result())

        # set optimizer attributes
        self.time_opt = time_opt
        self.x_opt = x_opt
        self.penalty = loss_opt
        self.evals = evals
        self.status = status

        # set norm of the gradient
        # NOTE: np.zeros is a dummy array (signature requirement set by nlopt)
        self.gradient = grad_func(x_opt, np.zeros(x_opt.size))
        self.gradient_norm = np.linalg.norm(self.gradient)

        if verbose:
            print(f"Optimization total runtime: {round(time_opt, 6)} seconds")
            print("Number of evaluations incurred: {}".format(evals))
            print(f"Final value of the objective function: {round(loss_opt, 6)}")
            print(f"Norm of the gradient of the objective function: {round(self.gradient_norm, 6)}")
            print(f"Optimization status: {status}".format(status))
            print("----------")

        # exit like a champion
        return static_equilibrium(topology)

# ------------------------------------------------------------------------------
# Optimization parameters
# ------------------------------------------------------------------------------

    def optimization_parameters(self, topology):
        """
        Creates optimization paremeters array.
        Only one entry in the array per constraint.
        Takes care of keeping the ordering.
        """
        parameters = np.zeros(self.number_of_parameters())

        for pkey, parameter in self.parameters.items():
            parameters[pkey] = parameter.start_value(topology)

        return parameters

    def optimization_bounds(self, topology):
        """
        Creates optimization bounds array.
        Only one entry in the array per constraint.
        """
        bounds_low = np.zeros(self.number_of_parameters())
        bounds_up = np.zeros(self.number_of_parameters())

        for pkey, parameter in self.parameters.items():
            bounds_low[pkey] = parameter.bound_low(topology)
            bounds_up[pkey] = parameter.bound_up(topology)

        return bounds_low, bounds_up

# ------------------------------------------------------------------------------
# Updates
# ------------------------------------------------------------------------------

    def _update_parameters(self, topology, parameters):
        """
        Update the defined design parameters in a topology diagram.
        """
        for pkey, parameter in self.parameters.items():

            value = parameters[pkey]
            name = parameter.attr_name()
            key = parameter.key()

            if isinstance(parameter, NodeParameter):
                topology.node_attribute(key=key, name=name, value=value)
            elif isinstance(parameter, EdgeParameter):
                topology.edge_attribute(key=key, name=name, value=value)
            else:
                msg = "Parameter {} is neither a node nor an edge parameter! {}"
                raise TypeError(msg.format(type(parameter)))

# ------------------------------------------------------------------------------
# Penalty function
# ------------------------------------------------------------------------------

    def _calculate_penalty(self, eq_state):
        """
        """
        penalty = 0.0
        for constraint in self.constraints.values():
            penalty += constraint.penalty(eq_state)

        return penalty

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

    def _optimize_form(self, parameters, topology, tmax, eta):
        """
        """
        self._update_parameters(topology, parameters)

        eq_state = equilibrium_state_numpy(topology, tmax, eta)

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
# Magic methods
# ------------------------------------------------------------------------------

    def __repr__(self):
        """
        """
        tpl = "{} with {} parameters and {} constraints. Status: {}"
        return tpl.format(self.__class__.__name__, self.number_of_parameters(), self.number_of_constraints(), self.status)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
