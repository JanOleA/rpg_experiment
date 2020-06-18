import time
import os

import pygame
from pygame.locals import *
import numpy as np

slm = np.logspace(0.3, -0.8, 20)*0.6 # shadow length modifiers


class Wearable:
    """ Superclass for wearable items. These typically add some sprite to the
    wearer. Sprites are contained in the lists. Lists are named after which
    animation the sprite contains.
    """
    def __init__(self, name, icon, looticon = None):
        self.name = name
        self.walkcycle = []
        self.hurt = []
        self.slash = []
        self.spellcast = []
        self.thrust = []
        self.bow = []
        self.icon = icon
        if looticon is None:
            self.looticon = icon
        else:
            self.looticon = looticon
        self.id = f"{self.__class__.__name__}-{id(self)}"
        self._lootname = "some clothes"

    @property
    def lootname(self):
        return self._lootname


class Consumable:
    """ Superclass for consumable items """
    def __init__(self, name, icon, looticon = None):
        self.name = name
        self.icon = icon
        if looticon is None:
            self.looticon = icon
        else:
            self.looticon = looticon
        self.id = f"{self.__class__.__name__}-{id(self)}"
        self._lootname = "something to eat"

    @property
    def lootname(self):
        return self._lootname


class Ammo:
    """ Superclass for ammunition items """
    def __init__(self, name, icon, looticon = None, amount = 1):
        self.name = name
        self.icon = icon
        if looticon is None:
            self.looticon = icon
        else:
            self.looticon = looticon
        self.id = f"{self.__class__.__name__}-{id(self)}"
        self._projectile_type = Arrow
        self._amount = amount
        self.anim_image = []
        self._lootname = "some ammo"

    def reduce_amount(self, amount = 1):
        self._amount -= amount

    def increase_amount(self, amount = 1):
        self._amount += amount

    
    @property
    def amount(self):
        return self._amount

    @property
    def projectile_type(self):
        return self._projectile_type

    @property
    def lootname(self):
        return self._lootname


class Projectile:
    """ Superclass for projectiles. Projectiles move across the map and damage
    characters they hit.

    Subclasses should have a 'self.init' parameter indicating where the image
    can be found in the games image dictionary. E.g.: the arrow can be found in
    Game._images['bow']['WEAPON_arrow'], so the arrow subclass has:
    self.image = ['bow', 'WEAPON_arrow']
    """
    def __init__(self, x, y, direction, speed, damage):
        self._position = np.array([x, y])
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.timer = 0
        self.hitbox = pygame.Rect(x,y,1,1)

    def step(self):
        self.timer += 1
        x, y = self._position
        if self.direction == 0:
            self._position[1] -= self.speed
            self.hitbox = pygame.Rect(x - 8, y - 18, 16, 10)
        elif self.direction == 1:
            self._position[0] -= self.speed
            self.hitbox = pygame.Rect(x - 27, y + 7, 32, 4)
        elif self.direction == 2:
            self._position[1] += self.speed
            self.hitbox = pygame.Rect(x - 8, y + 8, 16, 10)
        elif self.direction == 3:
            self._position[0] += self.speed
            self.hitbox = pygame.Rect(x - 5, y + 7, 32, 4)

        return self.hitbox

    @property
    def position(self):
        return self._position


class Loot:
    """ Loot that the player can pick up. """
    def __init__(self, x, y, item, duration = 60):
        """ Defines the loot. 
        
        Arguments:
        x -- x-position in the map.
        y -- y-position in the map.
        item -- Object given to the player when the loot picked up.

        Keyword arguments:
        duration -- How many seconds the loot remains on the map. If 0 will remain
                    forever (default 60)
        """
        self._x = x
        self._y = y
        self._item = item
        self._icon = item.looticon
        self._position = np.array([x, y])
        self._duration = duration
        self._spawn_time = time.time()
        self.remove = False # if set to True, the loot will be removed from the
                            # map at first opportunity

    def step(self):
        if self._duration > 0:
            if time.time() - self._spawn_time > self._duration:
                self.remove = True


    @property
    def give_item(self):
        return self._item

    @property
    def give_item_name(self):
        return self._item.lootname
    
    @property
    def position(self):
        return self._position

    @property
    def image(self):
        return self._icon


class Arrow(Projectile):
    def __init__(self, x, y, direction, speed=6, damage=5):
        super().__init__(x, y, direction, speed, damage)
        self.image = ["bow", "WEAPON_arrow"]


class Outfit(Wearable):
    """ Subclass for outfit wearables. """
    def __init__(self, name, icon, looticon = None, has_hood=False, armor=0, durability_hit=0, lootname = "some clothes"):
        """ Outfit sprites are drawn above character sprites. If has_hood is
        set to True, the character's hair will not be drawn when the character
        is wearing this outfit.
        """
        super().__init__(name, icon, looticon)
        self.has_hood = has_hood
        self.armor = armor
        self.durability = 100
        self.durability_hit = durability_hit
        self._lootname = lootname


class Extra_Item(Wearable):
    """ Subclass for wearables that are drawn behind the character.
    E.g.: The arrow quiver.
    """
    def __init__(self, name, icon, looticon = None):
        super().__init__(name, icon, looticon)


class Quiver(Extra_Item):
    def __init__(self, name, icon, looticon = None):
        super().__init__(name, icon, looticon)


class Weapon(Wearable):
    """ Subclass for weapon wearables """
    def __init__(self, name, icon, looticon = None, type_="slash", range_=20, damage=10,
                 durability_hit=0, ranged=False, lootname = "a weapon"):
        """ type_ determines the animation that will be played on the attacking
        character when the weapon is used.
        
        Keyword arguments:
        type_ -- What kind of weapon this is ('slash', 'thrust', 'bow')
                 (default 'slash')
        range_ -- How far the weapon can hit (default 20)
        damage -- The damage the weapon does when hitting something (default 10)
        durability_hit -- How much durability the weapon loses with each hit
                          (default 0)
        ranged -- if True, is a ranged weapon (default False) 
        """
        super().__init__(name, icon, looticon)
        self.type = type_
        self.range = range_
        self.damage = damage
        self.durability = 100
        self.durability_hit = durability_hit
        self.ranged = ranged
        self._lootname = lootname


class Food(Consumable):
    """ Superclass for consumable foods """
    def __init__(self, name, icon, looticon = None, hunger_add = 1, health_add = 0, stamina_add = 0, lootname = "some food"):
        super().__init__(name, icon, looticon)
        self.hunger_add = hunger_add
        self.health_add = health_add
        self.stamina_add = stamina_add
        self._lootname = lootname


class ArrowAmmo(Ammo):
    def __init__(self, name, icon, looticon = None, amount = 1):
        super().__init__(name, icon, looticon, amount)
        self._lootname = "some arrows"
        