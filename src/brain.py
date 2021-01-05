from genome import Genome
from settings import GenomeSettings
from innovationManager import InnovationManager
from utils import sigmoid
from matplotlib import pyplot as plt

class Brain:
    """
    Base class to extend for a brain used in a population

    Methods to override:
    >def setInputValues(self):
    This method should fill the self.inputValues list property
    
    >def fitnessEvaluationMethod(self):
    This method should compute and return the fitness of the brain

    """
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

    @classmethod
    def crossover(cls, first, second):
        genome = Genome.crossover(first.genome, second.genome, sameFitness=first.fitness==second.fitness)
        return cls(genome)
    
    @classmethod
    def clone(cls, brain):
        copy = cls(brain.genome.clone(), generation=brain.generation)
        copy.fitness = brain.fitness
        return copy


    def setInputValues(self):
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
            self.setInputValues()
            self.generateOutputValues()
            score += 1
        return someFunction(score)

        Typical implementation for other:
        self.setInputValues()
        self.generateOutputValues()
        return 1 / distanceWithExpectedOutputs(self.outputValues)
        """

        raise NotImplementedError

    def generateOutputValues(self):
        self.outputValues = self.genome.generateOutputValues(self.inputValues)

    def evaluateFitness(self):
        self.fitness = self.fitnessEvaluationMethod()

    def mutate(self):
        self.genome.mutate()

    def distance(self, brain):
        return self.genome.distance(brain.genome)

    def plot(self, block=False, pauseTime=1.0, fname=None):
        plt.clf()
        plt.title(f"Fitness: {self.fitness}")
        self.genome.plot(block, pauseTime, fname)