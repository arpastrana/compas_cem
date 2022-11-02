import autograd.numpy as np

from compas_cem.equilibrium import EquilibriumState
from compas_cem.equilibrium import EquilibriumStructure


class EquilibriumModel:
    """
    An equilibrium model that implements the combinatorial equilibrium modeling (CEM) framework.

    Parameters
    ----------
    topology : `compas_cem.diagrams.TopologyDiagram`
        A valid topology diagram.
    """
    def __init__(self, topology):
        self.topology = topology
        self.structure = EquilibriumStructure(topology)

    def __call__(self, xyz, forces, lengths, loads):
        """
        Compute an equilibrium state.
        The computation follows the combinatorial equilibrium modeling (CEM) form-finding algorithm.
        """
        topology = self.topology
        n_seq = topology.number_of_sequences()

        pi = xyz
        th = np.zeros((n_seq, 3))

        for k in topology.sequences():
            d = None
            tk = th - d[k] - loads[k]
            pj = pi + forces[k] * tk / np.linalg.norm(tk)
            pi = pj

        r = tk

        return EquilibriumState()
