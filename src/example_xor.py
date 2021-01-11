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
        correct = True
        for i in tests:
            self.setInputValues(i)
            self.generateOutputValues()
            oo = 0 if self.outputValues[0] < 0.5 else 1

            dist += abs(i[2] - self.outputValues[0])
            if oo != i[2]:
                correct = False
            if show:
                print(f"i0: {i[0]}, i1: {i[1]}, expected: {i[2]}, result: {oo}")
        
        if correct:
            return 16
        return (4 - dist)**2

if __name__ == "__main__":
    #random.seed(1)#2#1

    genomeSettings = GenomeSettings(inputs=2, outputs=1, bias=1)
    populationSettings = PopulationSettings(size=150, genomeSettings=genomeSettings)

    neat = NEAT(populationSettings, Player)
    champion = neat.learn(iterations=1000, fitnessGoal=16)

    print(champion)
    print(champion.genome)

    champion.fitnessEvaluation(show=True)
    champion.plot(block=True)
    champion.genome.save("xor")

