
__all__ = [
    "solve_nlopt_proxy"
]

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def solve_nlopt_proxy(topology, goals, constraints, algorithm, kmax, stopval, stepsize):
    """
    """
    from compas_cem.optimization import Optimizer

    optimizer = Optimizer()
    optimizer.topology = topology

    # add goals
    for goal in goals:
        optimizer.add_goal(goal)
    
    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    optimizer.solve_nlopt(topology, algorithm, kmax, stopval, stepsize)

    return topology

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
