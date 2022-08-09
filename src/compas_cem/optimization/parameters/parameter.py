from math import fabs

from compas_cem.data import Data


__all__ = ["Parameter"]

# ------------------------------------------------------------------------------
# Base Parameter
# ------------------------------------------------------------------------------


class Parameter(Data):
    """
    Parametrizer.
    """
    def __init__(self, key, bound_low, bound_up, **kwargs):
        super(Parameter, self).__init__(**kwargs)
        self._key = key
        self._bound_up = bound_up
        self._bound_low = bound_low
        self._attr_name = None

    def start_value(self, topology):
        """
        The initial value of the optimization parameter.
        """
        raise NotImplementedError

    def key(self):
        """
        The parameter key in the diagram.
        """
        return self._key

    def bound_low(self, topology):
        """
        The lower bound of the optimization parameter.

        Notes
        -----
        If not set to ``None`` at instantiation, the bound is calculated as the
        starting value of this parameter minus this absolute value of the lower bound.
        Otherwise, it will return ``float("-inf")``.
        """
        if self._bound_low is not None:
            return self.start_value(topology) - fabs(self._bound_low)
        return float("-inf")

    def bound_up(self, topology):
        """
        The upper bound of the edge optimization parameter.

        Notes
        -----
        If not set to ``None`` at instantiation, the bound is calculated as the
        starting value of this parameter plus this absolute value of the upper bound.
        Otherwise, it will return ``float("inf")``.
        """
        if self._bound_up is not None:
            return self.start_value(topology) + fabs(self._bound_up)
        return float("inf")

    def attr_name(self):
        """
        The name of the attribute in the diagram to parametrize.
        """
        return self._attr_name

    def __repr__(self):
        """
        """
        st = "{0}(key={1!r}, bound_low={2!r}, bound_up={3!r})"
        return st.format(self.__class__.__name__, self._key, self._bound_low, self._bound_up)
