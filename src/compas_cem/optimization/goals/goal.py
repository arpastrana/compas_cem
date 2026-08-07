from abc import abstractmethod
from ast import literal_eval

from compas.data.encoders import cls_from_dtype
from compas.geometry import distance_point_point_sqrd

from compas_cem.data import Data

# ------------------------------------------------------------------------------
# Goal
# ------------------------------------------------------------------------------


class Goal(Data):
    """
    The blueprint of a goal.
    """

    def __init__(self, key=None, target=None, weight=1.0, **kwargs):
        super(Goal, self).__init__(**kwargs)
        self._key = key  # a topological key
        self._target = target  # a geometric target
        self._weight = weight  # the strength of the goal

    def key(self):
        """
        The key to an edge or a node in a form diagram.

        Returns
        -------
        key : ``int`` or ``tuple``
            The key to a node of an edge.
        """
        return self._key

    @abstractmethod
    def target(self):
        """
        The target to reach.
        """
        raise NotImplementedError

    @property
    def weight(self):
        """
        The strength of the goal.
        """
        return self._weight

    @abstractmethod
    def penalty(self):
        """
        Calculate the penalty caused by the goal.
        """
        raise NotImplementedError

    @property
    def __data__(self):
        """
        A data dictionary that represents a goal.

        Notes
        -----
        The key is stored as its representation so that node keys and edge keys
        can share one JSON-serializable field. The target carries its own type
        alongside it, because the concrete geometry class is not recoverable
        from the goal class alone.
        """
        data = {}

        data["key"] = repr(self.key())
        data["weight"] = self._weight
        data["target"] = self._target.__data__
        data["target_dtype"] = self._target.__dtype__

        return data

    @classmethod
    def __from_data__(cls, data):
        """
        Construct a goal from a data dictionary.

        Parameters
        ----------
        data :
            A data dictionary.

        Returns
        -------
        goal :
            A goal object.
        """
        target_cls = cls_from_dtype(data["target_dtype"])

        goal = cls()
        goal._key = literal_eval(data["key"])
        goal._weight = float(data["weight"])
        goal._target = target_cls.__from_data__(data["target"])

        return goal

    def __repr__(self):
        st = "{0}(key={1!r}, target={2!r}, weight={3!r})"
        return st.format(self.__class__.__name__, self._key, self._target, self._weight)


# ------------------------------------------------------------------------------
# Vector Goal
# ------------------------------------------------------------------------------


class VectorGoal(Goal):
    """
    The blueprint of a goal that measures distances between two vectors.
    """

    def target(self, *args, **kwargs):
        """
        The target vector.
        """
        return self._target

    def penalty(self, data):
        """
        The distance between the current and the target vector.

        Returns
        -------
        error : ``float``
            The squared difference.
        """
        vec_a = self.reference(data)
        vec_b = self.target(vec_a)

        return distance_point_point_sqrd(vec_a, vec_b) * self.weight


# ------------------------------------------------------------------------------
# Float Goal
# ------------------------------------------------------------------------------


class FloatGoal(Goal):
    """
    The blueprint of a goal that measures distances between two floats.
    """

    def target(self, *args, **kwargs):
        """
        The target float value.
        """
        return self._target

    def penalty(self, data):
        """
        The distance between the current and the target float.

        Returns
        -------
        error : ``float``
            The squared difference.
        """
        float_a = self.reference(data)
        float_b = self.target()
        diff = float_a - float_b

        return diff * diff * self.weight

    @property
    def __data__(self):
        """
        A data dictionary that represents a goal on a float value.

        Notes
        -----
        The target is a plain number here, so it is stored as its representation
        rather than as a nested data dictionary.
        """
        data = {}

        data["key"] = repr(self._key)
        data["target"] = repr(self._target)
        data["weight"] = self._weight

        return data

    @classmethod
    def __from_data__(cls, data):
        """
        Construct a goal on a float value from a data dictionary.

        Parameters
        ----------
        data :
            A data dictionary.

        Returns
        -------
        goal :
            A goal object.
        """
        goal = cls()
        goal._key = literal_eval(data["key"])
        goal._target = literal_eval(data["target"])
        goal._weight = float(data["weight"])

        return goal


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
