__all__ = [
    "Goal"
]


class Goal(object):
    def __init__(self, key, target_geo):
        self._key = key  # a topological key
        self._target_geo = target_geo  # a geometric target
        self._ref_geo = None
    
    def key(self):
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
        return
    
    def error(self):
        return
 

if __name__ == "__main__":
    pass
