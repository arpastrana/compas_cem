"""
The settings of the auxiliary trails that Grasshopper adds to a topology diagram.
"""

from dataclasses import dataclass
from math import copysign

from compas.geometry import length_vector

__all__ = ["AuxiliaryTrailSettings"]


@dataclass(frozen=True)
class AuxiliaryTrailSettings:
    """
    The length, state and direction of every auxiliary trail in a topology.

    Parameters
    ----------
    length :
        The length of every auxiliary trail edge.
    state :
        The sign of the force in every auxiliary trail edge: positive for
        tension, negative for compression.
    vector :
        The direction from a node to its auxiliary support in the topology.

    Notes
    -----
    The settings are a dataclass rather than a named tuple, because Grasshopper
    unpacks a tuple output into its items. The vector places the auxiliary
    supports in the topology only: the solver places each one along the
    residual force of its node, and the state decides on which side.
    """

    length: float = 1.0
    state: float = -1.0
    vector: tuple[float, float, float] = (-1.0, -1.0, -1.0)

    def __post_init__(self):
        if not self.length > 0.0:
            template = "The length must be positive, got {}."
            message = template.format(self.length)
            raise ValueError(message)
        if self.state == 0.0:
            message = "The state must be nonzero: positive for tension, negative for compression."
            raise ValueError(message)
        if length_vector(self.vector) == 0.0:
            message = "The vector must be nonzero."
            raise ValueError(message)

    @property
    def signed_length(self) -> float:
        """
        The length of every auxiliary trail edge, signed by its state.
        """
        signed_length = copysign(self.length, self.state)

        return signed_length
