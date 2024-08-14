from math import log
from pm4py.objects.petri_net.obj import PetriNet

def average_connector_degree(N: PetriNet):
    """
    A method calculating the average connector degree of a Petri net.

    Parameters
    ----------
    N: pm4py.objects.petri_net.obj.PetriNet
        the input Petri net, of which we want to know
        the average connector degree

    Returns
    -------
    float or None
        a float representing the average connector degree
        or None if the net does not have any connectors

    There are two types of connectors in Petri nets: and-connectors
    and xor-connectors. An and-connector is a transition that has
    more than one incoming or outgoing arc, an xor-connector is a
    place with more than one incoming or outgoing arc.
    The degree of a connector is the total number of arcs that start
    or end at the connector. The average connector degree is the sum
    of all connector-degrees divided by the number of connectors.
    """

    connector_degree_sum = 0
    number_of_connectors = 0
    for x in N.places.union(N.transitions):
        if len(x.in_arcs) > 1 or len(x.out_arcs) > 1:
            number_of_connectors += 1
            connector_degree_sum += len(x.in_arcs) + len(x.out_arcs)
    if number_of_connectors == 0:
        return None
    else:
        return connector_degree_sum / number_of_connectors


def connector_heterogeneity(N: PetriNet):
    """
    A method calculating the connector heterogeneity of a Petri net.

    Parameters
    ----------
    N: pm4py.objects.petri_net.obj.PetriNet
        the input Petri net, of which we want to know
        the connector heterogeneity score

    Returns
    -------
    float or None
        a float representing the connector heterogeneity
        or None if the net does not have any connectors

    There are two types of connectors in Petri nets: and-connectors
    and xor-connectors. An and-connector is a transition that has
    more than one incoming or outgoing arc, an xor-connector is a
    place with more than one incoming or outgoing arc.
    The connector heterogeneity describes the entropy of the connectors.
    If the net contains only one type of connectors, its connector
    heterogeneity is 0. If it contains both connector types equally
    often, its connector heterogeneity is 1.
    """

    and_connectors = [p.name for p in N.places if len(p.in_arcs) > 1 or len(p.out_arcs) > 1]
    xor_connectors = [t.name for t in N.transitions if len(t.in_arcs) > 1 or len(t.out_arcs) > 1]
    if len(and_connectors) + len(xor_connectors) == 0:
        return None
    rel_and = len(and_connectors) / (len(and_connectors) + len(xor_connectors))
    rel_xor = len(xor_connectors) / (len(and_connectors) + len(xor_connectors))
    if rel_and == 0 and rel_xor == 0:
        return None
    elif rel_and == 0 and rel_xor != 0:
        return -(rel_xor * log(rel_xor, 2))
    elif rel_and != 0 and rel_xor == 0:
        return -(rel_and * log(rel_and, 2))
    else:
        return -(rel_and * log(rel_and, 2) + rel_xor * log(rel_xor, 2))


def size(N: PetriNet):
    """
    A method returning the size of a Petri net

    Parameters
    ----------
    N: pm4py.objects.petri_net.obj.PetriNet
        the input Petri net, of which we want to know the size

    Returns
    -------
    int
        an integer value, which is the number of places plus
        the number of transitions in the net
    """

    return len(N.places) + len(N.transitions)
