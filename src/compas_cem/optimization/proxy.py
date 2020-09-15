
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
    return self_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize)


def solve_nlopt_proxy(form, goals, constraints, algorithm, kmax, stopval, stepsize):
    """
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

    optimizer.solve_nlopt(form, algorithm, kmax, stopval, stepsize)

    return form

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
