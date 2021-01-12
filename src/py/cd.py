import re
from src.py.node import Node, Graph
import sys
import math
from src.py.cdError import CDError

MAX_LEN = 100 # Hardcoded node limit.

# Stores the index of a node, and its position in the string.
class NodeRef:
    def __init__(self, index, pos):
        self.index = index
        self.pos = pos

# Various regexes:
numberRegex = "([1-9][0-9]*)"
fractionRegex = f"({numberRegex}\/{numberRegex})"

# Matches one of the following:
# A letter or the german eszett.
# A letter, surrounded by parentheses, with a possible hyphen.
# A fraction surrounded by parentheses.
# A number surrounded by parentheses.
nodeLabels = f"[a-zA-Zß]|\(((-?[a-zA-Z])|{fractionRegex}|{numberRegex})\)"

# Matches one of the follwing:
# A fraction of two natural numbers.
# A single number, possibly followed by '.
# A single letter, lowercase or uppercase, possibly followed by '.
# ∞, possibly followed by '.
# Ø
# 3 or more dots in succession. (...)
edgeLabels = f"({fractionRegex}|{numberRegex}|[a-zA-Z]|∞)'?|Ø|\.\.\.+"

virtualNodesLetter = "\*-?[a-z]"
virtualNodesNumber = f"\*-?[1-9]|\*\(-?{numberRegex}\)"

# Represents a Coxeter Diagram, and contains the necessary methods to parse it.
class CD:
    # Class initializer.
    def __init__(self, string):
        # The index of the CD at which we're reading.
        self.index = 0
        self.string = string

    # Tries to match a regex at certain point in the string.
    def matchRegex(self, regex):
        match = re.search(regex, self.string[self.index:])
        if match is None:
            return None

        span = match.span()

        if span[0] != 0:
            return None

        self.index += span[1] - span[0] - 1

        return match.group()

    def readNode(self):
        return self.matchRegex(nodeLabels)

    # Reads a number from a given position.
    def readNumber(self):
        return self.matchRegex(edgeLabels)

    # Reads a virtual node from a given position.
    def readVirtualNode(self, nodeType):
        if nodeType == 'letter':
            return self.matchRegex(virtualNodesLetter)
        elif nodeType == 'number':
            return self.matchRegex(virtualNodesNumber)
        else:
            self.error("Invalid virtual node type", dev = True)

    # Reads a number from a given position.
    def readNumber(self):
        return self.matchRegex(edgeLabels)

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

                # Tries to read the virtual node as a letter virtual node.
                virtualNode = self.readVirtualNode('letter')
                if virtualNode is not None:
                    # Hyphen.
                    if virtualNode[1] == '-':
                        nodeIndex = ord('a') - ord(virtualNode[2]) - 1
                    else:
                        nodeIndex = ord(virtualNode[1]) - ord('a')
                        nodeIndex = ord(virtualNode[1]) - ord('a')

                # Tries to read the virtual node as a number virtual node.
                else:
                    virtualNode = self.readVirtualNode('number')
                    # If the node couldn't be read either way:
                    if virtualNode is None:
                        self.error("Invalid virtual node.")

                    # Parenthesis.
                    if virtualNode[1] == '(':
                        virtualNode = virtualNode[2:-1]
                    else:
                        virtualNode = virtualNode[1:]

                    # Indexing starts at 1.
                    nodeIndex = int(virtualNode) - 1

                newNodeRef = NodeRef(nodeIndex, self.index)

                # Toggles the flag to link stuff.
                linkNodes = True

            # Does lacing stuff.
            elif cd[self.index] == "&":
                self.error("Laces not yet supported.")

            # Node values
            elif readingNode:
                index = self.index
                newNodeLabel = self.readNode()
                if newNodeLabel is None:
                    self.error("Invalid node symbol.")

                # Removes parentheses.
                if newNodeLabel[0] == '(':
                    newNodeLabel = newNodeLabel[1:-1]

                if len(nodes) > MAX_LEN:
                    self.error("Diagram too big.")

                newNodeRef = NodeRef(len(nodes), index)
                nodes.append(Node(newNodeLabel, index))

                # Toggles the flag to link stuff.
                linkNodes = True

            # Edge values
            else:
                edgeLabel = self.readNumber()
                if edgeLabel is None:
                    self.error(f"Invalid edge symbol.")

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

    # Raises an error with a certain message.
    # Shows as an "Unexpected error" if dev = True (these are errors that the devs didn't consider).
    def error(self, text, dev = False):
        msg = f"Diagram parsing failed at index {str(self.index)}. {text}"

        if dev:
            raise Exception(msg)
        else:
            raise CDError(msg)