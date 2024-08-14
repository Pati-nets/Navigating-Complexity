import pm4py
import id_process_tree
import quality
from utils import get_set_of_activities
from quality import calculate_quality, calculate_simplicity, calculate_complexity
from mutations import mutate
from copy import deepcopy
from random import seed, uniform
import math
import matplotlib.pyplot as plt
from pm4py.convert import convert_to_petri_net

class TreeEvolution:
    def __init__(self, init_tree, init_complexity):
        self.trees = [init_tree]
        self.complexity_scores = [init_complexity]

    def add_evolution(self, tree, complexity):
        self.trees += [tree]
        self.complexity_scores += [complexity]

    def store_evolution(self, filename):
        x = [i for i in range(len(self.complexity_scores))]
        plt.clf()
        plt.plot(x, self.complexity_scores)
        plt.savefig(filename)

def simple_evolutionary_tree_miner(log, desired_quality, w_f=0.5, w_p=0.25, w_g=0.1, w_s=0.15, initial_population_size=10, max_iterations=50, seed=-1, mode=-1):
    alphabet = get_set_of_activities(log)
    iterations = 0
    opt = None
    opt_quality = 0
    population = []
    simplicity_scores = []
    opt_qualities = []
    opt_simplicity = []
    opt_complexity = []
    evolutions = []
    for i in range(0, initial_population_size):
        # Generate a population of random trees where each activity occurs exactly once in each tree
        population += [id_process_tree.generate_random_process_tree(alphabet)]
        # The four quality dimensions are calculated for each candidate in the population
        quality = calculate_quality(population[i], log, w_f, w_p, w_g, w_s)
        simplicity_scores += [[calculate_simplicity(population[i], log)]]
        evolutions += [TreeEvolution(deepcopy(population[i]), calculate_complexity(population[i]))]
        # Test whether one of the process trees already has the desired overall quality
        if quality >= desired_quality:
            return population[i]
        # Update the index for the current best result
        if quality > opt_quality:
            opt = deepcopy(population[i])
            opt_quality = quality
    opt_qualities += [opt_quality]
    opt_simplicity += [calculate_simplicity(opt, log)]
    opt_complexity += [calculate_complexity(opt)]
    # Check if the maximum number of iterations is reached
    while iterations < max_iterations:
        iterations += 1
        for i in range(len(population)):
            population[i] = mutate(population[i], alphabet)
            tree = population[i]
            quality = calculate_quality(tree, log, w_f, w_p, w_g, w_s)
            simplicity_scores[i] += [calculate_simplicity(tree, log)]
            evolutions[i].add_evolution(deepcopy(tree), calculate_complexity(tree))
            if quality >= desired_quality:
                return tree
            if quality > opt_quality:
                opt = deepcopy(tree)
                opt_quality = quality
        opt_qualities += [opt_quality]
        opt_simplicity += [calculate_simplicity(opt, log)]
        opt_complexity += [calculate_complexity(opt)]
    import matplotlib.pyplot as plt
    import numpy as np
    x = [i for i in range(len(opt_simplicity))]
    plt.plot(x, opt_qualities)
    plt.plot(x, opt_simplicity)
    if seed < 0 and mode < 0:
        plt.savefig('output/opt-simplicity-changes.png')
    elif seed < 0 and mode > 0:
        plt.savefig('output/opt-simplicity-changes-mode'+str(mode)+'.png')
    elif seed > 0 and mode < 0:
        plt.savefig('output/opt-simplicity-changes-seed'+str(seed)+'.png')
    else:
        plt.savefig('output/opt-simplicity-changes-seed'+str(seed)+'-mode'+str(mode)+'.png')
    plt.plot(x, opt_complexity)
    if seed < 0 and mode < 0:
        plt.savefig('output/opt-complexity-changes.png')
    elif seed < 0 and mode > 0:
        plt.savefig('output/opt-complexity-changes-mode'+str(mode)+'.png')
    elif seed > 0 and mode < 0:
        plt.savefig('output/opt-complexity-changes-seed'+str(seed)+'.png')
    else:
        plt.savefig('output/opt-complexity-changes-seed'+str(seed)+'-mode'+str(mode)+'.png')
    for i in range(len(evolutions)):
        evolutions[i].store_evolution('output/evolutions/evolution-' + str(i))
    return opt


if __name__ == '__main__':
    seed(42)
    log = pm4py.read_xes('examplelog.xes')
    tree = simple_evolutionary_tree_miner(log, 0.9)
    tree.visualize_process_tree()
    print("Fitness: " + str(quality.calculate_fitness(tree, log)))
    print("Precision: " + str(quality.calculate_precision(tree, log)))
    print("Generalization: " + str(quality.calculate_generalization(tree, log)))
    print("Simplicity:" + str(quality.calculate_simplicity(tree, log)))
