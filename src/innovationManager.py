from dataclasses import dataclass
from settings import GenomeSettings

@dataclass
class ConnectionInnovation:
    def __init__(self, fromNode, toNode, innovationNumber, genome):
        # This connection was created between fromNode and toNode
        self.fromNode: int = fromNode
        self.toNode: int = toNode
        self.innovationNumber: int = innovationNumber
        self.genomeState = list(genome.connections)

@dataclass
class NodeInnovation:
    def __init__(self, connection, innovationNumber, genome):
        # This node was created by breaking this connection
        self.connection: int = connection
        self.innovationNumber: int = innovationNumber
        self.genomeState = list(genome.nodes)

class InnovationManager:
    def __init__(self, genomeSettings: GenomeSettings):
        self.connectionInnovationCounter = 0
        self.connectionInnovationHistory = []

        self.nodeInnovationCounter = genomeSettings.inputs + genomeSettings.outputs + genomeSettings.bias
        self.nodeInnovationHistory = []

    def findMatchingConnection(self, fromNode, toNode, genome):
        for innovation in self.connectionInnovationHistory:
            if innovation.fromNode != fromNode or innovation.toNode != toNode or len(innovation.genomeState) != len(genome.connections):
                continue
            if not any(c not in innovation.genomeState for c in genome.connections):
                return innovation
        return None

    def getConnectionInnovationNumber(self, fromNode, toNode, genome):
        innovation = self.findMatchingConnection(fromNode, toNode, genome)        
        
        if innovation is not None:
            return innovation.innovationNumber

        innovation = ConnectionInnovation(fromNode, toNode, self.connectionInnovationCounter, genome)
        self.connectionInnovationHistory.append(innovation)
        self.connectionInnovationCounter += 1
        return innovation.innovationNumber

    def findMatchingNode(self, connection, genome):
        for innovation in self.nodeInnovationHistory:
            if innovation.connection != connection or len(innovation.genomeState) != len(genome.nodes):
                continue
            if not any(n not in innovation.genomeState for n in genome.nodes):
                return innovation
        return None

    def getNodeId(self, connection, genome):
        innovation = self.findMatchingNode(connection, genome)        
        
        if innovation is not None:
            return innovation.innovationNumber

        innovation = NodeInnovation(connection, self.nodeInnovationCounter, genome)
        self.nodeInnovationHistory.append(innovation)
        self.nodeInnovationCounter += 1
        return innovation.innovationNumber

