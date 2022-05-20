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
