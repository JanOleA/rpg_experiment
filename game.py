import numpy as np
import sys
import os
import glob
import pygame
from pygame.locals import *
from characters import Player, Combat_Dummy
from items import Weapon, Outfit


class Game:
    def __init__(self, AA_text = True, draw_hitboxes = False):
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
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)

        self.AA_text = AA_text
        self._draw_hitboxes = draw_hitboxes

        self._circle_cache = {}

    
    def load_image_folder(self, folder_name, dict):
        for item in glob.glob(os.path.join(os.getcwd(),
                                           "sprites",
                                           "wulax",
                                           "png",
                                           folder_name,
                                           "*.png")):
            
            image = pygame.image.load(item)
            image.convert_alpha()
            item_name = item.split("\\")[-1].split(".p")[0]
            
            dict[item_name] = image

        for item in glob.glob(os.path.join(os.getcwd(),
                                           "sprites",
                                           "wulax",
                                           "png",
                                           "64x64",
                                           folder_name,
                                           "*.png")):
            
            image = pygame.image.load(item)
            image.convert_alpha()
            item_name = item.split("\\")[-1].split(".p")[0]
            
            dict[item_name] = image


    def get_icon(self, name):
        img = pygame.image.load(os.path.join(os.getcwd(),
                                             "sprites",
                                             "icons",
                                             f"{name}.png"))
        img.convert_alpha()
        return img


    def setup_outfits(self):
        robe_icon = self.get_icon("robe")
        robe = Outfit("Unhooded robe", robe_icon, armor = 1)
        robe.walkcycle = [self._walkcycle_images["FEET_shoes_brown"],
                          self._walkcycle_images["LEGS_robe_skirt"],
                          self._walkcycle_images["TORSO_robe_shirt_brown"]]
        robe.slash = [self._slash_images["FEET_shoes_brown"],
                      self._slash_images["LEGS_robe_skirt"],
                      self._slash_images["TORSO_robe_shirt_brown"]]
        robe.thrust = [self._thrust_images["FEET_shoes_brown"],
                       self._thrust_images["LEGS_robe_skirt"],
                       self._thrust_images["TORSO_robe_shirt_brown"]]

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

        self.outfits = [robe, platearmor]
        self.robe = robe
        self.platearmor = platearmor


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

        self._screen.blit(self.loadingtext, (5,5))
        pygame.display.flip()
        print("Loading...")

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

        self.setup_outfits()

        dagger_icon = self.get_icon("dagger")
        dagger = Weapon("Dagger", dagger_icon, damage = 10)
        dagger.slash = [self._slash_images["WEAPON_dagger"]]

        spear_icon = self.get_icon("spear")
        spear = Weapon("Spear", spear_icon, "thrust", range_ = 30, damage = 20)
        spear.thrust = [self._thrust_images["WEAPON_spear"]]

        hands_icon = self.get_icon("hands")
        hands = Weapon("Hands", hands_icon, "slash", damage = 2)

        self.player = Player(300, 300,
                             self._walkcycle_images,
                             self._slash_images,
                             self._thrust_images,
                             self.robe)

        self.player.add_outfit(self.platearmor)

        self.player.add_to_inventory(hands)
        self.player.equip_weapon("Hands")
        self.player.add_to_inventory(dagger)
        self.player.add_to_inventory(spear)

        self.npcs = []
        self.npcs.append(Combat_Dummy(self._combat_dummy_images["BODY_animation"], self._combat_dummy_images["BODY_death"], 700, 60))

        for i in range(9):
            self.npcs.append(Combat_Dummy(self._combat_dummy_images["BODY_animation"], self._combat_dummy_images["BODY_death"], np.random.randint(350,900), np.random.randint(0,700)))

        self._paused = False
        self._inventory = False
        self._pausebg = None
        self._inv_x = 0
        self._inv_y = 0
        self._hover_item = None

        self._day_time = 0

        pygame.mixer.music.play(loops = -1)
        pygame.mixer.music.set_volume(0.2)


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
                    self._paused = True
                    self._inventory = True
                    self._pausebg = self._screen.copy()


    def loop(self):
        self.attack_rects = {}
        self.hitboxes = {}
        if not self._paused:
            """ Unpaused loop """
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
            
            self._player_data = self.player.step(action, move_array, key_states[pygame.K_LSHIFT])

            if self._player_data[2] is not None:
                self.attack_rects[self.player] = self._player_data[2]

            self.hitboxes[self.player] = self._player_data[3]

            self._npc_datas = []

            for npc in self.npcs:
                npc_data = npc.step()
                self.hitboxes[npc] = npc_data[3]
                self._npc_datas.append(npc_data)

            for actor, attack_rect in self.attack_rects.items():
                attack_rect, attack_weapon = attack_rect
                for target, hitbox in self.hitboxes.items():
                    if actor == target or attack_rect is None:
                        continue
                    if attack_rect.colliderect(hitbox):
                        target.take_damage(attack_weapon.damage)

            candidate_pos = self._player_data[0].copy()
            playerhitbox = self.hitboxes[self.player]
            movement_x = self._player_data[4][0]
            movement_y = self._player_data[4][1]

            """ Collision testing the player """

            if movement_x > 0:
                for target, hitbox in self.hitboxes.items():
                    if target == self.player:
                        continue
                    candidate_hitbox = playerhitbox.move(movement_x + 1, 0)
                    if candidate_hitbox.colliderect(hitbox):
                        movement_x = 0
            elif movement_x < 0:
                for target, hitbox in self.hitboxes.items():
                    if target == self.player:
                        continue
                    candidate_hitbox = playerhitbox.move(movement_x - 1, 0)
                    if candidate_hitbox.colliderect(hitbox):
                        movement_x = 0

            if movement_y > 0:
                for target, hitbox in self.hitboxes.items():
                    if target == self.player:
                        continue
                    candidate_hitbox = playerhitbox.move(0, movement_y + 1)
                    if candidate_hitbox.colliderect(hitbox):
                        movement_y = 0
            elif movement_y < 0:
                for target, hitbox in self.hitboxes.items():
                    if target == self.player:
                        continue
                    candidate_hitbox = playerhitbox.move(0, movement_y - 1)
                    if candidate_hitbox.colliderect(hitbox):
                        movement_y = 0

            candidate_pos[0] += movement_x
            candidate_pos[1] += movement_y

            self.player.set_pos(candidate_pos)
            while candidate_pos[0] - self._cam_x >= self._width - 200:
                self._cam_x += abs(movement_x)
            while candidate_pos[1] - self._cam_y >= self._height - 200:
                self._cam_y += abs(movement_y)
            while candidate_pos[0] - self._cam_x <= 200:
                self._cam_x -= abs(movement_x)
            while candidate_pos[1] - self._cam_y <= 200:
                self._cam_y -= abs(movement_y)
        else:
            """ Paused loop """
            mouse_pos = pygame.mouse.get_pos()
            self._inv_x = (mouse_pos[0] - 32)//64
            self._inv_y = (mouse_pos[1] - 64)//64

        self._clock.tick_busy_loop(30)
        self.fps = self._clock.get_fps()


    def render(self):
        cam_x = max(self._cam_x, 0)
        cam_y = max(self._cam_y, 0)
        campos = np.array([cam_x, cam_y])
        if not self._paused:
            self._screen.blit(self._grass_bg, (0 - cam_x, 0 - cam_y))

            """ get player surfs """
            p_position = self._player_data[0]
            player_surf = self._player_data[1]
            sprite_size = player_surf.get_width()

            shadows = {}
            character_surfs = []
            character_positions = []
            yshifts = []
            healthbars = []

            shadow = pygame.transform.flip(pygame.transform.scale(player_surf, (sprite_size, sprite_size//2)), 0, 1)
            self.color_surface(shadow, 50, 50, 50, 150)
            shadows[shadow] = (p_position[0] - sprite_size//2, p_position[1] + sprite_size//2 - 6)
            character_surfs.append(player_surf)
            character_positions.append([p_position[0] - sprite_size//2, p_position[1] - sprite_size//2])
            yshifts.append(0)

            """ get NPC surfs """

            for npc_data in self._npc_datas:
                npc_position = npc_data[0]
                npc_surf = npc_data[1]
                yshifts.append(npc_data[4])
                shadow = npc_data[2]
                shadow.set_alpha(50)

                if npc_data[5] is not None:
                    healthbars.append(npc_data[5])

                shadows[shadow] = (npc_position[0] - sprite_size//2, npc_position[1] + sprite_size//2 - 6)

                character_surfs.append(npc_surf)
                character_positions.append([npc_position[0] - sprite_size//2, npc_position[1] - sprite_size//2])

            character_surfs = np.array(character_surfs)
            character_positions = np.array(character_positions)
            yshifts = np.array(yshifts)

            inds = character_positions[:,1].argsort()
            
            character_surfs = character_surfs[inds]
            character_positions = character_positions[inds]
            yshifts = yshifts[inds]

            """ Draw shadows """
            for shadow, pos in shadows.items():
                pos = np.array(pos) - campos
                self._screen.blit(shadow, pos)

            if self._draw_hitboxes:
                for a, hitbox in self.hitboxes.items():
                    hitbox.move_ip(-cam_x, -cam_y)
                    pygame.draw.rect(self._screen, self.WHITE, hitbox)

            """ Draw characters """
            for character_surf, pos, yshift in zip(character_surfs, character_positions, yshifts):
                pos[1] += yshift
                pos = pos.astype(int) - campos
                self._screen.blit(character_surf, pos)

            """ Draw healthbars """
            for healthbar in healthbars:
                bg = healthbar[1]
                fg = healthbar[0]
                fg.move_ip(-cam_x, -cam_y)
                bg.move_ip(-cam_x, -cam_y)
                pygame.draw.rect(self._screen, self.RED, bg)
                if fg.width > 0:
                    pygame.draw.rect(self._screen, self.GREEN, fg)


        if self._paused:
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
    game = Game()
    game.execute()




