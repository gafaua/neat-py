from brain import Brain
import random

class Species:
    def __init__(self, base: Brain):
        self.BrainClass = type(base)

        self.champion: Brain = self.BrainClass.clone(base)
        self.fitness = self.champion.fitness
        self.avgAdjustedFitness = 0
        
        self.population = [base]

        self.staleness = 0

    def __str__(self):
        value = f"Brains: {len(self.population)} Fitness: {self.fitness} Staleness: {self.staleness}\n"
        # value += f"\n"
        # value += f"\n"
        #for i, b in enumerate(self.population): value += f"   {i+1}.{str(b)}\n"
        return value

    def shouldContain(self, brain, threshold):
        return self.champion.distance(brain) < threshold

    def add(self, brain):
        self.population.append(brain)

    def sort(self):
        """
        Sort species population by fitness score
        make sure that this generation's fitness has been computed before!
        """
        self.population.sort(key=lambda b: b.fitness, reverse=True)

        if self.population[0].fitness > self.fitness:
            self.champion = self.BrainClass.clone(self.population[0])
            self.fitness = self.champion.fitness
            self.staleness = 0
        else:
            self.staleness += 1 # this species has not improve this generation

    def selectBrain(self):
        """
        Randomly selects a brain from this species w.r.t. its fitness.

        call .sort() before!
        """
        fitnessSum = 0
        for b in self.population: fitnessSum += b.fitness

        r = random.random() * fitnessSum
        runningSum = 0
        for b in self.population:
            runningSum += b.fitness
            if r < runningSum: 
                return b
        print(f"ERROR IN THE BRAIN SELECTION PROCESS: fitnessSum: {fitnessSum}, r: {r}, runningSum: {runningSum}")
        print(self)

    def updateAvgAdjustedFitness(self):
        """
        Updates this species average fitness

        make sure that this generation's fitness has been computed before!
        """

        self.avgAdjustedFitness = 0

        for b in self.population: 
            self.avgAdjustedFitness += b.fitness/len(self.population)

        self.avgAdjustedFitness /= len(self.population)

    def cull(self, cullRate=0.5):
        """
        Removes worst performing brains form population

        call .sort() before!
        """
        # don't cull if it leaves less than 2 brains
        if len(self.population)*(1-cullRate) < 2: 
            return
        
        for _ in range(int(len(self.population)*cullRate)):
            self.population.pop()

    def generateChild(self):
        """
        Generates a mutated clone child from this species
        """
        child = self.BrainClass.clone(self.selectBrain())
        child.mutate()
        return child

    def mate(self, species):
        """
        Generates a child by crossover between a child from this species
        a child from param species
        """
        parent1 = self.selectBrain()
        parent2 = species.selectBrain()
        if parent1.fitness > parent2.fitness:
            return self.BrainClass.crossover(parent1, parent2)
        else: 
            return self.BrainClass.crossover(parent2, parent1)