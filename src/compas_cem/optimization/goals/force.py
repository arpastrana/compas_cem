from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd


__all__ = [
    "TrailEdgeForceGoal",
    "NodeResidualGoal"
]


class TrailEdgeForceGoal(Goal):
    """
    Make a trail edge reach a target force value.
    """
    def __init__(self, edge=None, force=None):
        # TODO: needs different serialization mechanism
        super(TrailEdgeForceGoal, self).__init__(edge, force)

    def target_geometry(self):
        """
        """
        return self._target_geo

    def update(self, form):
        """
        """
        u, v = self.key()
        self._ref_geo = form.edge_force((u, v))
        
    def error(self):
        """
        """
        diff = self.reference_geometry() - self.target_geometry()
        return diff * diff


class NodeResidualGoal(Goal):
    """
    Makes the residual force at a node match a target residual vector.
    """
    def __init__(self, node=None, residual_vector=None):
        super(NodeResidualGoal, self).__init__(node, residual_vector)

    def update(self, form):
        """
        """
        self._ref_geo = form.node_residual(self.key())

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)


if __name__ == "__main__":

    from time import time
    from math import fabs

    from compas.geometry import Point

    from compas_cem.diagrams import FormDiagram
    
    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge
    from compas_cem.elements import DeviationEdge
    
    from compas_cem.loads import NodeLoad
    
    from compas_cem.supports import NodeSupport
    
    from compas_cem.optimization import Optimizer
    from compas_cem.optimization import DeviationEdgeConstraint
    from compas_cem.optimization import TrailEdgeConstraint
    
    from compas_cem.optimization import RootNodeConstraintY
    
    from compas_cem.optimization import PointGoal
    from compas_cem.optimization import TrailEdgeForceGoal
    
    from compas_cem.equilibrium import force_equilibrium
    
    from compas_cem.plotters import FormPlotter


    # create a form diagram
    form = FormDiagram()

    # add nodes
    form.add_node(Node(0, [0.0, 0.0, 0.0]))
    form.add_node(Node(1, [1.0, 0.0, 0.0]))
    form.add_node(Node(2, [2.0, 0.0, 0.0]))
    form.add_node(Node(3, [0.0, 1.0, 0.0]))
    form.add_node(Node(4, [1.0, 1.0, 0.0]))
    form.add_node(Node(5, [2.0, 1.0, 0.0]))
    
    # add edges with negative values for a compression-only structure
    form.add_edge(TrailEdge(0, 3, length=-1.0))
    form.add_edge(TrailEdge(1, 4, length=-1.0))
    form.add_edge(TrailEdge(2, 5, length=-1.0))
    
    form.add_edge(DeviationEdge(3, 4, force=-1.0))
    form.add_edge(DeviationEdge(4, 5, force=-1.0))

    # add supports
    form.add_support(NodeSupport(0))
    form.add_support(NodeSupport(1))
    form.add_support(NodeSupport(2))

    # add loads
    form.add_load(NodeLoad(4, [0.0, -1.0, 0.0]))

    # calculate equilibrium
    force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

    # optimization
    optimizer = Optimizer()

    # root node constraints
    optimizer.add_constraint(RootNodeConstraintY(3, 1.0, 1.0))
    optimizer.add_constraint(RootNodeConstraintY(4, 1.0, 1.0))
    # optimizer.add_constraint(RootNodeConstraintY(5, 1.0, 1.0))

    # deviation edge constraints 
    optimizer.add_constraint(DeviationEdgeConstraint((3, 4), 1.0, 1.0))
    optimizer.add_constraint(DeviationEdgeConstraint((4, 5), 1.0, 1.0))
    
    # goals
    point_a = Point(0.0, 1.5, 0.0)
    optimizer.add_goal((PointGoal(3, point_a)))
    optimizer.add_goal(TrailEdgeForceGoal((1, 4), 0.0))
    optimizer.add_goal(NodeResidualGoal(1, [0.0, 0.0, 0.0]))
    
    # optimization settings
    start = time()
    algo = "LD_LBFGS"  # LN_BOBYQA, LD_LBFGS, LD_MMA
    iters = 100  # 100
    stopval = 1e-6 # 1e-4
    step_size = 1e-6  # 1e-4

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form, algo, iters, step_size, stopval)

    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

    # plot
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_loads(scale=-0.25)
    plotter.draw_residuals(scale=1.0)
    plotter.draw_edges(text="force")
    plotter.show() 
