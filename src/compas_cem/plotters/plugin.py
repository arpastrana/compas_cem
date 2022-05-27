from compas.artists import Artist

from compas.plugins import plugin

from compas_cem.diagrams import TopologyDiagram
from compas_cem.diagrams import FormDiagram

from compas_cem.plotters import TopologyArtist
from compas_cem.plotters import FormArtist


@plugin(category="factories")
def register_artists():
    Artist.register(TopologyDiagram, TopologyArtist, context="Plotter")
    Artist.register(FormDiagram, FormArtist, context="Plotter")
