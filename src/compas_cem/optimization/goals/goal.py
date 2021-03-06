from abc import abstractmethod

from compas_cem.optimization import Serializable


__all__ = [
    "Goal"
]


class Goal(Serializable):
    """
    The blueprint of a goal.
    """
    def __init__(self, key, target):
        self._key = key  # a topological key
        self._target = target  # a geometric target

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

            * "node_key" : ``int``
            * "target_geo" : ``dict``
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
