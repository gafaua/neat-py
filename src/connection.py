import random

class Connection:
    def __init__(self, inNode, outNode, innovationNumber, weight=1.0, enabled=True):
        self.inNode = inNode
        self.outNode = outNode
        self.innovationNumber = innovationNumber
        self.weight = weight
        self.enabled = enabled
    
    def __str__(self):
        pad = " " if self.weight > 0 else ""
        value = f"[{self.inNode.id}-{self.inNode.layer}] ----({pad}{self.weight:.3f})----> [{self.outNode.id}-{self.outNode.layer}]" if self.enabled else f"[{self.inNode.id}] /-/-({pad}{self.weight:.3f})/-/-> [{self.outNode.id}]"
        value += f" I.N.: {self.innovationNumber}"
        return value
    
    def __eq__(self, value):
        return self.innovationNumber == value.innovationNumber

    def __ne__(self, value):
        return self.innovationNumber != value.innovationNumber
    
    def __hash__(self):
        return hash(self.innovationNumber)

    def clone(self):
        return Connection(self.inNode.clone(), self.outNode.clone(), self.innovationNumber, weight=self.weight, enabled=self.enabled)

    def mutateWeight(self, step, stepRate):
        if random.random() < stepRate:
            self.weight += random.uniform(-step, step)
        else:
            self.weight = random.uniform(-2,2)
