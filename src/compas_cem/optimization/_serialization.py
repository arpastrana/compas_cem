import json

from compas.base import Base


__all__ = ["Serializable", "cls_from_dtype"]


# ------------------------------------------------------------------------------
# Base Class
# ------------------------------------------------------------------------------


class Serializable(Base):

    # --------------------------------------------------------------------------
    # Data
    # --------------------------------------------------------------------------

    @property
    def data(self):
        """
        """
        return

    @data.setter
    def data(self, data):
        """
        """
        return

    # --------------------------------------------------------------------------
    # IO - Data
    # --------------------------------------------------------------------------

    @classmethod
    def from_data(cls, data):
        """
        Creates a serializable object from structured data.

        Parameters
        ----------
        data : ``dict``
            The data dictionary.

        Returns
        -------
        object : ``cls``
            An instance of a ``cls`` object.

        Notes
        -----
        This constructor  is meant to be used in conjunction with the
        corresponding ``to_data()`` method.
        """
        serializable = cls()
        serializable.data = data
        return serializable

    def to_data(self):
        """
        Returns a dictionary of structured data representing a serializable object.

        Returns
        -------
        data : ``dict``
            The structured data.

        Notes
        ----
        This method produces the data that can be used in conjunction with the
        corresponding *from_data()* method.
        """
        return self.data

    # --------------------------------------------------------------------------
    # IO - JSON
    # --------------------------------------------------------------------------

    @classmethod
    def from_json(cls, filepath):
        """
        Construct a serializable object from structured data contained in a json file.

        Parameters
        ----------
        filepath : str
            The path to the json file.

        Returns
        -------
        object : ``cls``
            An instance of a ``cls`` object.

        Notes
        -----
        This constructor method is meant to be used in conjunction with the
        corresponding *to_json()* method.
        """
        with open(filepath, 'r') as fp:
            data = json.load(fp)
        optimizer = cls()
        optimizer.data = data
        return optimizer

    def to_json(self, filepath, pretty=False):
        """
        Serialize this object to a structured json.

        Parameters
        ----------
        filepath : str
            The path to the json file.

        Notes
        -----
        This constructor method is meant to be used in conjunction with the
        corresponding *from_json()* method.
        """
        with open(filepath, 'w+') as f:
            if pretty:
                json.dump(self.data, f, sort_keys=True, indent=4)
            else:
                json.dump(self.data, f)
        return

    def datatype(self):
        """
        Get the data type of this COMPAS object.

        Returns
        -------
        datatype : ``str``
            The data type of the COMPAS object in the following format:
            '{}/{}'.format(o.__class__.__module__, o.__class__.__name__).
        """
        return self.object_datatype(self)

    @staticmethod
    def object_datatype(o):
        return "{}/{}".format(o.__class__.__module__, o.__class__.__name__)

    @staticmethod
    def object_cls_from_dtype(dtype):
        return cls_from_dtype(dtype)

# ------------------------------------------------------------------------------
# Class from datatype
# ------------------------------------------------------------------------------


def cls_from_dtype(dtype):
    """
    Get the class object corresponding to a COMPAS data type specification.

    Parameters
    ----------
    dtype : str
        The data type of the COMPAS object in the following format:
        '{}/{}'.format(o.__class__.__module__, o.__class__.__name__).

    Returns
    -------
    :class:`compas.base.Base`

    Raises
    ------
    ValueError
        If the data type is not in the correct format.
    ImportError
        If the module can't be imported.
    AttributeError
        If the module doesn't contain the specified data type.
    """
    mod_name, attr_name = dtype.split('/')
    module = __import__(mod_name, fromlist=[attr_name])
    return getattr(module, attr_name)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
