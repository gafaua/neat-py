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
    def setInputValues(self, i):
        self.inputValues = [i[0], i[1]]
    
    def fitnessEvaluationMethod(self, show=False):
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
# seed: 0
# i: 2
# o: 1
# range (50)
if __name__ == "__main__":
    random.seed(1)

    genomeSettings = GenomeSettings(inputs=2, outputs=1, bias=0)
    # im = InnovationManager(genomeSettings)
    # pl = Player.create(im, genomeSettings)

    # print(type(pl).create(im, genomeSettings).fitnessEvaluationMethod())


    populationSettings = PopulationSettings(size=150, genomeSettings=genomeSettings)
    p = Population(populationSettings, Player)
    cnt = 0
    max_ = 1000
    while p.globalChampion.fitness < 13:
        cnt += 1
        if p.evolve():
            p.globalChampion.plot(pauseTime=0.0001)
        if cnt == max_:
            break

    print(p.globalChampion)
    print(p.globalChampion.genome)

    p.globalChampion.fitnessEvaluationMethod(show=True)
    p.globalChampion.plot(block=True)