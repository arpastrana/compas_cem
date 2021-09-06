from abc import abstractmethod
from ast import literal_eval

from compas.geometry import distance_point_point_sqrd

from compas_cem.optimization import Serializable


# ------------------------------------------------------------------------------
# Constraint
# ------------------------------------------------------------------------------


class Constraint(Serializable):
    """
    The blueprint of a constraint.
    """
    def __init__(self, key, target, weight):
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

    def target(self, *args, **kwargs):
        """
        The target to reach.

        Returns
        -------
        target : ``object``
            A target object.
        args : ``list``
            A list of additional arguments.
        kwargs : ``dict``
            A dictionary with extra named arguments
        """
        return self._target

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
        return

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
        data["target"] = self._target.to_data()
        data["datatype"] = self.datatype()
        data["target_datatype"] = self.object_datatype(self._target)

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
        target_cls = self.object_cls_from_dtype(data["target_datatype"])
        target = target_cls.from_data(data["target"])
        self._target = target

# ------------------------------------------------------------------------------
# Float Constraint
# ------------------------------------------------------------------------------


class FloatConstraint(Constraint):
    """
    The blueprint of a constraint that measures distances between two floats.
    """
    def penalty(self, data):
        """
        The distance between the current and the target float.

        Returns
        -------
        error : ``float``
            The squared difference.
        """
        float_a = self.reference(data)
        float_b = self.target(float_a)
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

        data["key"] = repr(self.key())
        data["target"] = repr(self.target())
        data["datatype"] = self.datatype()

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

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
