from math import fabs


__all__ = [
    "TrailEdgeConstraint",
    "DeviationEdgeConstraint"
]


class EdgeConstraint(object):
    def __init__(self, key, bound_low, bound_up):
        self._key = key
        self._bound_up = fabs(bound_up)
        self._bound_low = fabs(bound_low)
        self._attr_name = None

    def key(self):
        """
        """
        return self._key
   
    def start_value(self, topology):
        """
        """
        val = topology.edge_attribute(key=self.key(), name=self._attr_name)
        return val

    def bound_low(self, topology):
        """
        """
        return self.start_value(topology) - self._bound_low

    def bound_up(self, topology):
        """
        """
        return self.start_value(topology) + self._bound_up


class TrailEdgeConstraint(EdgeConstraint):
    def __init__(self, key, bound_low, bound_up):
        super(TrailEdgeConstraint, self).__init__(key, bound_low, bound_up)
        self._attr_name = "length"


class DeviationEdgeConstraint(EdgeConstraint):
    def __init__(self, key, bound_low, bound_up):
        super(DeviationEdgeConstraint, self).__init__(key, bound_low, bound_up)
        self._attr_name = "force"

if __name__ == "__main__":
    pass
