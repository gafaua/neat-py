from genome import Genome
from settings import GenomeSettings
from innovationManager import InnovationManager

class Brain:
    def __init__(self, genome, generation=0):
        self.genome: Genome = genome
        self.generation = generation
        self.fitness = 0.0

        self.inputValues = []
        self.outputValues = []
    
    def __str__(self):
        return f"Brain - Fitness: {self.fitness} - Generation: {self.generation} - Neurons: {len(self.genome.nodes) + len(self.genome.connections)}"

    @classmethod
    def create(cls, manager: InnovationManager, settings: GenomeSettings):
        genome = Genome(manager, settings)
        return cls(genome)

    def fetchInputs(self):
        """
        Method to overload to get inputs to feed to the neural network
        returns an array of inputs
        """
        raise NotImplementedError
        
    def fitnessEvaluationMethod(self):
        """
        Method to overload to establish an evaluation method
        This method returns a float fitness value

        Typical implementation for game:
        score = 0
        while(alive):
            self.fetchInputs()
            self.generateOutputs()
            score += 1
        return score * someFactor

        Typical implementation for other:
        self.fetchInputs()
        self.generateOutputs()
        return 1 / distanceWithExpectedOutputs(self.outputValues)
        """
        return self.genome.layers**2
        #raise NotImplementedError

    def generateOutputs(self):
        self.outputValues = self.genome.generateOutputs(inputValues)

    def evaluateFitness(self):
        self.fitness = self.fitnessEvaluationMethod()

    def mutate(self):
        self.genome.mutate()

    def crossover(self, brain):
        genome = self.genome.crossover(brain.genome, sameFitness=self.fitness==brain.fitness)
        return Brain(genome)

    def clone(self):
        copy = Brain(self.genome.clone(), generation=self.generation)
        copy.fitness = self.fitness
        return copy

    def distance(self, brain):
        return self.genome.distance(brain.genome)
