from dataclasses import dataclass
from settings import GenomeSettings

@dataclass
class ConnectionInnovation:
    def __init__(self, fromNode, toNode, innovationNumber):
        # This connection was created between fromNode and toNode
        self.fromNode: int = fromNode
        self.toNode: int = toNode
        self.innovationNumber: int = innovationNumber

@dataclass
class NodeInnovation:
    def __init__(self, connection, fromNode, toNode, innovationNumber):
        # This node was created by breaking this connection
        self.connection: int = connection
        self.fromNode: int = fromNode
        self.toNode: int = toNode

        self.innovationNumber: int = innovationNumber

class InnovationManager:
    def __init__(self, genomeSettings: GenomeSettings):
        self.connectionInnovationCounter = 0
        self.connectionInnovationHistory = []

        self.nodeInnovationCounter = genomeSettings.inputs + genomeSettings.outputs + genomeSettings.bias
        self.nodeInnovationHistory = []


    def getConnectionInnovationNumber(self, fromNode, toNode):
        innovation = None
  
        # find already existing matching connection
        for innov in self.connectionInnovationHistory:
            if innov.fromNode == fromNode and innov.toNode == toNode:
                innovation = innov
                break
   
        if innovation is not None:
            return innovation.innovationNumber

        innovation = ConnectionInnovation(fromNode, toNode, self.connectionInnovationCounter)
        self.connectionInnovationHistory.append(innovation)
        self.connectionInnovationCounter += 1
        return innovation.innovationNumber

    def getNodeId(self, connection, fromNode, toNode):
        innovation = None

        # find already existing matching node
        for innov in self.nodeInnovationHistory:
            if innov.fromNode == fromNode and innov.toNode == toNode and innov.connection == connection:
                innovation = innov
                break
        
        if innovation is not None:
            return innovation.innovationNumber

        innovation = NodeInnovation(connection, fromNode, toNode, self.nodeInnovationCounter)
        self.nodeInnovationHistory.append(innovation)
        self.nodeInnovationCounter += 1
        return innovation.innovationNumber

