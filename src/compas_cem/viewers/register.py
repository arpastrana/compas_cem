from compas_view2.objects import Object

from compas_cem.diagrams import FormDiagram
from compas_cem.diagrams import TopologyDiagram
from compas_cem.viewers import FormDiagramObject
from compas_cem.viewers import TopologyDiagramObject


def register_objects():
    Object.register(TopologyDiagram, TopologyDiagramObject)
    Object.register(FormDiagram, FormDiagramObject)
