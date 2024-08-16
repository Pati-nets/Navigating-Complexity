## Navigating Complexity:
## A Tool To Inspect the Impact of Different Complexity Measures to Process Discovery
This repository contains a tool designed to inspect the impact of properties for complexity measures on process discovery algorithms that optimize over the quality criteria. 


### Problem description
_Process discovery_ is a task of _process mining_, whose algorithms take an _event log_ as input and output a model reflecting the behavior of the event log.
As an example, consider the popular video game Minecraft. 
If we record every way in which we built a house in Minecraft, we could end up with the following (very simplified) event log:

![an exemplary event log](./readme-images/event-log.png)

The task of a process discovery algorithm is to find a process model reflecting the behavior in the event log. 
Such a process model can be, for example, a workflow net like in the following Figure:

![a process model for the event log](./readme-images/process-model.png)

### Dependencies
To execute this program, we advise to use `Python 3.8` or higher.

The program in this repository has the following external dependencies: 
- `pm4py v.2.7.11.12` (https://pypi.org/project/pm4py/2.7.11.12/)

After you installed these dependencies, head to the folder `etm-tool`, open a terminal and execute `python main.py`. 

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
	Contains a simple implementation of the evolutionary tree miner [1], 
	as well as methods to store the evolution of various quality scores.

`main.py`:
	Contains the main function and methods that read user input to 
	specify the parameters for the evolutionary tree miner.
