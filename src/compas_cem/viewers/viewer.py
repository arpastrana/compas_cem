from compas_viewer import Viewer

__all__ = ["Viewer"]


class Viewer(Viewer):
    """
    A thin wrapper on the `compas_viewer.Viewer`.

    This object exists only for API consistency with `compas_cem.plotters.Plotter`.
    """

    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__(*args, **kwargs)
