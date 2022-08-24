from compas_cem.optimization.parameters import EdgeParameter


__all__ = ["DeviationEdgeParameter"]


# ------------------------------------------------------------------------------
# Deviation Edge Parameter
# ------------------------------------------------------------------------------


class DeviationEdgeParameter(EdgeParameter):
    """
    Sets the force of a deviation edge as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(DeviationEdgeParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "force"

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
