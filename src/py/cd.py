import re
from node import Node, Graph

MAX_LEN = 100

# Custom class, to distinguish between caught and uncaught errors.
class CDError(Exception):
    pass

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    nodeLabels = "[oxsqfvhkuwFe]"
    edgeLabels = "[0-9]|[∞Ø/]"

    def __init__(self, string):
        # The index of the CD at which we're reading.
        self.index = 0

        # Removes hyphens from CD.
        self.string = string.translate({45: None})

    # Reads a number from a given position.
    # Returns it as a string.
    def readNumber(self):
        number = ""
        char = self.string[self.index]

        while re.findall(CD.edgeLabels, char):
            number += char
            self.index += 1

            if self.index < len(self.string):
                char = self.string[self.index]
            else:
                self.error("String index out of range while reading number.")

        self.index -= 1
        return number

    # Converts a textual Coxeter Diagram to a graph.
    def toGraph(self):
        self.index = 0
        cd = self.string

        nodes = [] # The nodes in the final graph.
        prevNode = None # Most recently read node.
        prevEdge = 0 # Most recently read edge label.
        prevSpace = False # Does a space separate the last two nodes?

        # Reads through string.
        while self.index < len(cd):
            # Skips spaces.
            if cd[self.index] == " ":
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

            # Edge values
            elif re.findall(CD.edgeLabels, cd[self.index]):
                if prevNode is None:
                    self.error("Node expected.")

                prevEdge = self.readNumber()

            # Node values
            elif re.findall(CD.nodeLabels, cd[self.index]):
                if len(nodes) > MAX_LEN:
                    self.error("Diagram too big.")

                newNode = Node(cd[self.index])
                nodes.append(newNode)

                # Toggles the flag to link stuff.
                linkNodes = True

            # No Matches
            else:
                self.error("Symbol not recognized.")

            # Links two nodes if necessary, just updates prevNode otherwise.
            if linkNodes:
                if prevNode is not None:
                    if prevEdge is None:
                        if not prevSpace:
                            self.error("Two nodes can't be adjacent.")
                    elif prevNode is not newNode:
                        prevNode.linkTo(newNode, prevEdge)

                linkNodes = False
                prevNode = newNode
                prevEdge = None

            prevSpace = (cd[self.index] == " ")
            self.index += 1

        return Graph(nodes)

    def error(self, text):
        raise CDError(f"Diagram parsing failed at index {str(self.index)}. {text}")