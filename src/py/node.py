from __future__ import annotations
from typing import List, Optional, Tuple

from src.py.exceptions import CDError
from sympy import Rational, Expr, Matrix, cos, pi, oo, zoo, sqrt, latex
from sympy.matrices.common import NonInvertibleMatrixError

# Nodes in a CD.
class Node:
    __comp: List[Node]

    # Class constructor.
    def __init__(self, value: str, index: int) -> None:
        self.stringIndex = index

        if value != 'ß':
            self.value = value
        else:
            self.value = '+'

        self.neighbors: List[Node] = []
        self.edgeLabels: List[str] = []
        self.visited: bool = False

        # The index of a node in the graph that contains it.
        self.arrayIndex: Optional[int] = None

        # The index of a node in the drawing screen.
        self.drawIndex: Optional[int] = None

        # Auxiliary for graph clone.
        self.cloneNode: Node

    # Clones a node, along with its neighbors.
    def clone(self) -> Node:
        newNode = Node(self.value, self.stringIndex)
        newNode.neighbors = list(self.neighbors)
        newNode.edgeLabels = list(self.edgeLabels)

        return newNode

    # Gets the degree of a node.
    def degree(self) -> int:
        return len(self.neighbors)

    # Links two nodes together.
    def linkTo(self, node: Node, label: str) -> None:
        if self is node:
            raise CDError("Can't link node to self.")

        if node in self.neighbors:
            raise CDError("Can't link two nodes twice.")

        if label == "1" or label == "1/2":
            raise CDError(f"Invalid edge label {label}.")

        if label != "2":
            self.neighbors.append(node)
            self.edgeLabels.append(label)
            node.neighbors.append(self)
            node.edgeLabels.append(label)

    @staticmethod
    def labelToNumber(label: str):
        if label == '∞':
            return oo
        elif label == 'Ø':
            return None

        try:
            return Rational(label)
        except TypeError as e:
            raise CDError(f"Edge label {label} could not be recognized as a value.")

    @staticmethod
    def nodeToNumber(label: str):
        if label in Node.__dictionary:
            return Node.__dictionary[label]

        try:
            return 2 * cos(pi / Rational(label))
        except TypeError as e:
            raise CDError(f"Node label {label} could not be recognized as a value.")

    __dictionary = {
        'o': 0,
        'x': 1,
        'q': sqrt(2),
        'f': (1 + sqrt(5)) / 2,
        'v': (sqrt(5) - 1) / 2,
        'h': sqrt(3),
        'k': sqrt(2 + sqrt(2)),
        'u': 2,
        'w': 1 + sqrt(2),
        'F': (3 + sqrt(5)) / 2
    }

    # Gets the connected component of a node.
    def component(self) -> List[Node]:
        Node.__comp = []
        self.__component()

        return Node.__comp

    # Auxiliary function for component.
    def __component(self) -> None:
        self.visited = True
        Node.__comp.append(self)

        # Performs DFS.
        for node in self.neighbors:
            if not node.visited:
                node.__component()

# The CD as a graph.
class Graph:
    # Class constructor.
    def __init__(self, array: List[Node]) -> None:
        self.array = array
        self.idx: int

        # If the nodes already have array indices, that is,
        # if they were already part of a previous graph,
        # we clone them so as to not run into weird issues.
        if len(self) > 0:
            if self[0].arrayIndex is not None:
                # Associates a clone for every node.
                for i in range(len(array)):
                    self[i].cloneNode = self[i].clone()

                # Replaces the original nodes with their clones.
                for i in range(len(self)):
                    self[i] = self[i].cloneNode
                    self[i].arrayIndex = i

                # Links the cloned nodes.
                for node in self:
                    for i in range(len(node.neighbors)):
                        node.neighbors[i] = node.neighbors[i].cloneNode
            else:
                for i in range(len(array)):
                    array[i].arrayIndex = i

    # Class iterator.
    def __iter__(self) -> Graph:
        self.idx = 0
        return self

    # Next iterator method.
    def __next__(self) -> Node:
        if self.idx < len(self):
            x = self[self.idx]
            self.idx += 1
            return x

        raise StopIteration

    def __getitem__(self, key: int) -> Node:
        return self.array[key]

    def __setitem__(self, key: int, value: Node) -> None:
        self.array[key] = value

    def __delitem__(self, key: int) -> None:
        del self.array[key]

    def __len__(self):
        return len(self.array)

    # Gets the connected components of a graph.
    def components(self) -> List[Graph]:
        components: List[Graph] = []

        # Puts the connected components in an array.
        for node in self:
            if not node.visited:
                components.append(Graph(node.component()))

        # Resets visited attribute.
        for node in self:
            node.visited = False

        return components

    # Gets the Schläfli matrix of a graph.
    def schlafli(self) -> Matrix:
        n = len(self)
        matrix: List[List[Expr]] = []

        # For every node in the graph:
        for i in range(n):
            matrix.append([0] * n)

            node = self.array[i]
            neighbors = node.neighbors
            edgeLabels = node.edgeLabels
            matrix[i][i] = 2

            # For every other node in the graph:
            for j in range(len(neighbors)):
                neighbor = neighbors[j]
                label = Node.labelToNumber(edgeLabels[j])

                if label is None:
                    raise CDError("Ø not permitted in circumradius computation.")

                assert isinstance(neighbor.arrayIndex, int)

                # Fills in the matrix entries.
                matrix[i][neighbor.arrayIndex] = -2 * cos(pi / label)

        return Matrix(matrix)

    # Gets the circumradius of a polytope's CD.
    # Is meant for a single connected component
    # (but it will work ok for non-connex graphs).
    def __circumradius(self) -> Expr:               
        rings = [] 
        allZero = True

        # Creates the vector of distances of the point to the mirrors.
        for i in range(len(self)):
            val = Node.nodeToNumber(self.array[i].value)
            rings.append(val)

            if val != 0:
                allZero = False

        # If all distances are zero, the circumradius is zero.
        if allZero:
            return 0

        # Does the actual calculation.
        # Formula found by Wendy Krieger.
        ringVector = Matrix(rings)

        try:
            stott = self.schlafli() ** -1
        except NonInvertibleMatrixError:
            return oo

        return sqrt(((stott * ringVector).T * ringVector)[0, 0] / 2)

    # Gets the circumradius of a polytope's CD.
    # Depends on __circumradius.
    def circumradius(self) -> Expr:
        res = 0
        for component in self.components():
            res += component.__circumradius() ** 2

        return sqrt(res)

    # Same as circumradius, except that it returns a tuple of messages to post.
    def circumradiusFormat(self, mode: str = 'plain') -> Tuple[str, str]:
        circ = self.circumradius()
        return Graph.format(circ, mode), Graph.format(circ.evalf(), 'plain')

    @staticmethod
    # Formats a sympy result into something that can be posted on Discord.
    def format(number, mode: str) -> str:
        if mode == 'latex':
            return '$' + latex(number) + '$'
        # Maybe print exponents in Unicode?
        elif mode == 'plain':
            return (str(number)
                .replace('**', '^')
                .replace('*', '×')
                .replace('I', 'i')
                .replace('-', '–')
                .replace('oo', '∞')
            )
        else:
            raise Exception("Invalid format mode.")

    # Gets the rank and curvature of a polytope's CD.
    def spaceOf(self) -> str:
        schlafli = self.schlafli()
        n = len(self)

        # If a mirror configuration can be built in Euclidean space,
        # the Schläflian suffices to determine whether it is spherical or Euclidean.
        valid: bool = True
        mirrorNormals: List[List[Expr]] = []

        # For each of the mirrors:
        for i in range(n):
            mirrorNormals.append([0] * n)
            norm = 0

            # For each of the other mirrors we've already placed:
            for j in range(i):
                # Calculates their dot product.
                dot = 0
                for k in range(j):
                    dot += mirrorNormals[i][k] * mirrorNormals[j][k]

                # Defines the next coordinate of the i-th mirror so that
                # the dot product between the i-th and j-th mirror checks out.
                mirrorNormals[i][j] = (schlafli[i,j] / 2 - dot) / mirrorNormals[j][j]
                norm += mirrorNormals[i][j] ** 2

            # If the mirror normal can't be built, then the mirror config is hyperbolic.
            if norm == zoo or norm > 1:
                valid = False
                break

            mirrorNormals[i][i] = sqrt(1 - norm)

        if not valid:
            return f" is a {n}D hyperbolic polytope."

        schlaflian = schlafli.det()

        try:
            if schlaflian > 0:
                curv = "spherical"
            elif schlaflian == 0:
                curv = "Euclidean"
            else:
                raise Exception("The Schläflian of a valid mirror arrangement must be non-negative.")
        except TypeError as e:
            raise CDError(f"Couldn't determine sign of Schläflian (≈ {schlaflian.evalf()}). The space of the polytope is probably Euclidean.")

        return f" is a {n}D {curv} polytope."
