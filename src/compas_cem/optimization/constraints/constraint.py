from abc import abstractmethod
from ast import literal_eval

from compas.data.encoders import cls_from_dtype

from compas.geometry import distance_point_point_sqrd

from compas_cem.data import Data


# ------------------------------------------------------------------------------
# Constraint
# ------------------------------------------------------------------------------


class Constraint(Data):
    """
    The blueprint of a constraint.
    """
    def __init__(self, key, target, weight, **kwargs):
        super(Constraint, self).__init__(**kwargs)
        self._key = key  # a topological key
        self._target = target  # a geometric target
        self._weight = weight  # the strength of the constraint

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
        The strength of the constraint.
        """
        return self._weight

    @abstractmethod
    def penalty(self):
        """
        Calculate the penalty caused by the constraint.
        """
        raise NotImplementedError

    @property
    def data(self):
        """
        A data dictionary that represents a ``Constraint`` object.

        Returns
        -------
        data : ``dict``
            A dictionary that contains the following key-value pairs:

            * "key" : ``str``
            * "datatype" : ``str`
            * "target" : ``str``
            * "target_datatype" : ``str``
        """
        data = {}

        data["key"] = repr(self.key())
        data["weight"] = self._weight
        data["target"] = self._target.to_data()
        data["target_dtype"] = self._target.dtype

        return data

    @data.setter
    def data(self, data):
        """
        Overwrites this object's attributes with a data dictionary.

        Parameters
        ----------
        data : ``dict``
            A dictionary that contains the following key-value pairs:

            * "key" : ``str``
            * "datatype" : ``str`
            * "target" : ``str``
            * "target_datatype" : ``str``
        """
        self._key = literal_eval(data["key"])
        self._weight = float(data["weight"])

        # TODO: Is hard-coding a Vector here is a good idea?
        target_cls = cls_from_dtype(data["target_dtype"])
        self._target = target_cls.from_data(data["target"])

    def __repr__(self):
        st = "{0}(key={1!r}, target={2!r}, weight={3!r})"
        return st.format(self.__class__.__name__, self._key, self._target, self._weight)

# ------------------------------------------------------------------------------
# Vector Constraint
# ------------------------------------------------------------------------------


class VectorConstraint(Constraint):
    """
    The blueprint of a constraint that measures distances between two vectors.
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
# Float Constraint
# ------------------------------------------------------------------------------


class FloatConstraint(Constraint):
    """
    The blueprint of a constraint that measures distances between two floats.
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
    def data(self):
        """
        A data dictionary that represents a ``Constraint`` object.

        Returns
        -------
        data : ``dict``
            A dictionary that contains the following key-value pairs:

            * "key" : ``str``
            * "datatype" : ``str`
            * "target" : ``str``
        """
        data = {}

        data["key"] = repr(self._key)
        data["target"] = repr(self._target)
        data["weight"] = self._weight

        return data

    @data.setter
    def data(self, data):
        """
        Overwrites this object's attributes with a data dictionary.

        Parameters
        ----------
        data : ``dict``
            A dictionary that contains the following key-value pairs:

            * "key" : ``str``
            * "target" : ``str`
        """
        self._key = literal_eval(data["key"])
        self._target = literal_eval(data["target"])
        self._weight = float(data["weight"])

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
