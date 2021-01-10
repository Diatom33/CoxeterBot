import re
from node import Node, Graph

MAX_LEN = 100

from cdError import CDError

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    # Matches every possible node label.
    nodeLabels = "[a-zA-Zß]"

    # Matches either a fraction, or a single number, or a special symbol.
    edgeLabels = "([1-9][0-9]*\/[1-9][0-9]*)|[1-9][0-9]*|[∞Ø]"

    def __init__(self, string):
        # The index of the CD at which we're reading.
        self.index = 0

        # Removes hyphens from CD.
        self.string = string.translate({45: None})

    # Reads a number from a given position.
    # Returns whether it succeeded.
    def readNumber(self):
        match = re.search(CD.edgeLabels, self.string[self.index:])
        if match is None:
            return False

        span = match.span()

        if span[0] != 0:
            return False

        self.index += span[1] - span[0] - 1
        self.number = match.group()

        return True

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
            elif self.readNumber():
                if prevNode is None:
                    self.error("Node expected before edge.")

                prevEdge = self.number

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
                self.error("Node symbol not recognized.")

            # Links two nodes if necessary.
            if linkNodes:
                # If there's no previous node, just updates prevNode.
                if prevNode is not None:
                    # If prevEdge is None, this means there's two nodes one after another.
                    if prevEdge is None:
                        # Two consecutive nodes must be separated by a space.
                        if not prevSpace:
                            self.error("Two nodes can't be adjacent.")
                    # If prevEdge is not None, tries to link the nodes.
                    else:
                        try:
                            prevNode.linkTo(newNode, prevEdge)
                        except CDError as e:
                            self.error(str(e))

                # Updates variables.
                linkNodes = False
                prevNode = newNode
                prevEdge = None

            prevSpace = (cd[self.index] == " ")
            self.index += 1

        if prevEdge is None:
            return Graph(nodes)
        else:
            self.error("Node expected before string end.")

    def error(self, text):
        raise CDError(f"Diagram parsing failed at index {str(self.index)}. {text}")