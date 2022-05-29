# Agent-based model of Central Place Foraging under Predation Risk 

## About

This is an agent-based model of central place foraging in Python, using the Mesa framework.
It simulates a food foraging agent (let's say a squirrel) in a landscape with spatially varying danger. The agent can differ in its risk aversion, i.e. how likely it is to choose food from risky patches. Currently, the agent cannot die, i.e. making risky choices does not have negative consequences. This is a future feature to be implemented.

## Model Description

Here you can see a visualisation of the model. The agent traverses a grid environment in which food is placed. Different grid squares have a different risk associated with them. The risk distribution is generated using random gaussian fields.

When going around, the agent decides whether to eat food immediatly to restore energy or whether to forage food. For this, there is also a calculation of the net energy return of a given food item, i.e. energy spend getting and possibly storing it vs. energy to be gained.

### Agent Types

#### Food
#### Squirrel

## Visualisation

Here you can see an animation of the model.

![GIF animation of the model running](https://github.com/syntheticdinosaur/Central-Place-Foraging/blob/master/docs/images/Model.gif)

Still under devlopment (refactoring)



![Animation showing the development of paths with increasing risk aversion of foraging agent](https://github.com/syntheticdinosaur/Central-Place-Foraging/blob/master/docs/images/Simulation.gif)
