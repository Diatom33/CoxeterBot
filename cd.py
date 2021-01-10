import re
from node import Node, Graph

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    nodeLabels = "[oxsqfvhkuwFe]"

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

        while char.isdigit() or char == "/":
            number += char
            self.index += 1
            char = self.string[self.index]

        self.index -= 1
        return number

    # Converts a textual Coxeter Diagram to a graph.
    def toGraph(self):
        self.index = 0
        cd = self.string

        nodes = [] # The nodes in the final graph.
        prevNode = None # Most recently read node.
        prevEdge = 0 # Most recently read edge label.

        # Reads through string.
        while self.index < len(cd):
            # Skips spaces.
            if cd[self.index] == " ":
                pass

            # Reads virtual node
            elif cd[self.index] == "*":
                self.index += 1
                nodeIndex = ord(cd[self.index]) - ord('a')

                if nodeIndex < 0 or nodeIndex >= 26:
                    raise ValueError("Virtual node at index " + str(self.index) + "not a lowercase letter.")

                if prevNode is None:
                    prevNode = nodes[nodeIndex]
                else:
                    prevNode.linkTo(nodes[nodeIndex], prevEdge)

            # Edge values
            elif cd[self.index].isdigit() or cd[self.index] == "/":
                prevEdge = self.readNumber()

            # Node values
            elif re.findall(CD.nodeLabels, cd[self.index]):
                newNode = Node(cd[self.index])
                nodes.append(newNode)

                if prevNode is not None and prevEdge is not None:
                    prevNode.linkTo(newNode, prevEdge)

                prevNode = newNode
                prevEdge = None

            # No Matches
            else:
                raise ValueError("Diagram parsing failed at index " + str(self.index) + ".")

            self.index += 1

        return Graph(nodes)