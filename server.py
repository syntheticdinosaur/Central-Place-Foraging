# -*- coding: utf-8 -*-
"""
Central Place Foraging in Squirrels under Predation Risk
========================================================

Server for interactive visualization of the model in a web browser.

Based on the following papers:
    1.
    2.

   

@author:        Joshua Woller
@affiliation:   University of Tuebingen
@date:          May 2022
"""
# Mesa Imports
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import \
    ModularServer, VisualizationElement, CHART_JS_FILE
# Model and Agent Imports
from foraging_agents import Food, Squirrel, SafeSpot, DangerZone
from foraging_model  import ForagingModel
# Visualization
import matplotlib.pyplot as plt
from  matplotlib.colors import rgb2hex
# Math
import numpy as np
# Replace normal asyncio. Necessary for some IDEs, e.g. Spyder.
import nest_asyncio
nest_asyncio.apply()

# Declaration of Constants
GRIDHEIGHT  = 20
GRIDWIDTH   = 20

MAXRISK = 3
MAXSIZE = 3

MAXFOOD = int(GRIDHEIGHT*GRIDWIDTH/2) if 100>GRIDHEIGHT*GRIDWIDTH/2 else 100
MAXHIDING = 10

HISTBINS = list(range(21))
HISTSIZE = (100,500)
SERVER_PORT = 8560


class TextElement(VisualizationElement):
    """ Provides text output to web server visualization """
    package_includes = ["TextModule.js"]
    js_code = "elements.push(new TextModule());"
    
    def stored_energy(self, squirrel):
        try:
            return str(squirrel.storage[0].energy)
        except IndexError:
            return "No food held"
        
    
    def render(self, model):
        return f"Energy of Squirrel: {model.squirrel.energy:.2f} \n \
                 state: {model.squirrel.state}, \
                     Energy of held food: {self.stored_energy(model.squirrel)}"
                 
js_file = "HistogramModule.js"

class HistogramModule(VisualizationElement):
    """ Provides histogram to web server visualization """
    package_includes = [CHART_JS_FILE]
    local_includes = [js_file]

    def __init__(self, bins, canvas_height, canvas_width, vis_var):

        
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"
        self.vis_var = vis_var
        
        
    def render(self, model):
        stored = [agent for agent in getattr(model, self.vis_var)]
        distance_vals = [agent.distance for agent in stored]
        hist = np.histogram(distance_vals, bins=self.bins)[0]
        return [int(x) for x in hist]

def cmap2hex(c:range(0,1), cmap):
    return rgb2hex(cmap(c))

def portrayal(agent):
    """ Determines how individual agents are displayed on the grid """
    if agent is None:
        return

    portrayal = {}

    if isinstance(agent, Squirrel):
        portrayal["Shape"] = "rect"
        portrayal["Filled"]= "true"
        portrayal["Color"] = "#FFCD01" if len(agent.storage) == 0 else "#db4646"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Layer"] = 2
        
    if isinstance(agent, DangerZone):
        portrayal["Shape"] = "rect"
        portrayal["Filled"]= "true"
        portrayal["Color"] = cmap2hex(agent.risk/MAXRISK, plt.cm.gray_r)
        portrayal["w"] = 1.05
        portrayal["h"] = 1.05
        portrayal["Alpha"] = 0.7
        portrayal["Layer"] = 1
    
    if isinstance(agent, SafeSpot):
        portrayal["Shape"] = "circle"
        portrayal["Filled"]= "true"
        portrayal["Color"] = "#235347"
        portrayal["r"] = 0.8
        portrayal["Layer"] = 2
        
    elif isinstance(agent, Food):
        portrayal["Shape"] = "circle"
        portrayal["Filled"]= "true"
        portrayal["Alpha"] = 0.7
        portrayal["Color"] = cmap2hex(agent.energy/8, plt.cm.YlGnBu)
        portrayal["r"] = 1/(MAXSIZE+1-agent.size)
        portrayal["Layer"] = 3

    return portrayal

#==============================================================================
# Intialise model parameters and visualisation elements
#==============================================================================

canvas_element = CanvasGrid(portrayal, GRIDHEIGHT, GRIDWIDTH, 500, 500)
chart_element = ChartModule([{"Label": "Food", "Color": "#666666"},
                             {"Label": "Eaten", "Color": "#db4646"},
                             {"Label":"Stored", "Color": "#2A52BE"}])

text_element = TextElement()


histogram = HistogramModule(HISTBINS, HISTSIZE[0], HISTSIZE[1], "stored")
#histogram2 = HistogramModuleEaten(HISTBINS, HISTSIZE[0], HISTSIZE[1])

model_params = {
    "max_risk": UserSettableParameter(
        "slider","Maximum Risk", 3, 1, MAXRISK,  1,
        description="Choose Maximum Risk in Map"
    ),
    "n_food": UserSettableParameter(
        "slider", "Initial Number of Food Items", 100, 5, MAXFOOD, 1,
        description="Specify how much food will be in the field initially"),
    "n_safespots":  UserSettableParameter(
        "slider", "Number of Hiding Places", 1, 1, MAXHIDING, 1,
        description = "Number of Storage Sites for Squirrel's Food"),
    "squirrel_metabolism":  UserSettableParameter(
        "slider", "Metabolic Rate of Squirrel", 0.1, 0.01, 1, 0.1,
        description = "Energy consumption per step"),
    "squirrel_risk_aversion":  UserSettableParameter(
        "slider", "Risk Aversion of Forager", 1, 0.01, 4, 0.1,
        description = "How the squirrel weights the risk while foraging. < 1 = riskier behaviour, > 1, safer behaviour"),
    "height": GRIDHEIGHT, "width": GRIDWIDTH}

server = ModularServer(ForagingModel, [canvas_element, text_element, histogram,
                                       chart_element],
                       "Central Place Foraging under Predation Risk",
                       model_params)

def main():
       server.port = SERVER_PORT
       server.launch()

#if __name__ == "__main__":
#    main()
