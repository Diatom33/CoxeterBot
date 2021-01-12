from PIL import Image, ImageDraw, ImageFont
from node import Node, Graph
from cdError import CDError
import math

# Constants:
SCALE = 0.8

NODE_RADIUS = 12
NODE_BORDER_WIDTH = 4

RING_RADIUS = 24
RING_WIDTH = 4

NODE_SPACING = 90
COMPONENT_SPACING = 90

LINE_WIDTH = 8
TEXT_DISTANCE = 20

ELLIPSIS_RADIUS = 3

FONT_NAME = "Lora-Regular"
FONT_OUTLINE = 2

EDGE_FONT_SIZE = 24
NODE_FONT_SIZE = 18
HOLOSNUB_FONT_SIZE = 36

EDGE_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", EDGE_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)
NODE_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", NODE_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)
HOLOSNUB_FONT = ImageFont.truetype(f"../ttf/{FONT_NAME}.ttf", HOLOSNUB_FONT_SIZE, layout_engine = ImageFont.LAYOUT_BASIC)

PADDING = 40

# Draws a graph.
class Draw:
    # Class constructor.
    def __init__(self, graph):
        # Variables to see where the next node goes.
        # Provisional, probably.
        self.x, self.y = 0, 0

        # The elements of the graph.
        self.nodes, self.edges = [], []

        # The bounding box of the graph.
        self.minX, self.minY, self.maxX, self.maxY = math.inf, math.inf, -math.inf, -math.inf

        for component in graph.components():
            self.add(component)

    def currentPos(self):
        return (self.x, self.y)

    # Adds a new component to the diagram.
    # Currently, just puts everything in a straight line.
    # TODO: make this draw the trees prettily.
    def add(self, component):
        straight, firstNode = self.isStraight(component)

        if straight:
            drawingMode = 'line'

            self.addNode(firstNode, self.currentPos(), drawingMode)
            prevNode = firstNode

            if firstNode.degree() != 0:
                node = firstNode.neighbors[0]

                while node.degree() != 1:
                    self.x += NODE_SPACING
                    self.addNode(node, self.currentPos(), drawingMode)

                    if node.neighbors[0] is prevNode:
                        prevNode = node
                        node = node.neighbors[1]
                    else:
                        prevNode = node
                        node = node.neighbors[0]

                self.x += NODE_SPACING
                self.addNode(node, self.currentPos(), drawingMode)
        else:
            drawingMode = 'polygon'

            n = len(component)
            radius = NODE_SPACING / (2 * math.sin(math.pi / n))
            self.x += radius

            angle = math.pi / 2 + math.pi / n
            for node in component:
                self.addNode(node, (
                    self.x + radius * math.cos(angle),
                    self.y + radius * math.sin(angle)
                ), drawingMode)
                angle += 2 * math.pi / n

            self.x += radius

        self.x += COMPONENT_SPACING

    # Adds a node in a particular position.
    def addNode(self, node, coords, drawingMode):
        # Adds the node.
        newNode = {
            "value": node.value,
            "xy": (coords[0], coords[1])
        }
        self.updateBoundingBox(coords)

        # Adds the arrayIndex property to the node, storing its index in the array.
        node.arrayIndex = len(self.nodes)
        self.nodes.append(newNode)

        # Adds edges.
        i = 0
        for neighbor in node.neighbors:
            # Guarantees no duplicates.
            if hasattr(neighbor, 'arrayIndex'):
                self.edges.append({
                    0: neighbor.arrayIndex,
                    1: node.arrayIndex,
                    "label": node.edgeLabels[i],
                    "drawingMode": drawingMode
                })

            i += 1

    # A connected graph is a line graph iff every vertex has degree ≤ 2,
    # and at least one vertex has degree 1.
    # Returns whether the graph is a line graph, and if so, its first node (in string order).
    def isStraight(self, component):
        if len(component) < 3:
            return (True, component[0])

        isCycle = True
        firstNode = None

        for node in component:
            degree = node.degree()

            if degree > 2:
                return (False, None)
            elif degree == 1:
                isCycle = False
                if firstNode is None or firstNode.stringIndex > node.stringIndex:
                    firstNode = node

        return (not isCycle, firstNode)

    # Transforms node coordinates to image coordinates.
    def transformCoords(self, coords):
        return (coords[0] - self.minX + PADDING, coords[1] - self.minY + PADDING)

    # Updates the bounding box of the nodes.
    def updateBoundingBox(self, coords):
        x, y = coords

        self.minX = min(self.minX, x)
        self.maxX = max(self.maxX, x)
        self.minY = min(self.minY, y)
        self.maxY = max(self.maxY, y)

    # Gets the size of the bounding box.
    def size(self):
        return (
            round(self.maxX - self.minX + 2 * PADDING),
            round(self.maxY - self.minY + 2 * PADDING)
        )

    # Draws the graph.
    def draw(self):
        self.image = Image.new('RGB', size = self.size(), color = 'white')
        self.draw = ImageDraw.Draw(self.image)

        # Draws the edges.
        for edge in self.edges:
            node0, node1, label = self.nodes[edge[0]], self.nodes[edge[1]], edge['label']

            # Edge coordinates.
            edgeXy = (
                self.transformCoords(node0['xy']),
                self.transformCoords(node1['xy']),
            )

            # Text coordinates.
            textXy = list(map(lambda a, b: (a + b) / 2, edgeXy[0], edgeXy[1]))
            if edge['drawingMode'] == 'line':
                textXy[1] += TEXT_DISTANCE

            # Draws edge.
            if label == 'Ø':
                edgeType = 'dotted'
            elif label[:3] == '...':
                edgeType = 'ellipsis'
            else:
                edgeType = 'normal'

            self.drawEdge(edgeXy, edgeType)

            # Draws label.
            if edgeType == 'normal' and label != '3':
                self.drawText(textXy, label, textType = 'edge')

        # Draws each node.
        for node in self.nodes:
            value = node['value']
            xy = self.transformCoords(node['xy'])

            # Chooses the fill color.
            if value == 's' or value == '+':
                nodeFill = 'white'
                radius = RING_RADIUS
            else:
                nodeFill = 'black'
                radius = NODE_RADIUS

            # Draws the node.
            self.__drawCircle(xy = xy, radius = radius, fill = nodeFill)

            # Draws the ring.
            if value != 'o' and value != 's':
                self.__drawRing(xy = xy, radius = RING_RADIUS, fill = 'black')

                # Draws the mark.
                if value != 'x':
                    if value == '+':
                        textType = 'holosnub'
                    else:
                        textType = 'node'

                    self.drawText(xy = xy, text = value, textType = textType)

        return self.image.resize(
            size = (round(self.image.size[0] * SCALE), round(self.image.size[1] * SCALE)),
            resample = Image.BICUBIC
        )

    # Draws an edge on the image, of one of various parts..
    def drawEdge(self, xy, edgeType):
        if edgeType == 'normal':
            self.__drawLine(
                xy = xy,
                width = LINE_WIDTH,
                fill = 'black'
            )

        elif edgeType == 'dotted':
            # Number of dashes in edge.
            dashes = 5

            # Direction vector of each dash.
            delta = tuple(map(lambda x, y: (y - x) / (2 * dashes - 1), xy[0], xy[1]))

            xy = list(xy)
            xy[1] = tuple(map(lambda x, y: x + y, xy[0], delta))

            for i in range(dashes):
                self.__drawLine(
                    xy = tuple(xy),
                    width = LINE_WIDTH,
                    fill = 'black'
                )

                xy[0] = tuple(map(lambda x, y: x + 2 * y, xy[0], delta))
                xy[1] = tuple(map(lambda x, y: x + 2 * y, xy[1], delta))

        elif edgeType == 'ellipsis':
            # Controls the dot spacing.
            spacing = 6

            # Direction vector between two ellipses.
            delta = tuple(map(lambda x, y: (y - x) / spacing, xy[0], xy[1]))

            xy = tuple(map(lambda x, y: x + y * (spacing / 2 - 1), xy[0], delta))

            for i in range(3):
                self.__drawCircle(
                    xy = xy,
                    radius = ELLIPSIS_RADIUS,
                    fill = 'black'
                )

                xy = tuple(map(lambda x, y: x + y, xy, delta))
        else:
            self.error("Edge type not recognized.", dev = True)

    # Draws text with a border at some particular location.
    def drawText(self, xy, text, textType):
        # Configures text attributes.
        if textType == 'node':
            font = NODE_FONT
            foreColor = 'white'
            backColor = 'black'

            # Offset, seems necessary for some reason.
            xy = list(map(lambda a, b: a + b, xy, (1, -2)))
        elif textType == 'holosnub':
            font = HOLOSNUB_FONT
            foreColor = 'black'
            backColor = 'white'

            # Offset, seems necessary for some reason.
            xy = list(map(lambda a, b: a + b, xy, (0.5, -3)))
        elif textType == 'edge':
            font = EDGE_FONT
            foreColor = 'black'
            backColor = 'white'
        else:
            self.error("Text type not recognized.", dev = True)

        # Positions text correctly.
        textSize = self.draw.textsize(text = text, font = font)
        xy = list(map(lambda a, b: a - b / 2, xy, textSize))

        # Draws border.
        self.__drawText(xy = (xy[0] - FONT_OUTLINE, xy[1]), text = text, fill = backColor, font = font)
        self.__drawText(xy = (xy[0] + FONT_OUTLINE, xy[1]), text = text, fill = backColor, font = font)
        self.__drawText(xy = (xy[0], xy[1] - FONT_OUTLINE), text = text, fill = backColor, font = font)
        self.__drawText(xy = (xy[0], xy[1] + FONT_OUTLINE), text = text, fill = backColor, font = font)

        # Overlays text.
        self.__drawText(xy = xy, text = text, fill = foreColor, font = font)

    # Primitive to draw a line on the image.
    def __drawLine(self, xy, width, fill):
        # Rounds coordinates.
        xy = tuple(map(lambda x: tuple(map(round, x)), xy))

        self.draw.line(
            xy = xy,
            width = width,
            fill = fill
        )

    # Primitive to draw a circle on the image.
    def __drawCircle(self, xy, radius, fill):
        # Rounds coordinates.
        x, y = xy
        xy = tuple(map(round, (x - radius, y - radius, x + radius, y + radius)))

        self.draw.ellipse(
            xy = xy,
            fill = fill,
            outline = 'black',
            width = NODE_BORDER_WIDTH
        )

    # Primitive to draw a ring on the image.
    def __drawRing(self, xy, radius, fill):
        # Rounds coordinates.
        x, y = xy
        xy = tuple(map(round, (x - radius, y - radius, x + radius, y + radius)))

        self.draw.arc(
            xy = xy,
            start = 0,
            end = 360,
            fill = 'black',
            width = RING_WIDTH
        )

    # Primitive to draw text on the image.
    def __drawText(self, xy, text, fill, font):
        xy = tuple(map(round, xy))
        self.draw.text(xy = xy, text = text, fill = fill, font = font)

    # Shows the graph.
    def show(self):
        self.draw().show()

    # Saves the graph.
    def save(self, *args):
        self.draw().save(*args)

    def error(self, text, dev = False):
        msg = f"Graph drawing failed. {text}"

        if dev:
            raise Exception(msg)
        else:
            raise CDError(msg)