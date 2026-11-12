import pytest
from compas.data import json_dumps
from compas.data import json_loads

from compas_cem.optimization import Optimizer
from compas_cem.optimization import PointGoal
from compas_cem.optimization import TrailEdgeParameter

# ==============================================================================
# Tests
# ==============================================================================


def test_relative_bounds_offset_start(compression_strut):
    """
    Checks that relative bounds are distances from the start value, sign ignored.
    """
    parameter = TrailEdgeParameter((0, 1), bound_low=-1.0, bound_up=2.0)

    assert parameter.bound_low(compression_strut) == -2.0
    assert parameter.bound_up(compression_strut) == 1.0


def test_absolute_bounds_as_given(compression_strut):
    """
    Checks that absolute bounds are the values the parameter may take.
    """
    parameter = TrailEdgeParameter(
        (0, 1), bound_low=-3.0, bound_up=-0.5, is_absolute=True
    )

    assert parameter.bound_low(compression_strut) == -3.0
    assert parameter.bound_up(compression_strut) == -0.5


@pytest.mark.parametrize("is_absolute", [False, True])
def test_missing_bounds_unbounded(compression_strut, is_absolute):
    """
    Checks that a parameter without bounds is unbounded, absolute or not.
    """
    parameter = TrailEdgeParameter((0, 1), is_absolute=is_absolute)

    assert parameter.bound_low(compression_strut) == float("-inf")
    assert parameter.bound_up(compression_strut) == float("inf")


def test_absolute_survives_data(compression_strut):
    """
    Checks that absolute bounds stay absolute through a JSON round trip.
    """
    parameter = TrailEdgeParameter(
        (0, 1), bound_low=-3.0, bound_up=-0.5, is_absolute=True
    )
    text = json_dumps(parameter)
    loaded = json_loads(text)

    assert isinstance(loaded, TrailEdgeParameter)
    assert loaded.bound_low(compression_strut) == -3.0
    assert loaded.bound_up(compression_strut) == -0.5


def test_old_data_loads_relative(compression_strut):
    """
    Checks that data saved without the absolute flag loads with relative bounds.
    """
    parameter = TrailEdgeParameter((0, 1), bound_low=-1.0, bound_up=2.0)
    data = parameter.__data__
    del data["_is_absolute"]
    loaded = TrailEdgeParameter.__from_data__(data)

    assert loaded.bound_low(compression_strut) == -2.0
    assert loaded.bound_up(compression_strut) == 1.0


def test_absolute_bound_stops_solver(compression_strut):
    """
    Checks that the solver stops at an absolute bound short of the goal.
    """
    compression_strut.build_trails()
    optimizer = Optimizer()
    # The support reaches this point with a trail length of -3.
    goal = PointGoal(0, [0.0, -1.0, 0.0])
    parameter = TrailEdgeParameter(
        (0, 1), bound_low=-2.0, bound_up=-0.5, is_absolute=True
    )
    optimizer.add_goal(goal)
    optimizer.add_parameter(parameter)
    form = optimizer.solve(compression_strut)

    assert form.edge_attribute((0, 1), "length") == pytest.approx(-2.0)


def test_start_outside_bounds_raises(compression_strut):
    """
    Checks that a start value outside absolute bounds stops the solve with a clear error.
    """
    compression_strut.build_trails()
    optimizer = Optimizer()
    goal = PointGoal(0, [0.0, -1.0, 0.0])
    parameter = TrailEdgeParameter(
        (0, 1), bound_low=0.5, bound_up=2.0, is_absolute=True
    )
    optimizer.add_goal(goal)
    optimizer.add_parameter(parameter)

    with pytest.raises(ValueError, match="outside its bounds"):
        optimizer.solve(compression_strut)
