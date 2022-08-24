from ast import literal_eval

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

    def start_value(self, topology):
        """
        The initial value of the edge optimization parameter.
        """
        val = topology.edge_attribute(key=self.key(), name=self._attr_name)
        return val

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

        data["_key"] = repr(self._key)
        data["_bound_up"] = self._bound_up
        data["_bound_low"] = self._bound_low
        data["_attr_name"] = self._attr_name

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
        self._key = tuple(literal_eval(data["_key"]))
        self._attr_name = str(data["_attr_name"])

        for bound_name in ["_bound_up", "_bound_low"]:
            bound = data[bound_name]
            if bound is not None:
                bound = float(bound)
            setattr(self, bound_name, bound)


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
