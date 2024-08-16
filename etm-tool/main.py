from convert import convert_to_marked_petri_net
from etm import simple_evolutionary_tree_miner
from id_process_tree import generate_random_process_tree
from mutations import mutate
import quality
import pm4py
from pm4py.objects.log.obj import Trace, Event, EventLog
from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
from random import randrange, seed
from datetime import datetime
import os

def ask_user_for_seed():
    """
    Repeadedly asks the user to input a seed until it gets a valid one.

    Returns
    -------
    int
        the input seed or a random number between 0 and 1,000,000 if the
        user decided to randomly generate a seed
    """

    print("Specifiy a seed (a natural number) or press enter to use a random seed.")
    seed = -1
    while seed < 0:
        seed_string = input("Seed: ")
        if seed_string == "":
            seed = randrange(0, 1000000)
            print("Using random seed " + str(seed) + ".")
            break
        try:
            seed = int(seed_string)
        except:
            seed = -1
        if seed >= 0:
            break
        else:
            seed = -1
            print("Invalid input: " + seed_string)
            print("Please try again or exit the program with CTRL + C.")
    return seed


def create_tree_and_event_log(alphabet, folder_path):
    """
    Creates an event log with the specified alphabet by randomly
    creating and mutating a process tree.

    Parameters
    ----------
    alphabet: list
        a list containing the symbols that are allowed to appear
        in leaf nodes of the process tree
    folder_path: str
        a path specifying the folder where the process tree and
        the event log should be stored

    Returns
    -------
    (IdentifiableProcessTree, pm4py.objects.log.obj.EventLog)
        a pair consisting of the randomly generated process tree
        and the event log that was obtained by it by a playout

    This method permanently stores the generated process tree in a .png
    file and the generated event log in an .xes file.
    """

    print("Generating a random process tree...")
    tree = generate_random_process_tree(alphabet)
    while tree.tree_size() < 15:
        tree = mutate(tree, alphabet)
    tree.flatten()
    pm4py.save_vis_process_tree(tree, folder_path + '/OriginalProcessTree.png')
    print("Generating an event log from the created process tree...")
    log = pm4py.play_out(tree.build_process_tree())
    pm4py.write_xes(log, folder_path + '/EventLog.xes')
    return (tree, log)


def ask_user_for_mode():
    """
    Repeadedly asks the user to input a mode for complexity calculation
    until it gets a valid one.

    Returns
    -------
    int
        the chosen mode for complexity calculation, which is a number in
        the interval [0,2]
    """

    print("Please specify the number of the complexity measure you would like to inspect.")
    print("0: Size")
    print("1: Average Connector Degree")
    print("2: Connector Heterogeneity")
    mode = -1
    while mode < 0:
        mode_string = input("Specify one of the numbers above: ")
        try:
            mode = int(mode_string)
        except:
            mode = -1
        if mode in range(0,3):
            break
        else:
            mode = -1
            print("Invalid input: " + mode_string)
            print("Please try again or exit the program with CTRL + C.")
    return mode


def ask_for_weight(message):
    """
    Repeadedly asks a user to specify a weight between 0 and 1 until
    the user inputs a valid value.

    Parameters
    ----------
    message: str
        the message to be displayed while waiting for the input

    Returns
    -------
    float
        a value between 0 and 1 specified by the user
    """

    w = -1
    while w < 0:
        string = input(message)
        try:
            w = float(string)
        except:
            print("Invalid input " + f_string)
            print("Please try again or exit the program with CTRL + C.")
        if w >= 0 and w <= 1:
            break
        else:
            print("Invalid input " + f_string)
            print("Please specify a value between 0 and 1.")
            print("You can try again or exit the program with CTRL + C.")
    return w


def ask_user_for_quality_threshold():
    """
    Repeadedly asks a user to specify a quality threshold between 0 and 1
    until the user inputs a valid value.

    Returns
    -------
    float
        a value between 0 and 1 specified by the user
    """

    print("Please specify the quality threshold when the algorithm can stop.")
    q = ask_for_weight("Quality threshold: ")
    return q


def ask_user_for_weights():
    """
    Asks the user if he wants to specify the weights for the quality
    calculation, reads them if he does and uses default values if he
    does not.

    Returns
    -------
    (float, float, float, float)
        four values representing the weights for the quality calculation,
        i.e. the weight for the fitness score, the weight for the precision
        score, the weight for the generalization score and the weight for
        the simplicity score
    """

    specify = False
    while True:
        answer = input("Do you want to specify the weights for the quality calculation? (y/n) ")
        if answer.lower() == "y" or answer.lower() == "yes":
            specify = True
            break
        elif answer.lower() == "n" or answer.lower() == "no":
            specify = False
            break
        else:
            print("Invalid input: " + answer)
            print("Please try again or exit the program with CTRL + C.")
    if specify:
        print("Please specify the weights.")
        while True:
            w_f = ask_for_weight("fitness-weight = ")
            w_p = ask_for_weight("precision-weight = ")
            w_g = ask_for_weight("generalization-weight = ")
            w_s = ask_for_weight("simplicity-weight = ")
            if (w_f + w_p + w_g + w_s) == 1:
                return (w_f, w_p, w_g, w_s)
            else:
                print("Invalid input: " + str((w_f, w_p, w_g, w_s)))
                print("The weights must sum to exactly 1.")
                print("Please try again or exit the program with CTRL + C.")
    else:
        w_f = 0.4
        w_p = 0.25
        w_g = 0.1
        w_s = 0.25
        print("Using the following default values: ")
        print("fitness-weight = " + str(w_f))
        print("precision-weight = " + str(w_p))
        print("generalization-weight = " + str(w_g))
        print("simplicity-weight = " + str(w_s))
        return (w_f, w_p, w_g, w_s)


def ask_user_for_max_iterations():
    """
    Repeadedly asks the user to specify the maximum number of
    iterations the algorithm should undergo

    Returns
    -------
    int
        the maximum number of iterations specified by the user
    """

    iterations = 500
    print("Please specify the maximum number of iterations the ETM should take or press enter to use the default (" + str(iterations) + ").")
    while True:
        iterations_string = input("Maximum number of iterations: ")
        if iterations_string == "":
            return iterations
        try:
            iterations = int(iterations_string)
        except:
            print("Invalid input: " + iterations_string)
            print("Please try again or exit the program with CTRL + C.")
            continue
        if iterations >= 0:
            return iterations
        else:
            print("Invalid input: " + iterations_string)
            print("Please try again or exit the program with CTRL + C.")


def ask_user_for_fitness_calculation():
    print("When using token-based replay for the calculation of fitness, ", end='')
    print("reproducibility may not be guaranteed. You may want to switch ", end='')
    print("to alignment-based fitness, but be aware that this takes longer.")
    while True:
        answer = input("Do you want to use alignment-based fitness? (y/n) ")
        if answer.lower() == "y" or answer.lower() == "yes":
            quality.use_alignments = True
            break
        elif answer.lower() == "n" or answer.lower() == "no":
            quality.use_alignments = False
            break
        else:
            print("Invalid input: " + answer)
            print("Please try again or exit the program with CTRL + C.")



if __name__ == '__main__':
    now = datetime.now()
    output_folder = 'output' + str(now)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        os.makedirs(output_folder + '/evolutions')
    # set the seed for executing the ETM algorithm
    seed(ask_user_for_seed())
    print()
    # randomly generate a process tree to create an event log
    tree, log = create_tree_and_event_log(['a','b','c','d','e'], output_folder)
    print()
    # set the mode for complexity calculation
    mode = ask_user_for_mode()
    quality.init_simplicity_evaluator(tree, mode)
    print()
    # read the quality threshold from the user
    q = ask_user_for_quality_threshold()
    print()
    # read the weights for the quality calculation from the user
    (w_f, w_p, w_g, w_s) = ask_user_for_weights()
    print()
    # read the maximum number of iterations from the user
    it = ask_user_for_max_iterations()
    print()
    # ask if the user wants to use alignment-based fitness
    ask_user_for_fitness_calculation()
    print()

    print("Starting Evolutionary Tree Miner...")
    result = simple_evolutionary_tree_miner(log, q, w_f, w_p, w_g, w_s, 10, it, output_folder)
    pm4py.save_vis_process_tree(result._get_root(), output_folder + '/ETM-Result.png')

    fitness = quality.calculate_fitness(result, log)
    precision = quality.calculate_precision(result, log)
    generalization = quality.calculate_generalization(result, log)
    simplicity = quality.calculate_simplicity(result, log)
    quality = quality.calculate_quality(result, log, w_f, w_p, w_g, w_s, fitness, precision, generalization, simplicity)
    print()
    print("Quality of the resulting model")
    print("---------------------------------")
    print("Quality \t | " + str(quality))
    print("Fitness \t | " + str(fitness))
    print("Precision \t | " + str(precision))
    print("Generalization \t | " + str(generalization))
    print("Simplicity \t | " + str(simplicity))
