import sys
import os
import time

import pygame
from pygame.locals import *
import numpy as np

from gameobjects import MessageBox, GameMap, Trigger


pygame.font.init()
font_normal = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Regular.ttf"), 18)
font_normal_bold = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Bold.ttf"), 18)
font_big = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Regular.ttf"), 25)
font_big_bold = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Bold.ttf"), 25)


class TriggerScript:
    """ Triggerscripts can currently display a messagebox. Next on the plan
    is the ability to add NPCs or change the map on trigger.    
    """
    def __init__(self, name, movement_req = None):
        """ Initializes the trigger script object 
        
        Keyword arguments:
        movement_req -- the direction the player must be moving for the script
                        to trigger (0 = up, 1 = left, 2 = down, 3 = right)
                        None = no requirement (default None)
        """
        self.movement_req = movement_req
        self.messageboxes = []
        self.npcs = []
        self.setmap = None

    def add_messagebox(self, text, font,
                       duration=10, AA_text=True,
                       tcolor=(255, 255, 255),
                       bgcolor=(0, 0, 0, 155)):
        self.messageboxes.append(MessageBox(text, font, 1280, 800))

    def add_npc(self):
        # TODO: Implement
        pass

    def set_new_map(self):
        # TODO: Implement
        pass

    def __call__(self):
        return self.messageboxes, self.npcs, self.setmap, self.movement_req

triggerscripts = {}

def new_script(name, movement_req):
    script = TriggerScript(name, movement_req)
    triggerscripts[name] = script

    return script

cave1_script = new_script("cave1", movement_req = 0)
cave1_script.add_messagebox("You don't feel like going in there right now.", font_normal)

villa1 = new_script("villa1", movement_req = 0)
villa1.add_messagebox("The door won't open. It's locked.", font_normal)

villa2 = new_script("villa2", movement_req = 0)
villa2.add_messagebox("The door won't open. It's locked.", font_normal)

