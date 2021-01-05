#file -- node.py --
class Node:
    #Class constructor.
    def __init__(self, value):
        self.value = value
        self.neighbors = []
        self.visited = False
    
    #Links two nodes together.
    def linkTo(self, node):
        self.neighbors.append(node)
        node.neighbors.append(self)

    #Gets the connected components of a graph.
    def components(self, graph):
        components = []
        
        for node in graph:
            if not node.visited:
                components.append(node.component())
                
        return components

    #Gets the connected component of a node.
    def component(self):
        Node._comp = []        
        self._component()
        
        return Node._comp
        
    #Auxiliary function for component.
    def _component(self):
        self.visited = True
        Node._comp.append(self)
        
        for node in self.neighbors:
            if not node.visited:
                node._component()