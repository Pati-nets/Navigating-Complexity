# Navigating Complexity
## A Tool To Inspect the Impact of Different Complexity Measures to Process Discovery
...

### Overview of the python files
`complexity.py`:
	Contains methods to calculate the complexity of a Petri net.
	At the moment, the only complexity measures implemented are:
	- average connector degree 
	- connector heterogeneity
	- size

`simplicity.py`:
	Contains a class that converts complexity measures into 
	simplicity measures, where the scores range from 0 to 1.
	It does so by using a reference model whose simplicity 
	score is known. At the moment, this calculation is only 
	available for the following complexity measures:
	- average connector degree
	- connector heterogeneity
	- size
	
`quality.py`:
	Contains methods to calculate the quality of a process tree. 
	These methods use the fitness-, precision and generalization-
	calculations provided by the process mining library PM4Py.

`convert.py`:
	Contains method to compose workflow nets and to convert 
	a process tree into a workflow net without removing tau-
	transitions.
	
`utils.py`:
	Contains a method to extract the activities of an event log.

`id_process_tree.py`:
	Contains a class that represents process trees that are equipped 
	with a unique identifier. This avoids that two different nodes 
	with the same label and operator attribute are considered equal. 
	Furthermore, contains methods to randomly create process trees.

`mutations.py`:
	Contains methods to randomly mutate a process tree according to 
	the mutation operations introduced in [1].
	
`etm.py`:
	...

`main.py`:
	...
