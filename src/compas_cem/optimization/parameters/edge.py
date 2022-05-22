from ast import literal_eval
from math import fabs

from compas_cem.optimization.parameters import Parameter


__all__ = ["TrailEdgeParameter",
           "DeviationEdgeParameter"]

# ------------------------------------------------------------------------------
# Base Edge Parameter
# ------------------------------------------------------------------------------


class EdgeParameter(Parameter):
    """
    Parametrize and edge to solve an optimization problem.
    """
    def __init__(self, key, bound_low, bound_up, **kwargs):
        super(EdgeParameter, self).__init__(key, bound_low, bound_up, **kwargs)

    def key(self):
        """
        The edge key.
        """
        return self._key

    def start_value(self, topology):
        """
        The initial value of the edge optimization parameter.
        """
        val = topology.edge_attribute(key=self.key(), name=self._attr_name)
        return val

    def bound_low(self, topology):
        """
        The lower bound of the edge optimization parameter.

        Notes
        -----
        Calculated as the initial parameter minus this bound's absolute value.
        """
        return self.start_value(topology) - fabs(self._bound_low)

    def bound_up(self, topology):
        """
        The upper bound of the edge optimization parameter.

        Notes
        -----
        Calculated as the initial parameter plus this bound's absolute value.
        """
        return self.start_value(topology) + fabs(self._bound_up)

    def attr_name(self):
        """
        The name of the edge attribute to parametrize.
        """
        return self._attr_name

    def __repr__(self):
        """
        """
        st = "{0}(key={1!r}, bound_low={2!r}, bound_up={3!r})"
        return st.format(self.__class__.__name__, self._key, self._bound_low, self._bound_up)

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
            * "datatype" : ``str``

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
