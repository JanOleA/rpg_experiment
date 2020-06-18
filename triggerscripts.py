import sys
import os
import time

import pygame
from pygame.locals import *
import numpy as np

from gameobjects import MessageBox, GameMap, Trigger

pygame.font.init()
font_normal = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amatic-Bold.ttf"), 25)
font_big = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amatic-Bold.ttf"), 30)

directions = {"up": 0,
              "left": 1,
              "down": 2,
              "right": 3}

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

    def set_map(self, map_name, player_position, camera_position):
        """ Load a new map and put the player in it.

        Arguments:
        map_object -- the name of the map. If it is already loaded in the game,
                      it won't be loaded again.
        player_position -- tuple of the starting position of the player in the
                           new map (x, y)
        camera_position -- tuple of the starting position of the camera in the
                           new map (x, y)
        """
        self.setmap = (map_name, player_position, camera_position)

    def add_npc(self):
        # TODO: Implement
        pass

    def __call__(self):
        return self.messageboxes, self.npcs, self.setmap, self.movement_req

triggerscripts = {}

def new_script(name, movement_req = None):
    script = TriggerScript(name, movement_req)
    triggerscripts[name] = script

    return script

""" Parse the triggerscripts.script file """
with open("triggerscripts.script", "r") as infile:
    print("Loading triggerscripts...")
    lines = infile.readlines()
    parse_depth = 0
    change_map = False
    for line in lines:
        line = line.split("#")[0].strip()
        if "{" in line:
            line = line.split("{")
            if line[0].strip() == "change_map" and parse_depth == 1:
                change_map = True
            if parse_depth == 0:
                trigger_name = line[0].strip()
                script_ = new_script(trigger_name)
            parse_depth += 1
        elif "}" in line:
            line = line.split("}")
            if change_map:
                script_.set_map(map_name, player_pos, camera_pos)
                change_map = False
            parse_depth -= 1
        else:
            if parse_depth == 1:
                change_map = False
                if "movement_requirement" in line:
                    req = line.split("=")[-1].strip()
                    script_.movement_req = directions[req]
                if "show_messagebox" in line:
                    msg_text = line.split('"')[1]
                    script_.add_messagebox(msg_text, font_normal)
            elif parse_depth == 2:
                if change_map:
                    if "map_name" in line:
                        map_name = line.split("=")[1].strip()
                    elif "player_pos" in line:
                        player_pos = np.array(line.split("=")[1].strip().strip("()").replace(" ", "").split(","), dtype = np.float64)
                    elif "camera_pos" in line:
                        camera_pos = np.array(line.split("=")[1].strip().strip("()").replace(" ", "").split(","), dtype = np.float64)
        if parse_depth < 0:
            print("Parse error in triggerscripts.")
            sys.exit(1)
        