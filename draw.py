from PIL import Image, ImageDraw
from node import Node, Graph

# Constants:
NODE_RADIUS = 3
RING_RADIUS = 6

# Draws a graph.
class Draw:
    # Class constructor.
    def __init__(self, graph):
        self.x = 20
        self.y = 20

        self.image = Image.new('RGB', size = (100, 50), color = (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        for component in graph.components():
            self.add(component)

    # Adds a new component to the diagram.
    # Currently, just puts everything in a straight line.
    # TODO: make this draw the trees prettily.
    def add(self, component):
        for node in component:
            self.addNode(node, self.x, self.y)
            self.x += 20
        
        self.x += 20

    # Adds a node in a particular position.
    def addNode(self, node, x, y):
        # Chooses the fill color.
        if node.value == 's':
            nodeFill = (255, 255, 255)
            radius = RING_RADIUS
        else:
            nodeFill = (0, 0, 0)
            radius = NODE_RADIUS

        # Draws the node.
        self.draw.ellipse( \
            [x - radius, y - radius, x + radius, y + radius], \
            fill = nodeFill, \
            outline = (0, 0, 0), \
            width = 1
        )

        # Draws the ring.
        if node.value == 'x':
            self.draw.arc( \
                [x - RING_RADIUS, y - RING_RADIUS, x + RING_RADIUS, y + RING_RADIUS], \
                start = 0, \
                end = 360, \
                fill = (0, 0, 0), \
                width = 1 \
            )

    # Shows the graph.
    def show(self):
        self.image.show()