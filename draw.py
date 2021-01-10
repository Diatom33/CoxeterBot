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
        self.nodes = []

        for component in graph.components():
            self.add(component)

    # Adds a new component to the diagram.
    # Currently, just puts everything in a straight line.
    # TODO: make this draw the trees prettily.
    def add(self, component):
        for node in component:
            self.addNode(node, (self.x, self.y))
            self.x += 20

        self.x += 20

    # Adds a node in a particular position.
    def addNode(self, node, coords):
        newNode = {
            "value": node.value,
            "x": coords[0],
            "y": coords[1]
        }

        self.nodes.append(newNode)

    # Draws the graph.
    def draw(self):
        image = Image.new('RGB', size = (100, 50), color = (255, 255, 255))
        draw = ImageDraw.Draw(image)

        for node in self.nodes:
            value = node['value']
            x = node['x']
            y = node['y']

            # Chooses the fill color.
            if value == 's':
                nodeFill = (255, 255, 255)
                radius = RING_RADIUS
            else:
                nodeFill = (0, 0, 0)
                radius = NODE_RADIUS

            # Draws the node.

            draw.ellipse( \
                [x - radius, y - radius, x + radius, y + radius], \
                fill = nodeFill, \
                outline = (0, 0, 0), \
                width = 1
            )

            # Draws the ring.
            if value == 'x':
                draw.arc( \
                    [x - RING_RADIUS, y - RING_RADIUS, x + RING_RADIUS, y + RING_RADIUS], \
                    start = 0, \
                    end = 360, \
                    fill = (0, 0, 0), \
                    width = 1 \
                )

        return image

    # Shows the graph.
    def show(self):
        self.draw().show()

    # Saves the graph.
    def save(self, *args):
        self.draw().save(*args)