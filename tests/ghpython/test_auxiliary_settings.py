import pytest

from compas_cem.ghpython import AuxiliaryTrailSettings

# ==============================================================================
# Tests
# ==============================================================================


def test_settings_defaults():
    """
    Checks the default settings: one unit in compression, toward negative x, y and z.
    """
    settings = AuxiliaryTrailSettings()

    assert settings.length == 1.0
    assert settings.state == -1.0
    assert settings.vector == (-1.0, -1.0, -1.0)
    assert settings.signed_length == -1.0


@pytest.mark.parametrize("state, signed_length", [(2.0, 0.5), (-0.1, -0.5)])
def test_signed_length_follows_state(state, signed_length):
    """
    Checks that only the sign of the state reaches the signed length.
    """
    settings = AuxiliaryTrailSettings(length=0.5, state=state)

    assert settings.signed_length == signed_length


@pytest.mark.parametrize(
    "values, match",
    [
        ({"length": 0.0}, "length must be positive"),
        ({"length": -1.0}, "length must be positive"),
        ({"state": 0.0}, "state must be nonzero"),
        ({"vector": (0.0, 0.0, 0.0)}, "vector must be nonzero"),
    ],
)
def test_settings_reject_bad_values(values, match):
    """
    Checks that a non-positive length, a zero state or a zero vector raises.
    """
    with pytest.raises(ValueError, match=match):
        AuxiliaryTrailSettings(**values)
