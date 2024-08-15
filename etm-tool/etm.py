import quality
from id_process_tree import generate_random_process_tree
from utils import get_set_of_activities
from mutations import mutate
from copy import deepcopy
import matplotlib.pyplot as plt

class TreeEvolution:
    """
    A class that represents the evolution of complexity scores for
    a specific process tree.

    Attributes
    ----------
    trees: list
        a list of IdentifiableProcessTrees that represents the state
        of the tree in each iteration
    complexity_scores: list
        a list of floats representing the complexity scores of the
        tree in each iteration

    Methods
    -------
    add_evolution(tree, complexity)
        adds a new evolution of the tree, as well as its complexity
        score, to the list of evolutions and scores
    store_evolution(filename)
        saves a plotted graph showing the evolution of complexity scores
        in a file whose name is specified by the parameter
    """

    def __init__(self, init_tree, init_complexity):
        """
        Parameters
        ----------
        init_tree: IdentifiableProcessTree
            the initial process tree in iteration step 0
        init_complexity: float
            the complexity score of the initial process tree
        """

        self.trees = [init_tree]
        self.complexity_scores = [init_complexity]


    def add_evolution(self, tree, complexity):
        """
        Adds a new evolution of the tree, as well as its complexity
        score, to the list of evolutions and scores.

        Parameters
        ----------
        tree: IdentifiableProcessTree
            the process tree that should be added as a new evolution
        complexity: float
            the complexity score of the newly added process tree
        """

        self.trees += [tree]
        self.complexity_scores += [complexity]


    def store_evolution(self, filename):
        """
        Saves a plotted graph showing the evolution of complexity scores
        in a file whose name is specified by the parameter.

        Parameters
        ----------
        filename: str
            the name of the file where the image should be stored
        """

        x = [i for i in range(len(self.complexity_scores))]
        plt.clf()
        ax = plt.gca()
        ax.set_xlim([1, len(self.complexity_scores)])
        plt.plot(x, self.complexity_scores)
        plt.xlabel("ETM iteration step")
        plt.ylabel("complexity score")
        plt.savefig(filename)


def store_opt_qualities(opt_qualities, output_folder):
    """
    Stores the list containing tree qualities by creating a
    graph for each quality dimension and saving them in one picture.

    Parameters
    ----------
    opt_qualities: list
        the list containing the quality dimension scores that
        should be exported into an image
    output_folder: str
        the path of the folder where the picture should be saved
    """

    x = [i for i in range(len(opt_qualities))]
    q = [opt_qualities[i][0] for i in range(len(opt_qualities))]
    f = [opt_qualities[i][1] for i in range(len(opt_qualities))]
    p = [opt_qualities[i][2] for i in range(len(opt_qualities))]
    g = [opt_qualities[i][3] for i in range(len(opt_qualities))]
    s = [opt_qualities[i][4] for i in range(len(opt_qualities))]
    plt.plot(x, q)
    plt.plot(x, f)
    plt.plot(x, p)
    plt.plot(x, g)
    plt.plot(x, s)
    plt.xlabel("change in the optimum")
    plt.ylabel("quality")
    plt.legend(["quality", "fitness", "precision", "generalization", "simplicity"])
    plt.savefig(output_folder + "/opt-qualities")


def simple_evolutionary_tree_miner(log, desired_quality, w_f=0.5, w_p=0.25, w_g=0.1, w_s=0.15, population_size=10, max_iterations=500, output_folder='output'):
    """
    Executes the evolutionary tree miner on the specified log until the
    desired quality or a maximum amount of iterations is reached.

    Parameters
    ----------
    log: pm4py.objects.log.obj.EventLog
        the event log whose behavior should be modeled
    desired_quality: float
        a threshold value that determines with which model quality
        the algorithm is allowed to terminate early
    w_f: float (default 0.5)
        the weight for the fitness score when calculating the
        quality of a model
    w_p: float (default 0.25)
        the weight for the precision score when calculating the
        quality of a model
    w_g: float (default 0.1)
        the weight for the generalization score when calculating the
        quality of a model
    w_s: float (default 0.15)
        the weight for the simplicity score when calculating the
        quality of a model
    population_size: int
        the size of the process tree population containing the trees
        that mutate in each generation
    max_iterations: int
        the maximum number of iterations the algorithm should perform
        until terminating
    output_folder: str
        the path of the folder where the output should be stored

    Returns
    -------
    IdentifiableProcessTree
        a process tree with the best quality among all generated trees
        with respect to the event log and the specified weights
    """

    alphabet = get_set_of_activities(log)
    iterations = 0
    opt = None
    opt_quality = 0
    population = []
    evolutions = []
    opt_quality_dimensions = []
    for i in range(0, population_size):
        # Generate a population of random trees where each activity occurs exactly once in each tree
        population += [generate_random_process_tree(alphabet)]
        # The four quality dimensions are calculated for each candidate in the population
        fit = quality.calculate_fitness(population[i], log)
        prec = quality.calculate_precision(population[i], log)
        gen = quality.calculate_generalization(population[i], log)
        sim = quality.calculate_simplicity(population[i], log)
        qual = quality.calculate_quality(population[i], log, w_f, w_p, w_g, w_s, fit, prec, gen, sim)
        evolutions += [TreeEvolution(deepcopy(population[i]), quality.calculate_complexity(population[i]))]
        # Test whether one of the process trees already has the desired overall quality
        if qual >= desired_quality:
            opt_quality_dimensions += [(qual, fit, prec, gen, sim)]
            store_opt_qualities(opt_quality_dimensions, output_folder)
            return population[i]
        # Update the index for the current best result
        if qual > opt_quality:
            opt_quality_dimensions += [(qual, fit, prec, gen, sim)]
            opt = deepcopy(population[i])
            opt_quality = qual
    # Check if the maximum number of iterations is reached
    while iterations < max_iterations:
        iterations += 1
        for i in range(len(population)):
            population[i] = mutate(population[i], alphabet)
            fit = quality.calculate_fitness(population[i], log)
            prec = quality.calculate_precision(population[i], log)
            gen = quality.calculate_generalization(population[i], log)
            sim = quality.calculate_simplicity(population[i], log)
            qual = quality.calculate_quality(population[i], log, w_f, w_p, w_g, w_s, fit, prec, gen, sim)
            evolutions[i].add_evolution(deepcopy(population[i]), quality.calculate_complexity(population[i]))
            if qual >= desired_quality:
                opt_quality_dimensions += [(qual, fit, prec, gen, sim)]
                store_opt_qualities(opt_quality_dimensions, output_folder)
                return population[i]
            if qual > opt_quality:
                opt_quality_dimensions += [(qual, fit, prec, gen, sim)]
                opt = deepcopy(tree)
                opt_quality = qual
    # Store the evolution with respect to the quality dimensions
    store_opt_qualities(opt_quality_dimensions, output_folder)
    for i in range(len(evolutions)):
        evolutions[i].store_evolution(output_folder + '/evolutions/evolution-tree-' + str(i + 1))
    return opt
