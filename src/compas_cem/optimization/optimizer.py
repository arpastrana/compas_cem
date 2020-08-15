from nlopt import opt
from nlopt import LN_BOBYQA


__all__ = [
    "optimize_topology"
]


def optimize_topology():
    """
    """
    algo = LN_BOBYQA
    solver = opt(algo, 10)
    print("hello world!")

if __name__ == "__main__":
    pass

"""
db0_T = O.relativeTolerance
int0_I = O.maxIterations
nl0_Algo = dc_Algo["algo_name"]


# Optimization function
def Optimization(
    db1_InitialValues,
    db1_BoundUp,
    db1_BoundLow,
    db0_T, - ok
    int0_I, - ok
    nl0_Algo - ok
    ):

    # solver = opt(algo, length(initial_values))
    # solver.set_xtol_rel(tolerance)
    # solver.set_maxeval(max_iterations)
    solver = nl.NLoptSolver(nl0_Algo, len(db1_InitialValues), db0_T, int0_I)

    # solver.set_lower_bounds(lb)
    solver.SetLowerBounds(Array[float]( db1_BoundLow ))  
    
    # solver.set_upper_bounds(ub)
    solver.SetUpperBounds(Array[float]( db1_BoundUp ))  

    # solver.set_min_objective(grad)
    solver.SetMinObjective.Overloads[Func[Array[float], Array[float], float]](Grad)

    initialValue = Array[float](db1_InitialValues)

    # xopt = solver.optimize(initial_values)
    # opt_val = opt.last_optimum_value()
    # result = solver.last_optimize_result()

    out, finalScore = solver.Optimize(initialValue)
    return finalScore

dc1_Algo = {"LD_SLSQP" : nl.NLoptAlgorithm.LD_SLSQP,
            "LN_BOBYQA" : nl.NLoptAlgorithm.LN_BOBYQA,
            "GD_MLSL" : nl.NLoptAlgorithm.GD_MLSL,
            "LD_LBFGS" : nl.NLoptAlgorithm.LD_LBFGS,
            "LD_AUGLAG" : nl.NLoptAlgorithm.LD_AUGLAG,
            "LN_SBPLX" : nl.NLoptAlgorithm.LN_SBPLX,
            "LN_COBYLA" : nl.NLoptAlgorithm.LN_COBYLA,
            "LD_TNEWTON" : nl.NLoptAlgorithm.LD_TNEWTON,
            "GN_ISRES" : nl.NLoptAlgorithm.GN_ISRES,
            "GN_MLSL" : nl.NLoptAlgorithm.GN_MLSL}
"""