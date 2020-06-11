import pygame
import time
import os
from pygame.locals import *
import numpy as np

slm = np.logspace(0.3, -0.8, 20) # shadow length modifiers

class Wearable:
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
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.id = f"{self.__class__.__name__}-{id(self)}"


class Structure:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.id = f"{self.__class__.__name__}-{id(self)}"


class Projectile:
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
    def __init__(self, x, y, direction, speed = 3, damage = 5):
        super().__init__(x, y, direction, speed, damage)
        self.image = ["bow", "WEAPON_arrow"]


class Outfit(Wearable):
    def __init__(self, name, icon, has_hood = False, armor = 0, durability_hit = 0):
        super().__init__(name, icon)
        self.has_hood = has_hood
        self.armor = armor
        self.durability = 100
        self.durability_hit = durability_hit


class Weapon(Wearable):
    def __init__(self, name, icon, type_ = "slash", range_ = 20, damage = 10, durability_hit = 0, projectile = None, facing = 0):
        super().__init__(name, icon)
        self.type = type_
        self.range = range_
        self.damage = damage
        self.durability = 100
        self.durability_hit = durability_hit
        self.projectile = projectile
        self.facing = facing


class Food(Consumable):
    def __init__(self, name, icon, hunger_add = 1, health_add = 0, stamina_add = 0):
        super().__init__(name, icon)
        self.hunger_add = hunger_add
        self.health_add = health_add
        self.stamina_add = stamina_add