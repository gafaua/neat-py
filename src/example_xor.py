import random
from settings import GenomeSettings, PopulationSettings
from matplotlib import pyplot as plt
from population import Population
from brain import Brain
from neat import NEAT

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
    random.seed(1)#2#1

    genomeSettings = GenomeSettings(inputs=2, outputs=1, bias=1)

    populationSettings = PopulationSettings(size=200, genomeSettings=genomeSettings)

    neat = NEAT(populationSettings, Player)
    champion = neat.learn(iterations=1000, fitnessGoal=12)

    print(champion)
    print(champion.genome)

    champion.fitnessEvaluation(show=True)
    champion.plot(block=True)
    champion.genome.save("xor")

