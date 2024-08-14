import pm4py
import copy
import id_process_tree
from id_process_tree import IdentifiableProcessTree
from pm4py.objects.process_tree.obj import Operator
from random import choice, randrange, seed, shuffle, random


def remove_random_node_mutation(tree):
    """
    Randomly selects a node from the process tree and removes
    it from the process tree if its parent is not an iteration-node.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree in which a random node should be removed

    Returns
    -------
    IdentifiableProcessTree
        a copy of the input process tree where the change was performed
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and set the start for the search of a random node to the root of the tree
    remove_node = root.choose_random_node(True, True)                            # choose a random node of the tree, but none whose parent is an iteration-operator and not the root
    if remove_node is not None:                                                  # if there is no node besides the root, do nothing. Otherwise
        remove_node.parent.remove_child(remove_node)                             # remove the chosen node from the child-list of its parent
    return root                                                                  # return the resulting process tree


def add_random_node_mutation(tree, activities):
    """
    Randomly selects a node in the process tree and randomly
    selects an activity from the log to add the activity as
    a child of the chosen node.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree into which a random activity should be added
    activities: list
        the list of activities we allow to add to the tree

    Returns
    -------
    IdentifiableProcessTree
        a copy of the input process tree where the change was performed
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and set the start for the search of a random node to the root of the tree
    change_node = root.choose_random_node()                                      # choose any random node of the tree (possibly the root or the child of an iteration-operator)
    if change_node is None:                                                      # the situation where the tree has no nodes left should not occur
        raise Exception("The tree lost all of its nodes.")                       # if it does anyways, throw an exception
    add_activity = choice(activities + [None])                                   # choose a random activity from the set of activities, or None for a tau-transition
    new_leaf = IdentifiableProcessTree(label=add_activity)                       # create a new node for the chosen activity
    # If the selected node in the tree is a leaf, an operator
    # node is randomly chosen. The selected node and the randomly
    # chosen activity are then placed in the tree at the location
    # of the selected node under the randomly chosen operator.
    if change_node.is_leaf():                                                    # if the randomly selected node is a leaf (has no children):
        change_node.insert_op_node_parent(new_leaf)                              # insert the new operator node as the parent of the chosen node and the new leaf
    else:                                                                        # if the selected node is not a leaf, it is an operator node
        # If the selected node is an operator node the activity can be
        # added as an additional child, in an arbitrary location, to
        # this operator node.
        if randrange(2) == 0:                                                    # choose at random which operation to perform in this case
            change_node.add_child(new_leaf)                                      # in the first case, simply add the node for the randomly chosen activity as a child of the chosen node
        else:                                                                    # otherwise
            # It is also possible to add the activity next to the selected
            # operator node, under a randomly chosen operator.
            change_node.insert_op_node_parent(new_leaf)                          # insert the new operator node as the parent of the chosen node and the new leaf
    return root                                                                  # return the resulting process tree


def random_node_mutation(tree, activities):
    """
    Randomly selects a node from the process tree and changes its type.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree in which a node should change its type
    activities: list
        the list of activities we allow to add to the tree

    Returns
    -------
    IdentifiableProcessTree
        a copy of the input process tree where the change was performed

    If the chosen node is a leaf it is assigned a new activity. If it is
    an operator, on the other hand, it is assigned another operator type,
    except but not the iteration-operator.
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and set the root as the starting point for the search of a random node
    change_node = root.choose_random_node()                                      # choose a random node, possibly the root or a child of a loop node
    if change_node is None:                                                      # if the result is None, the tree has no nodes left
        raise Exception("The tree lost all of its nodes.")                       # raise an exception in this case
    if change_node.is_leaf():                                                    # if the chosen node is a leaf
        alt_activity = choice(activities + [None])                               # choose an activity or None for a tau-transition
        change_node.label = alt_activity                                         # change the label to the chosen activity
    else:                                                                        # otherwise the node is an operator-node
        alt_op = id_process_tree.choose_random_operator(no_loop=True)            # choose a new operator for this node that isn't an iteration-operator
        change_node.operator = alt_op                                            # change the operator type to the newly chosen one
    return root                                                                  # return the resulting process tree


def normalization_mutation(tree):
    """
    Applies a normalization operation on the whole process tree.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the process tree that should be normalized

    Returns
    -------
    IdentifiableProcessTree
        a copy of the process tree where the normalization was performed

    Normalization consists of two phases: flattening and sorting. Flattening
    of a process tree means that operators that have children that are of the
    same operator type are 'flattened' by absorbing the children of the child-
    operator, except when the node is an iteration-operator, since flattening
    can change the behavior in this case. The sorting phase sorts the children
    of a node alphabetically (in case of leaves), by operator type and then
    by size of the subtree. Sorting is not applied to sequence- and iteration-
    operators, since this would change the behavior.
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and store its root
    root.flatten()                                                               # flatten the tree, starting from the root
    root.sort()                                                                  # sort the tree, starting from the root
    return root                                                                  # return the resulting process tree


def remove_useless_node_mutation(tree):
    """
    Randomly selects a useless node from the tree (if there is any) and removes
    it without changing the behavior of the process tree.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the process tree of which a useless node should be deleted

    Returns
    -------
    IdentifiableProcessTree
        a copy of the process tree where the useless node was deleted
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and store its root
    (node, reason) = root.get_any_useless_node()                                 # choose a random useless node of the process tree
    if reason == 1:                                                              # if it is a tau-node in a sequence or parallel construct
        node.remove_node_from_tree()                                             # remove the node from the tree
    if reason == 2:                                                              # if the node is an operator node with only one child
        child = node.children.pop(0)                                             # get the child of the useless node
        node.replace_node_with(child)                                            # replace the node with the child
    if reason == 3:                                                              # if the node is an operator node that has only useless nodes as children
        return root                                                              # do nothing, since it is not clear how to handle this case
    if reason == 4:                                                              # if the node is a tau-node that is not the first tau node in a choice
        node.remove_node_from_tree()                                             # remove the node from the tree
    if reason == 5:                                                              # if the node is a loop consisting of only one other loop and otherwise tau-children
        loop_child = None                                                        # find the single loop-child:
        for child in node.children:                                              # iterate through all children of the node
            if child.operator == Operator.LOOP:                                  # if you found the loop-child
                loop_child = child                                               # store it
                break                                                            # end the for-loop
        node.replace_node_with(loop_child)                                       # replace the node with its loop-child
    if reason == 6:                                                              # if the node is a tau node of a parent for which condition 5 holds
        parent = node.parent                                                     # store the parent of the node
        loop_child = None                                                        # find the single loop-child:
        for child in parent.children:                                            # iterate through all children of the parent (i.e. through all siblings of the node)
            if child.operator == Operator.LOOP:                                  # if you find the loop-child
                loop_child = child                                               # store it
                break                                                            # end the for-loop
        parent.replace_node_with(loop_child)                                     # replace the parent with its loop-child
    if reason == 7:                                                              # if the node is of the same type as its parent
        parent = node.parent                                                     # store the parent of this node
        node.parent = None                                                       # set the parent of the node to be removed to None
        parent.children.remove(node)                                             # remove the node from the children-list of the parent
        for c in node.children:                                                  # add all children of the node
            parent.add_child(c)                                                  # as new children of the parent
    return root                                                                  # return the resulting process tree


def replace_tree_mutation(tree, alphabet):
    """
    Replaces the whole tree by a randomly created process tree.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree that should be replaced by a new randomly created
        process tree
    activities: list
        the list of activities we allow to add to the tree

    Returns
    -------
    IdentifiableProcessTree
        a copy of the new randomly created process tree

    The main purpose of this mutation operation is to increase
    the variateion of the population.
    """

    return id_process_tree.generate_random_process_tree(alphabet)                # return a new process tree as the result of this method


def shuffle_mutation(tree):
    """
    Rearranges the order of the children in a randomly chosen choice- or
    parallel-operator.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree in which a choice- or parallel-operator should
        reorder its children

    Returns
    -------
    IdentifiableProcessTree
        a copy of the input process tree where the children of
        a randomly chosen choice- or parallel-operator were rearranged

    The main purpose of this mutation is to change the structure of the
    process tree to possibly make it better suited for one of the other
    mutations to improve the quality of the process tree.
    """

    root = copy.deepcopy(tree._get_root())                                       # copy the tree and store its root
    node = root.choose_random_choice_par()                                       # choose a random node that is a choice- or parallel-operator
    if node is not None:
        shuffle(node.children)                                                   # change the order of the children of the chosen node
    return root                                                                  # return the resulting process tree


# Randomly chooses one of the mutations for the passed process tree
def mutate(tree, alphabet, prob_remove=0.15, prob_add=0.3, prob_mutate=0.15, prob_norm=0.15, prob_useless=0.15, prob_replace=0.05):
    """
    Randomly chooses a mutation for the passed process tree and performs it.

    Parameters
    ----------
    tree: IdentifiableProcessTree
        the tree that should be mutated
    alphabet: list
        a list of symbols that are allowed to add to a process tree
    prob_remove: float (default 0.15)
        the probability to remove a node from the tree
    prob_add: float (default 0.3)
        the probability to randomly add a new node to the tree
    prob_mutate: float (default 0.15)
        the probability to change the type of a node in the tree
    prob_norm: float (default 0.15)
        the probability to normalize the process tree
    prob_useless: float (default 0.15)
        the probability to remove a useless node from the tree
    prob_replace: float (default 0.05)
        the probability to replace the tree by a newly generated one

    Returns
    -------
    IdentifiableProcessTree
        a copy of the mutated input process tree 
    """

    prob_sum = 0
    r = random()
    if r <= prob_remove:
        prob_sum += prob_remove
        return remove_random_node_mutation(tree._get_root())
    elif r <= prob_sum + prob_add:
        prob_sum += prob_add
        return add_random_node_mutation(tree._get_root(), alphabet)
    elif r <= prob_sum + prob_mutate:
        prob_sum += prob_mutate
        return random_node_mutation(tree._get_root(), alphabet)
    elif r <= prob_sum + prob_norm:
        prob_sum += prob_norm
        return normalization_mutation(tree._get_root())
    elif r <= prob_sum + prob_useless:
        prob_sum += prob_useless
        return remove_useless_node_mutation(tree._get_root())
    elif r <= prob_sum + prob_replace:
        prob_sum += prob_replace
        return replace_tree_mutation(tree._get_root(), alphabet)
    else:
        return shuffle_mutation(tree._get_root())
