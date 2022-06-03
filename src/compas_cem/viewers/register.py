from compas_view2.objects import Object

from compas_cem.diagrams import TopologyDiagram
from compas_cem.diagrams import FormDiagram

from compas_cem.viewers import TopologyDiagramObject
from compas_cem.viewers import FormDiagramObject


def register_objects():
    Object.register(TopologyDiagram, TopologyDiagramObject)
    Object.register(FormDiagram, FormDiagramObject)
