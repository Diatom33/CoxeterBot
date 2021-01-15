from __future__ import annotations
from typing import List, Optional, Tuple

from sympy.core.numbers import Infinity
from sympy.matrices.common import NonInvertibleMatrixError
from src.py.exceptions import CDError
import sympy

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
            return sympy.oo
        return sympy.Rational(label)

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
    def schlafli(self) -> sympy.Matrix:
        n = len(self.array)
        matrix: List[List[float]] = []

        for i in range(n):
            self.array[i].arrayIndex = i

        for i in range(n):
            matrix.append([0] * n)
            node0 = self.array[i]
            neighbors = node0.neighbors
            edgeLabels = node0.edgeLabels
            matrix[-1][i] = 2

            for j in range(len(neighbors)):
                neighbor = neighbors[j]
                label = Node.labelToNumber(edgeLabels[j])

                assert isinstance(neighbor.arrayIndex, int)
                matrix[-1][neighbor.arrayIndex] = -2 * sympy.cos(sympy.pi / label)
                

        for node in self.array:
            node.arrayIndex = None

        return sympy.Matrix(matrix)

    # Gets the circumradius of a polytope's CD.
    def circumradius(self) -> Tuple[str, str]:
        try:
            stott = self.schlafli() ** -1
        except NonInvertibleMatrixError:
            return '$\infty$', '$\infty$'

        rings = []

        for i in range(len(self.array)):
            rings.append(int(self.array[i].value == 'x'))
        ringVector = sympy.Matrix(rings)

        E = sympy.sqrt(((stott * ringVector).T * ringVector)[0, 0] / 2)
        return Graph.format(E), Graph.format(E.evalf())

    @staticmethod
    def format(number: str) -> str:
        return '$' + sympy.latex(number) + '$'