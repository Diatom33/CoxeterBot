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
                    self.error(f"Virtual node at index {str(self.index)} not a lowercase letter.")
                if nodeIndex >= len(nodes):
                    self.error("Node index out of range.")

                # Either declares prevNode or connects prevNode to this node.
                if prevNode is None:
                    prevNode = nodes[nodeIndex]
                else:
                    prevNode.linkTo(nodes[nodeIndex], prevEdge)

            # Edge values
            elif cd[self.index].isdigit() or cd[self.index] == "/":
                if prevNode is None:
                    self.error("Node expected.")

                prevEdge = self.readNumber()

            # Node values
            elif re.findall(CD.nodeLabels, cd[self.index]):
                newNode = Node(cd[self.index])
                nodes.append(newNode)

                if prevNode is not None:
                    if prevEdge is None:
                        if not prevSpace:
                            self.error("Two nodes can't be adjacent.")
                    else:
                        prevNode.linkTo(newNode, prevEdge)

                prevNode = newNode
                prevEdge = None

            # No Matches
            else:
                self.error("Symbol not recognized.")

            prevSpace = (cd[self.index] == " ")
            self.index += 1

        return Graph(nodes)

    def error(self, text):
        raise ValueError(f"Diagram parsing failed at index {str(self.index)}. {text}")