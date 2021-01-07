import random
from settings import GenomeSettings, PopulationSettings
from matplotlib import pyplot as plt
from population import Population
from brain import Brain

class Player(Brain):
    def setInputValues(self, i):
        self.inputValues = [i[0], i[1]]
    
    def fitnessEvaluation(self, show=False):
        tests = [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]

        dist = 0

        for i in tests:
            self.setInputValues(i)
            self.generateOutputValues()
            oo = 0.0 if self.outputValues[0] < 0.5 else 1.0

            dist += abs(i[2] - self.outputValues[0])
            if show:
                print(f"i0: {i[0]}, i1: {i[1]}, expected: {i[2]}, result: {oo}")

        return (4 - dist)**2

if __name__ == "__main__":
    random.seed(2)#2

    genomeSettings = GenomeSettings(inputs=2, outputs=1, bias=0)
    populationSettings = PopulationSettings(size=200, genomeSettings=genomeSettings)

    pop = Population(populationSettings, Player)
    cnt = 0
    max_ = 1000
    while pop.globalChampion.fitness < 12:
        cnt += 1
        if pop.evolve():
            pop.globalChampion.plot(pauseTime=0.0001)
        if cnt == max_:
            break
    print(pop)
    print(pop.globalChampion)
    print(pop.globalChampion.genome)

    pop.globalChampion.fitnessEvaluation(show=True)
    pop.globalChampion.plot(block=True)