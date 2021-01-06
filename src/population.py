from species import Species
from settings import GenomeSettings, PopulationSettings
from innovationManager import InnovationManager
import random

# TODO Deal with staleness problem
# TODO Test with real optimization problem

class Population:
    def __init__(self, settings: PopulationSettings, BrainClass: type):
        self.settings = settings
        self.BrainClass = BrainClass

        self.species = []
        self.brains = []
        self.championHistory = []

        self.generation = 0

        self.innovationManager = InnovationManager(self.settings.genome)

        for _ in range(self.settings.size):
            b = self.BrainClass.create(self.innovationManager, self.settings.genome)
            b.mutate()
            self.brains.append(b)

        self.globalChampion = self.brains[0]


    def __str__(self):
        value = "POPULATION:\n\n"
        value += f"Size: {self.settings.size}\n"
        value += f"Generation: {self.generation}\n"
        value += f"{len(self.species)} species:\n"
        for i, s in enumerate(self.species): value += f"Species {i+1}\n" + str(s)
        return value

    def evolve(self):
        print(f"Generation: {self.generation}")

        newChampion = False

        self.speciate()

        # evaluate the fitness of every brain of this population
        for b in self.brains: 
            b.evaluateFitness()

        # cull species and compute adjusted average fitness to prepare the next generation
        for s in self.species:
            s.sort()
            s.cull(self.settings.cullRate)
            s.updateAvgAdjustedFitness()

        # sort species by their respective champion
        self.species.sort(key=lambda s: s.fitness, reverse=True)
        
        # update best player if needed
        if self.globalChampion.fitness < self.species[0].population[0].fitness:
            newChampion = True
            self.globalChampion = self.species[0].population[0]
            self.championHistory.append(self.BrainClass.clone(self.globalChampion))
            print(f"New champion brain - Generation {self.generation} - Fitness {self.globalChampion.fitness}")
        
        avgAdjustedFitnessSum = self.getAvgAdjustedFitnessSum()

        i = 0
        while i < len(self.species):
            nOffspring = self.settings.size * (self.species[i].avgAdjustedFitness / avgAdjustedFitnessSum)
            if self.species[i].staleness >= self.settings.maxStaleness or \
               nOffspring < 1:
                del self.species[i]
                i -= 1
            i += 1

        self.generation += 1

        nextGeneration = []
        avgAdjustedFitnessSum = self.getAvgAdjustedFitnessSum()

        for s in self.species:
            best = self.BrainClass.clone(s.champion)
            best.generation = self.generation
            nextGeneration.append(best)

            nOffspring = int(self.settings.size * (s.avgAdjustedFitness / avgAdjustedFitnessSum) - 1)
            for _ in range(nOffspring):
                nextGeneration.append(self.generateOffspring(s))

        while len(nextGeneration) < self.settings.size:
            nextGeneration.append(self.generateOffspring(self.species[0]))

        self.brains = nextGeneration

        return newChampion

    def generateOffspring(self, s: Species):
        offspring = None
        if random.random() < self.settings.crossoverRate:
            other = s
            if random.random() < self.settings.interSpeciesCrossoverRate:
                other = random.choice(self.species)
            offspring = s.mate(other)
        else:
            offspring = s.generateChild()
        return offspring

    def speciate(self):
        # assign a species to every brain 
        for b in self.brains:
            lonely = True
            for s in self.species:
                if s.shouldContain(b, self.settings.speciesDistanceThreshold):
                    s.add(b)
                    lonely = False
                    break
            if lonely:
                self.species.append(Species(b))
    
    def getAvgAdjustedFitnessSum(self):
        avgAdjustedFitnessSum = 0
        for s in self.species: 
            avgAdjustedFitnessSum += s.avgAdjustedFitness
        return avgAdjustedFitnessSum
