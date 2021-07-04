from abc import abstractmethod

from compas_cem.optimization import Serializable


__all__ = ["Constraint"]


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

    def target(self):
        """
        The target to reach.

        Returns
        -------
        target : ``object``
            A target object.
        """
        return self._target

    @abstractmethod
    def error(self):
        """
        Calculate the error to the target.
        """
        return

    @property
    def weight(self):
        """
        The strength of the constraint.
        """
        return self._weight

# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------
    # TODO: Update serialization after autodiff. Danger of not working in Rhino!

    @property
    def data(self):
        """
        A data dictionary that represents a ``Goal`` object.

        Returns
        -------
        data : ``dict``
            A dictionary that contains the following key-value pairs:
        """

        data = {}
        data["datatype"] = self.datatype()
        data["node_key"] = str(self._key)
        data["target_datatype"] = self.object_datatype(self._target)
        data["target"] = self._target.to_data()

        return data

    @data.setter
    def data(self, data):
        """
        Overwrites this object's attributes with a data dictionary.

        Parameters
        ----------
        data : ``dict``
            A data dictionary.
        """
        self._key = int(data["node_key"])
        target_cls = self.object_cls_from_dtype(data["target_datatype"])
        target = target_cls.from_data(data["target"])
        self._target = target


if __name__ == "__main__":
    pass
