import complexity
from simplicity import Simplicity
from utils import get_set_of_activities
from convert import convert_to_marked_petri_net
from pm4py import fitness_token_based_replay, fitness_alignments, precision_token_based_replay
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator

# global variables for simplicity calculation
S = Simplicity(None)
m = 0
use_alignments = False

def init_simplicity_evaluator(tree, mode=0):
    """
    A method to initialize the Simplicity-class of simplicity.py.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the tree for the reference model that should be used
        to calculate the relative simplicity
    mode: int (default 0)
        an integer value specifying which complexity measure
        should be used to calculate simplicity

    This method automatically converts the input process tree
    into a marked Petri net. It initializes the global variables
    S and m that are used to calculate simplicity and complexity
    in the desired way
    """

    reference_model, im, fm = convert_to_marked_petri_net(tree)
    global S,m
    S = Simplicity(reference_model)
    m = mode


def calculate_quality(tree, log, w_f, w_p, w_g, w_s, f=-1, p=-1, g=-1, s=-1):
    """
    Calculates the quality of a process tree according to the event
    log and the specified weights for fitness, precision, generalization
    and simplicity.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose quality should be calculated
    log: pm4py.objects.log.obj.EventLog
        the event log for whose behavior the tree should reflect
    w_f: float
        a float value in [0,1] representing the importance of the
        fitness score compared to the other quality dimensions
    w_p: float
        a float value in [0,1] representing the importance of the
        precision score compared to the other quality dimensions
    w_g: float
        a float value in [0,1] representing the importance of the
        generalization score compared to the other quality dimensions
    w_s: float
        a float value in [0,1] representing the importance of the
        simplicity score compared to the other quality dimensions
    f: float (default -1)
        a float value in [0,1] representing an already known fitness
        score for the model. If the value is not in [0,1] the fitness
        score is calculated instead
    p: float (default -1)
        a float value in [0,1] representing an already known precision
        score for the model. If the value is not in [0,1] the precision
        score is calculated instead
    g: float (default -1)
        a float value in [0,1] representing an already known generalization
        score for the model. If the value is not in [0,1] the generalization
        score is calculated instead
    s: float (default -1)
        a float value in [0,1] representing an already known simplicity
        score for the model. If the value is not in [0,1] the simplicity
        score is calculated instead

    Returns
    -------
    float
        the quality of the model, calculated as
        w_f * f + w_p * p + w_g * g + w_s * s
        where f, p, g, s are the scores for fitness, precision,
        generalization and simplicity
    """

    fit = f
    if fit < 0 or fit > 1:
        fit = calculate_fitness(tree, log)
    prec = p
    if prec < 0 or prec > 1:
        prec = calculate_precision(tree, log)
    gen = g
    if gen < 0 or gen > 1:
        gen = calculate_generalization(tree, log)
    sim = s
    if sim < 0 or sim > 1:
        sim = calculate_simplicity(tree, log)
    return w_f * fit + w_p * prec + w_g * gen + w_s * sim


def calculate_fitness(tree, log):
    """
    A method for calculating the fitness of a process tree according
    to an event log with token based replay.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose fitness should be calculated
    log: pm4py.objects.log.obj.EventLog
        the event log for whose behavior the tree should reflect

    Returns
    -------
    float
        a value in [0,1] reflecting the fitness of the tree with
        respect to the event log

    This method uses the fitness calculation of pm4py, but only
    if all activities in the event log are part of the process
    tree. This is because otherwise, trees that consist of only
    one node contained in the event log would get perfect fitness
    and would therefore lead the ETM to believe it found a perfect
    process model, since precision and simplicity would also be 1.
    """

    net, im, fm = convert_to_marked_petri_net(tree)
    global use_alignments
    if use_alignments:
        return fitness_alignments(log, net, im, fm)['log_fitness']
    else:
        log_activities = get_set_of_activities(log)
        tree_labels = tree._get_root().list_leaf_labels()
        if set(log_activities) <= set(tree_labels):
            return fitness_token_based_replay(log, net, im, fm)['log_fitness']
        else:
            return 0


def calculate_precision(tree, log):
    """
    A method for calculating the precision of a process tree according
    to an event log with token based replay.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose precision should be calculated
    log: pm4py.objects.log.obj.EventLog
        the event log for whose behavior the tree should reflect

    Returns
    -------
    float
        a value in [0,1] reflecting the precision of the tree with
        respect to the event log

    This method uses the precision calculation based on token-based
    replay provided by pm4py.
    """

    net, im, fm = convert_to_marked_petri_net(tree)
    precision = precision_token_based_replay(log, net, im, fm)
    return precision


def calculate_generalization(tree, log):
    """
    A method for calculating the generalization of a process tree
    according to an event log.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose generalization should be calculated
    log: pm4py.objects.log.obj.EventLog
        the event log for whose behavior the tree should reflect

    Returns
    -------
    float
        a value in [0,1] reflecting the generalization of the tree with
        respect to the event log

    This method uses the generalization calculation provided by pm4py.
    """

    net, im, fm = convert_to_marked_petri_net(tree)
    generalization = generalization_evaluator.apply(log, net, im, fm)
    return generalization

def calculate_simplicity(tree, log):
    """
    A method for calculating the simplicity of a process tree.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose simplicity should be calculated
    log: pm4py.objects.log.obj.EventLog
        the event log for whose behavior the tree should reflect:
        not used yet, but simplicity measures that take the event
        log into account are imaginable

    Returns
    -------
    float
        a value in [0,1] reflecting the simplicity of the tree

    To calculate the simplicity of the net, this method uses the
    Simplicity-class and the mode provided by a call of
    init_simplicity_evaluator(tree, mode)
    This method should not be called before calling init_simplicity_evaluator.
    """

    global S, m
    net, im, fm = convert_to_marked_petri_net(tree)
    if m == 0:
        return S.size(net)
    elif m == 1:
        return S.average_connector_degree(net)
    elif m == 2:
        return S.connector_heterogeneity(net)
    else:
        raise Exception("Unsupported Mode for Simplicity Evaluation: " + str(m))


def calculate_complexity(tree):
    """
    A method for calculating the complexity of a process tree.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the process tree whose complexity should be calculated

    Returns
    -------
    float
        a value in [0,1] reflecting the complexity of the tree

    To calculate the complexity of the net, this method uses the
    mode provided by a call of
    init_simplicity_evaluator(tree, mode)
    It is advised to call init_simplicity_evaluator before this
    method, since otherwise the default mode 0 (size) will be used.
    """

    global m
    net, im, fm = convert_to_marked_petri_net(tree)
    if m  == 0:
        return complexity.size(net)
    elif m == 1:
        return complexity.average_connector_degree(net)
    elif m == 2:
        return complexity.connector_heterogeneity(net)
    else:
        raise Exception("Unsupported Mode for Complexity Evaluation:" + str(m))
