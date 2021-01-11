import re
from node import Node, Graph

MAX_LEN = 100

from cdError import CDError

# Stores the index of a node, and its position in the string.
class NodeRef:
    def __init__(self, index, pos):
        self.index = index
        self.pos = pos

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    # Matches every letter, or the German eszett.
    nodeLabels = "[a-zA-Zß]"

    # Matches one of the follwing:
    # A fraction of two natural numbers.
    # A single number, possibly followed by '.
    # A single letter, lowercase or uppercase, possibly followed by '.
    # ∞, possibly followed by '.
    # Ø
    # 3 or more dots in succession. (...)
    edgeLabels = "(([1-9][0-9]*\/[1-9][0-9]*)|[1-9][0-9]*|[a-zA-Z]|∞)'?|Ø|\.\.\.+"

    def __init__(self, string):
        # The index of the CD at which we're reading.
        self.index = 0
        self.string = string

    # Reads a number from a given position.
    def readNumber(self):
        match = re.search(CD.edgeLabels, self.string[self.index:])
        if match is None:
            return None

        span = match.span()

        if span[0] != 0:
            return None

        self.index += span[1] - span[0] - 1

        return match.group()

    # Converts a textual Coxeter Diagram to a graph.
    def toGraph(self):
        self.index = 0
        cd = self.string

        nodes = [] # The nodes in the final graph.
        edges = [] # The node pairs to link in the final graph.

        prevNodeRef = None # Most recently read node.
        edgeLabel = None # Most recently read edge label.
        readingNode = True # Are we reading a node (or an edge)?

        # Reads through string.
        while self.index < len(cd):
            # Skips spaces.
            if cd[self.index] == " ":  
                if readingNode:
                    self.error("Expected node label, got space instead.") 
                    
                readingNode = True
                edgeLabel = None

            # Skips hyphens in the middle of the string.
            elif cd[self.index] == "-":
                pass

            # Reads virtual node
            elif cd[self.index] == "*":
                if not readingNode:
                    self.error("Expected edge label, got virtual node instead.")

                self.index += 1
                hyphen = False

                # Hyphen.
                if self.index < len(cd) and cd[self.index] == '-':
                    hyphen = True
                    self.index += 1

                # Declares the node index.
                if self.index < len(cd):
                    nodeIndex = ord(cd[self.index]) - ord('a')
                else:
                    self.error("Expected lowercase letter, got string end instead.")

                # Checks that the node index is valid.
                if nodeIndex < 0 or nodeIndex >= 26:
                    self.error("Virtual node not a lowercase letter.")

                # Puts a minus sign if necessary.
                if hyphen:
                    nodeIndex = -(nodeIndex + 1)

                newNodeRef = NodeRef(nodeIndex, self.index)

                # Toggles the flag to link stuff.
                linkNodes = True

            # Does lacing stuff.
            elif cd[self.index] == "&":
                self.error("Laces not yet supported.")

            # Node values
            elif readingNode:
                if len(nodes) > MAX_LEN:
                    self.error("Diagram too big.")

                if not re.findall(CD.nodeLabels, cd[self.index]):
                    self.error(f"Invalid node symbol {cd[self.index]}")

                newNodeRef = NodeRef(len(nodes), self.index)
                nodes.append(Node(cd[self.index]))

                # Toggles the flag to link stuff.
                linkNodes = True

            # Edge values
            else:
                edgeLabel = self.readNumber()
                if edgeLabel is None:
                    self.error(f"Invalid edge symbol {cd[self.index]}")

                readingNode = True

            # Links two nodes if necessary.
            if linkNodes:
                if not (prevNodeRef is None or edgeLabel is None):
                    edges.append({
                        0: newNodeRef,
                        1: prevNodeRef,
                        "label": edgeLabel,
                    })

                # Updates variables.
                linkNodes = False
                prevNodeRef = newNodeRef
                edgeLabel = None
                readingNode = False

            self.index += 1

        # Throws an error if the CD ends in an edge label.
        if readingNode:
            self.error("Node label expected, got string end instead.")

        # Links corresponding nodes.
        for edge in edges:
            # Checks if nodes in range.
            for i in range(2):
                # Configures where the error will appear.
                self.index = edge[i].pos

                index = edge[i].index
                if index >= len(nodes) or index < -len(nodes):
                    self.error("Virtual node index out of range")

            # Attempts to link each pair.
            try:
                # Configures where the error will appear.
                self.index = max(edge[0].pos, edge[1].pos)

                nodes[edge[0].index].linkTo(nodes[edge[1].index], edge["label"])
            except CDError as e:
                self.error(str(e))

        # Returns the graph.
        return Graph(nodes)

    def error(self, text):
        raise CDError(f"Diagram parsing failed at index {str(self.index)}. {text}")