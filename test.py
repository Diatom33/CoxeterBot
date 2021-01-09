from node import Node, Graph
from draw import Draw 

array = [Node('x'), Node('o'), Node('s')]
array[0].linkTo(array[1], 3)
array[1].linkTo(array[2], 3)

Draw(Graph(array)).show()