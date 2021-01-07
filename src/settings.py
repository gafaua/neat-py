from dataclasses import dataclass

@dataclass
class MutationSettings:
    def __init__(self,
                 weightMutationRate: float = 0.8,
                 weightMutationStep: float = 2.5,
                 weightMutationStepRate: float = 0.8,
                 weightMutationNewRate: float = 0.3,
                 addConnectionMutationRate: float = 0.1,
                 addNodeMutationRate: float = 0.01,
                 togglesEnableMutationRate: float = 0.05,
                 reEnableMutationRate: float = 0.2):
        self.weightMutationRate = weightMutationRate
        self.weightMutationStep = weightMutationStep
        self.weightMutationStepRate = weightMutationStepRate
        self.weightMutationNewRate = weightMutationNewRate
        self.addConnectionMutationRate = addConnectionMutationRate
        self.addNodeMutationRate = addNodeMutationRate
        self.togglesEnableMutationRate = togglesEnableMutationRate
        self.reEnableMutationRate = reEnableMutationRate

@dataclass
class DistanceSettings:
    def __init__(self,
                 coeffDisjoint: float = 1.1,
                 coeffWeights: float = 0.4):
        self.coeffDisjoint = coeffDisjoint
        self.coeffWeights = coeffWeights

@dataclass
class GenomeSettings:
    def __init__(self,
                 inputs: int = 0,
                 outputs: int = 0,
                 bias: int = 0,
                 mutationSettings: MutationSettings = MutationSettings(),
                 distanceSettings: DistanceSettings = DistanceSettings()):
        self.inputs = inputs
        self.outputs = outputs
        self.bias = bias
        self.mutation = mutationSettings
        self.distance = distanceSettings

@dataclass
class PopulationSettings:
    def __init__(self,
                 size: int,
                 genomeSettings: GenomeSettings,
                 speciesDistanceThreshold: float = 3,
                 cullRate: float = 0.5,
                 maxStaleness: int = 100,
                 crossoverRate: float = 0.75,
                 interSpeciesCrossoverRate: float = 0.0001):
        self.size = size
        self.genome = genomeSettings
        self.speciesDistanceThreshold = speciesDistanceThreshold
        self.cullRate = cullRate
        self.maxStaleness = maxStaleness
        self.crossoverRate = crossoverRate
        self.interSpeciesCrossoverRate = interSpeciesCrossoverRate