from typing import NamedTuple

import jax.numpy as jnp


__all__ = ["EquilibriumState"]


class EquilibriumState(NamedTuple):
    xyz : jnp.array  # N x 3
    reaction_forces: jnp.array  # N x 3
    lengths: jnp.array  # M x 1
    forces: jnp.array  # M x 1
