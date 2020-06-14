import sys
import os
import glob
import time

import pygame
from pygame.locals import *
import numpy as np

from characters import Player, Combat_Dummy
from items import Weapon, Outfit, Arrow, Projectile
from gameobjects import GameMap, MessageBox, Trigger
from triggerscripts import triggerscripts


class Game:
    def __init__(self, AA_text=True, draw_hitboxes=False, draw_triggers=False):
        """ General setup for the game.

        Keyword arguments:
        AA_text - 
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

        self._circle_cache = {}

    def load_image_folder(self, folder_name, dict):
        """ Load images from all sprite folders with the given folder name
        into the specified dictionary
        """
        print(f"Loading images from: wulax.{folder_name}")
        folders = glob.glob(os.path.join(os.getcwd(),
                                           "sprites",
                                           "wulax",
                                           "png",
                                           folder_name,
                                           "*.png"))

        folders += glob.glob(os.path.join(os.getcwd(),
                                           "sprites",
                                           "wulax",
                                           "png",
                                           "64x64",
                                           folder_name,
                                           "*.png"))
                                           
        for item in folders:            
            image = pygame.image.load(item)
            image.convert_alpha()
            item_name = item.split("\\")[-1].split(".p")[0] # use the filename as key, but without '.png'
            
            dict[item_name] = image

    def get_icon(self, name):
        img = pygame.image.load(os.path.join(os.getcwd(),
                                             "sprites",
                                             "icons",
                                             f"{name}.png"))
        img.convert_alpha()
        return img


    """ Outfit definitions """
    def make_unhooded_robe(self):
        robe_icon = self.get_icon("robe")
        robe = Outfit("Unhooded robe", robe_icon, armor = 2)
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

    def make_platearmor(self):
        platearmor_icon = self.get_icon("platearmor")
        platearmor = Outfit("Plate armor", platearmor_icon, has_hood = True, armor = 5)
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

    """ Weapon definitions """
    def make_dagger(self):
        dagger_icon = self.get_icon("dagger")
        dagger = Weapon("Dagger", dagger_icon, damage = 10)
        dagger.slash = [self._slash_images["WEAPON_dagger"]]
        return dagger

    def make_spear(self):
        spear_icon = self.get_icon("spear")
        spear = Weapon("Spear", spear_icon, "thrust", range_ = 30, damage = 20)
        spear.thrust = [self._thrust_images["WEAPON_spear"]]
        return spear

    def make_bow(self):
        bow_icon = self.get_icon("bow")
        bow = Weapon("Bow", bow_icon, "bow", range_ = 10, damage = 0, projectile = Arrow) # damage = 0 -> ranged weapon
        bow.bow = [self._bow_images["WEAPON_bow"], self._bow_images["WEAPON_arrow"]]
        return bow


    def init_game(self):
        pygame.init()
        pygame.display.set_caption("Game")
        self._screen = pygame.display.set_mode(self._size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        pygame.font.init()
        self.font_normal = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Regular.ttf"), 18)
        self.font_normal_bold = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Bold.ttf"), 18)
        self.font_big = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Regular.ttf"), 25)
        self.font_big_bold = pygame.font.Font(os.path.join(os.getcwd(), "font", "Amble-Bold.ttf"), 25)
        self.loadingtext = self.font_big.render("Loading...", self.AA_text, self.WHITE)

        self._screen.blit(self.loadingtext, (self._width/2 - self.loadingtext.get_width()/2,
                                             self._height/2 - self.loadingtext.get_height()/2))
        pygame.display.flip()
        print("Loading...")

        self.map1 = GameMap("map1.tmx")
        self._mapwidth, self._mapheight = self.map1.mapsize

        self.map = self.map1

        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(os.getcwd(), "music", "pugnateii.mp3"))

        self._clock = pygame.time.Clock()
        self._grass_bg = pygame.image.load(os.path.join(os.getcwd(), "graphics", "grass_bg.png"))

        self._inventory_menu = pygame.image.load(os.path.join(os.getcwd(), "graphics", "inventorymenu.png"))
        self._inventory_menu.convert_alpha()
        
        self._walkcycle_images = {}
        self._bow_images = {}
        self._hurt_images = {}
        self._slash_images = {}
        self._spellcast_images = {}
        self._thrust_images = {}

        self._combat_dummy_images = {}
        
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

        hands_icon = self.get_icon("hands")
        hands = Weapon("Hands", hands_icon, "slash", damage = 2)

        robe = self.make_unhooded_robe()
        bow = self.make_bow()
        spear = self.make_spear()

        self.player = Player(300, 300,
                             self._walkcycle_images, 
                             self._slash_images,
                             self._thrust_images,
                             self._bow_images,
                             self._hurt_images,
                             robe)

        self.player.add_to_inventory(hands)
        self.player.equip_weapon("Hands")

        self.player.add_to_inventory(bow)
        self.player.add_to_inventory(spear)

        self.npcs = []
        self.npcs.append(Combat_Dummy(self._images, 10*32, 3*32))
        self._projectiles = []

        self._paused = False
        self._inventory = False
        self._pausebg = None
        self._inv_x = 0
        self._inv_y = 0
        self._hover_item = None

        self._day_time = 0

        #pygame.mixer.music.play(loops = -1)
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

    def on_event(self, event):
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
                else:
                    if self._inv_hint in self._messageboxes:
                        self._messageboxes.remove(self._inv_hint)
                    self._paused = True
                    self._inventory = True
                    self._pausebg = self._screen.copy()
                    self._paused_render = self.inventory_render


    """ Game loop methods """
    def standard_loop(self, action, move_array, key_states):
        """ Normal gameplay loop """
        """ Player step """
        self._player_data = self.player.step(self._day_time, action, move_array, key_states[pygame.K_LSHIFT])

        if self._player_data[2][0] is not None:
            """ Character is attacking """
            rect = self._player_data[2][0]
            attack_weapon = self._player_data[2][1]

            if attack_weapon.projectile is not None:
                """ Make projectile """
                direction = attack_weapon.facing
                x, y = rect.center
                if direction == 1 or direction == 3:
                    y -= 12 # move arrow up to align with character
                new_projectile = attack_weapon.projectile(x, y, direction)
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
                self.attack_rects[self.player] = self._player_data[2]

        self.hitboxes[self.player] = self._player_data[3]

        """ NPC steps """
        self._npc_datas = []
        for npc in self.npcs:
            npc_data = npc.step(self._day_time)
            self.hitboxes[npc] = npc_data[3]
            self._npc_datas.append(npc_data)

        for _, hitbox in self.map.collision_hitboxes + self.map.water_hitboxes:
            self.hitboxes[_] = hitbox

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
                            if isinstance(attack_weapon[0], Projectile):
                                del_projectiles.append(attack_weapon)
                        else:
                            target.take_damage(attack_weapon.damage)
                    except AttributeError:
                        """ Target can't take damage """
                        if isinstance(attack_weapon, list):
                            if isinstance(attack_weapon[0], Projectile) and not "wmapobj" in target:
                                del_projectiles.append(attack_weapon)

        for projectile in del_projectiles:
            if projectile in self._projectiles:
                self._projectiles.remove(projectile)

        candidate_pos = self._player_data[0].copy()
        playerhitbox = self.hitboxes[self.player]
        movement_x = self._player_data[4][0]
        movement_y = self._player_data[4][1]

        """ Checking player triggers """
        trigger = playerhitbox.collidedict(self.map.triggers, 1)
        if trigger is not None:
            trigger_name = trigger[0]()
            if trigger_name is not None:
                if trigger_name in triggerscripts:
                    add_mboxes, add_npcs, newmap, movement_req = triggerscripts[trigger_name]()
                    can_trigger = False
                    if movement_req is not None:
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
                    else:
                        trigger[0].untrigger()
                    
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
        while candidate_pos[0] - self._cam_x >= self._width - 200:
            self._cam_x += abs(movement_x)
        while candidate_pos[1] - self._cam_y >= self._height - 200:
            self._cam_y += abs(movement_y)
        while candidate_pos[0] - self._cam_x <= 200:
            self._cam_x -= abs(movement_x)
        while candidate_pos[1] - self._cam_y <= 200:
            self._cam_y -= abs(movement_y)

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
            yshifts.append(npc_data[4])
            shadow = npc_data[2]

            if npc_data[5] is not None:
                healthbars.append(npc_data[5])

            if shadow_state <= 20:
                shadows[shadow] = (npc_position[0] - sprite_size//2, npc_position[1] + sprite_size//2 - 8)
            else:
                shadows[shadow] = (npc_position[0] - sprite_size//2, npc_position[1] + sprite_size//2 - shadow.get_height() - 3)

            item_surfs.append(npc_surf)
            item_positions.append([npc_position[0] - sprite_size//2, npc_position[1] - sprite_size//2])

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

        item_surfs = np.array(item_surfs)
        item_positions = np.array(item_positions)
        yshifts = np.array(yshifts)

        inds = item_positions[:,1].argsort()
            
        item_surfs = item_surfs[inds]
        item_positions = item_positions[inds]
        yshifts = yshifts[inds]

        """ Draw shadows """
        if self._day_time <= 200:
            for shadow, pos in shadows.items():
                pos = np.array(pos) - campos
                self._screen.blit(shadow, pos)

        """ Draw characters and items """
        for surf, pos, yshift in zip(item_surfs, item_positions, yshifts):
            pos[1] += yshift
            pos = pos.astype(int) - campos
            self._screen.blit(surf, pos)
        
        """ Draw items that are always above """
        self._screen.blit(self.map.above_surf, (0 - cam_x, 0 - cam_y))

        """ Draw night effect """
        night = pygame.surface.Surface((self._width, self._height))
        night.fill(self.BLACK)
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
            for a, hitbox in self.hitboxes.items():
                draw_hitbox = hitbox.move(-cam_x, -cam_y)
                pygame.draw.rect(self._screen, self.WHITE, draw_hitbox)

            for a, hitbox in self.map.water_hitboxes:
                draw_hitbox = hitbox.move(-cam_x, -cam_y)
                pygame.draw.rect(self._screen, self.BLUE, draw_hitbox)

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
        
        self._screen.blit(time_text, (5, self._height - 25))

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
            self._screen.blit(icon, (column*64 + 42, row*64 + 74))
            
        try:
            if self._inv_x != -1 and self._inv_y != -1:
                self._hover_item = inv_matrix[self._inv_y][self._inv_x]
                hover_item = self._hover_item[0]
                nametext = self.font_big_bold.render(f"{hover_item.name.title()}", self.AA_text, self.WHITE)
                if isinstance(hover_item, Weapon):
                    text2 = self.font_normal.render(f"Damage: {hover_item.damage}", self.AA_text, self.WHITE)
                    text3 = self.font_normal.render(f"Range: {hover_item.range}", self.AA_text, self.WHITE)
                    text4 = self.font_normal.render(f"Durability: {hover_item.durability}", self.AA_text, self.WHITE)
                self._screen.blit(nametext, (450, 168))
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
                    nametext = self.font_big_bold.render(f"{hover_item.name.title()}", self.AA_text, self.WHITE)
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

    def render(self):
        cam_x = min(max(self._cam_x, 0), self._mapwidth - self._width)
        cam_y = min(max(self._cam_y, 0), self._mapheight - self._height)
        campos = np.array([cam_x, cam_y])
        if not self._paused:
            self._unpaused_render(cam_x, cam_y, campos)
        if self._paused:
            self._paused_render(cam_x, cam_y, campos)

        time_now = time.time()
        del_messageboxes = []
        tsurf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        move_up = 0
        for i, box in enumerate(self._messageboxes):
            text, textpos, bgrect, bgcolor = box()
            bgrect = bgrect.move(0, -move_up)
            textpos = (textpos[0], textpos[1] - move_up)
            pygame.draw.rect(self._screen, bgcolor, bgrect)
            tsurf.blit(text, textpos)
            move_up += bgrect.height + 10
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




