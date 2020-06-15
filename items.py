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
    def __init__(self, name, icon):
        self.name = name
        self.walkcycle = []
        self.hurt = []
        self.slash = []
        self.spellcast = []
        self.thrust = []
        self.bow = []
        self.icon = icon
        self.id = f"{self.__class__.__name__}-{id(self)}"


class Consumable:
    """ Superclass for consumable items """
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.id = f"{self.__class__.__name__}-{id(self)}"


class Structure:
    """ Superclass for structures. Mostly buildings. Structures typically have
    an "inside" and an outside. When the player is outside the inside should
    usually not be rendered.
    """
    def __init__(self, name):
        self.name = name
        self.id = f"{self.__class__.__name__}-{id(self)}"


class StaticItem:
    """ Superclass for map items that do not move """
    def __init__(self, name, surf):
        self.name = name
        self.surf = surf
        self.id = f"{self.__class__.__name__}-{id(self)}"

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

    def step(self):
        self.timer += 1
        x, y = self._position
        if self.direction == 0:
            self._position[1] -= self.speed
            hitbox = pygame.Rect(x - 8, y - 5, 16, 10)
        elif self.direction == 1:
            self._position[0] -= self.speed
            hitbox = pygame.Rect(x - 16, y - 2, 32, 4)
        elif self.direction == 2:
            self._position[1] += self.speed
            hitbox = pygame.Rect(x - 8, y - 5, 16, 10)
        elif self.direction == 3:
            self._position[0] += self.speed
            hitbox = pygame.Rect(x - 16, y - 2, 32, 4)

        return hitbox

    @property
    def position(self):
        return self._position


class Arrow(Projectile):
    def __init__(self, x, y, direction, speed=6, damage=5):
        super().__init__(x, y, direction, speed, damage)
        self.image = ["bow", "WEAPON_arrow"]


class Outfit(Wearable):
    """ Subclass for outfit wearables. """
    def __init__(self, name, icon, has_hood=False, armor=0, durability_hit=0):
        """ Outfit sprites are drawn above character sprites. If has_hood is
        set to True, the character's hair will not be drawn when the character
        is wearing this outfit.
        """
        super().__init__(name, icon)
        self.has_hood = has_hood
        self.armor = armor
        self.durability = 100
        self.durability_hit = durability_hit


class Extra_Item(Wearable):
    """ Subclass for wearables that are drawn behind the character.
    E.g.: The arrow quiver.
    """
    def __init__(self, name, icon):
        super().__init__(name, icon)


class Weapon(Wearable):
    """ Subclass for weapon wearables """
    def __init__(self, name, icon, type_="slash", range_=20, damage=10,
                 durability_hit=0, projectile=None):
        """ type_ determines the animation that will be played on the attacking
        character when the weapon is used.
        
        Keyword arguments:
        type_ -- What kind of weapon this is ('slash', 'thrust', 'bow')
                 (default 'slash')
        range_ -- How far the weapon can hit (default 20)
        damage -- The damage the weapon does when hitting something (default 10)
        durability_hit -- How much durability the weapon loses with each hit
                          (default 0)
        projectile -- Projectile object to create when used. If None, will not
                      make any (default None) and the weapon is considered melee
        """
        super().__init__(name, icon)
        self.type = type_
        self.range = range_
        self.damage = damage
        self.durability = 100
        self.durability_hit = durability_hit
        self.projectile = projectile


class Food(Consumable):
    """ Superclass for consumable foods """
    def __init__(self, name, icon, hunger_add = 1, health_add = 0, stamina_add = 0):
        super().__init__(name, icon)
        self.hunger_add = hunger_add
        self.health_add = health_add
        self.stamina_add = stamina_add
