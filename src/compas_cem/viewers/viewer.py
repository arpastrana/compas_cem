from compas_view2.app import App

from compas_cem.diagrams import FormDiagram
from compas_cem.diagrams import TopologyDiagram


__all__ = ["Viewer"]


class Viewer(App):
    """
    A thin wrapper on the :class:`compas_view2.app.App`.

    The intention is to facilitate some operations specific to CEM, such as
    registering the diagram objects, and adding the viewer itself as an attribute
    of the objects.
    """
    def __init__(self, *args, **kwargs):
        super(Viewer, self).__init__(*args, **kwargs)

    def add(self, data, **kwargs):
        """
        Add a COMPAS data object to the viewer.

        It adds a viewer argument if the object is a :class:`compas_cem.diagrams.FormDiagram`
        or a :class:`compas_cem.diagrams.TopologyDiagram`.

        Parameters
        ----------
        data: :class:`compas.geometry.Primitive` | :class:`compas.geometry.Shape` | :class:`compas.datastructures.Datastructure`
            A COMPAS data object.
        **kwargs : dict, optional
            Additional visualization options.

        Returns
        -------
        view_data :class:`compas_view2.objects.Object`
            A visualization object.
        """
        if isinstance(data, (FormDiagram, TopologyDiagram)):
            kwargs = kwargs or {}
            kwargs["viewer"] = self
        return super(Viewer, self).add(data, **kwargs)
