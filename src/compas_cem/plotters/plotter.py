from compas_plotters import Plotter


__all__ = ["Plotter"]


class Plotter(Plotter):
    """
    A thin wrapper on the :class:`compas_plotters.plotter.Plotter`.

    This object exists only for API consistency with `compas_cem.viewers.Viewer`.
    """
    def __init__(self, *args, **kwargs):
        super(Plotter, self).__init__(*args, **kwargs)
