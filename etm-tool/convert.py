from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.objects.process_tree.obj import Operator

# global variables for generating IDs for places and transitions
plID = 0
trID = 0

def copy_places_transitions_and_arcs(from_net, to_net):
    """
    Copies all places, transitions and arcs from the first
    Petri net to the second Petri net.

    Parameters
    ----------
    from_net: pm4py.objects.petri_net.obj.PetriNet
        the net whose places, transitions and arcs should be copied
    to_net: pm4py.objects.petri_net.obj.PetriNet
        the net into which the places, transitions and arcs should
        be added
    """

    for p in from_net.places:
        to_net.places.add(p)
    for t in from_net.transitions:
        to_net.transitions.add(t)
    for a in from_net.arcs:
        to_net.arcs.add(a)


def create_place():
    """
    Creates a new place with a unique ID and returns it.

    Returns
    -------
    pm4py.objects.petri_net.obj.PetriNet.Place
        the created place
    """

    global plID
    p = PetriNet.Place(name="p_"+str(plID))
    plID += 1
    return p


def create_transition(label):
    """
    Creates a new transition with the specified label and a unique ID
    and returns it.

    Parameters
    ----------
    label: str
        the label the new transition should get

    Returns
    -------
    pm4py.objects.petri_net.obj.PetriNet.Transition
        the created transition
    """

    global trID
    t = PetriNet.Transition(name="t_"+str(trID), label=label)
    trID += 1
    return t


def sequence_composition(nets, initial_places, final_places):
    """
    Performs a sequential composition on the specified nets.

    Parameters
    ----------
    nets: list
        a list containing all workflow nets that should be sequentially
        composed in the order they should be composed
    initial_places: list
        a list containing the initial places of the nets in the nets-list,
        occurring in the same order as the nets they belong to
    final_places: list
        a list containing the final places of the nets in the nets-list,
        occurring in the same order as the nets they belong to

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.PetriNet.Place,
     pm4py.objects.petri_net.obj.PetriNet.Place)
        the Petri net obtained by sequentially composing the input nets,
        as well as the new initial and final place
    """

    sequence_net = PetriNet("N_seq")
    for net in nets:
        copy_places_transitions_and_arcs(net, sequence_net)
    for i in range(len(nets) - 1):
        t = create_transition(None)
        sequence_net.transitions.add(t)
        petri_utils.add_arc_from_to(final_places[i], t, sequence_net)
        petri_utils.add_arc_from_to(t, initial_places[i+1], sequence_net)
    return (sequence_net, initial_places[0], final_places[-1])


def parallel_composition(nets, initial_places, final_places):
    """
    Performs a parallel composition on the specified nets.

    Parameters
    ----------
    nets: list
        a list containing all workflow nets that should be parallely
        composed in the order they should be composed
    initial_places: list
        a list containing the initial places of the nets in the nets-list,
        occurring in the same order as the nets they belong to
    final_places: list
        a list containing the final places of the nets in the nets-list,
        occurring in the same order as the nets they belong to

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.PetriNet.Place,
     pm4py.objects.petri_net.obj.PetriNet.Place)
        the Petri net obtained by parallely composing the input nets,
        as well as the new initial and final place
    """

    parallel_net = PetriNet("N_and")
    for net in nets:
        copy_places_transitions_and_arcs(net, parallel_net)
    pi = create_place()
    parallel_net.places.add(pi)
    ti = create_transition(None)
    parallel_net.transitions.add(ti)
    to = create_transition(None)
    parallel_net.transitions.add(to)
    po = create_place()
    parallel_net.places.add(po)
    petri_utils.add_arc_from_to(pi, ti, parallel_net)
    petri_utils.add_arc_from_to(to, po, parallel_net)
    for i in range(len(nets)):
        petri_utils.add_arc_from_to(ti, initial_places[i], parallel_net)
        petri_utils.add_arc_from_to(final_places[i], to, parallel_net)
    return (parallel_net, pi, po)


def choice_composition(nets, initial_places, final_places):
    """
    Performs a choice composition on the specified nets.

    Parameters
    ----------
    nets: list
        a list containing all workflow nets that should be choice-
        composed in the order they should be composed
    initial_places: list
        a list containing the initial places of the nets in the nets-list,
        occurring in the same order as the nets they belong to
    final_places: list
        a list containing the final places of the nets in the nets-list,
        occurring in the same order as the nets they belong to

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.PetriNet.Place,
     pm4py.objects.petri_net.obj.PetriNet.Place)
        the Petri net obtained by choice-composing the input nets,
        as well as the new initial and final place
    """

    choice_net = PetriNet("N_xor")
    for net in nets:
        copy_places_transitions_and_arcs(net, choice_net)
    pi = create_place()
    choice_net.places.add(pi)
    po = create_place()
    choice_net.places.add(po)
    for i in range(len(nets)):
        ti = create_transition(None)
        choice_net.transitions.add(ti)
        to = create_transition(None)
        choice_net.transitions.add(to)
        petri_utils.add_arc_from_to(pi, ti, choice_net)
        petri_utils.add_arc_from_to(ti, initial_places[i], choice_net)
        petri_utils.add_arc_from_to(final_places[i], to, choice_net)
        petri_utils.add_arc_from_to(to, po, choice_net)
    return (choice_net, pi, po)


def loop_composition(nets, initial_places, final_places):
    """
    Performs a loop composition on the specified nets.

    Parameters
    ----------
    nets: list
        a list containing all workflow nets that should be loop-
        composed in the order they should be composed
    initial_places: list
        a list containing the initial places of the nets in the nets-list,
        occurring in the same order as the nets they belong to
    final_places: list
        a list containing the final places of the nets in the nets-list,
        occurring in the same order as the nets they belong to

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.PetriNet.Place,
     pm4py.objects.petri_net.obj.PetriNet.Place)
        the Petri net obtained by loop-composing the input nets,
        as well as the new initial and final place
    """

    loop_net = PetriNet("N_loop")
    for net in nets:
        copy_places_transitions_and_arcs(net, loop_net)
    pi = create_place()
    loop_net.places.add(pi)
    ti = create_transition(None)
    loop_net.transitions.add(ti)
    petri_utils.add_arc_from_to(pi, ti, loop_net)
    po = create_place()
    loop_net.places.add(po)
    to = create_transition(None)
    loop_net.transitions.add(to)
    petri_utils.add_arc_from_to(to, po, loop_net)
    p_loop_start = create_place()
    loop_net.places.add(p_loop_start)
    petri_utils.add_arc_from_to(ti, p_loop_start, loop_net)
    p_loop_end = create_place()
    loop_net.places.add(p_loop_end)
    petri_utils.add_arc_from_to(p_loop_end, to, loop_net)
    t_restart = create_transition(None)
    loop_net.transitions.add(t_restart)
    petri_utils.add_arc_from_to(t_restart, initial_places[0], loop_net)
    petri_utils.add_arc_from_to(p_loop_start, t_restart, loop_net)
    t_end_loop = create_transition(None)
    loop_net.transitions.add(t_end_loop)
    petri_utils.add_arc_from_to(final_places[0], t_end_loop, loop_net)
    petri_utils.add_arc_from_to(t_end_loop, p_loop_end, loop_net)
    for i in range(1, len(nets)):
        t_restart = create_transition(None)
        loop_net.transitions.add(t_restart)
        petri_utils.add_arc_from_to(final_places[i], t_restart, loop_net)
        petri_utils.add_arc_from_to(t_restart, p_loop_start, loop_net)
        t_end_loop = create_transition(None)
        loop_net.transitions.add(t_end_loop)
        petri_utils.add_arc_from_to(t_end_loop, initial_places[i], loop_net)
        petri_utils.add_arc_from_to(p_loop_end, t_end_loop, loop_net)
    return (loop_net, pi, po)


def convert_to_petri_net(tree):
    """
    A method that recursively translates a process tree in to a workflow net.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the tree that should be converted into a workflow net

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.PetriNet.Place,
     pm4py.objects.petri_net.obj.PetriNet.Place)
        the workflow net obtained after the conversion, as well as
        its initial and final place

    This method creates a workflow net according to the composition rules
    used to create block-structured workflow nets, without removing tau
    transitions. If the passed tree is a leaf, this method returns a workflow
    net containing only an initial place, a final place and a transition with
    the label specified in the tree node.
    The only allowed Operators in tree-nodes are SEQUENCE, PARALLEL, XOR and LOOP.
    """

    if tree.is_leaf():
        result_net = PetriNet("N_"+str(tree.label))
        initial_place = create_place()
        transition = create_transition(tree.label)
        final_place = create_place()
        result_net.places.add(initial_place)
        result_net.transitions.add(transition)
        result_net.places.add(final_place)
        petri_utils.add_arc_from_to(initial_place, transition, result_net)
        petri_utils.add_arc_from_to(transition, final_place, result_net)
        return (result_net, initial_place, final_place)
    else:
        operator = tree.operator
        nets = []
        initial_places = []
        final_places = []
        for child in tree.children:
            (net, ip, fp) = convert_to_petri_net(child)
            nets += [net]
            initial_places += [ip]
            final_places += [fp]
        if operator is Operator.SEQUENCE:
            return sequence_composition(nets, initial_places, final_places)
        elif operator is Operator.PARALLEL:
            return parallel_composition(nets, initial_places, final_places)
        elif operator is Operator.XOR:
            return choice_composition(nets, initial_places, final_places)
        elif operator is Operator.LOOP:
            return loop_composition(nets, initial_places, final_places)
        else:
            raise Exception("Unsupported operator " + str(operator) + ".")


def convert_to_marked_petri_net(tree):
    """
    A method that recursively translates a process tree in to a
    marked workflow net.

    Parameters
    ----------
    tree: id_process_tree.IdentifiableProcessTree
        the tree that should be converted into a marked workflow net

    Returns
    -------
    (pm4py.objects.petri_net.obj.PetriNet,
     pm4py.objects.petri_net.obj.Marking,
     pm4py.objects.petri_net.obj.Marking)
        the workflow net obtained after the conversion, as well as
        its initial and final marking

    This method calls the method
    convert_to_petri_net(tree)
    and adds an initial marking [p_i], where p_i is the initial place
    of the resulting workflow net, and a final marking [p_o], where
    p_o is the final place of the resulting workflow net.
    """

    (net, initial_place, final_place) = convert_to_petri_net(tree)
    initial_marking = Marking()
    initial_marking[initial_place] = 1
    final_marking = Marking()
    final_marking[final_place] = 1
    return (net, initial_marking, final_marking)
