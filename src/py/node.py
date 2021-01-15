from __future__ import annotations
from typing import List
from src.py.exceptions import CDError

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