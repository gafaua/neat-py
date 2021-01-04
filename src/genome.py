from node import Node
from connection import Connection
from innovationManager import InnovationManager
from settings import GenomeSettings
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
        self.maxConnections = len(self.connections)

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
        # TODO differenciate inputs/bias/outputs
        #      add title
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
        plt.clf()
        nx.draw_networkx(G, arrows=True, **options)

        if fname is not None:
            plt.savefig(fname=fname)

        if block:
            plt.show()
        else:
            plt.pause(pauseTime)

    def computeMaxConnections(self):
        maxConnections = 0
        layerNodes = [0] * self.layers
        nodes = self.nodes.values()

        for layer in range(self.layers):
            for node in nodes:
                if node.layer == layer:
                    layerNodes[layer] += 1

        for i in range(self.layers):
            for j in range(i + 1, self.layers):
                maxConnections += layerNodes[i] * layerNodes[j]

        self.maxConnections = maxConnections

    def generateNetwork(self):
        if len(self.network) == len(self.nodes):
            return
        # first sort key is layer, second is id to make sure inputs and outputs are ordered
        self.network = sorted(self.nodes.values(), key=lambda n: (n.layer, n.id))

    def isFullyConnected(self):
        return len(self.connections) == self.maxConnections

    def addConnection(self):
        if self.isFullyConnected():
            return

        # TODO remove first fully connected nodes
        def getTwoRandomNodes():
            n1, n2 = random.sample(list(self.nodes.values()), 2)
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
        self.createConnection(n1, newNode)
        # add connection newNode --weight--> n2
        self.createConnection(newNode, n2, oldConnection.weight)

        self.computeMaxConnections()

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

    def generateOutputs(self, inputValues):
        # ordering nodes according to their respective layer and id
        self.generateNetwork()
        print("Network:")
        for node in self.network:
            print(node)

        inputs = inputValues + [1]*self.settings.bias

        # setting input values to the input nodes
        for i in range(self.settings.inputs + self.settings.bias):
            self.network[i] = inputs[i]

        # resetting to 0 the values of every other nodes
        for i in range(self.settings.inputs + self.settings.bias, len(self.nodes)):
            self.network[i].value = 0

        # forward pass
        for node in self.network:
            node.forward()

        outputs = list(map(lambda n: n.value, self.network[-self.settings.outputs:]))
        return outputs

    def crossover(self, genome, sameFitness=False):
        """
        Generates the crossover child between self and param genome
        This method assumes that self has a better fitness score than genome
        """

        child = Genome(self.innovationManager)

        child.settings = self.settings

        connections = []
        if sameFitness:
            # add all disjoint and excess connection genes and randomly select common ones
            common = set(self.connections).intersection(set(genome.connections))
            connections = [self.connections[c] for c in self.connections if c not in common] + \
                          [genome.connections[c] for c in genome.connections if c not in common] + \
                          [self.connections[c] if random.random() < 0.5 else genome.connections[c] for c in common]
        else:
            connections = [c for c in self.connections.values()] + \
                          [genome.connections[c] for c in genome.connections if c not in self.connections]

        connections.sort(key=lambda c: c.inNode.layer)
        #add input & bias & output nodes
        for n in self.inputNodes(): child.nodes[n.id] = n.clone()
        for n in self.outputNodes(): child.nodes[n.id] = n.clone()
        pr = False

        # add connections
        for c in connections:
            inNode = child.nodes.get(c.inNode.id)
            outNode = child.nodes.get(c.outNode.id)
            if inNode is None:
                print(c)
                inNode = c.inNode.clone()
                child.nodes[inNode.id] = inNode
                pr = True
            if outNode is None:
                outNode = c.outNode.clone()
                child.nodes[outNode.id] = outNode
            connection = Connection(inNode, outNode, c.innovationNumber, c.weight, c.enabled)
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

        child.computeMaxConnections()

        if pr:
            print(child)
            child.plot(block=True)
            

        return child

    def clone(self):
        copy = Genome(self.innovationManager)
        copy.settings = self.settings
        copy.maxConnections = self.maxConnections
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

    def distance(self, genome, coeffDisjoint=1.0, coeffWeights=1.0):
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

        return coeffDisjoint * (n1 + n2 - 2*len(common)) / N + coeffWeights * weightDistanceAvg / len(common)
