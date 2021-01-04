    def crossover_old(self, genome, sameFitness=False):
        """
        Generates the crossover child between self and param genome
        This method assumes that self has a better fitness score than genome
        """

        child = Genome(self.inputs, self.outputs, self.innovationManager)
        
        connections = []
        if sameFitness:
            # add all disjoint and excess connection genes and randomly select common ones
            common = set(self.connections).intersection(set(genome.connections))
            connections = [self.connections[c] for c in self.connections if c not in common] + \
                          [genome.connections[c] for c in genome.connections if c not in common] + \
                          [self.connections[c] if random.random() < 0.5 else genome.connections[c] for c in common]
        else:
            connections = [c for c in self.connections.values()] + \
                          [genome.connections[c] for c in genome.connections if c not in self.connections]

        connections.sort(key=lambda c: c.inNode.layer)

        layer = 0
        stack = []

        while len(child.connections) < len(connections):
            for i in range(len(child.connections), len(connections)):
                if connections[i].inNode.layer > layer:
                    break
                stack.append(connections[i])

            while len(stack) > 0:
                c: Connection = stack.pop()
                inLayer = child.nodes[c.inNode.id].layer
                if c.outNode.id in child.nodes:
                    if child.nodes[c.outNode.id].layer <= inLayer:
                        child.shiftLayers(child.nodes[c.outNode.id], inLayer)
                else:
                    child.nodes[c.outNode.id] = Node(c.outNode.id, inLayer + 1)

                connection = Connection(child.nodes[c.inNode.id], child.nodes[c.outNode.id], c.innovationNumber, c.weight, c.enabled)
                child.nodes[c.inNode.id].addConnection(connection)
                child.connections[connection.innovationNumber] = connection

            layer += 1

        for n in child.outputNodes():
            n.layer = layer

        child.layers = layer + 1

        child.computeMaxConnections()
        return child
