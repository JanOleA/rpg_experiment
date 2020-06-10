import pygame
import time
from pygame.locals import *


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



class Outfit(Wearable):
    def __init__(self, name, icon, has_hood = False, armor = 0, durability_hit = 0):
        super().__init__(name, icon)
        self.has_hood = has_hood
        self.armor = armor
        self.durability = 100
        self.durability_hit = durability_hit


class Weapon(Wearable):
    def __init__(self, name, icon, type_ = "slash", range_ = 20, damage = 10, durability_hit = 0):
        super().__init__(name, icon)
        self.type = type_
        self.range = range_
        self.damage = damage
        self.durability = 100
        self.durability_hit = durability_hit


class Food(Consumable):
    def __init__(self, name, icon, hunger_add = 1, health_add = 0, stamina_add = 0):
        super().__init__(name, icon)
        self.hunger_add = hunger_add
        self.health_add = health_add
        self.stamina_add = stamina_add