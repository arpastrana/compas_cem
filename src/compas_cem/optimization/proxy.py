
__all__ = [
    "optimizer_solve_nlopt_proxy",
    "solve_nlopt_proxy"
]

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def optimizer_solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize):
    """
    A wrapper around ``Optimizer.solve_nlopt`` to be used with an ``rpc.Proxy``.
    """
    return solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize)


def solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize):
    """
    Deprecated version of ``optimizer_solve_nlopt_proxy``.
    """
    from compas_cem.optimization import Optimizer

    optimizer = Optimizer()
    optimizer.form = form

    # add goals
    for goal in goals:
        optimizer.add_goal(goal)
    
    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    x_opt, l_opt = optimizer.solve_nlopt(form, algorithm, kmax, stepsize, stopval)

    return form, x_opt, l_opt

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
