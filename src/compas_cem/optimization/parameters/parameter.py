from math import fabs

from compas_cem.data import Data

__all__ = ["Parameter"]

# ------------------------------------------------------------------------------
# Base Parameter
# ------------------------------------------------------------------------------


class Parameter(Data):
    """
    A node or edge attribute that an optimizer varies.

    Parameters
    ----------
    key :
        The key of the node or edge to parametrize.
    bound_low :
        The lower bound. ``None`` leaves the parameter unbounded from below.
    bound_up :
        The upper bound. ``None`` leaves the parameter unbounded from above.
    is_absolute :
        If ``True``, the bounds are the values the parameter may take. Otherwise,
        each bound is a distance from the start value, and its sign is ignored.
    """

    def __init__(
        self, key=None, bound_low=None, bound_up=None, is_absolute=False, **kwargs
    ):
        super(Parameter, self).__init__(**kwargs)
        self._key = key
        self._bound_up = bound_up
        self._bound_low = bound_low
        self._is_absolute = is_absolute
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
        An absolute bound is returned as given. A relative bound is subtracted
        from the start value, sign ignored. Without a bound, it returns
        ``float("-inf")``.
        """
        if self._bound_low is None:
            return float("-inf")
        if self._is_absolute:
            return self._bound_low
        return self.start_value(topology) - fabs(self._bound_low)

    def bound_up(self, topology):
        """
        The upper bound of the optimization parameter.

        Notes
        -----
        An absolute bound is returned as given. A relative bound is added to the
        start value, sign ignored. Without a bound, it returns ``float("inf")``.
        """
        if self._bound_up is None:
            return float("inf")
        if self._is_absolute:
            return self._bound_up
        return self.start_value(topology) + fabs(self._bound_up)

    def attr_name(self):
        """
        The name of the attribute in the diagram to parametrize.
        """
        return self._attr_name

    def __repr__(self):
        """ """
        st = "{0}(key={1!r}, bound_low={2!r}, bound_up={3!r}, is_absolute={4!r})"
        return st.format(
            self.__class__.__name__,
            self._key,
            self._bound_low,
            self._bound_up,
            self._is_absolute,
        )
