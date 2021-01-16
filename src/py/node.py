from __future__ import annotations
from typing import List, Optional, Tuple

from src.py.exceptions import CDError
from sympy import Rational, Matrix, cos, pi, oo, sqrt, latex
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

        # This is used internally both by the graph and draw classes, so beware!
        self.arrayIndex: Optional[int] = None

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
        if label in Node.dictionary:
            return Node.dictionary[label]

        try:
            return 2 * cos(pi / Rational(label))
        except TypeError as e:
            raise CDError(f"Node label {label} could not be recognized as a value.")

    dictionary = {
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
        self.idx = 0
        self.arrayIndex: int

    # Class iterator.
    def __iter__(self) -> Graph:
        self.idx = 0
        return self

    # Next iterator method.
    def __next__(self) -> Node:
        if self.idx < len(self.array):
            x = self.array[self.idx]
            self.idx += 1
            return x

        raise StopIteration

    # Gets the connected components of a graph.
    def components(self) -> List[List[Node]]:
        components: List[List[Node]] = []

        # Puts the connected components in an array.
        for node in self:
            if not node.visited:
                components.append(node.component())

        # Resets visited attribute.
        for component in components:
            for node in component:
                node.visited = False

        return components

    # Gets the Schläfli matrix of a graph.
    def schlafli(self) -> Matrix:
        n = len(self.array)
        matrix: List[List[float]] = []

        # Saves the index of each node on the array as a property of the node itself.
        for i in range(n):
            self.array[i].arrayIndex = i

        # For every node in the graph:
        for i in range(n):
            matrix.append([0] * n)
            node = self.array[i]
            neighbors = node.neighbors
            edgeLabels = node.edgeLabels
            matrix[-1][i] = 2

            # For every other node in the graph:
            for j in range(len(neighbors)):
                neighbor = neighbors[j]
                label = Node.labelToNumber(edgeLabels[j])

                if label is None:
                    raise CDError("Ø not permitted in circumradius computation.")

                assert isinstance(neighbor.arrayIndex, int)

                # Fills in the matrix entries.
                matrix[-1][neighbor.arrayIndex] = -2 * cos(pi / label)

        for node in self:
            node.arrayIndex = None

        return Matrix(matrix)

    # Gets the circumradius of a polytope's CD.
    def __circumradius(self):
        try:
            stott = self.schlafli() ** -1
        except NonInvertibleMatrixError:
            return oo

        rings = []

        for i in range(len(self.array)):
            rings.append(Node.nodeToNumber(self.array[i].value))
        ringVector = Matrix(rings)

        return sqrt(((stott * ringVector).T * ringVector)[0, 0] / 2)

    def circumradius(self, mode: str = 'plain') -> Tuple[str, str]:
        res = 0
        for component in self.components():
            res += Graph(component).__circumradius() ** 2

        s = sqrt(res)
        return Graph.format(s, mode), Graph.format(s.evalf(), 'plain')

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
        schlaflian = schlafli.det()
        dimen = schlafli.shape[0]

        if schlaflian > 0:
            curv = "spherical"
        elif schlaflian == 0:
            curv = "euclidean"
        else:
            curv = "hyperbolic"

        return f" is a {str(dimen)}D {curv} polytope."
