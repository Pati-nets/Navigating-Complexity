import complexity
from pm4py.objects.petri_net.obj import PetriNet
from math import ceil

class Simplicity:
    """
    A class for calculating simplicity when a reference model is known.

    Attributes
    ----------
    reference_model: pm4py.objects.petri_net.obj.PetriNet
        a Petri net whose simplicity is known and can
        be used as a reference for other Petri nets
    reference_simplicity: float (default 0.5)
        the simplicity of the reference net

    Methods
    -------
    average_connector_degree(other_model)
        A method returning a simplicity score for the average
        connector degree according to the reference model.
    connector_heterogeneity(other_model)
        A method returning a simplicity score for the connector
        heterogeneity according to the reference model.
    size(other_model)
        A method returning a simplicity score for the size according
        to the reference model.
    """

    def __init__(self, reference_model: PetriNet, reference_simplicity=0.75):
        """
        Parameters
        ----------
        reference_model: pm4py.objects.petri_net.obj.PetriNet
            a Petri net whose simplicity is known and can
            be used as a reference for other Petri nets
        reference_simplicity: float (default 0.5)
            the simplicity of the reference net
        """

        self.ref_model = reference_model
        self.ref_simplicity = reference_simplicity


    def average_connector_degree(self, other_model):
        """
        A method returning a simplicity score for the average
        connector degree according to the reference model.

        Parameters
        ----------
        other_model: pm4py.objects.petri_net.obj.PetriNet
            the model for which we want to calculate a simplicity score

        Returns
        -------
        float
            a float in [0,1] representing the simplicity of the
            process model's average connector degree with respect
            to the reference model

        By knowing the simplicity of the reference model, we can calculate
        which average connector degree would be considered bad in a Petri
        net. For example, if our reference model has an average connector
        degree of D and a simplicity of 0.5, we assume that the net should
        get a simplicity score of 0 if it has an average connector degree
        of 2*D or higher. The smaller the average connector degree is than
        2*D, the closer the simplicity score is to 1.
        In the case that the net does not have any connectors, we set its
        simplicity to 0.
        """
        acd = complexity.average_connector_degree(other_model)
        if acd == None:
            acd = 0
        ref_acd = complexity.average_connector_degree(self.ref_model)
        if ref_acd == None:
            ref_acd = 0
        N = ceil(ref_acd / (1 - self.ref_simplicity))
        return 1 - min(acd / N, 1)


    def connector_heterogeneity(self, other_model):
        """
        A method returning a simplicity score for the connector
        heterogeneity according to the reference model.

        Parameters
        ----------
        other_model: pm4py.objects.petri_net.obj.PetriNet
            the model for which we want to calculate a simplicity score

        Returns
        -------
        float
            a float in [0,1] representing the simplicity of the
            process model's connector heterogeneity

        The connector heterogeneity measure only returns values in
        the interval [0,1], so we may ignore the reference model
        and simply return the score of this measure.
        In the case that the net does not have any connectors, we set its
        simplicity to 0.
        """
        conn_het = complexity.connector_heterogeneity(other_model)
        if conn_het == None:
            conn_het = 0
        return conn_het


    def size(self, other_model):
        """
        A method returning a simplicity score for the size according
        to the reference model.

        Parameters
        ----------
        other_model: pm4py.objects.petri_net.obj.PetriNet
            the model for which we want to calculate a simplicity score

        Returns
        -------
        float
            a float in [0,1] representing the simplicity of the
            process model's size with respect to the reference model

        By knowing the simplicity of the reference model, we can calculate
        how many nodes would be considered bad in a Petri net. For example,
        if our reference model has N nodes and a simplicity of 0.5, we assume
        that 2*N or more nodes should give a simplicity score of 0. The
        smaller the size is than 2*N, the closer the simplicity score is to 1.
        """

        size = complexity.size(other_model)
        ref_size = complexity.size(self.ref_model)
        N = ceil(ref_size / (1 - self.ref_simplicity))
        return 1 - min(size / N, 1)
