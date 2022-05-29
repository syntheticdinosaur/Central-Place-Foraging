# Agent-based model of Central Place Foraging under Predation Risk 

## About

This is an agent-based model of central place foraging in Python, using the Mesa framework.
It simulates a food foraging agent (let's say a squirrel) in a landscape with spatially varying danger. The agent can differ in its risk aversion, i.e. how likely it is to choose food from risky patches. Currently, the agent cannot die, i.e. making risky choices does not have negative consequences. This is a future feature to be implemented.

## Model Description

Here you can see a visualisation of the model. The agent traverses a grid environment in which food is placed. Different grid squares have a different risk associated with them. The risk distribution is generated using random gaussian fields.


![GIF animation of the model running](https://github.com/syntheticdinosaur/Central-Place-Foraging/blob/master/docs/images/Model.gif)


 The foraging agent has a risk aversion parameter. The higher the risk aversion, the more it will try to exclude risky areas from the search for food, and the less likely it is to traverse through risky areas when bringing food back to its central place.
 
![Animation showing the development of paths with increasing risk aversion of foraging agent](https://github.com/syntheticdinosaur/Central-Place-Foraging/blob/master/docs/images/Simulation.gif)

When going around, the agent decides whether to eat food immediatly to restore energy or whether to forage food. For this, there is also a calculation of the net energy return of a given food item, i.e. energy spend getting and possibly storing it vs. energy to be gained.
Collected food is gathered at the central place (e.g., the green circle in the visualization beneath)

### Agent Types

#### Food
#### Squirrel
#### SafeSpot

## To Dos

- batchrunner
- agent death implementation
- smarter 'foraging vs. eating' decision
- increase visualizaiton efficiency (currently it crowds the agent space)
- better fit to existing ecological models
- visualization for Jupyter Notebooks
- General refactoring
- add list of dependencies
- implement testing procedures (unit test etc.)
