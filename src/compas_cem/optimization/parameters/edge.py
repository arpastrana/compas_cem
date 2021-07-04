from ast import literal_eval
from math import fabs

from compas_cem.optimization import Serializable


__all__ = ["TrailEdgeParameter",
           "DeviationEdgeParameter"]

# ------------------------------------------------------------------------------
# Base Edge Parameter
# ------------------------------------------------------------------------------


class EdgeParameter(Serializable):
    """
    Parametrize and edge to solve an optimization problem.
    """
    def __init__(self, key, bound_low, bound_up):
        self._key = key
        self._bound_up = bound_up
        self._bound_low = bound_low
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
        return self.start_value(topology) - fabs(self._bound_low)

    def bound_up(self, topology):
        """
        """
        return self.start_value(topology) + fabs(self._bound_up)

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
        A data dictionary that represents an ``EdgeParameter`` object.

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
        self._key = tuple(literal_eval(data["key"]))
        self._bound_up = float(data["bound_up"])
        self._bound_low = float(data["bound_low"])
        self._attr_name = str(data["attr_name"])

# ------------------------------------------------------------------------------
# Trail Edge Parameter
# ------------------------------------------------------------------------------


class TrailEdgeParameter(EdgeParameter):
    """
    Sets the length of a trail edge as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(TrailEdgeParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "length"

# ------------------------------------------------------------------------------
# Deviation Edge Parameter
# ------------------------------------------------------------------------------


class DeviationEdgeParameter(EdgeParameter):
    """
    Sets the force of a deviation edge as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(DeviationEdgeParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "force"

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
