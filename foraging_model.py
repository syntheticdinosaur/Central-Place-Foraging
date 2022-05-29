# -*- coding: utf-8 -*-
"""
Central Place Foraging in Squirrels under Predation Risk

Model of foraging under predation. Can be run non-interactively or passed to 
server.py function for interactive visualization.

@author: Joshua Woller, University of Tuebingen
"""

# Mesa imports
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import gaussian_random_fields as gr

# Model agents
from foraging_agents import Food, Animal, Squirrel, SafeSpot, CountDummy, DangerZone

# Math stuff
import numpy as np
import random

# For visualization of non-interactive model run
import seaborn as sns
from matplotlib import pyplot as plt

# Create Model
class ForagingModel(Model):    
    description = (
        "A model simulating central place foraging under the risk of predation\
        in squirrels."
        )
    def __init__(self,
                 height:int = 20,
                 width:int = 20,
                 torus:bool = False,
                 n_food:int = 15,
                 n_squirrel:int = 1,
                 n_safespots:int = 5,
                 max_risk:int = 3,
                 verbose:bool = True,
                 squirrel_metabolism = 0.1,
                 squirrel_risk_aversion = 1):
        super().__init__()        
        self.height, self.width = [height, width] #enforce square shape later!
        self.food_supply = n_food
        self.n_safespots = n_safespots      
        self.eaten  = list()
        self.stored = list()        
        self.verbose = True
        
        # Activation Schedule of Agents        
        self.schedule = RandomActivation(self)        
        #======================================================================
        # Init grids for agent placement, risk estimation and pathfinding
        #======================================================================
        # Agent Grid
        self.grid = MultiGrid(self.height, self.width, torus)
        # Grid for pathfinding algorithm of agents
        self.pathgrid = np.ones((self.height, self.width))  
        self.heatmap = np.zeros((self.height, self.width)) 
        # Spatial Distribution of Risk using Gaussian Random Field
        # alpha parameter is the smoothness of the gaussian, recommend 4 to 6
        self.danger = gr.gaussian_random_field(alpha = 6, size = self.height, seed = 500)
        # Make positive everywhere
        self.danger += np.abs(self.danger.min())
        # Normalise, then scale to maximal risk.
        self.danger = self.danger/self.danger.max()*max_risk
        
        #======================================================================
        # Initialise all agents
        #======================================================================
        
        for index in np.ndindex(self.height, self.width):
                risk = self.danger[index]
                danger_dummy = DangerZone(self.next_id(), model = self,
                                          pos = index,
                                          risk = risk)               
                self.grid.place_agent(danger_dummy,  index)
                self.grid.empties.add(index)
                #self.schedule.add(danger_dummy)                
                
        # Initialise Safe Spots, i.e. storage sites for food
        for idx in range(self.n_safespots):
                if  idx == 0:
                    pos = (int(self.height/2), int(self.width/2))
                else:
                    pos = self.grid.find_empty()
                spot = SafeSpot(self.next_id(), model = self,
                            pos = pos)
                self.grid.place_agent(spot, pos)
                self.schedule.add(spot)
                
        # Initialise Food Agents
        for pos in range(self.food_supply):
                pos = self.grid.find_empty()
                size = random.choice([1,2,3])
                nutr_value = random.choice([2,4,8])
                risk = self.danger[pos[0], pos[1]]
                food = Food(self.next_id(), model = self,
                            pos = pos, size = size, nutrition = nutr_value,
                            risk = risk)                
                self.grid.place_agent(food, pos)
                self.schedule.add(food)
        
        # Initialise Squirrel Agent    
        start_loc = (int(self.height/2)+1, int(self.width/2)+1)
        self.squirrel = Squirrel(self.next_id(), model = self, fov = 4,
                          pos = start_loc, home = start_loc,
                          metabolism = squirrel_metabolism,
                          risk_aversion = squirrel_risk_aversion)
        self.grid.place_agent(self.squirrel, self.squirrel.home)
        self.schedule.add(self.squirrel)
        
        """
        for index in np.ndindex(self.height, self.width):
                risk = self.danger[index[0], index[1]]
                self.empties.add(index)
                danger_dummy = DangerZone(self.next_id(), model = self,
                                          pos = (index[0], index[1]),
                                          risk = risk)               
                self.grid.place_agent(danger_dummy, (index[0], index[1]))
                #self.schedule.add(danger_dummy)
                
        """
        
        #======================================================================
        # Set datacollection and start running the model
        #======================================================================
        model_reporters = {
            "Food": lambda m: self.count_food(),
            "Eaten": lambda m: len(self.eaten),
            "Stored": lambda m: len(self.stored),
        }

        self.datacollector = DataCollector(
            model_reporters=model_reporters)
        self.datacollector.collect(self)        
        self.running = True       

    def count_food(self):
        """ Helper method to count food. """
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Food):
                count += 1
        return count 
    
    def step(self):
        """ A step in the model """
        self.schedule.step() 
        self.heatmap[self.squirrel.pos] += 1
        if not(self.grid.exists_empty_cells()):
            self.running = False
        self.datacollector.collect(self)
        if self.count_food() == 0 and len(self.squirrel.storage) == 0:
            self.running = False

    def run_model(self, n_steps:int = 150):
        """ Run the model for n_steps steps. """                    
        for step in range(n_steps):             
            self.step()            



def main(n_steps = 400, risk = 1, n_food = 50):
    foraging_model = ForagingModel(n_food = n_food, n_safespots = 1,
                                   squirrel_risk_aversion = risk, verbose = False)
    foraging_model.run_model(n_steps = n_steps)
    """
    fig, axes = plt.subplots(2,2, figsize = (8,8))
    
    distance_bins = list(range(1,11))
    risk_bins     = list(range(1,6))
    sns.histplot(x = [agent.distance for agent in foraging_model.stored],
                 ax = axes[0,0], bins = distance_bins )
    axes[0,0].set_title("Distance of Stored Food")
    sns.histplot(x = [agent.distance for agent in foraging_model.eaten],
                 ax = axes[0,1], bins = distance_bins)
    axes[0,1].set_title("Distance of Eaten Food")
    sns.histplot(x = [agent.risk for agent in foraging_model.stored],
                 ax = axes[1,0], bins = risk_bins)
    axes[1,0].set_title("Risk of Stored Food")    
    sns.histplot(x = [agent.risk for agent in foraging_model.eaten],
                 ax = axes[1,1], bins = risk_bins)
    axes[1,1].set_title("Risk of Eaten Food")
    fig.tight_layout()"""
    return foraging_model
    
if __name__ == '__main__':
    risks = [0.2, 0.4, 0.6, 0.8, 1, 1.5, 2, 3, 4]
    #fig, axes = plt.subplots(3,2, sharex = True, sharey = True, figsize = (8,4)) 
    #axes = axes.flatten()
    for idx, risk in enumerate(risks):
        print(risk)
        m = np.zeros([20,20, len(risks)])
        for _ in range(3):
            model = main(n_steps = 500, risk = risk, n_food = 80)
            
        
           
            model.heatmap[10,10] = 0
            model.heatmap[int(model.height/2), int(model.width/2)] = 0
            #axes2[1].imshow(model.heatmap, cmap = "gray_r")
            #axes2[0].imshow(model.danger, cmap = "gray_r")
            m[:,:,idx] += model.heatmap
            
            #f = model.heatmap/np.max(model.heatmap)
            #axes2[2].imshow(f, cmap = "gray_r")
            #plot_data = (model.danger*f)#.flatten()
            #plot_data = plot_data[plot_data != 0]
            #model.danger[plot_data > 0]
            #np.where(plot_data > 0, 1, 0)
            #axes2[2].imshow(model.danger * np.where(plot_data > 0, 1, 0), cmap = "gray_r")

           
        fig, axes = plt.subplots(1,2, sharex = True, sharey = True, figsize = (8,4)) 
        axes[0].imshow(m[:,:,idx], cmap = "cividis")
        axes[0].set(title = "Heatmap of agent position", yticks =[], xticks = [])
        axes[1].imshow(model.danger, cmap = "cividis")
        axes[1].set(title = "Risk Distribution", yticks =[], xticks = [])
        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=None, cmap="cividis"),
                     ax = axes[0], label="Location visited", orientation="vertical",
                     ticks = [0,1])
        cbar.ax.set_yticklabels(["never", "often"]) 
        cbar2 = fig.colorbar(plt.cm.ScalarMappable(norm=None, cmap="cividis"),
                     ax = axes[1], label="Risk", orientation="vertical",
                     ticks = [0,1])
        cbar2.ax.set_yticklabels(["low", "high"]) 
        fig.suptitle(f"Risk Aversion: {risk}")
        fig.tight_layout()
        plt.show()      
  