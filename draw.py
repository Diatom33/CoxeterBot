from PIL import Image, ImageDraw
from node import Node, Graph
import math

# Constants:
NODE_RADIUS = 3
RING_RADIUS = 6
PADDING = 10

# Draws a graph.
class Draw:
    # Class constructor.
    def __init__(self, graph):
        # Variables to see where the next node goes.
        # Provisional, probably.
        self.x, self.y = 0, 0

        # The elements of the graph.
        self.nodes = []
        self.edges = []

        # The bounding box of the graph.
        self.minX, self.minY, self.maxX, self.maxY = math.inf, math.inf, -math.inf, -math.inf

        for component in graph.components():
            self.add(component)

    # Adds a new component to the diagram.
    # Currently, just puts everything in a straight line.
    # TODO: make this draw the trees prettily.
    def add(self, component):
        for node in component:
            self.addNode(node, (self.x, self.y))
            self.x += 20

        self.x += 10

    # Adds a node in a particular position.
    def addNode(self, node, coords):
        newNode = {
            "value": node.value,
            "x": coords[0],
            "y": coords[1]
        }

        self.updateBoundingBox(coords)

        self.nodes.append(newNode)

    # Updates the bounding box of the nodes.
    def updateBoundingBox(self, coords):
        x, y = coords

        self.minX = min(self.minX, x)
        self.maxX = max(self.maxX, x)
        self.minY = min(self.minY, y)
        self.maxY = max(self.maxY, y)

    # Gets the size of the bounding box.
    def size(self):
        return (self.maxX - self.minX + 2 * PADDING, self.maxY - self.minY + 2 * PADDING)

    # Draws the graph.
    def draw(self):
        image = Image.new('RGB', size = self.size(), color = 'white')
        draw = ImageDraw.Draw(image)

        for node in self.nodes:
            value = node['value']
            x = node['x'] - self.minX + PADDING
            y = node['y'] - self.minX + PADDING

            # Chooses the fill color.
            if value == 's':
                nodeFill = 'white'
                radius = RING_RADIUS
            else:
                nodeFill = 'black'
                radius = NODE_RADIUS

            # Draws the node.

            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius],
                fill = nodeFill,
                outline = 'black',
                width = 1
            )

            # Draws the ring.
            if value == 'x':
                draw.arc(
                    [x - RING_RADIUS, y - RING_RADIUS, x + RING_RADIUS, y + RING_RADIUS],
                    start = 0,
                    end = 360,
                    fill = 'black',
                    width = 1
                )

        return image

    # Shows the graph.
    def show(self):
        self.draw().show()

    # Saves the graph.
    def save(self, *args):
        self.draw().save(*args)