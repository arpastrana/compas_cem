from compas.artists import Artist

from compas.plugins import plugin

from compas_cem.diagrams import TopologyDiagram
from compas_cem.diagrams import FormDiagram

from compas_cem.ghpython.artists import TopologyArtist
from compas_cem.ghpython.artists import FormArtist


@plugin(category="factories", requires=["Rhino"])
def register_artists():
    Artist.register(TopologyDiagram, TopologyArtist, context="Grasshopper")
    Artist.register(FormDiagram, FormArtist, context="Grasshopper")
