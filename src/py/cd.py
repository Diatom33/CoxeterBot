import re
from node import Node, Graph

MAX_LEN = 100

from cdError import CDError

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    # Matches every possible node label.
    nodeLabels = "[a-zA-Zß]"

    # Matches either a fraction, or a single number, or a single letter, or a special symbol.
    edgeLabels = "([1-9][0-9]*\/[1-9][0-9]*)|[1-9][0-9]*|[a-zA-Z]|[∞Ø]"

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
        prevNode = None # Most recently read node.
        prevEdge = 0 # Most recently read edge label.
        prevSpace = False # Does a space separate the last two nodes?

        readingNode = True # Are we reading a node (or an edge)?

        # Reads through string.
        while self.index < len(cd):
            # Skips spaces.
            if cd[self.index] == " ":
                readingNode = True

            # Skips hyphens in the middle of the string.
            elif cd[self.index] == "-":
                pass

            # Reads virtual node
            elif cd[self.index] == "*":
                self.index += 1

                # Declares the node index.
                if self.index < len(cd):
                    nodeIndex = ord(cd[self.index]) - ord('a')
                else:
                    self.error("Lowercase letter expected.")

                # Checks that the node index is valid.
                if nodeIndex < 0 or nodeIndex >= 26:
                    self.error("Virtual node not a lowercase letter.")
                if nodeIndex >= len(nodes):
                    self.error("Node index out of range.")

                # Toggles the flag to link stuff.
                newNode = nodes[nodeIndex]
                linkNodes = True

            # Node values
            elif readingNode:
                if len(nodes) > MAX_LEN:
                    self.error("Diagram too big.")

                if not re.findall(CD.nodeLabels, cd[self.index]):
                    self.error(f"Invalid node symbol {cd[self.index]}")

                newNode = Node(cd[self.index])
                nodes.append(newNode)

                # Toggles the flag to link stuff.
                linkNodes = True

                readingNode = False

            # Edge values
            else:
                if prevNode is None:
                    self.error("Node expected before edge.")

                prevEdge = self.readNumber()
                if prevEdge is None:
                    self.error(f"Invalid edge symbol {cd[self.index]}")

                readingNode = True

            # Links two nodes if necessary.
            if linkNodes:
                if not (prevNode is None or prevEdge is None):
                    try:
                        prevNode.linkTo(newNode, prevEdge)
                    except CDError as e:
                        self.error(str(e))

                # Updates variables.
                linkNodes = False
                prevNode = newNode
                prevEdge = None

            self.index += 1

        if prevEdge is None:
            return Graph(nodes)
        else:
            self.error("Node expected before string end.")

    def error(self, text):
        raise CDError(f"Diagram parsing failed at index {str(self.index)}. {text}")