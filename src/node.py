import enum
from utils import sigmoid

class Node:
    def __init__(self, id, layer):
        self.id = id
        self.value = 0
        self.layer = layer
        self.outputs = []    # All connections that receive this node's value as inNode

    def __str__(self):
        value = f"Node ({self.id}) [{self.layer}] connected to -> {list(map(lambda x: x.outNode.id, self.outputs))}"
        return value
    
    def __eq__(self, value):
        return self.id == value.id

    def __hash__(self):
        return hash(self.id)

    def clone(self):
        # returns an empty copy of self
        return Node(self.id, 0)
    
    def neighbours(self):
        return list(map(lambda c: c.outNode, self.outputs))
    
    def addConnection(self, connection):
        self.outputs.append(connection)

    def isConnectedTo(self, node):
        return node.id in map(lambda x: x.outNode.id, self.outputs)
    
    def forward(self):
        if self.layer > 0:
            self.value = sigmoid(self.value)
        
        for c in self.outputs:
            if c.enabled:
                c.outNode.value += self.value * c.weight
    