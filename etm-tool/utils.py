# Returns the set of activities that are used in the passed event log.
def get_set_of_activities(log):
    """
    A method that returns the set of activities that occur
    in the passed event log.

    Parameters
    ----------
    log: pm4py.objects.log.obj.EventLog
        the event log of which we want to extract the occurring activities

    Returns
    -------
    list
        a list of the names of activities that occur in the passed event log
    """

    activities = []
    for trace in log:
        for event in trace:
            name = event['concept:name']
            if name not in activities:
                activities += [name]
    return activities
