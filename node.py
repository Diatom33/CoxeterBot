#file -- node.py --
import re
class Node:
    #Class constructor.
    def __init__(self, value):
        self.value = value
        self.neighbors = []
        self.edgelabels = []
        self.visited = False

    #Links two nodes together.
    def linkTo(self, node, label):
        self.neighbors.append(node)
        self.edgelabels.append(label)
        node.neighbors.append(self)
        node.edgelabels.append(label)

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

def CDToGraph(cd):
    nodes = []
    index = 0
    readnum = False
    memnum = ""
    possvalues = "[oxqfvhkuwFe]"
    cd = cd.translate({45: None})
    # Reads through string.
    for i in range(len(cd)):
        # Spaces and *
        if (cd[i] == " " or cd[i] == "*"):
            continue
        # Virtual nodes
        if (cd[i-1] == "*"):
            if (ord(cd[i]) - 97 > 25 or ord(cd[i]) - 97 < 0):
                raise ValueError("One of those virtual nodes is not a lowercase letter")
            if (cd[i-2].isdigit()):
                nodes[index-1].linkTo(nodes[ord(cd[i])-97], memnum)
            if (cd[i+1].isdigit() or re.findall()):
                # Start wait to read node
                readnum = True
            continue
        # Edge Values
        if (cd[i].isdigit() or cd[i] == "/"):
            if (readnum):
                continue
            memnum = ""
            j = i
            while True:
                if (not (cd[j].isdigit() or cd[j] == "/")):
                    break
                memnum = memnum + cd[j]
                j += 1
            readnum = True
            continue
        # Node Values
        if (re.findall(possvalues, cd[i])):
            newnode = Node(index, cd[i])
            nodes.append(newnode)
            if (readnum):
                if (re.findall(possvalues, cd[i-(len(memnum)+1)])):
                    nodes[index-1].linkTo(nodes[index], memnum)
                else:
                    nodes[ord(cd[i - (len(memnum) + 1)]) - 97].linkTo(nodes[index], memnum)
            readnum = False
            index += 1
            continue
        # No Matches
        raise ValueError("I don't know one of these symbols")
    return nodes
