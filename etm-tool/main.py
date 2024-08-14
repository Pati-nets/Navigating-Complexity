import pm4py
import random
from convert import convert_to_marked_petri_net
from pm4py.objects.log.obj import Trace, Event, EventLog
from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
import id_process_tree
import mutations
import etm
import quality
import simplicity


if __name__ == '__main__':
    # set the seed for executing the ETM algorithm
    print("Specify a seed (a natural number) or just press enter to use a random one.")
    seed = -1
    seed_string = input("Seed: ")
    try:
        seed = int(seed_string)
    except:
        seed = random.randrange(0, 1000000)
        print("No seed set, using random seed " + str(seed) + ".")
    if seed >= 0:
        random.seed(seed)

    # specify the alphabet for the process tree to be found
    alphabet = ['a','b','c','d','e']

    print("Generate random process tree...")
    tree = id_process_tree.generate_random_process_tree(alphabet)
    for i in range(1000):
        tree = mutations.mutate(tree, alphabet)
    tree.flatten()
    pm4py.save_vis_process_tree(tree, 'output/OriginalProcessTree-seed'+str(seed)+'.png')

    print("Generating event log from process tre...")
    log = pm4py.play_out(tree.build_process_tree())

    print("Which complexity measure would you like to inspect?")
    print("0: Size")
    print("1: Average Connector Degree")
    print("2: Connector Heterogeneity")
    mode_input = input("Specify one of the numbers above: ")
    mode = 0
    try:
        mode = int(mode_input)
    except:
        print("Input could not be interpreted as an integer value. Terminating...")
        quit()
    if mode not in [0, 1, 2]:
        print("Input is not a valid mode. Terminating...")
        quit()
    quality.init_simplicity_evaluator(tree, mode)

    print("Starting Evolutionary Tree Miner...")
    result = etm.simple_evolutionary_tree_miner(log, 0.99, seed=seed, mode=mode)
    from pm4py.convert import convert_to_petri_net
    pn, im, fm = convert_to_marked_petri_net(result)
    pm4py.view_petri_net(pn, im, fm)
    pm4py.save_vis_process_tree(result._get_root(), 'output/Result-seed'+str(seed)+'-mode'+str(mode)+'.png')
    print("Fitness: " + str(quality.calculate_fitness(result, log)))
    print("Precision: " + str(quality.calculate_precision(result, log)))
    print("Generalization: " + str(quality.calculate_generalization(result, log)))
    print("Simplicity:" + str(quality.calculate_simplicity(result, log)))
