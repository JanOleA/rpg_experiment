import time

import numpy as np
import pygame
from pygame.locals import *

from items import Weapon, Outfit

slm = np.logspace(0.3, -0.8, 20) # shadow length modifiers


class NPC:
    """ Superclass for non-player characters """
    def __init__(self):
        self.id = f"{self.__class__.__name__}-{id(self)}"

    def color_surface(self, surface, red, green, blue, alpha):
        arr = pygame.surfarray.pixels3d(surface)
        arr[:,:,0] = red
        arr[:,:,1] = green
        arr[:,:,2] = blue

        alphas = pygame.surfarray.pixels_alpha(surface)
        alphas[alphas != 0] = alpha


class Combat_Dummy(NPC):
    def __init__(self, images, x, y):
        super().__init__()
        self._default_images = images["combat_dummy"]["BODY_animation"]
        self._death_images = images["combat_dummy"]["BODY_death"]
        self._health = 300
        self._maxhealth = self._health
        self._anim_step = 0
        self._state = "idle"
        self._anim_speed = 0.5
        self._sprite_size = 64
        self._position = np.array([x, y])
        self._y_shift = 5

        self._hitbox = pygame.Rect(self._position[0] - 12, self._position[1] - 8 + self._y_shift, 24, 32)
        self._shadow = None
        self._healthbar = None
        self._last_hit_timer = 60
        self._prev_shadow_state = None

    def take_damage(self, damage):
        if self._state != "dead":
            self._health -= damage
            self._state = "hit"
            if self._health <= 0:
                self._state = "dead"
                self._anim_step = 0
                self._hitbox = pygame.Rect(self._position[0] - 12, self._position[1] + self._y_shift, 24, 22)
                self._health = 0
            self._last_hit_timer = 0

    def step(self, day_time):
        images = self._default_images
        if self._state != "idle":
            if self._anim_step < 8:
                self._anim_step += self._anim_speed
            if self._state == "hit":
                if self._anim_step > 7:
                    self._anim_step = 0
                    self._state = "idle"
            if self._state == "dead":
                images = self._death_images
                if self._anim_step > 5:
                    self._anim_step = 5

        sprite_y = 0
        sprite_x = int(self._anim_step)*self._sprite_size

        character_surf = pygame.Surface((self._sprite_size, self._sprite_size), pygame.SRCALPHA)

        character_surf.blit(images, (0, 0), (sprite_x, sprite_y, self._sprite_size, self._sprite_size))

        if self._last_hit_timer < 60:
            self._last_hit_timer += 1
            health = pygame.Rect(self._position[0] - 16, self._position[1] - 32, int(self._health/self._maxhealth*32), 5)
            health_bg = pygame.Rect(self._position[0] - 16, self._position[1] - 32, 32, 5)
            self._healthbar = [health, health_bg]
        else:
            self._healthbar = None
        
        shadow_state = int(day_time//5)

        if self._shadow == None or (self._state != "idle" and (self._state != "dead" or self._anim_step != 5)) or shadow_state != self._prev_shadow_state:
            if shadow_state < 20:
                self._shadow = pygame.transform.flip(pygame.transform.scale(character_surf, (self._sprite_size, int(self._sprite_size*slm[shadow_state]))), 0, 1)
            elif shadow_state < 40:
                self._shadow = pygame.transform.scale(character_surf, (self._sprite_size, int(self._sprite_size*slm[19 - shadow_state]/2)))
            
            if shadow_state >= 40:
                alpha_modifier = 0
            else:
                alpha_modifier = 1

            self.color_surface(self._shadow, 50, 50, 50, (150 - 6*abs(20 - shadow_state))*alpha_modifier)

        self._prev_shadow_state = shadow_state

        return self._position, character_surf, self._shadow, self._hitbox, self._y_shift, self._healthbar


    @property
    def position(self):
        return self._position


class Player:
    def __init__(self, x, y,
                 walkcycle_images,
                 slash_images,
                 thrust_images,
                 bow_images,
                 hurt_images,
                 starting_outfit):
        self.walkcycle = [walkcycle_images["BODY_male"], walkcycle_images["HEAD_hair_blonde"]]
        self.slash = [slash_images["BODY_male"], slash_images["HEAD_hair_blonde"]]
        self.thrust = [thrust_images["BODY_male"], thrust_images["HEAD_hair_blonde"]]
        self.bow = [bow_images["BODY_male"], bow_images["HEAD_hair_blonde"]]
        self.hurt = [hurt_images["BODY_male"], hurt_images["HEAD_hair_blonde"]]

        self.behind = []

        self._outfit = starting_outfit

        self._outfits = [starting_outfit]
        self._equipped_weapon = None
        self._inventory = {}

        self._sprite_size = 64
        self._anim_step = 0
        self._state = "idle"
        self._body = [self.walkcycle[0]]
        self._hair = [self.walkcycle[1]]
        self._outfit_anim = starting_outfit.walkcycle
        self._weapon_anim = []
        self._facing = 3 # 0: up, 1: left, 2: down, 3: right
        self._position = np.array([x, y])
        self._speed = 2
        self._anim_speed = 0.5
        self._health = 100
        self._maxhealth = self._health
        self._stamina = 200
        self._maxstamina = self._stamina
        self.id = f"{self.__class__.__name__}-{id(self)}"
        self._shadow = None
        self._prev_shadow_state = None
        self._shadowlength_modifier = 1
        self._time_since_sprinting = 0


    """ Inventory and outfit methods"""
    def add_outfit(self, outfit):
        if not outfit in self._outfits:
            self._outfits.append(outfit)

    def equip_outfit(self, index):
        self._outfit = self._outfits[index]
        self.set_state("idle")
        self._anim_step = 0

    def equip_weapon(self, key):
        if isinstance(self._inventory[key], Weapon):
            self._equipped_weapon = self._inventory[key]

    def add_to_inventory(self, item):
        for key, it in self._inventory.items():
            if item == it:
                return
        itemname = item.name
        base = itemname
        i = 2
        while itemname in self._inventory:
            itemname = f"{base} {i}"
            i += 1
        self._inventory[itemname] = item

    def remove_from_inventory(self, item):
        if item in self._inventory:
            del self._inventory[item]

    def get_inventory(self):
        return self._inventory

    def get_outfits(self):
        return self._outfits


    """ Behavior methods """
    def set_state(self, state):
        self._shadowlength_modifier = 1
        if state == "walk":
            self._state = "walk"
            self._body = [self.walkcycle[0]]
            self._hair = [self.walkcycle[1]]
            self._outfit_anim = self._outfit.walkcycle
            self._weapon_anim = []
        elif state == "slash":
            self._state = "slash"
            self._body = [self.slash[0]]
            self._hair = [self.slash[1]]
            self._outfit_anim = self._outfit.slash
            self._weapon_anim = self._equipped_weapon.slash
        elif state == "thrust":
            self._state = "thrust"
            self._body = [self.thrust[0]]
            self._hair = [self.thrust[1]]
            self._outfit_anim = self._outfit.thrust
            self._weapon_anim = self._equipped_weapon.thrust
        elif state == "idle":
            self._state = "idle"
            self._body = [self.walkcycle[0]]
            self._hair = [self.walkcycle[1]]
            self._outfit_anim = self._outfit.walkcycle
            self._weapon_anim = []
        elif state == "bow":
            self._state = "bow"
            self._body = [self.bow[0]]
            self._hair = [self.bow[1]]
            self._outfit_anim = self._outfit.bow
            self._weapon_anim = self._equipped_weapon.bow
        elif state == "dead":
            self._state = "dead"
            self._body = [self.hurt[0]]
            self._hair = [self.hurt[1]]
            self._outfit_anim = self._outfit.hurt
            self._weapon_anim = []
            self._facing = 0
            self._shadowlength_modifier = 0.3
        self._anim_step = 0

    def get_weapon_hit_rect(self):
        if self._facing == 0:
            attac_rect = pygame.Rect(self._position[0] - 5, self._position[1] - self.equipped_weapon.range - 10, 10, self.equipped_weapon.range)
        elif self._facing == 2:
            attac_rect = pygame.Rect(self._position[0] - 5, self._position[1] + 30, 10, self.equipped_weapon.range)
        elif self._facing == 1:
            attac_rect = pygame.Rect(self._position[0] - self.equipped_weapon.range - 10, self._position[1] + 5, self.equipped_weapon.range, 10)
        elif self._facing == 3:
            attac_rect = pygame.Rect(self._position[0] + 10, self._position[1] + 5, self.equipped_weapon.range, 10)
        return attac_rect

    def step(self, day_time, action = None, move_array = np.zeros(4), sprint = False):
        attack_rect = None
        if self._state != "idle":
            self._anim_step += self._anim_speed
            if self._state == "walk":
                if self._anim_step > 8:
                    self._anim_step = 0
            if self._state == "slash":
                if self._anim_step == 4:
                    attack_rect = self.get_weapon_hit_rect()
                if self._anim_step > 5:
                    self._anim_step = 0
                    self.set_state("idle")
            if self._state == "thrust":
                if self._anim_step == 6:
                    attack_rect = self.get_weapon_hit_rect()
                if self._anim_step > 7:
                    self._anim_step = 0
                    self.set_state("idle")
            if self._state == "bow":
                if self._anim_step == 10:
                    self._equipped_weapon.facing = self._facing
                    attack_rect = self.get_weapon_hit_rect()
                if self._anim_step > 11:
                    if action == 4:
                        if self._anim_step > 12:
                            self._anim_step = 4
                    else:
                        self._anim_step = 0
                        self.set_state("idle")
            if self._state == "dead":
                if self._anim_step > 5:
                    self._anim_step = 5
        else:
            self._anim_step = 0

        if sprint and self._state == "walk":
            self._stamina -= 0.005
            if self._stamina > 0:
                self._speed = 5
                self._anim_speed = 1
                self._time_since_sprinting = 0
            else:
                self._speed = 2
                self._anim_speed = 0.5
                self._stamina = 0
        else:
            self._time_since_sprinting += 1
            self._time_since_sprinting = min(self._time_since_sprinting, 200)
            if self._stamina < self._maxstamina:
                self._stamina += self._time_since_sprinting**2*1e-4
            elif self._stamina > self._maxstamina:
                self._stamina = self._maxstamina
            self._speed = 2
            self._anim_speed = 0.5

        movement = np.zeros(2)
        if self._state == "walk":
            if move_array[0]:
                movement[1] = -self._speed
            elif move_array[2]:
                movement[1] = self._speed

            if move_array[1]:
                movement[0] = -self._speed
            elif move_array[3]:
                movement[0] = self._speed

        if self._state != "dead":
            if action == 0:
                # up
                self._facing = 0
                if self._state == "idle":
                    self.set_state("walk")
            elif action == 1:
                # left
                self._facing = 1
                if self._state == "idle":
                    self.set_state("walk")
            elif action == 2:
                # down
                self._facing = 2
                if self._state == "idle":
                    self.set_state("walk")
            elif action == 3:
                # right
                self._facing = 3
                if self._state == "idle":
                    self.set_state("walk")
            elif action == 4:
                if self._state == "idle" or (self._state == "walk" and self._anim_step == 8):
                    self.set_state(self._equipped_weapon.type)
            else:
                if self._state == "walk":
                    self.set_state("idle")

        sprite_y = int(self._facing*self._sprite_size)
        sprite_x = int(self._anim_step)*self._sprite_size

        self._layers = self._body + self._outfit_anim 
        if not self._outfit.has_hood:
            self._layers += self._hair
        self._layers += self._weapon_anim

        player_surf = pygame.Surface((self._sprite_size, self._sprite_size), pygame.SRCALPHA)
        for layer in self._layers:
            player_surf.blit(layer, (0, 0),
                             (sprite_x, sprite_y, self._sprite_size, self._sprite_size))            
        
        hitbox = pygame.Rect(self._position[0] - 12, self._position[1] + 1, 24, 28)

        shadow_state = int(day_time//5)

        if self._shadow == None or self._state != "idle" or shadow_state != self._prev_shadow_state or self._anim_step == 0:
            if shadow_state < 20:
                self._shadow = pygame.transform.flip(pygame.transform.scale(player_surf, (self._sprite_size, int(self._sprite_size*slm[shadow_state]*self._shadowlength_modifier))), 0, 1)
            elif shadow_state < 40:
                self._shadow = pygame.transform.scale(player_surf, (self._sprite_size, int(self._sprite_size*slm[19 - shadow_state]/2*self._shadowlength_modifier)))
            
            if shadow_state >= 40:
                alpha_modifier = 0
            else:
                alpha_modifier = 1.5

            self.color_surface(self._shadow, 50, 50, 50, (150 - 6*abs(20 - shadow_state))*alpha_modifier)

        self._prev_shadow_state = shadow_state

        return self._position, player_surf, [attack_rect, self.equipped_weapon], hitbox, movement, self._shadow

    def set_pos(self, pos):
        self._position = pos

    def take_damage(self, damage):
        if self._state != "dead":
            self._health -= damage
            if self._health <= 0:
                self.set_state("dead")
                self._health = 0
                self._facing = 0


    """ Drawing methods """
    def color_surface(self, surface, red, green, blue, alpha):
        arr = pygame.surfarray.pixels3d(surface)
        arr[:,:,0] = red
        arr[:,:,1] = green
        arr[:,:,2] = blue

        alphas = pygame.surfarray.pixels_alpha(surface)
        alphas[alphas != 0] = alpha


    @property
    def position(self):
        return self._position

    @property
    def equipped_weapon(self):
        return self._equipped_weapon

    @property
    def equipped_outfit(self):
        return self._outfit

    @property
    def health(self):
        return self._health

    @property
    def maxhealth(self):
        return self._maxhealth

    @property
    def stamina(self):
        return self._stamina

    @property
    def maxstamina(self):
        return self._maxstamina