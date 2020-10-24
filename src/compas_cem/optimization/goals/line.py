from compas.geometry import closest_point_on_line
from compas.geometry import distance_point_point_sqrd

from compas_cem.optimization.goals import Goal


__all__ = [
    "LineGoal"
]


class LineGoal(Goal):
    """
    Pulls the xyz position of a node to a target line ray.
    """
    def __init__(self, node=None, line=None):
        super(LineGoal, self).__init__(node, line)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, form):
        """
        """
        self._ref_geo = form.node_xyz(self.key())
        line = self._target_geo
        self._target_point = closest_point_on_line(self._ref_geo, line)

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)


if __name__ == "__main__":
    
    from time import time

    from compas.geometry import Line
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
    from compas_cem.optimization import PointGoal
    
    from compas_cem.equilibrium import force_equilibrium
    
    from compas_cem.plotters import FormPlotter


    # create a form diagram
    form = FormDiagram()

    # add nodes
    form.add_node(Node(0, [0.0, 0.0, 0.0]))
    form.add_node(Node(1, [1.0, 0.0, 0.0]))
    form.add_node(Node(2, [2.0, 0.0, 0.0]))
    form.add_node(Node(3, [3.0, 0.0, 0.0]))
    form.add_node(Node(4, [4.0, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    form.add_edge(TrailEdge(0, 1, length=-1.0))
    form.add_edge(DeviationEdge(1, 2, force=-1.0))
    form.add_edge(TrailEdge(2, 3, length=-1.0))
    form.add_edge(TrailEdge(3, 4, length=-1.0))

    # add supports
    form.add_support(NodeSupport(0))
    form.add_support(NodeSupport(4))

    # add loads
    form.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    form.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    # calculate equilibrium
    force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

    # optimization
    optimizer = Optimizer()
    
    optimizer.add_constraint(DeviationEdgeConstraint((1, 2), 1.0, 1.0))
    optimizer.add_constraint(TrailEdgeConstraint((2, 3), 1.0, 1.0))
    optimizer.add_constraint(TrailEdgeConstraint((3, 4), 1.0, 1.0))

    point_a = Point(3.0, -0.707, 0.0)
    optimizer.add_goal((PointGoal(3, point_a)))
    
    line = Line([4.0, 0.0, 0.0], [4.0, 1.0, 0.0])
    optimizer.add_goal((LineGoal(4, line)))
    
    # optimization settings
    start = time()
    algo = "LD_LBFGS"  # LN_BOBYQA, LD_LBFGS, LD_MMA
    iters = 100  # 100
    stopval = 1e-6 # 1e-4
    step_size = 1e-6  # 1e-4

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form, algo, iters, step_size, stopval)

    # print out results
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

    # plot
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_edges(text="force-length")
    plotter.draw_loads(scale=-0.25)
    plotter.draw_residuals(scale=0.10)
    plotter.show()
