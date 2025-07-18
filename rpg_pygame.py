#!/usr/bin/env python
print("--- RUNNING PYGAME VERSION ---")
import random
import os
import json
import pygame
from collections import deque

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 32
MAP_WIDTH = 25 
MAP_HEIGHT = 20
ROOM_MAX_SIZE = 8
ROOM_MIN_SIZE = 4
MAX_ROOMS = 12
MAX_DUNGEON_LEVEL = 5
HIGHSCORE_FILE = "rpg_highscores.json"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0) # For selection highlight

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python RPG Adventure")

# --- Font Setup ---
try:
    font = pygame.font.Font("C:/Windows/Fonts/seguiemj.ttf", 28)
except FileNotFoundError:
    print("Warning: Segoe UI Emoji font not found. Using default font.")
    font = pygame.font.Font(None, 32)

# --- Asset Loading ---
script_dir = os.path.dirname(os.path.abspath(__file__))


def load_sprite(path, size=(TILE_SIZE, TILE_SIZE)):
    try:
        sprite = pygame.image.load(os.path.join(script_dir, path)).convert_alpha()
        return pygame.transform.scale(sprite, size)
    except pygame.error:
        print(f"Error: Cannot load sprite '{path}'.")
        surface = pygame.Surface(size)
        surface.fill(RED)
        return surface

# --- Golden UI Assets ---
from golden_ui_loader import load_ui_elements
UI_ELEMENTS = load_ui_elements(os.path.join(script_dir, "ui_elements"), scale=2)

# Use golden backgrounds and panels

# Use UI_ELEMENTS for backgrounds and panels
gold_background = UI_ELEMENTS.get("background") or UI_ELEMENTS.get("main_bg")
gold_panel = UI_ELEMENTS.get("panel") or UI_ELEMENTS.get("panel_bg")
ui_panel_background = gold_panel

# Find a button image from UI_ELEMENTS
def get_button_images():
    # Try common keys
    for key in ["button", "button_001", "button_002", "button_003", "button_004", "button_005"]:
        if key in UI_ELEMENTS:
            # Try to find a hover variant
            hover_key = key + "_hover"
            hover_img = UI_ELEMENTS.get(hover_key, UI_ELEMENTS[key])
            return UI_ELEMENTS[key], hover_img
    # Fallback: use any image that looks like a button
    for k, v in UI_ELEMENTS.items():
        if "button" in k:
            return v, v
    # Fallback: use panel
    return gold_panel, gold_panel
button_img, button_img_hover = get_button_images()



# --- Button Class ---
class Button:
    def __init__(self, x, y, text, image, hover_image=None):
        self.image = image
        self.hover_image = hover_image if hover_image else image
        self.text = text
        self.width = image.get_width()
        self.height = image.get_height()
        # Center the button at (x, y)
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.is_hovered = False

    def draw(self, surface):
        current_image = self.hover_image if self.is_hovered else self.image
        surface.blit(current_image, self.rect.topleft)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

# --- Sprite Definitions ---
SPRITE_PATH = os.path.join("assets", "crawl-tiles Oct-5-2010")
SPRITES = {
    "player": load_sprite(os.path.join(SPRITE_PATH, "player/base/human_m.png")),
    "warrior": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/orc_warrior.png")),
    "mage": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/deep_elf_mage.png")),
    "archer": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/deep_elf_master_archer.png")),
    "goblin": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/goblin.png")),
    "orc": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/orc.png")),
    "troll": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/troll.png")),
    "dragon": load_sprite(os.path.join(SPRITE_PATH, "dc-mon/dragon.png")),
    "potion": load_sprite(os.path.join(SPRITE_PATH, "item/potion/i-heal.png")),
    "weapon": load_sprite(os.path.join(SPRITE_PATH, "item/weapon/short_sword1.png")),
    "armor": load_sprite(os.path.join(SPRITE_PATH, "item/armour/leather_armour1.png")),
    "wall": load_sprite(os.path.join(SPRITE_PATH, "dc-dngn/wall/brick_brown0.png")),
    "floor": load_sprite(os.path.join(SPRITE_PATH, "dc-dngn/floor/cobble_blood1.png")),
    "stairs": load_sprite(os.path.join(SPRITE_PATH, "dc-dngn/gateways/stone_stairs_down.png")),
}


# --- Sound Assets ---
music_loaded = False
try:
    pygame.mixer.music.load(os.path.join("assets", "music.ogg"))
    music_loaded = True
    sword_sound = pygame.mixer.Sound(os.path.join("assets", "sword.wav"))
    magic_sound = pygame.mixer.Sound(os.path.join("assets", "magic.wav"))
    arrow_sound = pygame.mixer.Sound(os.path.join("assets", "arrow.wav"))
    damage_sound = pygame.mixer.Sound(os.path.join("assets", "damage.wav"))
except pygame.error:
    print("Warning: Could not load sound assets. Game will run without sound.")
    sword_sound = None
    magic_sound = None
    arrow_sound = None
    damage_sound = None

# --- Character Classes ---
CLASSES = {
    "warrior": {"hp": 120, "attack": 15, "defense": 10, "sprite": SPRITES["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 80, "attack": 20, "defense": 5, "sprite": SPRITES["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 100, "attack": 12, "defense": 8, "sprite": SPRITES["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
    "goblin": {"hp": 30, "attack": 8, "defense": 2, "xp": 50, "sprite": SPRITES["goblin"]},
    "orc": {"hp": 50, "attack": 12, "defense": 4, "xp": 100, "sprite": SPRITES["orc"]},
    "troll": {"hp": 80, "attack": 15, "defense": 6, "xp": 150, "sprite": SPRITES["troll"]},
    "dragon": {"hp": 250, "attack": 25, "defense": 15, "xp": 1000, "sprite": SPRITES["dragon"]}
}

# --- Items ---
class Item:
    def __init__(self, name, sprite):
        self.name = name
        self.sprite = sprite

class Potion(Item):
    def __init__(self, name, hp_gain):
        super().__init__(name, SPRITES["potion"])
        self.hp_gain = hp_gain

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.hp_gain)
        return f'{target.name} used {self.name} and gained {self.hp_gain} HP.'

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, SPRITES["weapon"])
        self.attack_bonus = attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus):
        super().__init__(name, SPRITES["armor"])
        self.defense_bonus = defense_bonus

# --- Pre-defined Items ---
WEAPONS = [
    Weapon("Dagger", 3),
    Weapon("Short Sword", 5),
    Weapon("Long Sword", 7),
    Weapon("Battle Axe", 10)
]

ARMOR = [
    Armor("Leather Armor", 3),
    Armor("Chainmail", 5),
    Armor("Plate Armor", 7)
]

# --- Entities ---
class Entity:
    def __init__(self, x, y, name, hp, attack, defense, sprite):
        self.x = x
        self.y = y
        self.name = name
        self.base_attack = attack
        self.base_defense = defense
        self.max_hp = hp
        self.hp = hp
        self.sprite = sprite

    @property
    def attack(self):
        bonus = self.weapon.attack_bonus if hasattr(self, 'weapon') and self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = self.armor.defense_bonus if hasattr(self, 'armor') and self.armor else 0
        return self.base_defense + bonus

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        if damage > 0 and damage_sound:
            damage_sound.play()
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, x, y, name, char_class):
        super().__init__(x, y, name, CLASSES[char_class]["hp"], CLASSES[char_class]["attack"], CLASSES[char_class]["defense"], CLASSES[char_class]["sprite"])
        self.char_class = char_class
        self.xp = 0
        self.level = 1
        self.inventory = [Weapon(CLASSES[char_class]["weapon"], 5)]
        self.weapon = self.inventory[0]
        self.armor = None
        self.max_mana = CLASSES[char_class]["mana"]
        self.mana = self.max_mana
        self.skill_cooldown = 0

    def gain_xp(self, xp):
        self.xp += xp
        if self.xp >= self.level * 100:
            return self.level_up()
        return None

    def level_up(self):
        self.level += 1
        self.max_hp += 20
        self.hp = self.max_hp
        self.base_attack += 5
        self.base_defense += 2
        self.max_mana += 5
        self.mana = self.max_mana
        self.xp = 0
        return f'\n{self.name} leveled up to level {self.level}! Stats increased.'

class Enemy(Entity):
    def __init__(self, x, y, enemy_type):
        super().__init__(x, y, enemy_type.capitalize(), ENEMIES[enemy_type]["hp"], ENEMIES[enemy_type]["attack"], ENEMIES[enemy_type]["defense"], ENEMIES[enemy_type]["sprite"])
        self.xp = ENEMIES[enemy_type]["xp"]

# --- Map Generation ---
class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

class Dungeon:
    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level = level
        self.grid = [[SPRITES["wall"] for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.items = []
        self.enemies = []
        self.stairs_down = None

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.grid[y][x] = SPRITES["floor"]

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = SPRITES["floor"]

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = SPRITES["floor"]

    def generate(self):
        for _ in range(MAX_ROOMS):
            w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = random.randint(0, self.width - w - 1)
            y = random.randint(0, self.height - h - 1)

            new_room = Rect(x, y, w, h)
            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue

            self.create_room(new_room)
            (new_x, new_y) = new_room.center()

            if self.rooms:
                (prev_x, prev_y) = self.rooms[-1].center()
                if random.randint(0, 1) == 1:
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)
            
            self.place_content(new_room)
            self.rooms.append(new_room)
        
        if self.level < MAX_DUNGEON_LEVEL:
            last_room = self.rooms[-1]
            self.stairs_down = last_room.center()
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = SPRITES["stairs"]
        else: # Boss level
            boss_room = self.rooms[-1]
            boss_x, boss_y = boss_room.center()
            self.enemies.append(Enemy(boss_x, boss_y, "dragon"))

    def place_content(self, room):
        num_enemies = random.randint(0, 3)
        for _ in range(num_enemies):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(e.x == x and e.y == y for e in self.enemies):
                enemy_type = random.choice(list(ENEMIES.keys() - {'dragon'}))
                self.enemies.append(Enemy(x, y, enemy_type))
        
        num_items = random.randint(0, 2)
        for _ in range(num_items):
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            if not any(i.x == x and i.y == y for i in self.items):
                item_choice = random.random()
                if item_choice < 0.4:
                    item = Potion("Health Potion", 20)
                elif item_choice < 0.7:
                    item = random.choice(WEAPONS)
                else:
                    item = random.choice(ARMOR)
                item.x = x
                item.y = y
                self.items.append(item)

# --- Game ---
class Game:
    def main_menu(self):
        from ui import UIManager
        ui = UIManager(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT)
        waiting = True
        button_rects = {
            "play": pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 60, 220, 60),
            "options": pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 10, 220, 60),
            "quit": pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 80, 220, 60)
        }
        while waiting and not self.game_over:
            ui.draw_background()
            ui.draw_panel(SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 - 10, center=True)
            ui.draw_text("HEROES", SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 - 60, size=64)
            ui.draw_text("AND", SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2, size=32)
            ui.draw_text("VILLAINS", SCREEN_WIDTH // 2 + 120, SCREEN_HEIGHT // 2 + 50, size=64)
            ui.draw_button(ui.button_green, ui.icon_play, "PLAY", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 60)
            ui.draw_button(ui.button_blue, ui.icon_options, "OPTIONS", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 10)
            ui.draw_button(ui.button_red, ui.icon_quit, "QUIT", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 80)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.game_over = True
                        waiting = False
                    else:
                        self.game_state = "setup_num_players"
                        waiting = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if button_rects["play"].collidepoint(mx, my):
                        self.game_state = "setup_num_players"
                        waiting = False
                    elif button_rects["options"].collidepoint(mx, my):
                        self.add_message("Options menu coming soon!")
                    elif button_rects["quit"].collidepoint(mx, my):
                        self.game_over = True
                        waiting = False
    def __init__(self):
        self.players = []
        self.dungeon = None
        self.current_player_idx = 0
        self.game_over = False
        self.dungeon_level = 1
        self.messages = deque(maxlen=5)
        self.game_state = "main_menu"
        self.num_players = 0
        self.current_hero_setup = 1
        self.player_name = ""
        self.turn_order = []
        self.combat_turn_idx = 0
        self.inventory_selection = 0

    def add_message(self, text):
        self.messages.appendleft(text)

    def draw_text(self, text, x, y, color=WHITE, center=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.centerx = x
            text_rect.top = y
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, (x, y))

    def setup_num_players(self):
        if gold_background:
            screen.blit(gold_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("Enter number of heroes:", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, color=BLACK)

        one_player_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 - 50, "1 Player", button_img, button_img_hover)
        two_players_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 10, "2 Players", button_img, button_img_hover)
        three_players_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 70, "3 Players", button_img, button_img_hover)

        one_player_button.draw(screen)
        two_players_button.draw(screen)
        three_players_button.draw(screen)
        self.draw_text("--- MESSAGES ---", 820, SCREEN_HEIGHT - 280)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if one_player_button.handle_event(event):
                self.num_players = 1
                self.game_state = "setup_player_name"
            if two_players_button.handle_event(event):
                self.num_players = 2
                self.game_state = "setup_player_name"
            if three_players_button.handle_event(event):
                self.num_players = 3
                self.game_state = "setup_player_name"

    def setup_player_name(self):
        if gold_background:
            screen.blit(gold_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text(f"Enter name for hero {self.current_hero_setup}:", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, color=BLACK)
        
        name_panel = gold_panel
        screen.blit(name_panel, (SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 - 25))
        self.draw_text(self.player_name, SCREEN_WIDTH // 2 - 85, SCREEN_HEIGHT // 2 - 15, color=BLACK)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.player_name:
                    self.game_state = "setup_player_class"
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                else:
                    self.player_name += event.unicode

    def setup_player_class(self):
        if gold_background:
            screen.blit(gold_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text(f"Choose class for {self.player_name}:", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, color=BLACK)
        self.draw_text("Inventory", SCREEN_WIDTH // 2, 50, color=BLACK)
        warrior_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 - 50, "Warrior", button_img, button_img_hover)
        mage_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 10, "Mage", button_img, button_img_hover)
        archer_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 70, "Archer", button_img, button_img_hover)

        warrior_button.draw(screen)
        mage_button.draw(screen)
        archer_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            
            class_choice = None
            if warrior_button.handle_event(event):
                class_choice = "warrior"
            elif mage_button.handle_event(event):
                class_choice = "mage"
            elif archer_button.handle_event(event):
                class_choice = "archer"

            if class_choice:
                self.players.append(Player(0, 0, self.player_name, class_choice))
                self.player_name = ""
                if self.current_hero_setup < self.num_players:
                    self.current_hero_setup += 1
                    self.game_state = "setup_player_name"
                else:
                    self.new_level()
                    self.game_state = "playing"

    def new_level(self):
        self.dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT, self.dungeon_level)
        self.dungeon.generate()
        start_room = self.dungeon.rooms[0]
        for player in self.players:
            player.x, player.y = start_room.center()
        self.add_message(f"You have entered dungeon level {self.dungeon_level}.")

    def main_loop(self):
        self.draw_text("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150, color=BLACK)
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            self.add_message("Could not play music.")

        while not self.game_over:
            if self.game_state == "main_menu":
                self.main_menu()
            elif self.game_state == "setup_num_players":
                self.setup_num_players()
            elif self.game_state == "setup_player_name":
                self.setup_player_name()
            elif self.game_state == "setup_player_class":
                self.setup_player_class()
            elif self.game_state == "playing":
                self.run_game()
            elif self.game_state == "combat":
                self.run_combat()
            elif self.game_state == "inventory":
                self.run_inventory()
            elif self.game_state == "game_over":
                self.game_over_screen()
            elif self.game_state == "game_won":
                self.game_won_screen()
            elif self.game_state == "leaderboard":
                self.leaderboard_screen()

    def run_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                self.handle_input(event.key)
        self.draw_game()

    def handle_input(self, key):
        player = self.players[self.current_player_idx]
        if key == pygame.K_w:
            self.move_player(player, 'w')
        elif key == pygame.K_s:
            self.move_player(player, 's')
        elif key == pygame.K_a:
            self.move_player(player, 'a')
        elif key == pygame.K_d:
            self.move_player(player, 'd')
        elif key == pygame.K_i:
            self.game_state = "inventory"
            self.inventory_selection = 0
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def move_player(self, player, direction):
        dx, dy = 0, 0
        if direction == 'w': dy = -1
        if direction == 's': dy = 1
        if direction == 'a': dx = -1
        if direction == 'd': dx = 1

        new_x, new_y = player.x + dx, player.y + dy

        if not (0 <= new_x < self.dungeon.width and 0 <= new_y < self.dungeon.height):
            self.add_message("You can't move off the map.")
            return

        if self.dungeon.grid[new_y][new_x] == SPRITES["stairs"]:
            self.dungeon_level += 1
            self.new_level()
            return

        if self.dungeon.grid[new_y][new_x] == SPRITES["floor"]:
            enemies_in_pos = [e for e in self.dungeon.enemies if e.x == new_x and e.y == new_y]
            if enemies_in_pos:
                self.start_combat(enemies_in_pos)
            else:
                player.x = new_x
                player.y = new_y
                for item in list(self.dungeon.items):
                    if item.x == new_x and item.y == new_y:
                        player.inventory.append(item)
                        self.dungeon.items.remove(item)
                        self.add_message(f"{player.name} picked up a {item.name}.")
        else:
            self.add_message("You can't move there.")

    def draw_game(self):
        screen.fill(BLACK)
        # Draw map
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                screen.blit(self.dungeon.grid[y][x], (x * TILE_SIZE, y * TILE_SIZE))

        # Draw items, enemies, players
        for item in self.dungeon.items:
            screen.blit(item.sprite, (item.x * TILE_SIZE, item.y * TILE_SIZE))
        for enemy in self.dungeon.enemies:
            screen.blit(enemy.sprite, (enemy.x * TILE_SIZE, enemy.y * TILE_SIZE))
        for player in self.players:
            screen.blit(player.sprite, (player.x * TILE_SIZE, player.y * TILE_SIZE))

        # Draw UI
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        # Draw UI panel
        if ui_panel_background:
            screen.blit(ui_panel_background, (800, 0))
        else:
            pygame.draw.rect(screen, (40, 40, 40), (800, 0, SCREEN_WIDTH - 800, SCREEN_HEIGHT))

        # Draw player status
        y = 40
        self.draw_text("--- PARTY ---", 820, y, color=WHITE)
        y += 40
        for p in self.players:
            color = YELLOW if self.players[self.current_player_idx] == p else WHITE
            self.draw_text(f'{p.name} ({p.char_class}) - Lvl {p.level}', 820, y, color=color)
            
            # HP Bar
            hp_bar_width = int((p.hp / p.max_hp) * 150)
            pygame.draw.rect(screen, RED, pygame.Rect(820, y + 30, 150, 15))
            pygame.draw.rect(screen, GREEN, pygame.Rect(820, y + 30, hp_bar_width, 15))
            self.draw_text(f'{p.hp}/{p.max_hp}', 980, y + 28)
            
            if p.max_mana > 0:
                # Mana Bar
                mana_bar_width = int((p.mana / p.max_mana) * 150)
                pygame.draw.rect(screen, (0,0,100), pygame.Rect(820, y + 55, 150, 15))
                pygame.draw.rect(screen, BLUE, pygame.Rect(820, y + 55, mana_bar_width, 15))
                self.draw_text(f'{p.mana}/{p.max_mana}', 980, y + 53)

            y += 100

        # Draw messages
        y = SCREEN_HEIGHT - 280
        self.draw_text("--- MESSAGES ---", 820, y)
        for i, msg in enumerate(self.messages):
            if i < 10: # Limit messages shown
                self.draw_text(msg, 820, y + 30 + (i * 22))


    def start_combat(self, enemies):
        self.game_state = "combat"
        self.combat_enemies = enemies
        self.turn_order = self.players + self.combat_enemies
        random.shuffle(self.turn_order)
        self.combat_turn_idx = 0
        self.add_message("You've entered combat!")

    def run_combat(self):
        screen.fill(BLACK)
        # Draw map view on the left
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                screen.blit(self.dungeon.grid[y][x], (x * TILE_SIZE, y * TILE_SIZE))
        for item in self.dungeon.items:
            screen.blit(item.sprite, (item.x * TILE_SIZE, item.y * TILE_SIZE))
        for enemy in self.dungeon.enemies:
            screen.blit(enemy.sprite, (enemy.x * TILE_SIZE, enemy.y * TILE_SIZE))
        for player in self.players:
            screen.blit(player.sprite, (player.x * TILE_SIZE, player.y * TILE_SIZE))

        self.draw_combat_screen()
        entity = self.turn_order[self.combat_turn_idx]

        if isinstance(entity, Player):
            attack_button = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 120, "Attack", button_img, button_img_hover)
            skill_button = Button(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 60, "Skill", button_img, button_img_hover)

            attack_button.draw(screen)
            skill_button.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                if attack_button.handle_event(event):
                    self.player_attack()
                if skill_button.handle_event(event):
                    self.use_skill(entity, self.combat_enemies)
        else: # Enemy turn
            pygame.time.wait(500) # Pause for enemy turn
            self.enemy_attack(entity)

        if not any(p.is_alive() for p in self.players):
            self.add_message("Your party has been defeated. Game Over.")
            self.update_highscores()
            self.game_state = "game_over"
        elif not any(e.is_alive() for e in self.combat_enemies):
            if any(e.name == 'Dragon' for e in self.combat_enemies):
                self.add_message("Congratulations! You have defeated the Dragon and won the game!")
                self.update_highscores()
                self.game_state = "game_won"
            else:
                self.add_message("You won the battle!")
                self.game_state = "playing"
            total_xp = sum(e.xp for e in self.combat_enemies)
            xp_per_player = total_xp // len(self.players) if self.players else 0
            for p in self.players:
                if p.is_alive():
                    msg = p.gain_xp(xp_per_player)
                    if msg: self.add_message(msg)
            self.dungeon.enemies = [e for e in self.dungeon.enemies if e not in self.combat_enemies]

        pygame.display.flip()

    def player_attack(self):
        player = self.turn_order[self.combat_turn_idx]
        alive_enemies = [e for e in self.combat_enemies if e.is_alive()]
        if alive_enemies:
            target = random.choice(alive_enemies)
            damage = max(0, player.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{player.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def enemy_attack(self, enemy):
        alive_players = [p for p in self.players if p.is_alive()]
        if alive_players:
            target = random.choice(alive_players)
            damage = max(0, enemy.attack - target.defense)
            target.take_damage(damage)
            self.add_message(f"{enemy.name} hits {target.name} for {damage} damage.")
        self.next_turn()

    def next_turn(self):
        self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)
        while not self.turn_order[self.combat_turn_idx].is_alive():
            self.combat_turn_idx = (self.combat_turn_idx + 1) % len(self.turn_order)


    def draw_combat_screen(self):
        # Draw UI panel
        if ui_panel_background:
            screen.blit(ui_panel_background, (800, 0))
        else:
            pygame.draw.rect(screen, (40, 40, 40), (800, 0, SCREEN_WIDTH - 800, SCREEN_HEIGHT))

        # Draw combatants' stats
        y = 40
        self.draw_text("--- COMBAT ---", 820, y, color=WHITE)
        y += 40

        # Players
        for p in self.players:
            color = YELLOW if self.turn_order[self.combat_turn_idx] == p else WHITE
            self.draw_text(f'{p.name} HP: {p.hp}/{p.max_hp}', 820, y, color=color)
            y += 30
        
        y += 20
        # Enemies
        for e in self.combat_enemies:
            if e.is_alive():
                color = YELLOW if self.turn_order[self.combat_turn_idx] == e else WHITE
                self.draw_text(f'{e.name} HP: {e.hp}/{e.max_hp}', 820, y, color=color)
                y += 30

        # Draw message log
        y = SCREEN_HEIGHT - 280
        self.draw_text("--- MESSAGES ---", 820, y)
        for i, msg in enumerate(self.messages):
            if i < 10:
                self.draw_text(msg, 820, y + 30 + (i * 22))

    def use_skill(self, player, enemies):
        if player.char_class == "warrior":
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            if sword_sound:
                sword_sound.play()
            target = random.choice([e for e in enemies if e.is_alive()])
            damage = player.attack * 2
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            if magic_sound:
                magic_sound.play()
            self.add_message(f"{player.name} casts Fireball!")
            for enemy in enemies:
                if enemy.is_alive():
                    damage = player.attack // 2
                    enemy.take_damage(damage)
                    self.add_message(f"Fireball hits {enemy.name} for {damage} damage.")
            player.mana -= 10
        elif player.char_class == "archer":
            if player.skill_cooldown > 0:
                self.add_message(f"Double Shot is on cooldown for {player.skill_cooldown} more turns.")
                return
            if arrow_sound:
                arrow_sound.play()
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                target = random.choice([e for e in enemies if e.is_alive()])
                damage = player.attack
                target.take_damage(damage)
                self.add_message(f"{player.name} shoots {target.name} for {damage} damage.")
            player.skill_cooldown = 2
        self.next_turn()

    def run_inventory(self):
        player = self.players[self.current_player_idx]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                    self.game_state = "playing"
                if event.key == pygame.K_UP:
                    self.inventory_selection = max(0, self.inventory_selection - 1)
                if event.key == pygame.K_DOWN:
                    self.inventory_selection = min(len(player.inventory) - 1, self.inventory_selection + 1)
                if event.key == pygame.K_e:
                    if player.inventory:
                        item = player.inventory[self.inventory_selection]
                        if isinstance(item, Potion):
                            msg = item.use(player)
                            self.add_message(msg)
                            player.inventory.pop(self.inventory_selection)
                        elif isinstance(item, Weapon):
                            if player.weapon:
                                player.inventory.append(player.weapon)
                            player.weapon = item
                            player.inventory.pop(self.inventory_selection)
                            self.add_message(f"{player.name} equipped {item.name}.")
                        elif isinstance(item, Armor):
                            if player.armor:
                                player.inventory.append(player.armor)
                            player.armor = item
                            player.inventory.pop(self.inventory_selection)
                            self.add_message(f"{player.name} equipped {item.name}.")
                        self.inventory_selection = 0
        self.draw_inventory_screen()

    def draw_inventory_screen(self):
        if gold_background:
            screen.blit(gold_background, (0,0))
        else:
            screen.fill(BLACK)

        self.draw_text("Inventory", SCREEN_WIDTH // 2 - 100, 50, color=BLACK)
        self.draw_text("Press 'i' or 'ESC' to close", SCREEN_WIDTH // 2 - 200, 100, color=BLACK)

        player = self.players[self.current_player_idx]

        # Equipped items section
        self.draw_text("Equipped", 200, 200, color=BLACK)
        weapon_slot = gold_panel
        armor_slot = gold_panel
        screen.blit(weapon_slot, (150, 250))
        screen.blit(armor_slot, (350, 250))

        if player.weapon:
            screen.blit(player.weapon.sprite, (150, 250))
            self.draw_text(player.weapon.name, 150, 310, color=BLACK)
        if player.armor:
            screen.blit(player.armor.sprite, (350, 250))
            self.draw_text(player.armor.name, 350, 310, color=BLACK)

        # Inventory grid
        self.draw_text("Backpack", 700, 200, color=BLACK)
        inv_cols = 5
        inv_rows = 4
        item_slot = gold_panel

        for i in range(inv_cols * inv_rows):
            x = 700 + (i % inv_cols) * 100
            y = 250 + (i // inv_cols) * 100
            screen.blit(item_slot, (x, y))
            if i < len(player.inventory):
                item = player.inventory[i]
                screen.blit(item.sprite, (x, y))
                if i == self.inventory_selection:
                    pygame.draw.rect(screen, YELLOW, (x, y, item_slot.get_width(), item_slot.get_height()), 3)

        pygame.display.flip()

    def game_over_screen(self):
        if gold_background:
            screen.blit(gold_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("Game Over", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150, color=BLACK)

        menu_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2, "Main Menu", button_img, button_img_hover)
        menu_button.draw(screen)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if menu_button.handle_event(event):
                    self.__init__()
                    waiting = False

    def game_won_screen(self):
        if gold_background:
            screen.blit(gold_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("You Win!", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 150, color=BLACK)

        menu_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2, "Main Menu", button_img, button_img_hover)
        menu_button.draw(screen)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if menu_button.handle_event(event):
                    self.__init__()
                    waiting = False

    def update_highscores(self):
        scores = []
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    scores = json.load(f)
            except json.JSONDecodeError:
                scores = []
        
        total_xp = sum(p.xp for p in self.players)
        party_names = ", ".join([p.name for p in self.players])
        scores.append({"party": party_names, "level": self.dungeon_level, "xp": total_xp})
        
        scores = sorted(scores, key=lambda x: (x['level'], x['xp']), reverse=True)[:10]

        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f, indent=4)

    def leaderboard_screen(self):
        screen.fill(BLACK)
        self.draw_text("Leaderboard", SCREEN_WIDTH // 2 - 100, 50)

        scores = []
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    scores = json.load(f)
            except json.JSONDecodeError:
                scores = []

        y = 150
        for i, score in enumerate(scores):
            self.draw_text(f"{i+1}. {score['party']} - Level: {score['level']}, XP: {score['xp']}", 100, y)
            y += 40

        self.draw_text("Press ESC to return to the main menu", 100, SCREEN_HEIGHT - 100)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "main_menu"
                        waiting = False

if __name__ == "__main__":
    game = Game()
    game.main_loop()