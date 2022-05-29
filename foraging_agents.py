# -*- coding: utf-8 -*-
"""
Central Place Foraging in Squirrels under Predation Risk

Agents for the foraging model.

@author: Joshua Woller, University of Tuebingen
"""

from mesa import Agent
import random
import numpy as np
# pathfinding for agents
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.breadth_first import BreadthFirstFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from log_dist import log_random_index

class DangerZone(Agent):
    def __init__(self, unique_id, model, pos, risk):
        super().__init__(unique_id, model)
        self.pos = pos
        self.risk = risk
        
    def step(self):
        pass

class EmptyField:
    """
    Dummy Class to represent an empty field as target of agent
    """
    def __init__(self, pos:tuple[int,int] = None):
        self.pos = pos
        
class SafeSpot(Agent):
    """
    Spot where Squirrel can retreat and store food

    unique_id:  int         Identifier of agent within model
    model:      mesa.Model  Mesa Model to which agent belongs    
    pos:        tuple       Location of agent as 2-tuple of integers
    storage:    list        List of food stored at this safe spot
    
    """
    def __init__(self, unique_id, model, pos:tuple[int,int]):
        super().__init__(unique_id, model)
        self.pos = pos  
        self.storage = list()
        
    def store(self, food):
        self.storage.append(food)

    def step(self):
        pass      

class CountDummy:
    """
    Dummy object affording reduced representation of collected or eaten food.
    Used for histogram plotting, stored in a list as model attribute.
    
    risk:       float       Risk of represented food object
    distance:   int         Distance of food object from collecting agent or
                            nearest cache.
    """
    def __init__(self, original, reference_location):
        self.pos  = original.pos
        self.risk = original.risk
        self.distance = abs(np.subtract(self.pos, reference_location)).sum()

class Food(Agent):    
    """
    Food for Squirrel
    
    unique_id:  int         Identifier of agent within model
    model:      mesa.Model  Mesa Model to which agent belongs
    pos:        tuple       Location of agent as 2-tuple of integers
    size:       int         Size of food object; simulates handling time,
                            i.e. how many steps it takes to eat the food
    energy:     int         Energy gained by other agent if food is consumed
    risk:       float       Predation risk associated with food item.
                            Higher means more dangerous.
    profit:     float       Energetic profitability of item: energy/size
    visited:    bool        Flag: Has the food been visited by an agent?
    """
    def __init__(self,
                 unique_id,
                 model,
                 pos:tuple,
                 size:int,
                 nutrition:int,
                 risk:float):
        super().__init__(unique_id, model)
        self.pos = pos
        self.size = size
        self.energy = nutrition
        self.risk = risk
        self.profit = self.energy/self.size
        self.visited = False
        
    def step(self):
        pass


class Animal(Agent): 
    """ Base Class for Animals
        
    unique_id:  int         Identifier of agent within model
    model:      mesa.Model  Mesa Model to which agent belongs
    pos:        tuple       Location of agent as 2-tuple of integers
    fov:        int         How many grid squares in any direction the agent
                            can include in food search.
    energy:     int         Energy of agent; used up a bit with each step
    metabolism: float       Rate of energy loss per model step
    """
    def __init__(self,
                 unique_id,
                 model,
                 pos:tuple[int,int],
                 fov:int,
                 energy:int = 20,
                 metabolism:float = 0.2):
        super().__init__(unique_id, model)
        self.pos = pos        
        self.fov = fov
        self.energy = energy
        #energy cost per step
        self.metabolism = metabolism
        
        # Parameters for movement on the Grid
        # Current Agent object marked as target
        self.target = None
        self.path = list()
        
    def init_pathfinding_grid(self, PATHFINDER = AStarFinder, danger:bool = True):
            if danger:
                matrix = np.around(self.model.danger*(self.risk_aversion)).astype(int)
                matrix[np.where(matrix <= 0)] = 1
                self.agent_grid = PathGrid(matrix = matrix)            
            else:
                self.agent_grid = PathGrid(matrix = self.model.pathgrid)

            self.pathfinder = PATHFINDER(diagonal_movement= DiagonalMovement.always)
            
    
    def move(self, pos:tuple = False, danger:bool = True):        

        """ Plans and executes movement of agent.
        pos indicates the target position for a movement path, if False,
        the agent tries to move its previously initialised path """
        
        self.init_pathfinding_grid(danger = danger)
        
        # Perhaps do this only once
        # Decouple pathfinding from  movement
        if pos:
            start = self.agent_grid.node(self.pos[0], self.pos[1])
            end = self.agent_grid.node(pos[0], pos[1])
            self.path, _ = self.pathfinder.find_path(start, end , self.agent_grid)
            self.path = self.path[1:] # exclude self.path[0]-starting position
        
        if len(self.path) > 0:
            self.model.grid.move_agent(self, self.path.pop(0))   
                            
    def eat(self, food):
        pass
        
    def step(self):
        """ A step in the model """
        if self.target is None:
            self.update_neighbors()
        self.move()      
        self.energy -= self.metabolism
    
    def update_neighbors(self, fov = None, radius = 5):
        """
        Look around and see who the neighbors are.
        """
        self.neighborhood = self.model.grid.get_neighborhood(pos = self.pos,
                            moore = True,
                            radius = radius)
        self.neighbors = self.model.grid.get_neighbors(pos = self.pos,
                            moore = True,
                            radius = self.fov if fov is None else fov)
        distances = self._get_distance(self.neighborhood)
        empty_idx = [idx for idx, val in enumerate(distances) if val > radius -1]
        
        self.empty_neighbors = [self.neighborhood[idx] for idx in empty_idx if
                                not isinstance(self.neighborhood[idx], Food)]
        
        #[
        #   self.neighborhood[idx] for idx in empty_idx 
        #   if self.neighborhood[idx] in self.model.grid.empties
       #]
    """self.empty_neighbors = [
           self.neighborhood[idx] for idx in empty_idx 
           if self.model.grid.is_cell_empty(self.neighborhood[idx])
       ]"""
      
    def _get_distance(self, cell_list):
        """ Calculate distance from agent, either for list of position tuples
            or for a list of agents with a .pos attribute as location tuple """
            
        if isinstance(cell_list[0], (tuple, list)):
            distances = (abs(np.subtract(cell_list, self.pos)).sum(axis = 1))
        else:
            positions = [cell.pos for cell in cell_list]
            distances = (abs(np.subtract(positions, self.pos)).sum(axis = 1))
        return distances
        
class Squirrel(Animal): 
    """
    Class for foraging Squirrel. Child of Animal Class.            

    unique_id:  int         Identifier of agent within model
    model:      mesa.Model  Mesa Model to which agent belongs
    pos:        tuple       Location of agent as 2-tuple of integers
    fov:        int         How many grid squares in any direction the agent
                            can include in food search.
    energy:     int         Energy of agent; used up a bit with each step
    metabolism: float       Rate of energy loss per model step
    home:       tuple       Currently unused. Location of home cache. 
    state:                  Intended action of agent at a step
                            ["eat", "store", None]
    storage:    list        List of food the agent has stored during foraging
    
    caches:     list        List of caches in entire field
    cache:      SafeSpot    Currently selected safe spot for storing food   
    
    """
    def __init__(self,
                 unique_id,
                 pos:tuple[int,int],
                 model,
                 home:tuple[int,int],
                 fov:int,
                 metabolism:float,
                 risk_aversion:float= 1):
        super().__init__(unique_id, model, pos, fov, metabolism = metabolism)
        self.home = home
        self.storage = list()
        self.state = None
        self.risk_aversion = risk_aversion
        
        # Generate List of available safe spots in the environment
        full_view = self.model.grid.get_neighbors(pos = self.pos,
                            moore = True,
                            radius = max(self.model.height, self.model.width))
        self.caches = [cache for cache in full_view if isinstance(cache, SafeSpot)]
        self.cache = self.caches[np.argmin(self._get_distance(self.caches))]
        
        self.init_pathfinding_grid()
        
    def eat(self, food):
        """
        Eat a Food Agent, add energy to forager and remove food from the model
        """
        self.energy += food.energy
        self.model.eaten.append(CountDummy(food, self.cache.pos))
        self.model.grid.remove_agent(food)
        self.model.schedule.remove(food)    
        
    def pickup(self, food):
        """
        Pick up food, add it to agent's storage, remove it from model
        """
        self.model.stored.append(CountDummy(food, self.cache.pos))
        self.storage.append(food)
        self.model.grid.remove_agent(food)
        self.model.schedule.remove(food)
        
    def step(self):
        self.energy -= self.metabolism
        
        if self.target is None:        
            self.update_neighbors()
            all_food = [
                food for food in self.neighbors if isinstance(food, Food)
                ]          
            #if self.energy > 10 and len(all_food) > 0:
            #    all_food = [food for food in all_food if food.risk*self.risk_aversion < 2]
                
            if len(all_food) > 0:
                # If there is food nearby, go to the nearest food
                self.cache = self.caches[np.argmin(
                    self._get_distance(self.caches))]
                
                risks = [food.risk for food in all_food]
                positions = [food.pos for food in all_food]
                profit_eat= [food.profit for food in all_food] # should profit be weighted by risk?
                profit_store= [food.energy for food in all_food]
                #distances = abs(np.subtract(positions, self.pos)).sum(axis = 1) #does not match pathfinding
                #cachedist = abs(np.subtract(positions, self.cache.pos)).sum(axis = 1)
                
                self.init_pathfinding_grid()
                
                distances = list()
                for pos in positions:
                    start = self.agent_grid.node(self.pos[0], self.pos[1])
                    end = self.agent_grid.node(pos[0], pos[1])
                    path, _ = self.pathfinder.find_path(start, end , self.agent_grid)
                    distances.append(len(path))
                    
                cachedist = list()
                for pos in positions:
                        start = self.agent_grid.node(self.pos[0], self.pos[1])
                        end = self.agent_grid.node(self.cache.pos[0], self.cache.pos[1])
                        path, _ = self.pathfinder.find_path(start, end , self.agent_grid)
                        cachedist.append(len(path))
                        
                distances = np.array(distances)-np.array(risks)
                cachedist = np.array(cachedist)-np.array(risks)
                
                # Difference here can be used to decide whether to eat or to forage
                energy_eat = distances*self.metabolism
                energy_store = (distances+cachedist)*self.metabolism
                # use self.path
                energy_diff = np.argmax(energy_eat-energy_store)
                cachecost = profit_store - energy_store
                eatcost   = profit_eat - energy_eat
                
                # include risk assessment here
                # Check whether it is smarte to eat or to store
                
                if self.energy > 15:# or (not self.energy < 10 and np.argmax(cachecost) > 0):
                    self.target = all_food[np.argmax(cachecost)]
                    self.state  = "store"
                else:
                    self.target = all_food[np.argmax(eatcost)]    
                    self.state  = "eat"
            else:
               fields = [neighbor for neighbor in self.neighbors
                if neighbor.pos in self.empty_neighbors]
               field_risks = [neighbor.risk for neighbor in fields
                              if isinstance(neighbor, DangerZone)]
               index = log_random_index(field_risks, self.risk_aversion)   
               self.target = EmptyField(pos = fields[index].pos)
               #self.target = EmptyField(pos =
                                         #random.choice(self.empty_neighbors))    

        if self.pos != self.target.pos:
            self.move(self.target.pos)

        if self.pos == self.target.pos:
            # Check Type of target (Food or SafeSpot)
            
            if isinstance(self.target, Food):
                self.cache = self.caches[np.argmin(
                                         self._get_distance(self.caches))]
                if  self.state == "store" and not self.target.visited: #problem if we reduce size
                    self.pickup(self.target)
                    self.target = self.cache      #This is weird and should be changed 
                    self.target.visited = True
                elif self.state == "eat":                              
                    if self.target.size == 1:   
                        self.eat(self.target)
                        self.target = None
                    else:
                        self.target.visited = True
                        self.target.size -= 1
            
            elif isinstance(self.target, SafeSpot):
                self.cache.store(food = self.storage.pop(0))
                self.target = None
                
            elif isinstance(self.target, EmptyField):
                self.target = None
            else:
                pass
            

            
