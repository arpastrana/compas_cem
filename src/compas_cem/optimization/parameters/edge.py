from ast import literal_eval

from compas_cem.optimization.parameters import Parameter

__all__ = ["EdgeParameter"]

# ------------------------------------------------------------------------------
# Base Edge Parameter
# ------------------------------------------------------------------------------


class EdgeParameter(Parameter):
    """
    Parametrize and edge to solve an optimization problem.
    """

    def __init__(self, key=None, bound_low=None, bound_up=None, **kwargs):
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
    def __data__(self):
        """
        A data dictionary that represents an edge parameter.

        Notes
        -----
        The edge key is stored as its representation, because JSON allows only
        strings as dictionary keys and the key here is a pair of node keys.
        """
        data = {}

        data["_key"] = repr(self._key)
        data["_bound_up"] = self._bound_up
        data["_bound_low"] = self._bound_low
        data["_attr_name"] = self._attr_name

        return data

    @classmethod
    def __from_data__(cls, data):
        """
        Construct an edge parameter from a data dictionary.

        Parameters
        ----------
        data :
            A data dictionary.

        Returns
        -------
        parameter :
            An edge parameter object.
        """
        parameter = cls()
        parameter._key = tuple(literal_eval(data["_key"]))
        parameter._attr_name = str(data["_attr_name"])

        for bound_name in ["_bound_up", "_bound_low"]:
            bound = data[bound_name]
            if bound is not None:
                bound = float(bound)
            setattr(parameter, bound_name, bound)

        return parameter
