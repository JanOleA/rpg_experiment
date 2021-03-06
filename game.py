import sys
import os
import glob
import time
from copy import copy

import pygame
from pygame.locals import *
import numpy as np

from characters import Player, Combat_Dummy, NPC
from items import (Weapon, Outfit, Arrow, Projectile,
                   ArrowAmmo, Ammo, Loot, Extra_Item, Quiver)
from gameobjects import GameMap, MessageBox, Trigger
from triggerscripts import triggerscripts


class Game:
    def __init__(self, AA_text=True, draw_hitboxes=False, draw_triggers=False):
        """ General setup for the game.

        Keyword arguments:
        AA_text -- boolean, whether or not to draw text with anti-aliasing.
                   (default True)
        draw_hitboxes -- boolean, whether or not to draw the hitboxes of character
                         and items (default False)
        draw_triggers -- boolean, whether or not to draw the hitboxes of triggers
                         (default False)
        """
        self._running = True
        self._screen = None
        self._width = 1280
        self._height = 800
        self._cam_x = 0
        self._cam_y = 0
        self._size = (self._width, self._height)
        
        self.WHITE = (255, 255, 255)
        self.GREY = (150, 150, 150)
        self.RED = (255, 0, 0)
        self.DARKERRED = (200, 0, 0)
        self.DARKRED = (50, 0, 0)
        self.GREEN = (0, 255, 0)
        self.DARKERGREEN = (0, 200, 0)
        self.DARKGREEN = (0, 50, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)

        self.AA_text = AA_text
        self._draw_hitboxes = draw_hitboxes
        self._draw_triggers = draw_triggers

    def load_image_folder(self, folder_name, dict):
        """ Load images from all sprite folders with the given folder name
        into the specified dictionary.

        Arguments:
        folder_name -- folder to load images from, e.g. 'walkcycle' or 'slash'
        dict -- dictionary to load images into
        """
        print(f"Loading images from: sprites.wulax.png.{folder_name}")
        files = glob.glob(os.path.join(os.getcwd(),
                                       "sprites",
                                       "wulax",
                                       "png",
                                       folder_name,
                                       "*.png"))

        print(f"Loading images from: sprites.wulax.png.64x64.{folder_name}")
        files += glob.glob(os.path.join(os.getcwd(),
                                        "sprites",
                                        "wulax",
                                        "png",
                                        "64x64",
                                        folder_name,
                                        "*.png"))
                                           
        for item in files:            
            image = pygame.image.load(item).convert_alpha()
            item_name = item.split("\\")[-1].split(".p")[0] # use the filename as key, but without '.png'
            item_name = item_name.split("/")[-1]
            dict[item_name] = image

    def load_image_animations_combined(self, image_path, name):
        """ Loads an image where the animations are combined in the order:
        spellcast
        thrust
        walkcycle
        slash
        bow
        hurt

        Places the images in the correct dictionaries from self._images

        Arguments:
        image_path -- list containing the path to the image from game folder.
        name -- name of the object being loaded.
        """
        path = os.path.join(os.getcwd(), *image_path)
        print(f"Loading image: {'.'.join(image_path)}")
        full_image = pygame.image.load(path).convert_alpha()

        spellcast_surf = pygame.surface.Surface((64*7, 64*4), pygame.SRCALPHA)
        spellcast_surf.blit(full_image, (0,0))
        self._images["spellcast"][name] = spellcast_surf

        thrust_surf = pygame.surface.Surface((64*8, 64*4), pygame.SRCALPHA)
        thrust_surf.blit(full_image, (0,0), (0, 64*4, 64*8, 64*4))
        self._images["thrust"][name] = thrust_surf

        walk_surf = pygame.surface.Surface((64*9, 64*4), pygame.SRCALPHA)
        walk_surf.blit(full_image, (0,0), (0, 64*8, 64*9, 64*4))
        self._images["walkcycle"][name] = walk_surf

        slash_surf = pygame.surface.Surface((64*6, 64*4), pygame.SRCALPHA)
        slash_surf.blit(full_image, (0,0), (0, 64*12, 64*6, 64*4))
        self._images["slash"][name] = slash_surf

        bow_surf = pygame.surface.Surface((64*13, 64*4), pygame.SRCALPHA)
        bow_surf.blit(full_image, (0,0), (0, 64*16, 64*13, 64*4))
        self._images["bow"][name] = bow_surf

        hurt_surf = pygame.surface.Surface((64*6, 64), pygame.SRCALPHA)
        hurt_surf.blit(full_image, (0,0), (0, 64*20, 64*6, 64))
        self._images["hurt"][name] = hurt_surf

    def load_icons(self):
        """ Load all the icons from the icons folder. """
        files = glob.glob(os.path.join(os.getcwd(),
                                       "sprites",
                                       "icons",
                                       "*.png"))
        for item in files:
            item_name = item.split("\\")[-1].split(".p")[0] # use the filename as key, but without '.png'
            item_name = item_name.split("/")[-1]
            print(f"Loading sprites.icons.{item_name}.png")    
            image = pygame.image.load(item).convert_alpha()
            self._icons[item_name] = image

    def get_icon(self, name):
        img = self._icons[name]
        return img

    def load_legionarmor(self):
        """ Load all the legion armor images. """
        self.load_image_animations_combined(["sprites", "legionarmor", "Male_sandals.png"], "FEET_legionarmor_sandals_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "Male_legionSkirt.png"], "LEGS_legionarmor_skirt_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Male_legionplate_steel.png"], "TORSO_legionarmor_plate_steel_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Male_legion1helmet_steel.png"], "HEAD_legionarmor_helmet_steel_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Male_legionbauldron_steel.png"], "HANDS_legionarmor_bauldron_steel_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Male_legionplate_bronze.png"], "TORSO_legionarmor_plate_bronze_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Male_legion1helmet_bronze.png"], "HEAD_legionarmor_helmet_bronze_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Male_legionbauldron_bronze.png"], "HANDS_legionarmor_bauldron_bronze_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Male_legionplate_gold.png"], "TORSO_legionarmor_plate_gold_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Male_legion1helmet_gold.png"], "HEAD_legionarmor_helmet_gold_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Male_legionbauldron_gold.png"], "HANDS_legionarmor_bauldron_gold_male")
        self.load_image_animations_combined(["sprites", "legionarmor", "Female_sandals.png"], "FEET_legionarmor_sandals_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "Female_legionSkirt.png"], "LEGS_legionarmor_skirt_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Female_legionplate_steel.png"], "TORSO_legionarmor_plate_steel_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Female_legion1helmet_steel.png"], "HEAD_legionarmor_helmet_steel_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Female_legionbauldron_steel.png"], "HANDS_legionarmor_bauldron_steel_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Female_legionplate_bronze.png"], "TORSO_legionarmor_plate_bronze_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Female_legion1helmet_bronze.png"], "HEAD_legionarmor_helmet_bronze_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Female_legionbauldron_bronze.png"], "HANDS_legionarmor_bauldron_bronze_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "plate", "Female_legionplate_gold.png"], "TORSO_legionarmor_plate_gold_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "helmet", "Female_legion1helmet_gold.png"], "HEAD_legionarmor_helmet_gold_female")
        self.load_image_animations_combined(["sprites", "legionarmor", "bauldron", "Female_legionbauldron_gold.png"], "HANDS_legionarmor_bauldron_gold_female")


    """ Body images definitions """
    def make_standard_male(self):
        """ Create a dictionary to pass to the character 'images' argument with the
        images for a standard male with blonde hair.

        Returns:
        body_image_collection -- the dictionary containing the images. Can be passed
                                 directly as the 'images' argument when making a new
                                 character.
        """
        body_image_collection = {}
        body_image_collection["walkcycle"] = [self._walkcycle_images["BODY_male"], self._walkcycle_images["HEAD_hair_blonde"]]
        body_image_collection["slash"] = [self._slash_images["BODY_male"], self._slash_images["HEAD_hair_blonde"]]
        body_image_collection["thrust"] = [self._thrust_images["BODY_male"], self._thrust_images["HEAD_hair_blonde"]]
        body_image_collection["bow"] = [self._bow_images["BODY_male"], self._bow_images["HEAD_hair_blonde"]]
        body_image_collection["hurt"] = [self._hurt_images["BODY_male"], self._hurt_images["HEAD_hair_blonde"]]

        return body_image_collection

    """ Outfit definitions """
    def make_unhooded_robe(self):
        """ Make a new Outfit object for an unhooded robe.
        
        Returns:
        robe -- The Outfit object of a robe.        
        """
        robe_icon = self.get_icon("robe")
        looticon = self.get_icon("robe_looticon")
        robe = Outfit("Unhooded robe", robe_icon, looticon = looticon, armor = 2, lootname = "a robe without a hood")
        robe.walkcycle = [self._walkcycle_images["FEET_shoes_brown"],
                          self._walkcycle_images["LEGS_robe_skirt"],
                          self._walkcycle_images["TORSO_robe_shirt_brown"]]
        robe.slash = [self._slash_images["FEET_shoes_brown"],
                      self._slash_images["LEGS_robe_skirt"],
                      self._slash_images["TORSO_robe_shirt_brown"]]
        robe.thrust = [self._thrust_images["FEET_shoes_brown"],
                       self._thrust_images["LEGS_robe_skirt"],
                       self._thrust_images["TORSO_robe_shirt_brown"]]
        robe.hurt = [self._hurt_images["FEET_shoes_brown"],
                     self._hurt_images["LEGS_robe_skirt"],
                     self._hurt_images["TORSO_robe_shirt_brown"]]
        robe.bow = [self._bow_images["FEET_shoes_brown"],
                    self._bow_images["LEGS_robe_skirt"],
                    self._bow_images["TORSO_robe_shirt_brown"]]

        return robe

    def make_plainclothes(self):
        """ Make a new Outfit object for plain clothes.
        
        Returns:
        plainclothes -- The Outfit object of some plain clothes.        
        """
        icon = self.get_icon("plainclothes")
        looticon = self.get_icon("plainclothes_looticon")
        plainclothes = Outfit("Plain clothes", icon, looticon = looticon, armor = 1, lootname = "some plain clothes")
        plainclothes.walkcycle = [self._walkcycle_images["FEET_shoes_brown"],
                                  self._walkcycle_images["LEGS_pants_greenish"],
                                  self._walkcycle_images["TORSO_leather_armor_shirt_white"]]
        plainclothes.slash = [self._slash_images["FEET_shoes_brown"],
                              self._slash_images["LEGS_pants_greenish"],
                              self._slash_images["TORSO_leather_armor_shirt_white"]]
        plainclothes.thrust = [self._thrust_images["FEET_shoes_brown"],
                               self._thrust_images["LEGS_pants_greenish"],
                               self._thrust_images["TORSO_leather_armor_shirt_white"]]
        plainclothes.hurt = [self._hurt_images["FEET_shoes_brown"],
                             self._hurt_images["LEGS_pants_greenish"],
                             self._hurt_images["TORSO_leather_armor_shirt_white"]]
        plainclothes.bow = [self._bow_images["FEET_shoes_brown"],
                            self._bow_images["LEGS_robe_skirt"],
                            self._bow_images["TORSO_leather_armor_shirt_white"]]

        return plainclothes

    def make_platearmor(self):
        """ Make a new Outfit object for medieval plate armor.
        
        Returns:
        platearmor -- The Outfit object of the armor.        
        """
        platearmor_icon = self.get_icon("platearmor")
        looticon = self.get_icon("platearmor_looticon")
        platearmor = Outfit("Plate armor", platearmor_icon, looticon = looticon, has_hood = True, armor = 5, lootname = "a set of plate armor")
        platearmor.walkcycle = [self._walkcycle_images["FEET_plate_armor_shoes"],
                                self._walkcycle_images["LEGS_plate_armor_pants"],
                                self._walkcycle_images["TORSO_plate_armor_torso"],
                                self._walkcycle_images["TORSO_plate_armor_arms_shoulders"],
                                self._walkcycle_images["HEAD_plate_armor_helmet"],
                                self._walkcycle_images["HANDS_plate_armor_gloves"]]
        platearmor.slash = [self._slash_images["FEET_plate_armor_shoes"],
                            self._slash_images["LEGS_plate_armor_pants"],
                            self._slash_images["TORSO_plate_armor_torso"],
                            self._slash_images["TORSO_plate_armor_arms_shoulders"],
                            self._slash_images["HEAD_plate_armor_helmet"],
                            self._slash_images["HANDS_plate_armor_gloves"]]
        platearmor.thrust = [self._thrust_images["FEET_plate_armor_shoes"],
                             self._thrust_images["LEGS_plate_armor_pants"],
                             self._thrust_images["TORSO_plate_armor_torso"],
                             self._thrust_images["TORSO_plate_armor_arms_shoulders"],
                             self._thrust_images["HEAD_plate_armor_helmet"],
                             self._thrust_images["HANDS_plate_armor_gloves"]]
        platearmor.hurt = [self._hurt_images["FEET_plate_armor_shoes"],
                           self._hurt_images["LEGS_plate_armor_pants"],
                           self._hurt_images["TORSO_plate_armor_torso"],
                           self._hurt_images["TORSO_plate_armor_arms_shoulders"],
                           self._hurt_images["HEAD_plate_armor_helmet"],
                           self._hurt_images["HANDS_plate_armor_gloves"]]
        platearmor.bow = [self._bow_images["FEET_plate_armor_shoes"],
                          self._bow_images["LEGS_plate_armor_pants"],
                          self._bow_images["TORSO_plate_armor_torso"],
                          self._bow_images["TORSO_plate_armor_arms_shoulders"],
                          self._bow_images["HEAD_plate_armor_helmet"],
                          self._bow_images["HANDS_plate_armor_gloves"]]

        return platearmor

    def make_roman_platearmor(self, color = "steel"):
        """ Make a new Outfit object for Roman legion plate armor.
        
        Returns:
        legionarmor -- The Outfit object of the armor.        
        """
        color = color.lower()
        legionarmor_icon = self.get_icon(f"legionarmor_{color}")
        legionarmor_looticon = self.get_icon(f"legionarmor_{color}_looticon")
        legionarmor = Outfit(f"Legion Armor", legionarmor_icon, looticon = legionarmor_looticon, has_hood = True, armor = 5, lootname = f"a set of {color} Roman armor")

        legionarmor.walkcycle = [self._walkcycle_images["FEET_legionarmor_sandals_male"],
                                 self._walkcycle_images["LEGS_legionarmor_skirt_male"],
                                 self._walkcycle_images[f"TORSO_legionarmor_plate_{color}_male"],
                                 self._walkcycle_images[f"HEAD_legionarmor_helmet_{color}_male"],
                                 self._walkcycle_images[f"HANDS_legionarmor_bauldron_{color}_male"]]
        legionarmor.slash = [self._slash_images["FEET_legionarmor_sandals_male"],
                             self._slash_images["LEGS_legionarmor_skirt_male"],
                             self._slash_images[f"TORSO_legionarmor_plate_{color}_male"],
                             self._slash_images[f"HEAD_legionarmor_helmet_{color}_male"],
                             self._slash_images[f"HANDS_legionarmor_bauldron_{color}_male"]]
        legionarmor.thrust = [self._thrust_images["FEET_legionarmor_sandals_male"],
                              self._thrust_images["LEGS_legionarmor_skirt_male"],
                              self._thrust_images[f"TORSO_legionarmor_plate_{color}_male"],
                              self._thrust_images[f"HEAD_legionarmor_helmet_{color}_male"],
                              self._thrust_images[f"HANDS_legionarmor_bauldron_{color}_male"]]
        legionarmor.hurt = [self._hurt_images["FEET_legionarmor_sandals_male"],
                            self._hurt_images["LEGS_legionarmor_skirt_male"],
                            self._hurt_images[f"TORSO_legionarmor_plate_{color}_male"],
                            self._hurt_images[f"HEAD_legionarmor_helmet_{color}_male"],
                            self._hurt_images[f"HANDS_legionarmor_bauldron_{color}_male"]]
        legionarmor.bow = [self._bow_images["FEET_legionarmor_sandals_male"],
                           self._bow_images["LEGS_legionarmor_skirt_male"],
                           self._bow_images[f"TORSO_legionarmor_plate_{color}_male"],
                           self._bow_images[f"HEAD_legionarmor_helmet_{color}_male"],
                           self._bow_images[f"HANDS_legionarmor_bauldron_{color}_male"]]

        return legionarmor

    def make_quiver(self):
        """ Make a quiver 'Extra item'
        
        Returns:
        quiver -- The Extra_Item object of the quiver.        
        """
        quiver_icon = self.get_icon("bow")
        quiver = Quiver("Quiver", quiver_icon)
        quiver.walkcycle = [self._walkcycle_images["BEHIND_quiver"]]
        quiver.slash = [self._slash_images["BEHIND_quiver"]]
        quiver.thrust = [self._thrust_images["BEHIND_quiver"]]
        quiver.hurt = [self._hurt_images["BEHIND_quiver"]]
        quiver.bow = []

        return quiver

    """ Weapon definitions """
    def make_dagger(self):
        dagger_icon = self.get_icon("dagger")
        looticon = self.get_icon("dagger_looticon")
        dagger = Weapon("Dagger", dagger_icon, looticon = looticon, damage = 10, lootname = "a dagger")
        dagger.slash = [self._slash_images["WEAPON_dagger"]]
        return dagger

    def make_spear(self):
        spear_icon = self.get_icon("spear")
        looticon = self.get_icon("spear_looticon")
        spear = Weapon("Spear", spear_icon, looticon = looticon, type_ = "thrust", range_ = 30, damage = 20, lootname = "a spear")
        spear.thrust = [self._thrust_images["WEAPON_spear"]]
        return spear

    def make_bow(self):
        bow_icon = self.get_icon("bow")
        looticon = self.get_icon("bow_looticon")
        bow = Weapon("Bow", bow_icon, looticon = looticon, type_ = "bow", range_ = 10, damage = 0, ranged = True, lootname = "a bow")
        bow.bow = [self._bow_images["WEAPON_bow"]]
        return bow
    
    def make_arrow_ammo(self, amount = 1):
        arrow_icon = self.get_icon("arrow")
        looticon = pygame.surface.Surface((50,50), pygame.SRCALPHA)
        for i in range(min(amount, 10)):
            looticon.blit(self.get_icon("arrow_looticon"), (9, 30 - i*2))
        arrow_ammo = ArrowAmmo("Arrow", arrow_icon, looticon = looticon, amount = amount)
        arrow_ammo.anim_image = [self._bow_images["WEAPON_arrow"]]
        return arrow_ammo

    """ NPC definitions """
    def make_roman_soldier(self, x, y):
        """ Make a new roman soldier NPC. 
        
        Arguments:
        x -- initial x-position
        y -- initial y-position

        Returns:
        soldier -- the character as an NPC object.
        """
        hands = Weapon("Hands", self.hands_icon, type_ = "slash", damage = 2)
        spear = self.make_spear()
        armor = self.make_roman_platearmor()

        soldier = NPC(x, y, self.make_standard_male(),
                      armor,
                      hands)
        soldier.add_to_inventory(spear)
        soldier.equip_weapon(spear)

        return soldier


    """ Game initalization """
    def init_game(self):
        """ Loads and sets up the game. """
        pygame.init()
        pygame.display.set_caption("Game")
        self._screen = pygame.display.set_mode(self._size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        pygame.font.init()
        self.font_normal = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amatic-Bold.ttf"), 25)
        self.font_big = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amatic-Bold.ttf"), 30)
        self.loadingtext = self.font_big.render("Loading...", self.AA_text, self.WHITE)

        self._screen.blit(self.loadingtext, (self._width/2 - self.loadingtext.get_width()/2,
                                             self._height/2 - self.loadingtext.get_height()/2))
        pygame.display.flip()
        print("Loading...")

        self.map = None
        self._current_map_name = None
        self._maps = {}

        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(os.getcwd(), "music", "pugnateii.mp3"))

        self._clock = pygame.time.Clock()

        self._inventory_menu = pygame.image.load(os.path.join(os.getcwd(), "graphics", "inventorymenu.png"))
        self._inventory_menu.convert_alpha()

        self._scroll_messagebox_image_l = pygame.image.load(os.path.join(os.getcwd(), "graphics", "scroll_msgbox_left.png")).convert_alpha()
        self._scroll_messagebox_image_m = pygame.image.load(os.path.join(os.getcwd(), "graphics", "scroll_msgbox_middle.png")).convert_alpha()
        self._scroll_messagebox_image_r = pygame.image.load(os.path.join(os.getcwd(), "graphics", "scroll_msgbox_right.png")).convert_alpha()
        
        self._walkcycle_images = {}
        self._bow_images = {}
        self._hurt_images = {}
        self._slash_images = {}
        self._spellcast_images = {}
        self._thrust_images = {}

        self._combat_dummy_images = {}
        self._icons = {}

        self.load_icons()
        
        self.load_image_folder("walkcycle", self._walkcycle_images)
        self.load_image_folder("bow", self._bow_images)
        self.load_image_folder("hurt", self._hurt_images)
        self.load_image_folder("slash", self._slash_images)
        self.load_image_folder("spellcast", self._spellcast_images)
        self.load_image_folder("thrust", self._thrust_images)
        self.load_image_folder("combat_dummy", self._combat_dummy_images)

        self._images = {"walkcycle": self._walkcycle_images,
                        "bow": self._bow_images,
                        "hurt": self._hurt_images,
                        "slash": self._slash_images,
                        "spellcast": self._spellcast_images,
                        "thrust": self._thrust_images,
                        "combat_dummy": self._combat_dummy_images}

        self.load_legionarmor()

        self.hands_icon = self.get_icon("hands")
        hands = Weapon("Hands", self.hands_icon, type_ = "slash", damage = 2)

        plainclothes = self.make_plainclothes()

        self.player = Player(300, 300,
                             self.make_standard_male(),
                             plainclothes,
                             hands)

        init_script = triggerscripts["game_init"]
        init_values = init_script()

        self._projectiles = []
        map_name, new_player_position, new_cam_position = init_values[2]
        self.load_new_map(map_name, new_player_position, new_cam_position)

        self.npcs = [] # NPCs currently in the map
        self.loot = [] # loot currently on the map

        self.manual_initial_item_setup()

        self._paused = False
        self._inventory = False
        self._pausebg = None
        self._inv_x = 0
        self._inv_y = 0
        self._hover_item = None
        self._day_time = 0

        #pygame.mixer.music.play(loops = -1) # -1 means loops forever
        #pygame.mixer.music.set_volume(0.1)

        self._has_displayed_sunset_msgbox = False
        self._messageboxes = []
        self._inv_hint = MessageBox("Press tab to open the inventory",
                                    self.font_normal,
                                    self._width,
                                    self._height,
                                    AA_text=self.AA_text)
        self._messageboxes.append(self._inv_hint)

        self._loop_func = self.standard_loop
        self._unpaused_render = self.standard_render
        self._paused_render = self.inventory_render
        print("Loading completed...")

    def manual_initial_item_setup(self):
        """ For adding extra items to the map or player on startup. """
        spear = self.make_spear()
        self.loot.append(Loot(600, 350, spear, 0))
        platearmor = self.make_roman_platearmor()
        self.loot.append(Loot(800, 350, platearmor, 0))
        bow = self.make_bow()
        self.loot.append(Loot(400, 350, bow, 0))
        arrows = self.make_arrow_ammo(50)
        self.loot.append(Loot(450, 350, arrows, 0))

        new_soldier = self.make_roman_soldier(1000, 350)
        self.npcs.append(new_soldier)

    def on_event(self, event):
        """ pygame event handling """
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self._paused:
                    if self._hover_item is not None:
                        if isinstance(self._hover_item[0], Weapon):
                            self.player.equip_weapon(self._hover_item[1])
                        if isinstance(self._hover_item[0], Outfit):
                            self.player.equip_outfit(self._hover_item[1])
                        if isinstance(self._hover_item[0], Ammo):
                            if self.player.equipped_ammo == self._hover_item[0]:
                                self.player.unequip_ammo()
                            else:
                                self.player.equip_ammo(self._hover_item[1])
            elif event.button == 3:
                if self._paused:
                    if self._hover_item is not None:
                        item = self._hover_item[0]
                        if isinstance(item, Weapon):
                            self.player.remove_from_inventory(item)
                        if isinstance(item, Outfit):
                            self.player.remove_outfit(item)
                        if isinstance(self._hover_item[0], Ammo):
                            if self.player.equipped_ammo == self._hover_item[0]:
                                self.player.unequip_ammo()
                            self.player.remove_from_inventory(self._hover_item[0])

        if event.type == pygame.KEYDOWN:
            if not self._paused:
                pass
            else:
                pass

            if event.key == pygame.K_TAB:
                if self._paused:
                    if self._inventory:
                        self._paused = False
                        self._inventory == False
                        if self._inv_hint in self._messageboxes:
                            self._messageboxes.remove(self._inv_hint)
                            inv_hint_1 = MessageBox("Click an item in the inventory to equip it.", self.font_normal, self._width, self._height)
                            inv_hint_2 = MessageBox("Right click an item in the inventory to discard it.", self.font_normal, self._width, self._height)
                            self._messageboxes.append(inv_hint_2)
                            self._messageboxes.append(inv_hint_1)
                else:
                    self._paused = True
                    self._inventory = True
                    self._pausebg = self._screen.copy()
                    self._paused_render = self.inventory_render

    def load_new_map(self, new_map, new_player_position = None, new_cam_position = None):
        """ Stores the data from the currently loaded map into its GameMap object
        and loads the new map.
        
        Arguments:
        new_map -- Filename for the map to load. If it already exists in the self._maps
                   dictionary that object will be reused. Otherwise will be loaded from file.

        Keyword arguments:
        new_player_position -- (x, y) position of where the player starts in
                               the new map
        new_cam_position -- (x, y) position of where the camera starts in the
                            new map

        if the position arguments are None, the values will be loaded from the
        values stored in the new_map GameMap object.
        """
        load_start = time.time()
        self._unpaused_render = self.loading_render
        self._paused_render = self.loading_render

        while len(self._projectiles) > 0:
            self._projectiles.pop()

        if self.map != None:
            self.render()

        if new_player_position is None:
            new_player_position = self._maps[new_map].stored_player_position
        if new_cam_position is None:
            new_cam_position = self._maps[new_map].stored_camera_position

        if self._current_map_name in self._maps:
            origmap = self._maps[self._current_map_name]
            origmap.store_data(self.npcs.copy(), self.loot.copy(), self.player.position.copy(), (self._cam_x, self._cam_y))

        if not new_map in self._maps:
            new_map_object = GameMap(new_map)
            self._maps[new_map] = new_map_object
        else:
            new_map_object = self._maps[new_map]

        self._current_map_name = new_map
        self.map = copy(new_map_object)

        npcs, loot, player_position, camera_position = self.map.retrieve_data()
        if new_player_position is None:
            new_player_position = player_position
        else:
            new_player_position = np.array(new_player_position)
        if camera_position is None:
            new_cam_position = camera_position

        self.npcs = npcs
        self.loot = loot
        self.player.set_pos(new_player_position)
        self._cam_x, self._cam_y = new_cam_position
        self._mapwidth = self.map.width
        self._mapheight = self.map.height

        load_end = time.time()

        time.sleep(max(0.3 - (load_end - load_start),0)) # keep the loading screen for at least 0.3 seconds
                                                         # because an instant skip looks unnatural
        self._unpaused_render = self.standard_render
        self._paused_render = self.inventory_render


    def character_attack(self, char_data, character):
        """ Check character data for whether or not a character is attacking,
        and handle the attack hitbox appropriately.
        """
        if char_data[2][0] is not None:
            """ Character is attacking """
            rect = char_data[2][0]
            attack_weapon = char_data[2][1]

            if attack_weapon.ranged is True:
                """ Make projectile """
                if character.equipped_ammo is not None:
                    direction = attack_weapon.facing
                    x, y = rect.center
                    if direction == 1 or direction == 3:
                        y -= 12 # move arrow up to align with character
                    new_projectile = character.equipped_ammo.projectile_type(x, y, direction)
                    character.equipped_ammo.reduce_amount()
                    img_ = new_projectile.image
                    layer = self._images[img_[0]][img_[1]]
                    projectile_surf = pygame.Surface((64, 64), pygame.SRCALPHA)
                    if direction != 0:
                        projectile_surf.blit(layer, (0, 0), (768, int(direction*64), 64, 64))
                    else:
                        projectile_surf.blit(layer, (0, 0), (768, 128, 64, 64))
                        projectile_surf = pygame.transform.flip(projectile_surf, 1, 1)

                    self._projectiles.append([new_projectile, projectile_surf])
            else:
                self.attack_rects[character] = char_data[2]

    def character_motion(self, char_position, movement, character, characterhitbox):
        if not character.can_move:
            return
        candidate_pos = char_position.copy()
        movement_x = movement[0]
        movement_y = movement[1]
        """ Collision testing the character """
        if character in self.hitboxes:
            hitboxes_no_character = self.hitboxes.copy()
            del hitboxes_no_character[character]
        else:
            hitboxes_no_character = self.hitboxes
        if movement_x > 0:
            candidate_hitbox = characterhitbox.move(movement_x + 1, 0)
            collides = candidate_hitbox.collidedict(hitboxes_no_character, 1)
            if collides is not None:
                movement_x = 0
        elif movement_x < 0:
            candidate_hitbox = characterhitbox.move(movement_x - 1, 0)
            collides = candidate_hitbox.collidedict(hitboxes_no_character, 1)
            if collides is not None:
                movement_x = 0

        if movement_y > 0:
            candidate_hitbox = characterhitbox.move(0, movement_y + 1)
            collides = candidate_hitbox.collidedict(hitboxes_no_character, 1)
            if collides is not None:
                movement_y = 0
        elif movement_y < 0:
            candidate_hitbox = characterhitbox.move(0, movement_y - 1)
            collides = candidate_hitbox.collidedict(hitboxes_no_character, 1)
            if collides is not None:
                movement_y = 0

        candidate_pos[0] += movement_x
        candidate_pos[1] += movement_y

        character.set_pos(candidate_pos)

    """ Game loop methods """
    def standard_loop(self, action, move_array, key_states):
        """ Normal gameplay loop """
        """ Player step """
        self._player_data = self.player.step(self._day_time, action, move_array, key_states[pygame.K_LSHIFT])
        self.character_attack(self._player_data, self.player)

        self.hitboxes[self.player] = self._player_data[3]
        
        for _, hitbox in self.map.collision_hitboxes + self.map.water_hitboxes:
            self.hitboxes[_] = hitbox

        """ NPC steps """
        self._npc_datas = []
        for npc in self.npcs:
            npc_data = npc.step(self._day_time, self._player_data[0])
            self.character_motion(npc_data[0], npc_data[4], npc, npc_data[3])
            self.hitboxes[npc] = npc_data[3]
            self._npc_datas.append(npc_data)
            self.character_attack(npc_data, npc)

        """ Check for loot pickups """
        del_loot = []
        for loot in self.loot:
            loot.step()
            player_dist = np.linalg.norm(loot.position - self._player_data[0])
            if player_dist < 32:
                self.player.add_to_inventory(loot.give_item)
                if isinstance(loot.give_item, Ammo):
                    quiver = self.make_quiver()
                    self.player.add_extra_item(quiver)
                loot_messagebox = MessageBox(f"You found {loot.give_item_name}", self.font_normal, self._width, self._height)
                self._messageboxes.append(loot_messagebox)
                del_loot.append(loot)
            if loot.remove:
                del_loot.append(loot)

        for loot in del_loot:
            if loot in self.loot:
                self.loot.remove(loot)

        """ Step projectiles and check if they have existed for too long """
        del_projectiles = []
        for projectile in self._projectiles:
            hitbox = projectile[0].step()
            if projectile[0].timer > 5 and projectile[0].timer <= 200:
                self.attack_rects[projectile[0]] = [hitbox, projectile]
            elif projectile[0].timer > 200:
                del_projectiles.append(projectile)

        """ Check hitboxes for weapon hits """
        for actor, attack_rect in self.attack_rects.items():
            attack_rect, attack_weapon = attack_rect
            for target, hitbox in self.hitboxes.items():
                if actor == target or attack_rect is None:
                    continue
                if attack_rect.colliderect(hitbox):
                    try:
                        if isinstance(attack_weapon, list):
                            target.take_damage(attack_weapon[0].damage)
                            self.character_motion(target.position, target.position - actor.position, target, self.hitboxes[target])
                            if isinstance(attack_weapon[0], Projectile):
                                del_projectiles.append(attack_weapon)
                        else:
                            self.character_motion(target.position, target.position - actor.position, target, self.hitboxes[target])
                            target.take_damage(attack_weapon.damage)
                    except AttributeError:
                        """ Target can't take damage """
                        if isinstance(attack_weapon, list):
                            if isinstance(attack_weapon[0], Projectile) and not "wmapobj" in target:
                                del_projectiles.append(attack_weapon)

        for projectile in del_projectiles:
            if projectile in self._projectiles:
                self._projectiles.remove(projectile)

        playerhitbox = self.hitboxes[self.player]
        candidate_pos = self._player_data[0].copy()
        movement_x = self._player_data[4][0]
        movement_y = self._player_data[4][1]

        """ Checking player triggers """
        trigger = playerhitbox.collidedict(self.map.triggers, 1)
        if trigger is not None:
            if trigger[0].disabled:
                del self.map.triggers[trigger[0]]
            trigger_name = trigger[0]()
            if trigger_name is not None:
                if trigger_name in triggerscripts:
                    add_mboxes, add_npcs, newmap, movement_req = triggerscripts[trigger_name]()
                    can_trigger = False
                    if movement_req is not None:
                        # check that the player is moving the correct direction
                        if movement_req == 0:
                            if movement_y < 0:
                                can_trigger = True
                        if movement_req == 1:
                            if movement_x < 0:
                                can_trigger = True
                        if movement_req == 2:
                            if movement_y > 0:
                                can_trigger = True
                        if movement_req == 3:
                            if movement_x > 0:
                                can_trigger = True
                    else:
                        can_trigger = True

                    if can_trigger:
                        for mbox in add_mboxes:
                            mbox.reset_init_time()
                        self._messageboxes += add_mboxes
                        self.npcs += add_npcs
                        if newmap is not None:
                            self.load_new_map(newmap[0], newmap[1], newmap[2])
                            return
                    else:
                        trigger[0].untrigger()
                else:
                    print(f"Attempted to trigger '{trigger_name}', but it does not exist in triggerscripts.")
                    
                    
        """ Collision testing the player """
        hitboxes_no_player = self.hitboxes.copy()
        del hitboxes_no_player[self.player]
        if movement_x > 0:
            candidate_hitbox = playerhitbox.move(movement_x + 1, 0)
            collides = candidate_hitbox.collidedict(hitboxes_no_player, 1)
            if collides is not None:
                movement_x = 0
        elif movement_x < 0:
            candidate_hitbox = playerhitbox.move(movement_x - 1, 0)
            collides = candidate_hitbox.collidedict(hitboxes_no_player, 1)
            if collides is not None:
                movement_x = 0

        if movement_y > 0:
            candidate_hitbox = playerhitbox.move(0, movement_y + 1)
            collides = candidate_hitbox.collidedict(hitboxes_no_player, 1)
            if collides is not None:
                movement_y = 0
        elif movement_y < 0:
            candidate_hitbox = playerhitbox.move(0, movement_y - 1)
            collides = candidate_hitbox.collidedict(hitboxes_no_player, 1)
            if collides is not None:
                movement_y = 0

        candidate_pos[0] += movement_x
        candidate_pos[1] += movement_y

        self.player.set_pos(candidate_pos)
        
        """ Move camera if player is moving towards an edge """
        while candidate_pos[0] - self._cam_x >= self._width - 400:
            if movement_x == 0:
                break
            self._cam_x += abs(movement_x)
        while candidate_pos[1] - self._cam_y >= self._height - 300:
            if movement_y== 0:
                break
            self._cam_y += abs(movement_y)
        while candidate_pos[0] - self._cam_x <= 400:
            if movement_x == 0:
                break
            self._cam_x -= abs(movement_x)
        while candidate_pos[1] - self._cam_y <= 300:
            self._cam_y -= abs(movement_y)
            if movement_y== 0:
                break

        self._day_time += 0.01
        if self._day_time >= 400:
            self._day_time = 0
            sunrise_msgbox = MessageBox("The sun just came up",
                                        self.font_normal,
                                        self._width,
                                        self._height,
                                        AA_text=self.AA_text)
            self._messageboxes.append(sunrise_msgbox)
            self._has_displayed_sunset_msgbox = False
        elif int(self._day_time) == 200 and not self._has_displayed_sunset_msgbox:
            sunset_msgbox = MessageBox("The sun just went below the horizon",
                                       self.font_normal,
                                       self._width,
                                       self._height,
                                       AA_text=self.AA_text)
            self._messageboxes.append(sunset_msgbox)
            self._has_displayed_sunset_msgbox = True

    def loop(self):
        self.attack_rects = {}
        self.hitboxes = {}
        if not self._paused:
            """ Unpaused loop """

            """ Player controls """
            key_states = pygame.key.get_pressed()
            move_array = np.zeros(4)
            action = None
            if key_states[pygame.K_SPACE]:
                action = 4               
            if key_states[pygame.K_w]:
                action = 0
                move_array[0] = 1
            if key_states[pygame.K_a]:
                action = 1
                move_array[1] = 1
            if key_states[pygame.K_s]:
                action = 2
                move_array[2] = 1
            if key_states[pygame.K_d]:
                action = 3
                move_array[3] = 1
            
            self._loop_func(action, move_array, key_states)
        else:
            """ Paused loop """
            mouse_pos = pygame.mouse.get_pos()
            self._inv_x = (mouse_pos[0] - 32)//64
            self._inv_y = (mouse_pos[1] - 64)//64

        self._clock.tick_busy_loop(30)
        self.fps = self._clock.get_fps()


    """ Game render methods """
    def standard_render(self, cam_x, cam_y, campos):
        black_bg = pygame.Rect(0, 0, self._width, self._height)
        pygame.draw.rect(self._screen, self.BLACK, black_bg)
        self._screen.blit(self.map.ground_surf, (0 - cam_x, 0 - cam_y))

        shadow_state = int(self._day_time//5)

        """ get player surf """
        p_position = self._player_data[0]
        player_surf = self._player_data[1]
        shadow = self._player_data[5]
        sprite_size = player_surf.get_width()

        shadows = {}
        item_surfs = []
        item_positions = []
        yshifts = []
        healthbars = []

        if shadow_state <= 20:
            shadows[shadow] = (p_position[0] - sprite_size//2, p_position[1] + sprite_size//2 - 8)
        else:
            shadows[shadow] = (p_position[0] - sprite_size//2, p_position[1] + sprite_size//2 - shadow.get_height() - 3)

        item_surfs.append(player_surf)
        item_positions.append([p_position[0] - sprite_size//2, p_position[1] - sprite_size//2])
        yshifts.append(0)

        """ get NPC surfs """
        for npc_data in self._npc_datas:
            npc_position = npc_data[0]
            npc_surf = npc_data[1]
            yshifts.append(npc_data[6])
            shadow = npc_data[5]

            if npc_data[7] is not None:
                healthbars.append(npc_data[7])

            if shadow_state <= 20:
                shadows[shadow] = (npc_position[0] - sprite_size//2, npc_position[1] + sprite_size//2 - 8)
            else:
                shadows[shadow] = (npc_position[0] - sprite_size//2, npc_position[1] + sprite_size//2 - shadow.get_height() - 3)

            item_surfs.append(npc_surf)
            item_positions.append([npc_position[0] - sprite_size//2, npc_position[1] - sprite_size//2 - yshifts[-1]])

        """ get projectile surfs """
        for projectile, surf in self._projectiles:
            projectile_position = projectile.position - 32
            item_surfs.append(surf)
            item_positions.append(projectile_position)
            yshifts.append(0)

        """ get static map object surfs """
        for surf, y in self.map.collision_obj_surfs:
            item_surfs.append(surf)
            item_positions.append(np.array([0, y - 32]))
            yshifts.append(32)

        for loot in self.loot:
            item_surfs.append(loot.image)
            item_positions.append(loot.position - 32)
            yshifts.append(0)

        item_surfs = np.array(item_surfs)
        item_positions = np.array(item_positions)
        yshifts = np.array(yshifts)

        inds = item_positions[:,1].argsort()
            
        item_surfs = item_surfs[inds]
        item_positions = item_positions[inds]
        yshifts = yshifts[inds]

        """ Draw shadows """
        if self.map.outdoors:
            if self._day_time <= 200:
                for shadow, pos in shadows.items():
                    pos = np.array(pos) - campos
                    self._screen.blit(shadow, pos)

        """ Draw characters and items """
        for surf, pos, yshift in zip(item_surfs, item_positions, yshifts):
            try:
                pos[1] += yshift
                pos = pos.astype(int) - campos
                self._screen.blit(surf, pos)
            except Exception as e:
                print(e)
                print(pos)
                sys.exit(1)
        
        """ Draw items that are always above """
        self._screen.blit(self.map.above_surf, (0 - cam_x, 0 - cam_y))

        """ Draw night effect """
        if self.map.outdoors:
            night = pygame.surface.Surface((self._width, self._height), pygame.HWSURFACE)
            alpha = None
            if self._day_time > 175 and self._day_time < 250:
                alpha = (255 - abs(250 - self._day_time)*3)/2  
            elif self._day_time >= 250 and self._day_time < 350:
                alpha = 255/2
            elif self._day_time >= 350:
                alpha = (255 - abs(350 - self._day_time)*3)/2
            elif self._day_time <= 25:
                alpha = (255 - abs(-self._day_time - 50)*3)/2

            if alpha is not None:
                night.fill((0, 0, 0))
                night.set_alpha(alpha)
                self._screen.blit(night, (0, 0))

        """ Draw healthbars """
        for healthbar in healthbars:
            bg = healthbar[1]
            fg = healthbar[0]
            fg.move_ip(-cam_x, -cam_y)
            bg.move_ip(-cam_x, -cam_y)
            pygame.draw.rect(self._screen, self.RED, bg)
            if fg.width > 0:
                pygame.draw.rect(self._screen, self.GREEN, fg)

        """ Draw hitboxes if set true """
        if self._draw_hitboxes:
            hitboxes_surf = pygame.surface.Surface((self._width, self._height), pygame.SRCALPHA)
            for a, hitbox in self.hitboxes.items():
                draw_hitbox = hitbox.move(-cam_x, -cam_y)
                pygame.draw.rect(hitboxes_surf, (255, 255, 255, 150), draw_hitbox)

            for a, hitbox in self.map.water_hitboxes:
                draw_hitbox = hitbox.move(-cam_x, -cam_y)
                pygame.draw.rect(hitboxes_surf, (0, 0, 255, 150), draw_hitbox)

            for projectile, a in self._projectiles:
                hitbox = projectile.hitbox
                draw_hitbox = hitbox.move(-cam_x, -cam_y)
                pygame.draw.rect(hitboxes_surf, (0, 255, 255, 100), draw_hitbox)

            self._screen.blit(hitboxes_surf, (0,0))

        if self._draw_triggers:
            for a, trigger in self.map.triggers.items():
                draw_trigger = trigger.move(-cam_x, -cam_y)
                pygame.draw.rect(self._screen, self.GREY, draw_trigger)

        """ Draw UI elements """
        hour = int(self._day_time/400*24) + 1
        if self._day_time < 200:
            time_text = self.font_normal.render(f"It is currently hour: {hour}", self.AA_text, self.WHITE)
        else:
            time_text = self.font_normal.render(f"It is currently night", self.AA_text, self.WHITE)

        hbar_width = 100
        hbar_height = 20
        health_width = int(self.player.health/self.player.maxhealth*hbar_width)
        player_health_bg = pygame.Rect(self._width - 10 - hbar_width, self._height - 10 - hbar_height, hbar_width, hbar_height)
        player_health_border = pygame.Rect(self._width - 11 - hbar_width, self._height - 11 - hbar_height, hbar_width + 2, hbar_height + 2)
        player_health = pygame.Rect(self._width - 10 - hbar_width, self._height - 10 - hbar_height, health_width, hbar_height)
        pygame.draw.rect(self._screen, self.GREY, player_health_border)
        pygame.draw.rect(self._screen, self.DARKRED, player_health_bg)
        if self.player.health > 0:
            pygame.draw.rect(self._screen, self.DARKERRED, player_health)

        stamina = max(self.player.stamina, 0)
        stamina_width = int(stamina/self.player.maxstamina*hbar_width)
        player_stamina_bg = pygame.Rect(self._width - 20 - hbar_width*2, self._height - 10 - hbar_height, hbar_width, hbar_height)
        player_stamina_border = pygame.Rect(self._width - 21 - hbar_width*2, self._height - 11 - hbar_height, hbar_width + 2, hbar_height + 2)
        player_stamina = pygame.Rect(self._width - 20 - hbar_width*2, self._height - 10 - hbar_height, stamina_width, hbar_height)
        pygame.draw.rect(self._screen, self.GREY, player_stamina_border)
        pygame.draw.rect(self._screen, self.DARKGREEN, player_stamina_bg)
        if stamina > 0:
            pygame.draw.rect(self._screen, self.DARKERGREEN, player_stamina)
        
        self._screen.blit(time_text, (5, self._height - 35))

    def loading_render(self, cam_x, cam_y, campos):
        black_bg = pygame.Rect(0, 0, self._width, self._height)
        pygame.draw.rect(self._screen, self.BLACK, black_bg)
        self._screen.blit(self.loadingtext, (self._width/2 - self.loadingtext.get_width()/2,
                                             self._height/2 - self.loadingtext.get_height()/2))

    def inventory_render(self, cam_x, cam_y, campos):
        self._hover_item = None
        self._screen.blit(self._pausebg, (0,0))
        fill_rect = pygame.Rect(0, 0, self._width, self._height)
        surf = pygame.Surface((self._width, self._height))
        pygame.draw.rect(surf, self.BLACK, fill_rect)
        surf.set_alpha(155)
        self._screen.blit(surf, (0,0))
        self._screen.blit(self._inventory_menu, (0,0))

        inv_matrix = []
        player_inventory = self.player.get_inventory()
        for i, key in enumerate(player_inventory):
            item = player_inventory[key]
            row = i//6
            column = i%6
            if column == 0:
                inv_matrix.append([])
            inv_matrix[row].append([item, key])
            icon = item.icon
            if isinstance(item, Ammo):
                valtext = self.font_normal.render(f"{item.amount}", self.AA_text, self.WHITE)
                text_x = column*64 + 91 - valtext.get_width()
                text_y = row*64 + 100
                self._screen.blit(valtext, (text_x, text_y))
            self._screen.blit(icon, (column*64 + 42, row*64 + 74))
            
        try:
            if self._inv_x != -1 and self._inv_y != -1:
                self._hover_item = inv_matrix[self._inv_y][self._inv_x]
                hover_item = self._hover_item[0]
                nametext = self.font_big.render(f"{hover_item.name.title()}", self.AA_text, self.WHITE)
                self._screen.blit(nametext, (450, 168))
                if isinstance(hover_item, Weapon):
                    text2 = self.font_normal.render(f"Damage: {hover_item.damage}", self.AA_text, self.WHITE)
                    text3 = self.font_normal.render(f"Range: {hover_item.range}", self.AA_text, self.WHITE)
                    text4 = self.font_normal.render(f"Durability: {hover_item.durability}", self.AA_text, self.WHITE)
                    self._screen.blit(text2, (450, 200))
                    self._screen.blit(text3, (450, 225))
                    self._screen.blit(text4, (450, 250))
        except IndexError:
            pass

        player_outfits = self.player.get_outfits()
        for i, item in enumerate(player_outfits):
            row = i//6
            column = i%6
            icon = item.icon
            self._screen.blit(icon, (column*64 + 42, row*64 + 650))

        if self._inv_x >= 0 and self._inv_x <= 5:
            if self._inv_y >= 9 and self._inv_y <= 10:
                index = (self._inv_y - 9)*6 + self._inv_x
                try:
                    self._hover_item = [player_outfits[index], index]
                    hover_item = player_outfits[index]
                    nametext = self.font_big.render(f"{hover_item.name.title()}", self.AA_text, self.WHITE)
                    if isinstance(hover_item, Outfit):
                        text2 = self.font_normal.render(f"Armor: {hover_item.armor}", self.AA_text, self.WHITE)
                        text3 = self.font_normal.render(f"Durability: {hover_item.durability}", self.AA_text, self.WHITE)
                    self._screen.blit(nametext, (450, 168))
                    self._screen.blit(text2, (450, 200))
                    self._screen.blit(text3, (450, 225))
                except IndexError:
                    pass

        equipped_weapon = self.player.equipped_weapon
        icon = equipped_weapon.icon
        self._screen.blit(icon, (458, 74))

        equipped_outfit = self.player.equipped_outfit
        icon = equipped_outfit.icon
        self._screen.blit(icon, (522, 74))

        equipped_ammo = self.player.equipped_ammo
        if equipped_ammo is not None:
            icon = equipped_ammo.icon
            valtext = self.font_normal.render(f"{equipped_ammo.amount}", self.AA_text, self.WHITE)
            text_x = 634 - valtext.get_width()
            text_y = 100
            self._screen.blit(valtext, (text_x, text_y))
            self._screen.blit(icon, (586, 74))

    def render(self):
        if self.map.outdoors:
            cam_x = min(max(self._cam_x, 0), self._mapwidth - self._width)
            cam_y = min(max(self._cam_y, 0), self._mapheight - self._height)
        else:
            cam_x = self._cam_x
            cam_y = self._cam_y

        campos = np.array([cam_x, cam_y])
        if not self._paused:
            self._unpaused_render(cam_x, cam_y, campos)
        if self._paused:
            self._paused_render(cam_x, cam_y, campos)

        if self._unpaused_render != self.loading_render and not self._paused:
            time_now = time.time()
            del_messageboxes = []
            tsurf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
            move_up = 0
            scroll_left_width = self._scroll_messagebox_image_l.get_width()
            scroll_right_width = self._scroll_messagebox_image_r.get_width()
            for i, box in enumerate(self._messageboxes):
                text, textpos, bgrect, bgcolor = box()
                bgrect = bgrect.move(0, -move_up)
                textpos = (textpos[0], textpos[1] - move_up)
                scroll_surf = pygame.surface.Surface((bgrect.width, 51), pygame.SRCALPHA)
                scroll_middle = pygame.transform.scale(self._scroll_messagebox_image_m, (scroll_surf.get_width() - scroll_left_width - scroll_right_width, 51))
                scroll_surf.blit(scroll_middle, (scroll_left_width, 0))
                scroll_surf.blit(self._scroll_messagebox_image_l, (0, 0))
                scroll_surf.blit(self._scroll_messagebox_image_r, (bgrect.width - scroll_right_width, 0))

                self._screen.blit(scroll_surf, (bgrect.left, bgrect.top - 5))
                tsurf.blit(text, textpos)
                move_up += bgrect.height + 13
                if (time_now - box.init_time) > box.duration:
                    del_messageboxes.append(box)

            if len(self._messageboxes) > 0:
                self._screen.blit(tsurf, (0,0))

                for box in del_messageboxes:
                    self._messageboxes.remove(box)
                
        fps_text = self.font_normal.render(f"FPS: {self.fps:2.1f}", self.AA_text, self.WHITE)
        self._screen.blit(fps_text, (self._width - 80, 5))

        pygame.display.flip()


    def cleanup(self):
        pygame.quit()

    def execute(self):
        if self.init_game() == False:
            self._running = False
 
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.loop()
            self.render()
        self.cleanup()

    def color_surface(self, surface, red, green, blue, alpha):
        arr = pygame.surfarray.pixels3d(surface)
        arr[:,:,0] = red
        arr[:,:,1] = green
        arr[:,:,2] = blue

        alphas = pygame.surfarray.pixels_alpha(surface)
        alphas[alphas != 0] = alpha


if __name__ == "__main__":
    game = Game(draw_hitboxes=False, draw_triggers=False)
    game.execute()




