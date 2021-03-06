import sys
import os
import time

import pygame
from pygame.locals import *
from pytmx import load_pygame
import numpy as np


class MessageBox:
    """ Object for displaying info boxes on the screen """
    def __init__(self, text, font, window_width, window_height,
                 duration=10, AA_text=True,
                 tcolor=(0, 0, 0),
                 bgcolor=(0, 0, 0, 155)):
        """ Initialize the object.

        Parameters:
        text -- Text string to display.
        font -- Pygame font to use.
        window_width -- Width of the game window.
        window_height -- Height of the game window.

        Keyword arguments:
        duration -- How many seconds to display the message box (default 10)
        AA_text -- Whether or not to anti-alias the text (default True)
        tcolor -- Color of the text (default white: (255, 255, 255))
        bgcolor -- Color and alpha of the background (default (0, 0, 0, 155))
        """

        self._text = font.render(text, AA_text, tcolor)
        self._duration = duration
        self._init_time = time.time()
        self._bgcolor = bgcolor

        textwidth = self._text.get_width()
        textheight = self._text.get_height()
        boxwidth = textwidth + 20
        boxheight = textheight + 20
        self._bgrect = pygame.Rect(window_width//2 - boxwidth//2,
                                   window_height - boxheight - 20,
                                   boxwidth, boxheight)
        self._textpos = (self._bgrect.left + 10, self._bgrect.top + 5)

    def __call__(self):
        return self._text, self._textpos, self._bgrect, self._bgcolor

    def reset_init_time(self):
        self._init_time = time.time()

    @property
    def init_time(self):
        return self._init_time

    @property
    def duration(self):
        return self._duration


class GameMap:
    """ Class for maps. Loads from a Tiled map. """
    def __init__(self, filename):
        tmx_data = load_pygame(os.path.join(os.getcwd(), "map", filename))
        self._mapwidth_tiles = tmx_data.width
        self._mapheight_tiles = tmx_data.height
        self._mapwidth = tmx_data.width*32
        self._mapheight = tmx_data.height*32
        self._map_layers = tmx_data.layers
        self._outdoors = tmx_data.outdoors

        self._water_matrix = np.zeros((self._mapwidth_tiles, self._mapheight_tiles))
        self._collision_object_matrix = np.zeros((self._mapwidth_tiles, self._mapheight_tiles))
        self._bridge_matrix = np.zeros((self._mapwidth_tiles, self._mapheight_tiles))

        self._ground_surf = pygame.Surface((self._mapwidth, self._mapheight))
        self._c_object_surfs = [] # collision objects on the map
        self._m_object_surfs = {} # non-collision objects on the map (M-objects)
        self._bridge_surf = pygame.Surface((self._mapwidth, self._mapheight), pygame.SRCALPHA)
        self._above_surf = pygame.Surface((self._mapwidth, self._mapheight), pygame.SRCALPHA)
        self._triggers = {}

        self._collision_hitboxes = []
        self._water_hitboxes = []

        self._stored_npcs = []
        self._stored_loot = []
        self._stored_player_position = (0,0)
        self._stored_camera_positon = (0,0)

        self.load_layers(filename, tmx_data)

    def load_layers(self, filename, tmx_data):
        """ Loop through layers and add appropriate items to the right arrays and lists. """
        for k, layer in enumerate(self._map_layers):
            print(f"Loading map: {filename:>10s} | Layer: {layer.name:>25s} | Layertype: {str(layer):>35s}")
            if ("ground" in layer.name.lower() or "water" in layer.name.lower()):
                for i in range(self._mapwidth_tiles):
                    for j in range(self._mapheight_tiles):
                        x = i*32
                        y = j*32
                        image = tmx_data.get_tile_image(i, j, k)
                        if image is not None:
                            self._ground_surf.blit(image, (x, y))
                            if "Water" in layer.name:
                                self._water_matrix[i, j] = 1
            
            if "c-objects" in layer.name.lower():
                """ Collision objects. Draw order is based on y position. """
                for j in range(self._mapheight_tiles):
                    y_surf = pygame.Surface((self._mapwidth, 32), pygame.SRCALPHA) # make a surf for this y-position
                    y = j*32
                    for i in range(self._mapwidth_tiles):
                        image = tmx_data.get_tile_image(i, j, k)
                        x = i*32
                        if image is not None:
                            y_surf.blit(image, (x, 0))
                            self._collision_object_matrix[i, j] = 1
                    self._c_object_surfs.append([y_surf, y])

            if "m-objects" in layer.name.lower():
                """ Non-collision objects. Draw order is based on y position. For same y-position
                M-objects are drawn above C-objects.
                """
                for j in range(self._mapheight_tiles):
                    y_surf = pygame.Surface((self._mapwidth, 32), pygame.SRCALPHA) # make a surf for this y-position
                    y = j*32
                    for i in range(self._mapwidth_tiles):
                        image = tmx_data.get_tile_image(i, j, k)
                        x = i*32
                        if image is not None:
                            y_surf.blit(image, (x, 0))
                    self._m_object_surfs[y] = y_surf
            
            if "n-objects" in layer.name.lower():
                """ Non-collision objects. Always draw above C-objects, M-objects and characters. """
                for i in range(self._mapwidth_tiles):
                    for j in range(self._mapheight_tiles):
                        x = i*32
                        y = j*32
                        image = tmx_data.get_tile_image(i, j, k)
                        if image is not None:
                            self._above_surf.blit(image, (x, y))

            if "bridges" in layer.name.lower():
                """ Bridges remove water hitboxes. Always drawn below characters. """
                offset_y = layer.offsety
                for i in range(self._mapwidth_tiles):
                    for j in range(self._mapheight_tiles):
                        x = i*32
                        y = j*32 + offset_y
                        image = tmx_data.get_tile_image(i, j, k)
                        if image is not None:
                            self._bridge_surf.blit(image, (x, y))
                            self._bridge_matrix[i, j] = 1

            if "colliders" in layer.name.lower():
                """ Not drawn """
                offset_y = layer.offsety
                offset_x = layer.offsetx
                for j in range(self._mapheight_tiles):
                    y = j*32 + offset_y
                    for i in range(self._mapwidth_tiles):
                        prop = tmx_data.get_tile_properties(i, j, k)
                        x = i*32 + offset_x
                        if prop is not None:
                            collidertype = prop["type"]
                            hitboxes = []
                            if collidertype == "Top":
                                hitboxes.append(pygame.Rect(x, y, 32, 4))
                            elif collidertype == "Left":
                                hitboxes.append(pygame.Rect(x, y, 4, 32))
                            elif collidertype == "Bottom":
                                hitboxes.append(pygame.Rect(x, y + 28, 32, 4))
                            elif collidertype == "Right":
                                hitboxes.append(pygame.Rect(x + 28, y, 4, 32))

                            if collidertype == "TLRM":
                                """ From top left to right middle """
                                hitboxes.append(pygame.Rect(x, y, 16, 8))
                                hitboxes.append(pygame.Rect(x+16, y+8, 16, 8))

                            if collidertype == "LMRB":
                                """ From left middle to right bottom """
                                hitboxes.append(pygame.Rect(x, y+12, 8, 8))
                                hitboxes.append(pygame.Rect(x+8, y+16, 12, 8))
                                hitboxes.append(pygame.Rect(x+20, y+24, 12, 8))

                            if collidertype == "LMRT":
                                """ From left middle to right top """
                                hitboxes.append(pygame.Rect(x, y+8, 12, 8))
                                hitboxes.append(pygame.Rect(x+12, y, 20, 8))

                            if collidertype == "LBRM":
                                """ From left bottom to right middle """
                                hitboxes.append(pygame.Rect(x, y+24, 8, 8))
                                hitboxes.append(pygame.Rect(x+8, y+20, 12, 8))
                                hitboxes.append(pygame.Rect(x+20, y+12, 12, 8))

                            if collidertype == "LTRB":
                                """ From left top to right bottom """
                                hitboxes.append(pygame.Rect(x, y, 16, 8))
                                hitboxes.append(pygame.Rect(x+12, y+8, 8, 8))
                                hitboxes.append(pygame.Rect(x+20, y+16, 12, 12))
                            
                            if collidertype == "LB":
                                """ Left bottom only """
                                hitboxes.append(pygame.Rect(x, y+24, 8, 8))

                            if collidertype == "LBRT":
                                """ From left bottom to right top """
                                hitboxes.append(pygame.Rect(x, y+20, 8, 12))
                                hitboxes.append(pygame.Rect(x+8, y+12, 12, 8))
                                hitboxes.append(pygame.Rect(x+16, y, 16, 12))

                            if collidertype == "RB":
                                """ Right bottom only """
                                hitboxes.append(pygame.Rect(x+24, y+24, 8, 8))

                            for l, hitbox in enumerate(hitboxes):
                                self._collision_hitboxes.append([f"{i}-{j}cmapobj-{collidertype}-{l}", hitbox])
        
            if "triggers" in layer.name.lower():
                for item in layer:
                    delay = 20
                    if "delay" in item.properties:
                        delay = item.properties["delay"]
                    max_num_triggers = 0
                    if "max_num_triggers" in item.properties:
                        max_num_triggers = item.properties["max_num_triggers"]
                    new_trigger = Trigger(item.name, delay = delay, max_num_triggers = max_num_triggers)
                    self._triggers[new_trigger] = pygame.Rect(item.x, item.y, item.width, item.height)

        for surf, y in self._c_object_surfs:
            if y in self._m_object_surfs:
                m_surf = self._m_object_surfs[y]
                surf.blit(m_surf, (0, 0))
                del self._m_object_surfs[y]

        for y, surf in self._m_object_surfs.items():
            self._c_object_surfs.append([surf, y])

        self._ground_surf.blit(self._bridge_surf, (0,0))

        checked_tiles = []
        """ Combine areas where we can use bigger rectangles for hitboxes. """
        for i in range(self._mapwidth_tiles):
            for j in range(self._mapheight_tiles):
                cur_tile = self._collision_object_matrix[i, j]
                if (i, j) in checked_tiles:
                    continue
                if cur_tile == 1:
                    combwidth = 1
                    combheight = 1
                    comb_size = self.recursive_expand_square(i, j,
                                                             combwidth,
                                                             combheight,
                                                             self._collision_object_matrix)
                    for ii in range(comb_size[0]):
                        for jj in range(comb_size[1]):
                            checked_tiles.append((i + ii, j + jj))

                    hitbox = pygame.Rect(i*32, j*32, comb_size[0]*32, comb_size[1]*32)
                    self._collision_hitboxes.append([f"{i}-{j}cmapobj-comb", hitbox])

        checked_tiles = []
        water_matrix = self._water_matrix - self._bridge_matrix
        """ Combine areas where we can use bigger rectangles for water """
        for i in range(self._mapwidth_tiles):
            for j in range(self._mapheight_tiles):
                cur_tile = water_matrix[i, j]
                if (i, j) in checked_tiles:
                    continue
                if cur_tile == 1:
                    combwidth = 1
                    combheight = 1
                    comb_size = self.recursive_expand_square(i, j,
                                                             combwidth,
                                                             combheight,
                                                             water_matrix)
                    for ii in range(comb_size[0]):
                        for jj in range(comb_size[1]):
                            checked_tiles.append((i + ii, j + jj))

                    hitbox = pygame.Rect(i*32, j*32, comb_size[0]*32, comb_size[1]*32)
                    self._water_hitboxes.append([f"{i}-{j}wmapobj-comb", hitbox])

    def store_data(self, npcs, loot, player_position, camera_position):
        """ Stores the current NPCs in the map, player position and camera
        position. This can be retrieved with 'retrieve_data()' when loading the
        map again.
        """
        self._stored_npcs = npcs
        self._stored_loot = loot
        self._stored_player_position = player_position
        self._stored_camera_positon = camera_position

    def retrieve_data(self):
        return self._stored_npcs, self._stored_loot, np.array(self._stored_player_position), self._stored_camera_positon


    def recursive_expand_square(self, x, y, cur_width, cur_height, matrix):
        """ Expand a square from one point in the matrix into its neighboring
        points as long all values in the expansion direction is 1.
        """
        exp_width = True
        exp_height = True

        for j in range(cur_height):
            if x + cur_width < self._mapwidth_tiles:
                if matrix[x + cur_width, y + j] == 0:
                    exp_width = False
            else:
                exp_width = False

        if exp_width:
            cur_width += 1

        for i in range(cur_width):
            if y + cur_height < self._mapheight_tiles:
                if matrix[x + i, y + cur_height] == 0:
                    exp_height = False
            else:
                exp_height = False

        if exp_height:
            cur_height += 1

        if exp_width or exp_height:
            return self.recursive_expand_square(x, y, cur_width, cur_height, matrix)
        else:
            return (cur_width, cur_height)


    @property
    def width(self):
        return self._mapwidth

    @property
    def height(self):
        return self._mapheight

    @property
    def stored_player_position(self):
        return self._stored_player_position

    @property
    def stored_camera_positon(self):
        return self._stored_camera_positon
    
    @property
    def stored_npcs(self):
        return self._stored_npcs

    @property
    def ground_surf(self):
        return self._ground_surf

    @property
    def collision_obj_surfs(self):
        """ C-objects surfs """
        return self._c_object_surfs

    @property
    def non_collison_obj_surfs(self):
        """ M-objects surfs """
        return self._m_object_surfs

    @property
    def bridge_surf(self):
        return self._bridge_surf

    @property
    def above_surf(self):
        """ N-objects surfs """
        return self._above_surf

    @property
    def mapsize(self):
        """ Map size in pixels as a tuple (x, y) """
        return (self._mapwidth, self._mapheight)

    @property
    def mapsize_tiles(self):
        """ Map size in number of 32x32 tiles as a tuple (x, y) """
        return (self._mapwidth_tiles, self._mapheight_tiles)

    @property
    def collision_hitboxes(self):
        return self._collision_hitboxes

    @property
    def water_hitboxes(self):
        return self._water_hitboxes

    @property
    def triggers(self):
        return self._triggers

    @property
    def outdoors(self):
        return self._outdoors


class Trigger:
    def __init__(self, name, delay = 20, max_num_triggers = 0):
        self._name = name
        self._is_triggered = False
        self._delay = delay
        self._last_triggered = time.time() - delay
        self._max_num_triggers = max_num_triggers
        self._times_triggered = 0
        self._disabled = False

    def untrigger(self):
        """ Reset the last triggered timer """
        self._last_triggered = time.time() - self._delay
        self._times_triggered -= 1
        if self._times_triggered < 0:
            self._times_triggered = 0

    def __str__(self):
        return f"Trigger: {self._name}"

    def __call__(self):
        if (time.time() - self._last_triggered > self._delay
                and not self._disabled):
            self._last_triggered = time.time()
            self._times_triggered += 1
            if self._times_triggered >= self._max_num_triggers and self._max_num_triggers != 0:
                self._disabled = True
            return self._name
        else:
            return None

    @property
    def disabled(self):
        return self._disabled

    @property
    def name(self):
        return self._name