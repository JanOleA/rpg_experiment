import time

import numpy as np
import pygame
from pygame.locals import *

from items import Weapon, Outfit, Ammo, Quiver, Extra_Item

slm = np.logspace(0.3, -0.8, 20)*0.6 # shadow length modifiers

class Character:
    """ Superclass for all characters """
    def __init__(self, x, y,
                 body_images,
                 starting_outfit,
                 hands = None):
        """ General initialization for characters that move.
        
        Arguments:
        x -- starting x-position
        y -- starting y-position
        body_images -- dictionary containing images for the characters body and
                       hair. Must have the following keys:
                            walkcyckle
                            slash
                            thrust
                            bow
                            hurt
        starting_outfit -- outfit the character starts with, must be Outfit
                           object.
        
        Keyword arguments:
        hands -- Weapon object the character always has. For humans this is
                 typically their hands, which are treated as a Weapon type.
                 (default None)
        """
        self.id = f"{self.__class__.__name__}-{id(self)}"

        self.walkcycle = body_images["walkcycle"]
        self.slash = body_images["slash"]
        self.thrust = body_images["thrust"]
        self.bow = body_images["bow"]
        self.hurt = body_images["hurt"]

        self.behind = None
        self._behind_anim = []

        self._outfit = starting_outfit
        self._outfits = [starting_outfit]

        self._equipped_weapon = None
        self._equipped_ammo = None

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
        self._shadow = None
        self._prev_shadow_state = None
        self._shadowlength_modifier = 1
        self._time_since_sprinting = 0
        self.can_move = True

        if hands is not None:
            self._hands = hands
            self.add_to_inventory(hands)
            self.equip_weapon(hands)

    def add_outfit(self, outfit):
        """ Add an Outfit object to the characters outfit inventory.
        
        Arguments:
        outfit -- the Outfit object to add to the inventory. If it is not the
                  correct type a messagse will be printed to the console.
        """
        if not outfit in self._outfits:
            if isinstance(outfit, Outfit):
                self._outfits.append(outfit)
            else:
                print(f"Attempted to add outfit: {outfit} to character {self}")
                print(f"but {outfit} is type: {type(outfit)}")

    def equip_outfit(self, index):
        """ Equip an outfit from the character's outfit inventory. Sets the
        characters state to idle and resets the animation loop.
        
        Arguments:
        index -- index in the outfit inventory where the outfit is stored.
        """
        self._outfit = self._outfits[index]
        self.set_state("idle")
        self._anim_step = 0

    def equip_weapon(self, key):
        """ Equip a weapon from the characters inventory.
        
        Arguments:
        key -- The key in the inventory dictionary the item is stored at.
               Alternatively the object itself can be passed as the argument, 
               and will be equipped if it exists in the inventory and is a
               Weapon object.
        """
        if key in self._inventory:
            if isinstance(self._inventory[key], Weapon):
                self._equipped_weapon = self._inventory[key]
        else:
            for k, item in self._inventory.items():
                if item == key and isinstance(item, Weapon):
                    self._equipped_weapon = self._inventory[k]

    def equip_ammo(self, key):
        """ Equip an ammunition type from the characters inventory.
        
        Arguments:
        key -- The key in the inventory dictionary the item is stored at.
               Alternatively the object itself can be passed as the argument, 
               and will be equipped if it exists in the inventory and is an
               Ammo object.
        """
        if key in self._inventory:
            if isinstance(self._inventory[key], Ammo):
                self._equipped_ammo = self._inventory[key]
        else:
            for k, item in self._inventory.items():
                if item == key and isinstance(item, Ammo):
                    self._equipped_ammo = self._inventory[k]

    def unequip_ammo(self):
        self._equipped_ammo = None

    def add_to_inventory(self, item):
        """ Add an item to the characters inventory. 
        
        Arguments:
        item -- The object to add to the inventory. If the object is an Outfit
                object it will be added to the outfit list. Otherwise it will
                be added to the inventory dictionary with a key generated from
                its name.
                If the item is an Ammo type and the same type of Ammo already
                exists in the inventory, the number of Ammo in 'item' will be
                added to the object already in the inventory.
        """
        if isinstance(item, Outfit):
            self.add_outfit(item)
            return
        for key, it in self._inventory.items():
            if type(it) == type(item) and isinstance(item, Ammo):
                it.increase_amount(item.amount)
                return
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
        """ Remove an item from the inventory dictionary.
        
        Arguments:
        item -- The item itself or the key to the item in the inventory dictionary.
                If the item is an equipped weapon it will first be unequipped.
                The characters "hands" cannot be removed.
        """
        if item == self._hands:
            return
        if item == self._equipped_weapon:
            self.equip_weapon(self._hands)
        if item in self._inventory:
            del self._inventory[item]
        else:
            for name, inv_item in self._inventory.items():
                if item == inv_item:
                    del self._inventory[name]
                    return

    def remove_outfit(self, item):
        """ Remove an outfit from the outfit list, unless it is the currently
        equipped outfit.

        Arguments:
        item -- The object to remove from the list.
        """
        if item in self._outfits and self._outfit != item:
            self._outfits.remove(item)

    def get_inventory(self):
        return self._inventory

    def get_outfits(self):
        return self._outfits

    def add_extra_item(self, item):
        """ Give the character an 'Extra item'. These are items that are purely 
        cosmetic and carried behind the normal sprite. E.g. arrow quivers. 
        """
        if isinstance(item, Extra_Item):
            self.behind = item
            if self._state == "walk" or self._state == "idle":
                self._behind_anim = item.walkcycle
            elif self._state == "slash":
                self._behind_anim = self.behind.slash
            elif self._state == "thrust":
                self._behind_anim = self.behind.thrust
            elif self._state == "idle":
                self._behind_anim = self.behind.walkcycle
            elif self._state == "bow":
                self._behind_anim = self.behind.bow
            elif self._state == "dead":
                self._behind_anim = self.behind.hurt

    def remove_extra_item(self):
        """ Remove the 'Extra item' from the character if it has one equipped. """
        self.behind = None
        self._behind_anim = []

    def get_weapon_hit_rect(self):
        """ Create and return the pygame rect that is the hitbox from the currently equipped
        weapon.

        Returns:
        attac_rect -- hitbox for weapon strike as pygame Rect object.
        """
        if self._facing == 0:
            attac_rect = pygame.Rect(self._position[0] - 5, self._position[1] - self.equipped_weapon.range - 10, 10, self.equipped_weapon.range)
        elif self._facing == 2:
            attac_rect = pygame.Rect(self._position[0] - 5, self._position[1] + 30, 10, self.equipped_weapon.range)
        elif self._facing == 1:
            attac_rect = pygame.Rect(self._position[0] - self.equipped_weapon.range - 10, self._position[1] + 5, self.equipped_weapon.range, 10)
        elif self._facing == 3:
            attac_rect = pygame.Rect(self._position[0] + 10, self._position[1] + 5, self.equipped_weapon.range, 10)
        return attac_rect

    def set_state(self, state):
        """ Set the current state of the character and reset the animation loop.
        Sets the correct animation files based on the images given in initialization,
        and from the outfit and weapon objects.

        Arguments:
        state -- the state to set the character to. The possible options are:
                 walk - walking
                 slash - attacking with a slashing weapon (sword, dagger, etc.)
                 thrust - attacking with a thrusting weapon (spear, etc.)
                 idle - standing still
                 bow - attacking with a bow
                 dead -- dying/dead

        """
        self._shadowlength_modifier = 1
        if state == "walk":
            self._state = "walk"
            self._body = [self.walkcycle[0]]
            self._hair = [self.walkcycle[1]]
            self._outfit_anim = self._outfit.walkcycle
            self._weapon_anim = []
            if self.behind is not None:
                self._behind_anim = self.behind.walkcycle
        elif state == "slash":
            self._state = "slash"
            self._body = [self.slash[0]]
            self._hair = [self.slash[1]]
            self._outfit_anim = self._outfit.slash
            self._weapon_anim = self._equipped_weapon.slash
            if self.behind is not None:
                self._behind_anim = self.behind.slash
        elif state == "thrust":
            self._state = "thrust"
            self._body = [self.thrust[0]]
            self._hair = [self.thrust[1]]
            self._outfit_anim = self._outfit.thrust
            self._weapon_anim = self._equipped_weapon.thrust
            if self.behind is not None:
                self._behind_anim = self.behind.thrust
        elif state == "idle":
            self._state = "idle"
            self._body = [self.walkcycle[0]]
            self._hair = [self.walkcycle[1]]
            self._outfit_anim = self._outfit.walkcycle
            self._weapon_anim = []
            if self.behind is not None:
                self._behind_anim = self.behind.walkcycle
        elif state == "bow":
            self._state = "bow"
            self._body = [self.bow[0]]
            self._hair = [self.bow[1]]
            self._outfit_anim = self._outfit.bow
            self._weapon_anim = self._equipped_weapon.bow
            if self.behind is not None:
                self._behind_anim = self.behind.bow
        elif state == "dead":
            self._state = "dead"
            self._body = [self.hurt[0]]
            self._hair = [self.hurt[1]]
            self._outfit_anim = self._outfit.hurt
            self._weapon_anim = []
            self._facing = 0
            self._shadowlength_modifier = 0.3
            if self.behind is not None:
                self._behind_anim = self.behind.hurt
        self._anim_step = 0

    def set_pos(self, pos):
        """ Set the player position. Stores it as a Numpy array.
        
        Arguments:
        pos -- iterable containing the position as x,y coordinates.
        """
        self._position = np.array(pos)

    def take_damage(self, damage):
        """ Reduce the characters health, and if it reaches 0 set the state to
        dead.
        
        Arguments:
        damage -- how much damage to inflict on the character.
        """
        if self._state != "dead":
            self._health -= damage
            if self._health <= 0:
                self.set_state("dead")
                self.can_move = False
                self._health = 0
                self._facing = 0

    def attack(self):
        """ Character attack, if the current state allows it. """
        if self._state == "idle" or (self._state == "walk" and self._anim_step == 8):
            self.set_state(self._equipped_weapon.type)

    def color_surface(self, surface, red, green, blue, alpha):
        """ Color a pygame Surface in the given color.
        
        Arguments:
        surface -- the pygame Surface to color.
        red -- red value to give the pixels.
        green -- green value to give the pixels.
        blue -- blue value to give the pixels.
        alpha -- alpha value to give the pixels. Will be applied to all pixels
                 in the surface that do not have an alpha value of 0.
        """
        arr = pygame.surfarray.pixels3d(surface)
        arr[:,:,0] = red
        arr[:,:,1] = green
        arr[:,:,2] = blue

        alphas = pygame.surfarray.pixels_alpha(surface)
        alphas[alphas != 0] = alpha


    """ Step forwards methods """
    def check_state(self, action = None):
        """ Checks the character state, ammunition remaining and sets the
        appropriate animation step. Creates the attack rect (hitbox) if the
        character is attacking.
        """
        if self.equipped_ammo is not None:
            if self.equipped_ammo.amount <= 0:
                equipped_ammo = self._equipped_ammo
                self.unequip_ammo()
                self.remove_from_inventory(equipped_ammo)
                remove_quiver = True
                for key, item in self._inventory.items():
                    if isinstance(item, Ammo):
                        self.equip_ammo(key)
                        remove_quiver = False
                        break
                if remove_quiver and isinstance(self.behind, Quiver):
                    self.remove_extra_item()

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

        return attack_rect

    def movement(self):
        """ Calculates the movement in the current step based on input or what
        the NPC knows. Should also set the self._facing variable for correct
        sprite animation.
        """
        movement = np.zeros(2)
        return movement

    def make_sprite(self, day_time):
        """ Takes the current state of the character and creates and returns the
        sprite, hitbox and shadow.
        """
        sprite_y = int(self._facing*self._sprite_size)
        sprite_x = int(self._anim_step)*self._sprite_size

        self._layers = self._behind_anim + self._body + self._outfit_anim 
        if not self._outfit.has_hood:
            self._layers += self._hair
        self._layers += self._weapon_anim
        if self.equipped_ammo is not None and self._state == "bow":
            self._layers += self.equipped_ammo.anim_image

        char_surf = pygame.Surface((self._sprite_size, self._sprite_size), pygame.SRCALPHA)
        for layer in self._layers:
            char_surf.blit(layer, (0, 0),
                           (sprite_x, sprite_y, self._sprite_size, self._sprite_size))            
        
        hitbox = pygame.Rect(self._position[0] - 12, self._position[1] + 1, 24, 28)

        if self._state == "dead":
            hitbox = pygame.Rect((-1000, -1000, 1, 1))

        shadow_state = int(day_time//5)

        if self._shadow == None or self._state != "idle" or shadow_state != self._prev_shadow_state or self._anim_step == 0:
            if shadow_state < 20:
                self._shadow = pygame.transform.flip(pygame.transform.scale(char_surf, (self._sprite_size, int(self._sprite_size*slm[shadow_state]*self._shadowlength_modifier))), 0, 1)
            elif shadow_state < 40:
                self._shadow = pygame.transform.scale(char_surf, (self._sprite_size, int(self._sprite_size*slm[19 - shadow_state]/2*self._shadowlength_modifier)))
            
            if shadow_state >= 40:
                alpha_modifier = 0
            else:
                alpha_modifier = 1.5

            self.color_surface(self._shadow, 50, 50, 50, (150 - 6*abs(20 - shadow_state))*alpha_modifier)

        self._prev_shadow_state = shadow_state

        return char_surf, hitbox

    def step(self, day_time):
        """ Main method for character control. Runs on every frame.
        
        Arguments:
        day_time -- The current day_time of the game. day_time runs from
                    0 to 400, with 0 being sunrise and 200 being sunset.

        Returns:
        self._position -- the position of the character in x,y coordinates.
        char_surf -- the pygame Surface for the character.
        [attack_rect, self.equipped_weapon] -- list containing the weapon strike
                                               hitbox and the currently equipped
                                               weapon. If the character is not
                                               attacking currently the hitbox
                                               will be None.
        hitbox -- the characters hitbox.
        movement -- the character current movement as dx,dy coordinates.
        self._shadow -- the characters shadow pygame Surface.
        """
        attack_rect = self.check_state()
        movement = self.movement()
        char_surf, hitbox = self.make_sprite(day_time)
        
        return self._position, char_surf, [attack_rect, self.equipped_weapon], hitbox, movement, self._shadow


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
    def equipped_ammo(self):
        return self._equipped_ammo

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


class NPC(Character):
    """ Class for non-player characters. See superclass for detailed docstrings. """
    def __init__(self, x, y,
                 body_images,
                 starting_outfit,
                 hands):
        super().__init__(x, y,
                         body_images,
                         starting_outfit,
                         hands)
                        
        self._y_shift = 0
        self._healthbar = None
        self._last_facing_change = time.time() - 0.3
        self._last_hit_timer = 60
        self.status = "passive"

    def take_damage(self, damage):
        if self._state != "dead":
            self._health -= damage
            if self._health <= 0:
                self.set_state("dead")
                self.can_move = False
                self._health = 0
                self._facing = 0
            self._last_hit_timer = 0

    def movement(self, target_position):
        movement = np.zeros(2)
        if self._state != "dead":
            dir_to_target = target_position - self._position
            dist_to_target = np.linalg.norm(dir_to_target)
            dir_to_target /= dist_to_target

            if dist_to_target > 32:
                movement = np.round(dir_to_target*self._speed)
            else:
                self.attack()

            now_time = time.time()

            if movement[1] < -0.5:
                # up
                if now_time - self._last_facing_change > 0.3:
                    self._facing = 0
                    self._last_facing_change = time.time()
                if self._state == "idle":
                    self.set_state("walk")
            elif movement[0] < -0.5:
                # left
                if now_time - self._last_facing_change > 0.3:
                    self._facing = 1
                    self._last_facing_change = time.time()
                if self._state == "idle":
                    self.set_state("walk")
            elif movement[1] > 0.5:
                # down
                if now_time - self._last_facing_change > 0.3:
                    self._facing = 2
                    self._last_facing_change = time.time()
                if self._state == "idle":
                    self.set_state("walk")
            elif movement[0] > 0.5:
                # right
                if now_time - self._last_facing_change > 0.3:
                    self._facing = 3
                    self._last_facing_change = time.time()
                if self._state == "idle":
                    self.set_state("walk")
            else:
                if self._state == "walk":
                    self.set_state("idle")

        
        return movement

    def step(self, day_time, player_position):
        """ Main method for controlling the character. Runs on every frame. """
        attack_rect = self.check_state()
        movement = self.movement(player_position)
        char_surf, hitbox = self.make_sprite(day_time)

        if self._last_hit_timer < 60:
            self._last_hit_timer += 1
            health = pygame.Rect(self._position[0] - 16, self._position[1] - 32, int(self._health/self._maxhealth*32), 5)
            health_bg = pygame.Rect(self._position[0] - 16, self._position[1] - 32, 32, 5)
            self._healthbar = [health, health_bg]
        else:
            self._healthbar = None

        if self._state == "dead":
            self._y_shift = 25
        
        return (self._position, char_surf,
                [attack_rect, self.equipped_weapon],
                hitbox, movement, self._shadow,
                self._y_shift, self._healthbar)


class Player(Character):
    """ Class for the player character. See superclass for detailed docstrings. """
    def __init__(self, x, y,
                 body_images,
                 starting_outfit,
                 hands):
        super().__init__(x, y,
                         body_images,
                         starting_outfit,
                         hands)

    def movement(self, action, move_array, sprint):
        """ Handles the movement calculation based on input by the player.
        
        Arguments:
        action -- what action the player currently wants the character to do.
                  The options are:
                      0 - move up
                      1 - move left
                      2 - move down
                      3 - move right
                      4 - attack
        move_array -- iterable with 1's for the directions the player wants to move
                      and 0 otherwise:
                          move_array[0] == 1 -> up
                          move_array[1] == 1 -> left
                          move_array[2] == 1 -> down
                          move_array[3] == 1 -> right
        sprint -- boolean, whether or not the player currently wants the
                  character to sprint.
        """
        if sprint and self._state == "walk":
            self._stamina -= 0.2
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
                self._facing = 0
            elif move_array[2]:
                movement[1] = self._speed
                self._facing = 2

            if move_array[1]:
                movement[0] = -self._speed
                self._facing = 1
            elif move_array[3]:
                movement[0] = self._speed
                self._facing = 3

        if self._state != "dead":
            if action == 0:
                # up
                if self._state == "idle":
                    self._facing = 0
                    self.set_state("walk")
            elif action == 1:
                # left
                if self._state == "idle":
                    self._facing = 1
                    self.set_state("walk")
            elif action == 2:
                # down
                if self._state == "idle":
                    self._facing = 2
                    self.set_state("walk")
            elif action == 3:
                # right
                if self._state == "idle":
                    self._facing = 3
                    self.set_state("walk")
            elif action == 4:
                self.attack()
            else:
                if self._state == "walk":
                    self.set_state("idle")
        
        return movement

    def step(self, day_time, action = None, move_array = np.zeros(4), sprint = False):
        """ Main method for controlling the player. Runs on every frame. """
        attack_rect = self.check_state(action)
        movement = self.movement(action, move_array, sprint)
        char_surf, hitbox = self.make_sprite(day_time)
        
        return self._position, char_surf, [attack_rect, self.equipped_weapon], hitbox, movement, self._shadow


class Combat_Dummy:
    def __init__(self, x, y, images):
        self.id = f"{self.__class__.__name__}-{id(self)}"
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
        self.can_move = False

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

    def step(self, day_time, player_position):
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

        return self._position, character_surf, [None, None], self._hitbox, np.zeros(2), self._shadow, self._y_shift, self._healthbar

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