from compas_cem.optimization.parameters import EdgeParameter


__all__ = ["TrailEdgeParameter"]


# ------------------------------------------------------------------------------
# Trail Edge Parameter
# ------------------------------------------------------------------------------


class TrailEdgeParameter(EdgeParameter):
    """
    Sets the length of a trail edge as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(TrailEdgeParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "length"

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
