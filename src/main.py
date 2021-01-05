import random
from innovationManager import InnovationManager
from genome import Genome
from settings import GenomeSettings, PopulationSettings
from timer import Timer
from matplotlib import pyplot as plt
from population import Population
from brain import Brain

def testTopologies(n, settings):
    random.seed(10)
    times = []
    for idx in range(n):
        t = Timer()
        manager = InnovationManager(settings.inputs + settings.bias + settings.outputs)
        a = Genome(manager, settings)
        b = Genome(manager, settings)
        t.record()
        for j in range(idx):
            a.mutate()
            b.mutate()
        t.record()
        if not a.isTopologyValid():
            print(a)
            print("TEST FAILED")
            print(f"a has an invalid topology when idx = {idx}")
            a.plot(block=True)
            return
        if not b.isTopologyValid():
            print(b)
            print("TEST FAILED")
            print(f"b has an invalid topology when idx = {idx}")
            b.plot(block=True)
            return
        c = a.crossover(b)
        if not c.isTopologyValid():
            print(c)
            print("TEST FAILED")
            print(f"c has an invalid topology when idx = {idx} after a.cross(b)")
            c.plot(block=True)
            return
        c = b.crossover(a)
        if not c.isTopologyValid():
            print(c)
            print("TEST FAILED")
            print(f"c has an invalid topology when idx = {idx} after b.cross(a)")
            c.plot(block=True)           
            return
        c = b.crossover(a, sameFitness=True)
        if not c.isTopologyValid():
            print(c)
            print("TEST FAILED")
            print(f"c has an invalid topology when idx = {idx} after b.cross(a, True)")
            c.plot(block=True)
            return

        print(f"idx: {idx}", end=' ')
        times.append(t.show())
    print("TEST PASSED!")
    x = range(n)
    m, c = zip(*times)
    plt.scatter(x,m, label="Mutation time")
    plt.scatter(x,c, label="Crossover time")
    plt.legend()
    plt.show()

class Player(Brain):
    def setInputValues(self):
        self.inputValues = []
    
    def fitnessEvaluationMethod(self):
        return len(self.genome.connections)
# seed: 0
# i: 2
# o: 1
# range (50)
if __name__ == "__main__":
    random.seed(1)

    genomeSettings = GenomeSettings(inputs=4, outputs=3, bias=0)
    # im = InnovationManager(genomeSettings)
    # pl = Player.create(im, genomeSettings)

    # print(type(pl).create(im, genomeSettings).fitnessEvaluationMethod())


    populationSettings = PopulationSettings(size=100, genomeSettings=genomeSettings)
    p = Population(populationSettings, Player)
    for i in range(200):
        if p.evolve():
            p.globalChampion.plot(pauseTime=0.0001)
    print(p)

    p.globalChampion.plot(block=True)