from compas_cem.elements import Node

from compas.utilities import geometric_key
from compas.utilities import is_item_iterable


__all__ = [
    "NodeMixins"
]


# ==============================================================================
# Node Mixins
# ==============================================================================

class NodeMixins(object):
    """
    """
    def add_node(self, node):
        """
        Adds double
        """
        key = node.key
        xyz = node.xyz
        x, y, z = xyz
        node = super(NodeMixins, self).add_node(key=key, x=x, y=y, z=z)
        self.gkey_node[self.gkey(xyz)] = node
        return node

    def node_exists(self, value):
        """
        Checks
        """
        return self.node_key(value) != None

    def node_key(self, value):
        """
        Gets
        """
        if value in self.node:
            key = value
        else:
            key = self.gkey_node.get(self.gkey(value))
        return key
  
    def update_node_xyz(self, key, xyz):
        """
        Modifies
        """
        gkey = self.gkey(xyz)
        if gkey in self.gkey_node:
            del self.gkey_node[gkey]
        self.add_node(Node(key, xyz))

    def node_xyz(self, key, xyz=None):
        """
        Gets or sets node coordinates.
        """
        if not xyz:
            return self.node_coordinates(key)
        self.update_node_xyz(key, xyz)

    def gkey(self, xyz):
        """
        Gets
        """
        return geometric_key(xyz, self.tol)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    from compas_cem.diagrams.form_diagram import FormDiagram
    
    form = FormDiagram()

    node = form.add_node()
    xyz = [1.0, 0.0, 0.0]
    form.node_xyz(node, xyz)
    
    assert form.node_xyz(node) == xyz
