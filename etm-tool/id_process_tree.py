from pm4py import view_process_tree
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator
from copy import deepcopy
from random import randrange, choice

ID = 0

class IdentifiableProcessTree(object):
    """
    A class used to represent process trees, where each element
    has a unique identifier.

    Attributes
    ----------
    _id: int
        the unique identifier of the node
    _operator: pm4py.objects.process_tree.obj.Operator
        the operator represented by this node, or None if it is a leaf
    _parent: IdentifiableProcessTree
        a pointer to the parent of this node, or None if this node is the root
    _children: list
        a list of process trees that are children of this node
    _label: str
        the label of this node if it is a leaf, or None otherwise

    Except for the identifier, the code of the first part of this class is
    from pm4py.objects.process_tree.obj. We added the unique identifier to
    differ between two nodes with the same label or operator. Furthermore,
    we added more utility methods to easily adapt process trees.
    """

    def __init__(self, operator=None, parent=None, children=None, label=None):
        # generate and store unique identifier
        global ID
        self._id = ID
        ID += 1
        self._operator = operator
        self._parent = parent
        self._children = list() if children is None else children
        self._label = label

    def __hash__(self):
        if self.label is not None:
            return hash((self._id, self.label))
        elif len(self.children) == 0:
            return self._id * 37
        else:
            h = 1337
            for i in range(len(self.children)):
                h += 41 * i * hash(self.children[i])
            if self.operator == Operator.SEQUENCE:
                h = h * 13
            elif self.operator == Operator.XOR:
                h = h * 17
            elif self.operator == Operator.OR:
                h = h * 23
            elif self.operator == Operator.PARALLEL:
                h = h * 29
            elif self.operator == Operator.LOOP:
                h = h * 37
            elif self.operator == Operator.INTERLEAVING:
                h = h * 41
            return self._id * h % 268435456

    def _set_operator(self, operator):
        self._operator = operator

    def _set_parent(self, parent):
        self._parent = parent

    def _set_label(self, label):
        self._label = label

    def _set_children(self, children):
        self._children = children

    def _get_children(self):
        return self._children

    def _get_parent(self):
        return self._parent

    def _get_operator(self):
        return self._operator

    def _get_label(self):
        return self._label

    def __eq__(self, other):
        if isinstance(other, ProcessTree):
            # Just check if the IDs are the same
            return self._id == other._id
        return False

    def __repr__(self):
        if self.operator is not None:
            rep = str(self._operator) + '( '
            for i in range(0, len(self._children)):
                child = self._children[i]
                if len(child.children) == 0:
                    if child.label is not None:
                        rep += '\'' + str(child) + '\'' + ', ' if i < len(self._children) - 1 else '\'' + str(
                            child) + '\''
                    else:
                        rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
                else:
                    rep += str(child) + ', ' if i < len(self._children) - 1 else str(child)
            return rep + ' )'
        elif self.label is not None:
            return self.label
        else:
            return 'tau'

    def __str__(self):
        return self.__repr__()

    def _get_root(self):
        root = self
        while root._get_parent() is not None:
            root = root._get_parent()
        return root

    def _print_tree(self):
        root = self._get_root()
        print(root)

    parent = property(_get_parent, _set_parent)
    children = property(_get_children, _set_children)
    operator = property(_get_operator, _set_operator)
    label = property(_get_label, _set_label)

    # New public methods of this class

    def build_process_tree(self, father=None):
        """
        Recursively translates this IdentifiableProcessTree into a
        ProcessTree as defined in the pm4py library.

        Parameters
        ----------
        father: IdentifiableProcessTree (default None)
            the father of the current node

        Returns
        -------
        pm4py.objects.process_tree.obj.ProcessTree
            the input process tree in the structure provided by pm4py
        """

        PT = ProcessTree(label=self.label, operator=self.operator)               # copy the label and the operator into a new ProcessTree structure
        PT.parent = father                                                       # set the parent to the ProcessTree passed as a parameter
        for child in self.children:                                              # go through all children,
            PT.children.append(child.build_process_tree(PT))                     # call the procedure for the children and add them as children to the current node
        return PT                                                                # return the resulting process tree


    def visualize_process_tree(self, format='png'):
        """
        Shows the process tree as a graphviz picture in the specified format.

        Parameters
        ----------
        format: str (default 'png')
            the format in which the process three should be shown
        """

        PT = self.build_process_tree()                                           # translate the IdentifiableProcessTree into a ProcessTree from pm4py
        view_process_tree(PT, format=format)                                     # use the method of pm4py to visualize the process tree


    def add_child(self, child):
        """
        Adds the passed child to the child-list of this root and sets the
        parent-pointer of the child to the root

        Parameters
        ----------
        child: IdentifiableProcessTree
            the node that should be added as a child of the current node
        """

        child.parent = self                                                      # set the parent pointer of the child to the root of this tree
        self.children.append(child)                                              # add the child to the list of children of this tree's root


    def remove_child(self, child):
        """
        Removes a child from the children-list of this tree's root.

        Parameters
        ----------
        child: IdentifiableProcessTree
            the child of the current node that should be removed
            from the children-list

        If this method leaves the root with less than two children,
        it replaces the current node by the only children or deletes
        it if there aren't any children left. This way, we avoid
        producing process trees that contain "useless" operator-nodes
        with zero or one children.
        """

        child.parent = None                                                      # set the parent of the child to be removed to None
        self.children.remove(child)                                              # remove the child from the children-list of this root
        # if this node has 0 or 1 children remaining,
        # add these children as children of the parent
        if len(self.children) < 2:                                               # if there are less than two children remaining for the root
            if self.parent is not None:                                          # and the parent of this root is present
                for child in self.children:                                      # go through all children to
                    self.parent.add_child(child)                                 # add the children of this root to the parent's children list
                self.parent.remove_child(self)                                   # and remove the root
            else:                                                                # otherwise, if the current node has no parent
                if len(self.children) == 0:                                      # and it also doesn't have any children
                    self.label = None                                            # it is the only node in the tree, so set its label to None
                    self.operator = None                                         # and its operator to None, thus creating a single tau-node
                else:                                                            # if the current node does have children
                    child = self.children.pop(0)                                 # it can only be one (otherwise we wouldn't land in this case), so store this child
                    child.parent = None                                          # set its parent to None, because it will become the root
                    self._id = child._id                                         # set the ID of this node to the ID of the child that will replace the node
                    self.label = child.label                                     # and replace the current root with the child by copying its label,
                    self.operator = child.operator                               # its operator
                    for grandchild in child.children:                            # and all of its children
                        self.add_child(grandchild)


    def swap_child(self, child, new_child):
        """
        Replaces the child passed as a first parameter with the
        node passed as the second parameter.

        Parameters
        ----------
        child: IdentifiableProcessTree
            the child of the current node that should be replaced
        new_child: IdentifiableProcessTree
            the node that should be a child of the current node instead
        """

        child.parent = None                                                      # set the parent of the old child to None
        self.children.remove(child)                                              # remove the child from the child-list, but don't delete inner nodes if they have only one child left
        self.add_child(new_child)                                                # because in the next step, add the new child to the children-list of this node


    def remove_all_children(self):
        """
        Removes all children of the current node by clearing its
        children list.
        """

        for c in self.children:                                                  # go through all children of the children-list
            c.parent = None                                                      # set their parent to None
        self.children.clear()                                                    # delete all contents of the children-list


    def is_leaf(self):
        """
        Returns whether the current node is a leaf.

        Returns
        -------
        bool
            a boolean that is True if the current node has no children
            and False otherwise
        """

        return len(self.children) == 0                                           # return whether this node has no children


    def list_leaf_labels(self):
        """
        Returns the list of labels the process tree contains.

        Returns
        -------
        list
            a list of strings that occur as labels in the process tree
        """

        if self.is_leaf():
            label = self.label
            return [label]
        else:
            labels = []
            for child in self.children:
                labels += child.list_leaf_labels()
            return labels


    def tree_size(self):
        """
        Returns the number of nodes in the tree that starts with the current
        node as the root.

        Returns
        -------
        int
            the number of nodes in the subtree of the current node; the
            current node is also counted
        """

        if self.is_leaf():                                                       # if the current node is a leaf
            return 1                                                             # it has no nodes below it, so the number of nodes in its subtree is 1
        else:                                                                    # otherwise
            sum = 1                                                              # count the current node
            for child in self.children:                                          # go through all children
                sum += child.tree_size()                                         # and add the number of nodes in their subtrees
            return sum                                                           # return the total number of nodes found in this way


    def insert_op_node_parent(self, new_leaf):
        """
        Adds a random operator node with the passed leaf as a child
        as the parent of this node.

        Parameters
        ----------
        new_leaf: IdentifiableProcessTree
            the second child that the new operator node should get

        If this node already has a parent, the new operator node
        replaces this node as a child of said parent.
        """

        op = choose_random_operator()                                            # choose a random operator for the parent node
        new_op_node = IdentifiableProcessTree(operator=op)                       # create a new node for the chosen operator
        if self.parent is not None:                                              # if this node has a parent
            self.parent.swap_child(self, new_op_node)                            # replace the node by the new operator node
        new_op_node.add_child(self)                                              # add this node as a child of the operator node
        new_op_node.add_child(new_leaf)                                          # add the new leaf as a child of the operator node


    def has_loop_parent(self):
        """
        Returns whether the parent of this node is an iteration-operator.

        Returns
        -------
        bool
            a boolean that is True if the current node has a parent that
            is an iteration-operator, or True if it either has no parent
            or its parent is not an iteration-operator
        """

        return self.parent is not None and self.parent.operator == Operator.LOOP # return whether the parent is present and whether it is a iteration-operator


    def list_all_nodes(self, ignore_if_parent_is_loop=False, ignore_root=False):
        """
        Returns a list of all nodes in the process tree in prefix order.

        Parameters
        ----------
        ignore_if_parent_is_loop: bool (default False)
            a boolean indicating whether nodes whose parents are iteration-
            nodes should be ignored (i.e. not appear in the list)
        ignore_root: bool (default False)
            a boolean indicating whether the root should be ignored
            (i.e. not appear in the list)

        Returns
        -------
        list
            a list of all nodes that should not be ignored in prefix order
        """

        all_nodes = []                                                           # create a list for all nodes in the tree
        if not ignore_root:                                                      # if the root should not be ignored
            if not ignore_if_parent_is_loop or self.has_loop_parent():           # and either we don't want to ignore nodes whose parents are loops or the parent of the current node is no loop
                all_nodes += [self]                                              # add the current node to the list of nodes
        if self.is_leaf():                                                       # if the node has no children, and is therefore a leaf, we are done
            return all_nodes                                                     # and return the list of nodes we collected
        else:                                                                    # otherwise
            for child in self.children:                                          # we go through all children of this node
                all_nodes += child.list_all_nodes()                              # and recursively collect the nodes in their subtrees
        return all_nodes                                                         # return the list of collected nodes


    def choose_random_node(self, ignore_if_parent_is_loop=False, without_root=False):
        """
        Uniformly chooses a random node of the process tree

        Parameters
        ----------
        ignore_if_parent_is_loop: bool (default False)
            a boolean indicating whether nodes whose parents are iteration-
            nodes should be ignored (i.e. not appear in the list)
        ignore_root: bool (default False)
            a boolean indicating whether the root should be ignored
            (i.e. not appear in the list)

        Returns
        -------
        IdentifiableProcessTree
            a uniformly chosen node of the process tree, where nodes
            with loop-parents and roots are ignored as specified, or
            None if no node in the tree fulfills the requirements
        """

        nodes = self.list_all_nodes(ignore_if_parent_is_loop, without_root)      # get a list of all nodes in the tree
        if len(nodes) == 0:                                                      # if there aren't any candidate nodes
            return None                                                          # return None
        return choice(nodes)                                                     # otherwise choose one of the nodes and return it


    def list_choice_and_par_nodes(self):
        """
        Returns a list of all nodes that are choice or parallel operators.

        Returns
        -------
        list
            a list containing all nodes of the process tree whose operator
            attribute is either Operator.XOR or Operator.PARALLEL
        """

        choice_par_nodes = []                                                    # create a list for all nodes that are choices or parallel connectors
        if self.operator in [Operator.XOR, Operator.PARALLEL]:                   # if the current node has one of these two types
            choice_par_nodes += [self]                                           # add it to the list
        if self.is_leaf():                                                       # if the current node is a leaf
            return choice_par_nodes                                              # there aren't any nodes left, so return the list of choice and parallel nodes
        else:                                                                    # otherwise
            for child in self.children:                                          # go through all children
                choice_par_nodes += child.list_choice_and_par_nodes()            # and collect the choice and parallel nodes of its children
        return choice_par_nodes                                                  # return the list of nodes collected in this way


    def choose_random_choice_par(self):
        """
        Uniformly chooses a random node of the process tree that
        is either a choice or a parallel operator.

        Returns
        -------
        IdentifiableProcessTree
            a uniformly chosen node of the process tree whose operator
            attribute is either Operator.XOR or Operator.PARALLLEL
        """

        choice_par_nodes = self.list_choice_and_par_nodes()                      # generate the list of all choice and parallel nodes
        if len(choice_par_nodes) == 0:
            return None
        return choice(choice_par_nodes)                                          # choose a random element of this list and return it


    def is_silent(self):
        """
        Returns whether this node is a silent transition.

        Returns
        -------
        bool
            a boolean that is True if the label of the current
            node is None and the operator of the current node
            is None, and False otherwise
        """

        return self.label is None and self.operator is None                      # return whether the label and the operator are both set to None


    def is_root(self):
        """
        Returns whether this node is the root of its process tree

        Returns
        -------
        bool
            a boolean that is True if the current node has no parent
            and False otherwise
        """

        return self.parent is None                                               # return whether this node has no parent


    def is_useless(self):
        """
        Returns a value > 0 if the current node is useless or a value = 0
        if it is not useless.

        Returns
        -------
        int
            an integer that is 0 if the current node is useless or a value
            between 1 and 7 if it is useless

        The concrete value returned represents the reason why the node
        is useless:
        1. The node is a tau-node in a sequence or a parallel construct;
        2. The node is an operator node with only one child;
        3. The node is an operator node that has only useless nodes as children;
        4. The node is a tau-node and is not the only tau-node in a choice;
        5. The node is a loop consisting of only one other loop function and
           otherwise tau-children;
        6. The node is a tau-node of a parent for which condition 5 holds;
        7. The node is of the same type as its parent (unless it is an
           iteration-operator);
        """

        if self.is_root() and self.is_leaf():                                    # if the tree consists of only a single node
            return 0                                                             # this node cannot be useless, so return 0
        # 1. The node is a tau-node in a sequence or a parallel construct;
        if self.is_silent() and self.parent.operator in [Operator.SEQUENCE, Operator.PARALLEL]:
            return 1
        # 2. The node is an operator node with only one child;
        if self.operator is not None and len(self.children) == 1:
            return 2
        # 4. The node is a tau-node and is not the only tau-node in a choice
        if self.label is None and self.operator is None and self.parent.operator == Operator.XOR:
            parent = self.parent
            tau_nodes = 0
            for sibling in parent.children:
                if sibling.label == None:
                    tau_nodes += 1
            if tau_nodes > 1:
                return 4
        # 5. The node is a loop consisting of only one other loop function and otherwise tau-children
        if self.operator == Operator.LOOP and self.starts_useless_double_loop():
            return 5
        # 6. The node is a tau-node of a parent for which condition 5 holds
        if self.label is None and self.operator is None and self.parent.starts_useless_double_loop():
            return 6
        # 7. The node is of the same type as its parent (unless it is an iteration-operator)
        if self.operator != Operator.LOOP and self.parent is not None and self.operator == self.parent.operator:
            return 7
        # 3. The node is an operator node that has only useless nodes as children;
        if self.operator is not None:
            for child in self.children:
                if child.is_useless() == 0:
                    return 0
            return 3
        return 0


    def list_useless_nodes(self, useless_dict = {}):
        """
        Fills the passed dictionary with nodes that are useless, as well as
        the numerical representation of the reason for its uselessness.

        Parameters
        ----------
        useless_dict: dict (default {})
            a dictionary into which the useless nodes should be added as keys
            with values indicating why the node is useless

        Returns
        -------
        dict
            a dictionary containing all useless nodes of this tree as keys
            whose values represent the reason why the node is useless

        Please be aware that this method changes the passed dictionary.
        The concrete values for each node represent the reason why the node
        is useless:
        1. The node is a tau-node in a sequence or a parallel construct;
        2. The node is an operator node with only one child;
        3. The node is an operator node that has only useless nodes as children;
        4. The node is a tau-node and is not the only tau-node in a choice;
        5. The node is a loop consisting of only one other loop function and
           otherwise tau-children;
        6. The node is a tau-node of a parent for which condition 5 holds;
        7. The node is of the same type as its parent (unless it is an
           iteration-operator);
        """

        root_useless = self.is_useless()                                         # store whether the current node is useless
        if root_useless != 0:                                                    # if it is
            useless_dict[self] = root_useless                                    # add it and the reason for its uselessness to the dictionary
        for child in self.children:                                              # go through all children of this node
            child.list_useless_nodes(useless_dict)                               # collect all useless nodes in the subtrees of the children
        return useless_dict                                                      # return the dictionary of useless nodes


    def get_any_useless_node(self):
        """
        Returns a uniformly chosen useless node of the process tree, as well
        as a numerical representation of the reason why the node is useless.

        Returns
        -------
        (IdentifiableProcessTree, int)
            a uniformly chosen node of the process tree that is useless and
            a numerical representation of the reason why the node is useless

        The concrete numerical value returned represents the reason why the node
        is useless:
        1. The node is a tau-node in a sequence or a parallel construct;
        2. The node is an operator node with only one child;
        3. The node is an operator node that has only useless nodes as children;
        4. The node is a tau-node and is not the only tau-node in a choice;
        5. The node is a loop consisting of only one other loop function and
           otherwise tau-children;
        6. The node is a tau-node of a parent for which condition 5 holds;
        7. The node is of the same type as its parent (unless it is an
           iteration-operator);
        """

        useless_dict = {}                                                        # initialize the dictionary of useless nodes and the reasons for their uselessness
        useless_dict = self.list_useless_nodes(useless_dict)                     # collect the dictionary of useless nodes
        if len(useless_dict) == 0:                                               # if there aren't any useless nodes in the tree
            return (None, 0)                                                     # return the special value (None, 0)
        node = choice(list(useless_dict.keys()))                                 # otherwise choose an arbitrary node from the dictionary
        reason = useless_dict[node]                                              # store the reason why this node is useless
        return (node, reason)                                                    # and return the pair of node and reason


    def starts_useless_double_loop(self):
        """
        Returns whether a node is a loop whose children consist of one exactly
        loop and otherwise just tau nodes.

        Returns
        -------
        bool
            a boolean that is True if the children of this node consist of
            exactly one loop node and otherwise tau nodes
        """

        if self.operator == Operator.LOOP:                                       # if this node is a iteration-operator
            number_of_loop_children = 0
            number_of_tau_children = 0
            for child in self.children:                                          # go through all children
                if child.operator == Operator.LOOP:                              # count the number of children that are also iteration-operators
                    number_of_loop_children += 1
                if child.is_silent():                                            # count the number of children that are tau-transitions
                    number_of_tau_children += 1
            if number_of_loop_children == 1:                                     # if the number of children that are iteration-operators is exactly one
                if number_of_tau_children == len(self.children) - 1:             # and all other children are tau-nodes
                    return True                                                  # return True, indicating that this node is useless
        return False                                                             # otherwise return False, indicating that this node is not useless


    def flatten(self):
        """
        Flattens a process tree by combining nodes with the same operator
        value that are in a parent-child relationship

        Returns
        -------
        IdentifiableProcessTree
            the flattened process tree, where no parent-child pair has the
            same operator type

        Flattening a process tree means that operators that have children
        with the same operator type are 'flattened' by absorbing the children
        of the child operator, except when the node is an iteration operator,
        since flattening in this case would change the behavior of the tree.
        """

        if not self.is_leaf():                                                   # continue only if the current node is not a leaf, since we don't have to do anything for leaf-nodes
            for child in self.children:                                          # go through all children
                child.flatten()                                                  # and flatten them
                if child.operator == self.operator:                              # if a child is an operator-node of the same type as the current node
                    child.parent = None                                          # set the parent of the child to remove to None
                    self.children.remove(child)                                  # remove the child from the children-list of the current node
                    for grandchild in child.children:                            # and go through all children of the child
                        self.add_child(grandchild)                               # to add them as children for the current node


    def sort(self):
        """
        Sorts a process tree by ordering the children of each node primarily
        by label, secondary by operator type and ternary by the size of the
        subtree.

        Sorting is not applied to sequence- and iteration-operators, since
        this would change the behavior of the tree.
        """

        # Inner method that returns by which keys nodes should be sorted
        def sorting_key(node):
            operator_value = {None: 0, Operator.SEQUENCE: 1, Operator.XOR: 2, Operator.PARALLEL: 3, Operator.LOOP: 4}
            if node.label != None:
                return (node.label, operator_value[node.operator], node.tree_size())
            else:
                return ('', operator_value[node.operator], node.tree_size())
        # Start of sorting
        if not self.is_leaf() and self.operator not in [Operator.SEQUENCE, Operator.LOOP]:
            self.children.sort(key = lambda c: sorting_key(c))
        for child in self.children:
            child.sort()


    def remove_node_from_tree(self):
        """
        Removes the current node from the process tree.

        If removing the node from the node from the child-list of the
        parent would leave the parent without any children, this
        method recursively removes the parent. If the node is the
        root of the tree, the method does nothing.
        """

        parent = self.parent                                                     # store the parent of this node
        if parent is not None:                                                   # if this node has no parent, do nothing
            parent.remove_child(self)                                            # otherwise remove this node from the parent's children-list


    def replace_node_with(self, replacement):
        """
        Replaces the current node with the node passed as an argument.

        Parameters
        ----------
        replacement: IdentifiableProcessTree
            the node that should replace the current node in the tree

        If the current node is the root, this method changes the root
        to the second parameter. Otherwise, it removes the first
        parameter from its parent's children list and appends the
        replacement to the children list instead.
        """

        if self.is_root():                                                       # if the current node is the root, i.e. it has no parent
            self._id = replacement._id                                           # set the ID of the old node to the ID of the replacement
            self.label = replacement.label                                       # set the label of this node to the label of the replacement
            self.operator = replacement.operator                                 # set the operator of this node to the operator of the replacement
            self.remove_all_children()                                           # remove all current children of this node
            for c in replacement.children:                                       # and go through all children of the replacement
                self.add_child(c)                                                # adding them as children instead
        else:                                                                    # if the current node has a parent
            parent = self.parent                                                 # store this parent
            parent.swap_child(self, replacement)                                 # and swap the current node with the replacement node


def choose_random_operator(no_loop=False):
    """
    Returns a randomly chosen operator of the list
    [Operator.SEQUENCE, Operator.PARALLEL, Operator.XOR, Operator.LOOP].

    Parameters
    ----------
    no_loop: bool
        a boolean indicating whether it should be impossible to choose
        a loop operator

    Returns
    -------
    pm4py.objects.process_tree.obj.Operator
        one randomly operator of the list
        [Operator.SEQUENCE, Operator.PARALLEL, Operator.XOR, Operator.LOOP]
        or the list [Operator.SEQUENCE, Operator.PARALLEL, Operator.XOR]
        if loops are not allowed
    """

    operators = [Operator.SEQUENCE, Operator.PARALLEL, Operator.XOR]
    if not no_loop:
        operators += [Operator.LOOP]
    return choice(operators)


def randomly_split_alphabet(alphabet, parts):
    """
    Randomly splits the passed alphabet into the specified amount of lists

    Parameters
    ----------
    alphabet: list / set
        a list containing each valid symbol of the alphabet exactly once
    parts: int
        the number of non-empty parts in which the alphabet should be splitted

    Returns
    -------
    list
        a list containing all parts into which the alphabet was splitted

    Example: When calling this method for alphabet = ['a','b','c','d'] and
    parts = 2, this method splits the alphabet randomly into two parts, but
    ensures that each part contains at least one symbol of the alphabet.
    For example, the output for this example could be [['c'],['a','b','d']].
    """

    to_distribute = deepcopy(list(alphabet))
    splitted_alphabets = []
    for i in range(0, parts):
        symbol = choice(to_distribute)
        splitted_alphabets += [[symbol]]
        to_distribute.remove(symbol)
    while len(to_distribute) != 0:
        splitted_alphabets[randrange(parts)] += [to_distribute[0]]
        to_distribute.pop(0)
    return splitted_alphabets


def generate_random_process_tree(alphabet):
    """
    Generates a random process tree by continuously splitting the
    alphabet and choosing random operators to combine the parts.

    Parameters
    ----------
    alphabet: list
        a list of symbols that the leaves of the process tree
        should have as labels

    Returns
    -------
    IdentifiableProcessTree
        the root of the generated process tree
    """

    if len(alphabet) == 1:
        return IdentifiableProcessTree(label=alphabet[0])
    else:
        op = choose_random_operator()
        root = IdentifiableProcessTree(operator=op, parent=None)
        # choose a random number of children in {2, 3, ..., |alphabet|}
        number_of_children = randrange(len(alphabet) - 1) + 2
        alphabets = randomly_split_alphabet(alphabet, number_of_children)
        for i in range(0,len(alphabets)):
            child = generate_random_process_tree(alphabets[i])
            root.add_child(child)
        return root
