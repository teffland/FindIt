"""
* Tree data structure
"""
class Node():
    """ Node data structure for tree"""
    def __init__(self, name='', data={}, children=[], parent=None):
        self.name = name
        self.data = data
        self.children = children
        self.parent = parent
        if parent: 
            self.parent.add_child(self)
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    def add_child(self, node):
        if not isinstance(node, Node):
            print "ERROR: childe node is not of type Node"
            return

        self.children.append(node)

class Tree():
    """ Tree data structure """
    def __init__(self):
        self.nodes = {}
        self.nodenameset = set(self.nodes.keys())

    def add_node(self, name, data, children=[], parent=None):
        if isinstance(parent, str) or isinstance(parent, unicode):
            try:
                parent = self.nodes[parent]
            except KeyError:
                print "ERROR: specified parent does not exist in tree"
                return
        n = Node(name=name, data=data, children=children, parent=parent)
        self.nodes[name] = n
