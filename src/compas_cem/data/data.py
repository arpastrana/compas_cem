from compas.data import Data

__all__ = ["Data"]


# ==============================================================================
# Data base class
# ==============================================================================


class Data(Data):
    """
    The base class every serializable COMPAS CEM object inherits from.

    Notes
    -----
    This exists as a single seam over the COMPAS base class, so the package can
    change what all of its serializable objects share without touching each one.
    """

    def __init__(self, **kwargs):
        super(Data, self).__init__(**kwargs)
