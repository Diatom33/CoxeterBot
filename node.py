#file -- node.py --
class Node:
    #Class constructor.
    def __init__(self, value):
        self.value = value
        self.neighbors = []
        self.edgeLabels = []
        self.visited = False
    
    #Links two nodes together.
    def linkTo(self, node, label):
        self.neighbors.append(node)
        self.edgeLabels.append(label)
        node.neighbors.append(self)
        node.edgeLabels.append(label)

    #Gets the connected component of a node.
    def component(self):
        Node.__comp = []        
        self.__component()
        
        return Node._comp
        
    #Auxiliary function for component.
    def __component(self):
        self.visited = True
        Node.__comp.append(self)
        
        for node in self.neighbors:
            if not node.visited:
                node.__component()
                
class Graph:
    #Class constructor.
    def __init__(self, array):
        self.array = array
        self.idx = 0
        return self
        
    #Iterator.
    def __next__(self):
        if self.idx < len(self.array):
            x = self.array[self.idx]
            self.idx += 1
            return x
            
        raise StopIteration
        
    #Gets the connected components of a graph.
    def components(self):
        components = []
        
        for node in self:
            if not node.visited:
                components.append(node.component())
                
        return components
