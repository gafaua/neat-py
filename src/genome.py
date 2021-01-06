from node import Node
from connection import Connection
from innovationManager import InnovationManager
from settings import GenomeSettings
from errors import InvalidTopologyError
import matplotlib.pyplot as plt
import networkx as nx
import random

class Genome:
    def __init__(self, innovationManager, settings: GenomeSettings=None):
        self.innovationManager: InnovationManager = innovationManager

        self.network = []

        if settings is None: # create empty Genome
            self.nodes = {}
            self.connections = {}
            return

        self.settings = settings

        self.layers: int = 2

        inputs, bias, outputs = self.settings.inputs, self.settings.bias, self.settings.outputs
        # [inputs] [bias] [outputs]
        self.nodes = {i: Node(i, 0) for i in range(inputs + bias)}
        self.nodes.update({i: Node(i, 1) for i in range(inputs + bias, inputs + bias + outputs)})

        self.connections = {}
        for n1 in self.inputNodes():
            for n2 in self.outputNodes():
                self.createConnection(n1, n2)

        # genome is fully connected on creation
        self.availableNodes = []

    def __str__(self):
        value = "Genome\n\n"
        value += f"Inputs:  {self.settings.inputs}\n"
        value += f"Bias:    {self.settings.bias > 1}\n"
        value += f"Hidden:  {len(self.nodes) - self.settings.inputs - self.settings.outputs - self.settings.bias}\n"
        value += f"Outputs: {self.settings.outputs}\n"
        value += f"Layers:  {self.layers}\n\n"
        value += f"Nodes:\n"

        for node in self.nodes.values():
            value += f"{str(node)}\n"

        value += f"\nConnections:\n"

        for connection in self.connections.values():
            value += f"{str(connection)}\n"
        return value

    def inputNodes(self):
        # input + bias
        return [self.nodes[i] for i in range(self.settings.inputs + self.settings.bias)]

    def outputNodes(self):
        return [self.nodes[i + self.settings.inputs + self.settings.bias] for i in range(self.settings.outputs)]

    def plot(self, block=False, pauseTime=1.0, fname=None):
        # TODO add title
        G = nx.DiGraph()

        nodeColors = []

        for node in self.nodes.values():
            G.add_node(node.id, layer=node.layer)
            color = "black"
            if node.layer == 0:
                if node.id == self.settings.inputs: #bias
                    color = "blue"
                else:
                    color = "green"
            elif node.layer == self.layers - 1:
                color = "red"
            nodeColors.append(color)

        for connection in self.connections.values():
            if connection.enabled:
                G.add_edge(connection.inNode.id, connection.outNode.id, weight=connection.weight)

        colors, widths = [], []
        for u,v,data in G.edges(data=True):
            colors.append('blue' if data['weight'] > 0 else 'red')
            widths.append(abs(data['weight']))

        options = {
            'node_color': nodeColors,
            'node_size': 1000,
            'node_shape': 'o',#so^>v<dph8
            'width': widths,
            'arrowstyle': '-|>',
            'arrowsize': 20,
            'font_color': 'white',
            'font_size': 20,
            'edge_color': colors,
            'pos': nx.multipartite_layout(G, subset_key='layer'),
            'linewidths': 2.0,
            'with_labels': True
        }
        nx.draw_networkx(G, arrows=True, **options)

        if fname is not None:
            plt.savefig(fname=fname)

        if block:
            plt.show()
        else:
            plt.pause(pauseTime)

    def updateAvailableNodes(self):
        layerNodes = [set() for _ in range(self.layers)]
        nodes = self.nodes.values()

        for node in nodes:
            layerNodes[node.layer].add(node)

        maxConnectionsPerLayer = [set() for _ in range(self.layers)]
        possibleConnections = set()
        for i in reversed(range(self.layers)):
            maxConnectionsPerLayer[i].update(possibleConnections)
            possibleConnections.update(layerNodes[i])
        
        self.availableNodes = set()
        
        for node in nodes:
            connectedTo = set(map(lambda c: c.outNode, node.outputs))
            availableToConnect = maxConnectionsPerLayer[node.layer].difference(connectedTo)
            if len(availableToConnect) > 0:
                self.availableNodes.update(availableToConnect)
                self.availableNodes.add(node)

    def generateNetwork(self):
        if len(self.network) == len(self.nodes):
            return
        # first sort key is layer, second is id to make sure inputs and outputs are ordered
        self.network = sorted(self.nodes.values(), key=lambda n: (n.layer, n.id))

    def addConnection(self):
        if len(self.availableNodes) < 2:
            return

        def getTwoRandomNodes():
            n1, n2 = random.sample(self.availableNodes, 2)
            if n1.layer > n2.layer:
                nTemp = n1
                n1 = n2
                n2 = nTemp
            return n1, n2

        n1, n2 = getTwoRandomNodes()

        while n1.layer == n2.layer or n1.isConnectedTo(n2):
            n1, n2 = getTwoRandomNodes()

        self.createConnection(n1, n2, weight=random.uniform(-2,2))

    def addNode(self):
        if len(self.connections) == 0:
            self.addConnection()
        
        # disable old connection
        oldConnection = random.sample(list(self.connections.values()), 1)[0]
        oldConnection.enabled = False
        n1, n2 = self.nodes[oldConnection.inNode.id], self.nodes[oldConnection.outNode.id]

        # create a new node
        newId = self.innovationManager.getNodeId(oldConnection.innovationNumber, self)
        newNode = Node(id=newId, layer=n1.layer + 1)

        # shift upper layers if necessary to respect the topological order
        if newNode.layer == n2.layer:
            self.layers += 1
            for node in self.nodes.values():
                if node.layer >= newNode.layer:
                    node.layer += 1

        self.nodes[newId] = newNode

        # add connection n1 --1.0--> newNode
        self.createConnection(n1, newNode, 1.0)
        # add connection newNode --weight--> n2
        self.createConnection(newNode, n2, oldConnection.weight)

        self.updateAvailableNodes()

    def mutate(self):
        if len(self.connections) == 0:
            self.addConnection()
        
        # mutate weight
        if random.random() < self.settings.mutation.weightMutationRate:
            for c in self.connections.values():
                c.mutateWeight(self.settings.mutation.weightMutationStep, self.settings.mutation.weightMutationStepRate)
            # if random.random() < self.settings.mutation.togglesEnableMutationRate:
            #     c.enabled = not c.enabled

        # add connection
        if random.random() < self.settings.mutation.addConnectionMutationRate:
            self.addConnection()
        
        # add node
        if random.random() < self.settings.mutation.addNodeMutationRate:
            self.addNode()

    def createConnection(self, n1, n2, weight=1.0):
        innovationNumber = self.innovationManager.getConnectionInnovationNumber(n1.id, n2.id, self)
        newConnection = Connection(n1, n2, innovationNumber, weight)
        n1.addConnection(newConnection)
        self.connections[innovationNumber] = newConnection

    def generateOutputValues(self, inputValues):
        # ordering nodes according to their respective layer and id
        self.generateNetwork()

        inputs = inputValues + [1]*self.settings.bias

        # setting input values to the input nodes
        for i in range(self.settings.inputs + self.settings.bias):
            self.network[i].value = inputs[i]

        # resetting to 0 the values of every other nodes
        for i in range(self.settings.inputs + self.settings.bias, len(self.nodes)):
            self.network[i].value = 0

        # forward pass
        for node in self.network:
            node.forward()

        outputs = list(map(lambda n: n.value, self.network[-self.settings.outputs:]))
        return outputs

    @classmethod
    def crossover(cls, first, second, sameFitness=False):
        """
        Generates the crossover child between param first and param second
        
        This method assumes that first has a better fitness score than second

        first: Genome

        second: Genome
        """

        child = cls(first.innovationManager)
        child.settings = first.settings

        # randomly add common connections (matching genes)
        common = set(first.connections).intersection(set(second.connections))
        connections = [first.connections[c] if random.random() < 0.5 else second.connections[c] for c in common]

        # add excess and disjoint genes from the most fit parent or from the smallest parent if both have the same fitness
        disjointSrc = second if sameFitness and len(first.connections) > len(second.connections) else first
        connections += [disjointSrc.connections[c] for c in disjointSrc.connections if c not in common] 

        connections.sort(key=lambda c: (c.inNode.layer, c.inNode.id))

        #add input & bias & output nodes
        for n in first.inputNodes(): child.nodes[n.id] = n.clone()
        for n in first.outputNodes(): child.nodes[n.id] = n.clone()

        inNodeNotFound = False
        # add connections
        for c in connections:
            inNode = child.nodes.get(c.inNode.id)
            outNode = child.nodes.get(c.outNode.id)
            if inNode is None:
                inNode = c.inNode.clone()
                child.nodes[inNode.id] = inNode
            if outNode is None:
                outNode = c.outNode.clone()
                child.nodes[outNode.id] = outNode

            enabled = c.enabled
            i = c.innovationNumber
            if i in common and not (first.connections[i].enabled and second.connections[i].enabled):
                enabled = random.random() < 0.25

            connection = Connection(inNode, outNode, c.innovationNumber, c.weight, enabled)
            inNode.addConnection(connection)
            child.connections[connection.innovationNumber] = connection

        # compute layers
        queue = []

        for n in child.inputNodes():
            queue.append(n)

        maxLayer = 1

        while len(queue) > 0:
            node = queue.pop()
            for n in node.neighbours():
                if n.layer <= node.layer:
                    n.layer = node.layer + 1
                    if n.layer > maxLayer:
                        maxLayer += 1
                queue.insert(0, n)
        
        child.layers = maxLayer + 1
        for n in child.outputNodes():
            n.layer = maxLayer

        child.updateAvailableNodes()

        # if False and not child.isTopologyValid():
        #     # make sure that the crossover worked correctly
        #     raise InvalidTopologyError("There was a problem during the crossover process")

        return child

    def clone(self):
        copy = Genome(self.innovationManager)
        copy.settings = self.settings
        copy.layers = self.layers

        for n in self.nodes.values():
            node = n.clone()
            node.layer = n.layer
            copy.nodes[n.id] = node

        for c in self.connections.values():
            inNode = copy.nodes[c.inNode.id]
            outNode = copy.nodes[c.outNode.id]

            connection = Connection(inNode, outNode, c.innovationNumber, c.weight, c.enabled)
            inNode.addConnection(connection)
            copy.connections[connection.innovationNumber] = connection

        copy.updateAvailableNodes()
        return copy

    def isTopologyValid(self):
        for c in self.connections.values():
            if c.inNode.layer >= c.outNode.layer:
                return False
        if len(self.connections) > 0:
            # inputs
            for n in self.inputNodes():
                if n.layer != 0:
                    return False
            # outputs
            for n in self.outputNodes():
                if n.layer != self.layers - 1:
                    return False

        return True

    def distance(self, genome):
        """
        Compute the distance between self and param genome
        """
        n1 = len(self.connections)
        n2 = len(genome.connections)
        N = max(n1, n2)
        if N < 20:
            N = 1

        common = set(self.connections).intersection(set(genome.connections))
        weightDistanceAvg = 0

        for c in common:
            weightDistanceAvg += abs(self.connections[c].weight - genome.connections[c].weight)

        return self.settings.distance.coeffDisjoint * (n1 + n2 - 2*len(common)) / N + \
               self.settings.distance.coeffWeights * weightDistanceAvg / len(common)
