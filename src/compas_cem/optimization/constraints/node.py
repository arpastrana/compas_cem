from ast import literal_eval
from math import fabs

from compas_cem.optimization import Serializable


__all__ = [
    "RootNodeConstraintX",
    "RootNodeConstraintY",
    "RootNodeConstraintZ"
]

# ------------------------------------------------------------------------------
# Base Node Constraint
# ------------------------------------------------------------------------------

class NodeConstraint(Serializable):
    def __init__(self, key, bound_low, bound_up):
        self._key = key
        self._bound_up = bound_up
        self._bound_low = bound_low
        self._attr_name = None

    def key(self):
        """
        """
        return self._key

    def start_value(self, form):
        """
        """
        val = form.node_attribute(key=self.key(), name=self._attr_name)
        return val

    def bound_low(self, form):
        """
        """
        return self.start_value(form) - fabs(self._bound_low)

    def bound_up(self, form):
        """
        """
        return self.start_value(form) + fabs(self._bound_up)

    def attr_name(self):
        """
        """
        return self._attr_name

# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------

    @property
    def data(self):
        """
        A data dictionary that represents an ``NodeConstraint`` object.

        Returns
        -------
            data : ``dict``
            A dictionary that contains the following key-value pairs:

            * "key" : ``tuple``
            * "bound up" : ``float``
            * "bound low" : ``float``
            * "attr name" : ``str``
            
        Notes
        -----
        All dictionary keys are converted to their representation value
        (``repr(key)``) to ensure compatibility of all allowed key types with
        the JSON serialization format, which only allows for dict keys that are strings.
        """

        # TODO: Check serialization mechanism.

        data = {}

        data["key"] = repr(self._key)
        data["bound_up"] = self._bound_up
        data["bound_low"] = self._bound_low
        data["attr_name"] = self._attr_name
        data["datatype"] = self.datatype()

        return data
    
    @data.setter
    def data(self, data):
        """
        Overwrites this object's attributes with a data dictionary.

        Parameters
        ----------
        data : ``dict``
            A data dictionary.
        """
        self._key = int(data["key"])
        self._bound_up = float(data["bound_up"])
        self._bound_low = float(data["bound_low"])
        self._attr_name = str(data["attr_name"])

# ------------------------------------------------------------------------------
# Root Node Constraint on X
# ------------------------------------------------------------------------------

class RootNodeConstraintX(NodeConstraint):
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(RootNodeConstraintX, self).__init__(key, bound_low, bound_up)
        self._attr_name = "x"

# ------------------------------------------------------------------------------
# Root Node Constraint on Y
# ------------------------------------------------------------------------------

class RootNodeConstraintY(NodeConstraint):
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(RootNodeConstraintY, self).__init__(key, bound_low, bound_up)
        self._attr_name = "y"

# ------------------------------------------------------------------------------
# Root Node Constraint on Z
# ------------------------------------------------------------------------------

class RootNodeConstraintZ(NodeConstraint):
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(RootNodeConstraintZ, self).__init__(key, bound_low, bound_up)
        self._attr_name = "z"


if __name__ == "__main__":

    from time import time

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
    
    from compas_cem.equilibrium import force_equilibrium
    
    from compas_cem.plotters import FormPlotter


    # create a form diagram
    form = FormDiagram()

    # add nodes
    form.add_node(Node(0, [0.0, 0.0, 0.0]))
    form.add_node(Node(1, [1.0, 0.0, 0.0]))
    form.add_node(Node(2, [2.0, 0.0, 0.0]))
    form.add_node(Node(3, [3.0, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    form.add_edge(TrailEdge(0, 1, length=-1.0))
    form.add_edge(DeviationEdge(1, 2, force=-1.0))
    form.add_edge(TrailEdge(2, 3, length=-1.0))

    # add supports
    form.add_support(NodeSupport(0))
    form.add_support(NodeSupport(3))

    # add loads
    form.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    form.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    # calculate equilibrium
    force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

    # optimization
    optimizer = Optimizer()

    optimizer.add_constraint(RootNodeConstraintY(1, 1.0, 1.0))
    optimizer.add_constraint(DeviationEdgeConstraint((1, 2), 1.0, 1.0))
    optimizer.add_constraint(TrailEdgeConstraint((2, 3), 1.0, 1.0))
    
    point_a = Point(1.0, -0.5, 0.0)
    optimizer.add_goal((PointGoal(1, point_a)))

    point_b = Point(3.0, -0.707, 0.0)
    optimizer.add_goal((PointGoal(3, point_b)))
    
    # optimization settings
    start = time()
    algo = "LD_LBFGS"  # LN_BOBYQA, LD_LBFGS, LD_MMA
    iters = 100  # 100
    stopval = 1e-6 # 1e-4
    step_size = 1e-6  # 1e-4

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form, algo, iters, step_size, stopval)

    # print out results
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

    # plot
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_edges(text="force-length")
    plotter.draw_loads(scale=-0.25)
    plotter.draw_residuals(scale=0.10)
    plotter.show()

