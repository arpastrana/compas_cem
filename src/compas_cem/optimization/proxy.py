from time import time


__all__ = ["optimizer_solve_nlopt_proxy", "solve_nlopt_proxy"]


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def optimizer_solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize):
    """
    A wrapper around ``Optimizer.solve_nlopt`` to be used with an ``rpc.Proxy``.
    """
    return solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize, "autodiff")


def solve_nlopt_proxy(form, goals, constraints, algorithm, iters, step_size, stop_val, mode):
    """
    Deprecated version of ``optimizer_solve_nlopt_proxy``.
    """
    from compas_cem.optimization import Optimizer

    optimizer = Optimizer()
    # optimizer.form = form

    # add goalso
    for goal in goals:
        optimizer.add_goal(goal)

    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    hyper_parameters = {"form": form,
                        "algorithm": algorithm,
                        "iters": iters,
                        "step_size": step_size,
                        "stop_val": stop_val,
                        "mode": mode
                        }

    start = time()
    x_opt, l_opt, evals = optimizer.solve_nlopt(**hyper_parameters)
    duration = time() - start

    return form, x_opt, l_opt, evals, duration

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
