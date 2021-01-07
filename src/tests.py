
import random
from timer import Timer
from innovationManager import InnovationManager
from genome import Genome
from matplotlib import pyplot as plt

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
