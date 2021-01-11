from population import Population
from settings import PopulationSettings
from brain import Brain

class NEAT:
    def __init__(self,
                 settings: PopulationSettings,
                 BrainClass: type,
                 baseBrain: Brain = None):
        if baseBrain is not None:
            # TODO instantiate population with baseBrain
            pass

        self.population = Population(settings, BrainClass)

    def learn(self, iterations, fitnessGoal):
        cnt = 0

        while self.population.globalChampion.fitness < fitnessGoal:
            cnt += 1
            if self.population.evolve():
                self.population.globalChampion.plot(pauseTime=0.0001)
            if cnt == iterations:
                break
        print(self.population)

        return self.population.globalChampion