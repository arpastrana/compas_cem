from compas.data import Data

from compas_cem.data import Serializable


__all__ = ["Data"]


# ==============================================================================
# Grasshopper data base class
# ==============================================================================

class GHData(object):
    """
    Base class for objects that are interoperable with Rhino/Grasshopper.
    """
    def ToString(self):
        """
        Show object representation as string in Rhino/Grasshopper.
        """
        return self.__repr__()

# ==============================================================================
# Data base class
# ==============================================================================

class Data(Data, GHData, Serializable):
    """
    """
    def __init__(self, **kwargs):
        super(Data, self).__init__(**kwargs)

