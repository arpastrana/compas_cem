from compas_cem.optimization import Serializable


__all__ = [
    "Goal"
]


class Goal(Serializable):
    def __init__(self, key, target_geo):
        self._key = key  # a topological key
        self._target_geo = target_geo  # a geometric target
        self._ref_geo = None
    
    def key(self):
        """
        """
        return self._key
    
    def reference_geometry(self):
        """
        """
        return self._ref_geo
    
    def target_geometry(self):
        """
        """
        return self._target_geo
    
    def update(self):
        """
        """
        return
    
    def error(self):
        """
        """
        return
 
# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------

    @property
    def data(self):
        """
        A data dictionary that represents a``Goal`` object.

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
        data["target_datatype"] = self.object_datatype(self._target_geo)
        data["target_geo"] = self._target_geo.to_data()

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
        target_geo_cls = self.object_cls_from_dtype(data["target_datatype"])
        target_geo = target_geo_cls.from_data(data["target_geo"])
        self._target_geo = target_geo


if __name__ == "__main__":
    pass
