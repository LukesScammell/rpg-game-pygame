#!/usr/bin/env python
import random
import os
import json
import pygame
from collections import deque

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAP_WIDTH = 40
MAP_HEIGHT = 20
TILE_SIZE = 24
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 15
MAX_DUNGEON_LEVEL = 5
HIGHSCORE_FILE = "rpg_highscores.json"

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Python RPG Adventure")
font = pygame.font.Font(None, 32)

# --- Image Assets ---
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    wood_background = pygame.image.load(os.path.join(script_dir, "assets", "gui-files", "wood background.png")).convert()
    paper_background = pygame.image.load(os.path.join(script_dir, "assets", "gui-files", "paper background.png")).convert()
    ui_sheet = pygame.image.load(os.path.join(script_dir,  "assets", "gui-files", "gui-files.png")).convert_alpha()
except pygame.error:
    print("Warning: Could not load image assets. Make sure you have the ' assets, gui-files,' folder with the required image files.")
    wood_background = None
    paper_background = None
    ui_sheet = None

# --- UI Slicing ---
def get_ui_image(x, y, w, h):
    if ui_sheet:
        return ui_sheet.subsurface(pygame.Rect(x, y, w, h))
    return pygame.Surface((w, h))

UI_ELEMENTS = {
    "button_blue": get_ui_image(34, 251, 190, 49),
    "button_blue_hover": get_ui_image(34, 300, 190, 49),
    "panel": get_ui_image(468, 96, 190, 45)
}

# --- Button Class ---
class Button:
    def __init__(self, x, y, text, image, hover_image=None):
        self.rect = pygame.Rect(x, y, image.get_width(), image.get_height())
        self.text = text
        self.image = image
        self.hover_image = hover_image if hover_image else image
        self.is_hovered = False

    def draw(self, surface):
        current_image = self.hover_image if self.is_hovered else self.image
        surface.blit(current_image, self.rect.topleft)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

# --- Sound Assets ---
try:
    pygame.mixer.music.load(os.path.join("assets", "music.ogg"))
    sword_sound = pygame.mixer.Sound(os.path.join("assets", "sword.wav"))
    magic_sound = pygame.mixer.Sound(os.path.join("assets", "magic.wav"))
    arrow_sound = pygame.mixer.Sound(os.path.join("assets", "arrow.wav"))
    damage_sound = pygame.mixer.Sound(os.path.join("assets", "damage.wav"))
except pygame.error:
    print("Warning: Could not load sound assets. Make sure you have the 'assets' folder with the required sound files.")

# --- UI Elements ---
UI = {
    "player": "🧑",
    "warrior": "🤺",
    "mage": "🧙",
    "archer": "🏹",
    "goblin": "👺",
    "orc": "👹",
    "troll": "🗿",
    "dragon": "🐉",
    "potion": "🧪",
    "weapon": "⚔️",
    "armor": "🛡️",
    "wall": "🧱",
    "floor": ".",
    "stairs": "🔽",
    "hp": "❤️",
    "xp": "✨",
    "mana": "💧",
    "attack": "💥",
    "defense": "🛡️",
    "level": "🌟"
}

# --- Character Classes ---
CLASSES = {
    "warrior": {"hp": 120, "attack": 15, "defense": 10, "icon": UI["warrior"], "weapon": "Sword", "mana": 0},
    "mage": {"hp": 80, "attack": 20, "defense": 5, "icon": UI["mage"], "weapon": "Staff", "mana": 20},
    "archer": {"hp": 100, "attack": 12, "defense": 8, "icon": UI["archer"], "weapon": "Bow", "mana": 0}
}

# --- Enemy Types ---
ENEMIES = {
    "goblin": {"hp": 30, "attack": 8, "defense": 2, "xp": 50, "icon": UI["goblin"]},
    "orc": {"hp": 50, "attack": 12, "defense": 4, "xp": 100, "icon": UI["orc"]},
    "troll": {"hp": 80, "attack": 15, "defense": 6, "xp": 150, "icon": UI["troll"]},
    "dragon": {"hp": 250, "attack": 25, "defense": 15, "xp": 1000, "icon": UI["dragon"]}
}

# --- Items ---
class Item:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

class Potion(Item):
    def __init__(self, name, hp_gain):
        super().__init__(name, UI["potion"])
        self.hp_gain = hp_gain

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.hp_gain)
        return f'{target.name} used {self.name} and gained {self.hp_gain} HP.'

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, UI["weapon"])
        self.attack_bonus = attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus):
        super().__init__(name, UI["armor"])
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
    def __init__(self, x, y, name, hp, attack, defense, icon):
        self.x = x
        self.y = y
        self.name = name
        self.base_attack = attack
        self.base_defense = defense
        self.max_hp = hp
        self.hp = hp
        self.icon = icon

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
        if damage > 0:
            try:
                damage_sound.play()
            except NameError:
                pass
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

class Player(Entity):
    def __init__(self, x, y, name, char_class):
        super().__init__(x, y, name, CLASSES[char_class]["hp"], CLASSES[char_class]["attack"], CLASSES[char_class]["defense"], CLASSES[char_class]["icon"])
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
        super().__init__(x, y, enemy_type.capitalize(), ENEMIES[enemy_type]["hp"], ENEMIES[enemy_type]["attack"], ENEMIES[enemy_type]["defense"], ENEMIES[enemy_type]["icon"])
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
        self.grid = [[UI["wall"] for _ in range(width)] for _ in range(height)]
        self.rooms = []
        self.items = []
        self.enemies = []
        self.stairs_down = None

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.grid[y][x] = UI["floor"]

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.grid[y][x] = UI["floor"]

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.grid[y][x] = UI["floor"]

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
            self.grid[self.stairs_down[1]][self.stairs_down[0]] = UI["stairs"]
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
        self.combat_enemies = []
        self.turn_order = []
        self.combat_turn_idx = 0

    def reset_game(self):
        self.__init__()

    def draw_text(self, text, x, y, color=WHITE):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    def main_menu(self):
        if wood_background:
            screen.blit(wood_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("Python RPG Adventure", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, color=BLACK)

        start_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2, "Start Game", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        quit_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 60, "Quit", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])

        start_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if start_button.handle_event(event):
                self.game_state = "setup_num_players"
            if quit_button.handle_event(event):
                self.game_over = True

    def setup_num_players(self):
        if paper_background:
            screen.blit(paper_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("Enter number of heroes:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, color=BLACK)

        one_player_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 - 50, "1 Player", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        two_players_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 10, "2 Players", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        three_players_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 70, "3 Players", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])

        one_player_button.draw(screen)
        two_players_button.draw(screen)
        three_players_button.draw(screen)

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
        if paper_background:
            screen.blit(paper_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text(f"Enter name for hero {self.current_hero_setup}:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, color=BLACK)
        
        name_panel = UI_ELEMENTS["panel"]
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
        if paper_background:
            screen.blit(paper_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text(f"Choose class for {self.player_name}:", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, color=BLACK)

        warrior_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 - 50, "Warrior", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        mage_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 10, "Mage", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        archer_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2 + 70, "Archer", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])

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
        try:
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass
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
            elif self.game_state == "game_over":
                self.game_over_screen()

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

        if self.dungeon.grid[new_y][new_x] == UI["stairs"]:
            self.dungeon_level += 1
            self.new_level()
            return

        if self.dungeon.grid[new_y][new_x] == UI["floor"]:
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
                icon = self.dungeon.grid[y][x]
                text = font.render(icon, True, WHITE)
                screen.blit(text, (x * TILE_SIZE, y * TILE_SIZE))

        # Draw items, enemies, players
        for item in self.dungeon.items:
            text = font.render(item.icon, True, WHITE)
            screen.blit(text, (item.x * TILE_SIZE, item.y * TILE_SIZE))
        for enemy in self.dungeon.enemies:
            text = font.render(enemy.icon, True, RED)
            screen.blit(text, (enemy.x * TILE_SIZE, enemy.y * TILE_SIZE))
        for player in self.players:
            text = font.render(player.icon, True, GREEN)
            screen.blit(text, (player.x * TILE_SIZE, player.y * TILE_SIZE))

        # Draw UI
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        # Draw player status
        y = 10
        for p in self.players:
            self.draw_text(f'{p.icon} {p.name} ({p.char_class}) | {UI["level"]} {p.level} | {UI["hp"]} {p.hp}/{p.max_hp}', 10, y)
            y += 30

        # Draw messages
        y = SCREEN_HEIGHT - 100
        for msg in self.messages:
            self.draw_text(msg, 10, y)
            y += 20

    def start_combat(self, enemies):
        self.game_state = "combat"
        self.combat_enemies = enemies
        self.turn_order = self.players + self.combat_enemies
        random.shuffle(self.turn_order)
        self.combat_turn_idx = 0
        self.add_message("You've entered combat!")

    def run_combat(self):
        if wood_background:
            screen.blit(wood_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_combat_screen()
        entity = self.turn_order[self.combat_turn_idx]

        if isinstance(entity, Player):
            attack_button = Button(100, SCREEN_HEIGHT - 120, "Attack", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
            skill_button = Button(100, SCREEN_HEIGHT - 60, "Skill", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])

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
            self.game_state = "game_over"
        elif not any(e.is_alive() for e in self.combat_enemies):
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
        entity = self.turn_order[self.combat_turn_idx]
        if not entity.is_alive():
            self.next_turn()

    def draw_combat_screen(self):
        # Draw players
        for i, player in enumerate(self.players):
            panel = UI_ELEMENTS["panel"]
            screen.blit(panel, (100, 50 + i * 60))
            self.draw_text(f'{player.icon} {player.name} {UI["hp"]} {player.hp}/{player.max_hp}', 110, 60 + i * 60, color=BLACK)

        # Draw enemies
        for i, enemy in enumerate(self.combat_enemies):
            panel = UI_ELEMENTS["panel"]
            screen.blit(panel, (SCREEN_WIDTH - 300, 50 + i * 60))
            self.draw_text(f'{enemy.icon} {enemy.name} {UI["hp"]} {enemy.hp}/{enemy.max_hp}', SCREEN_WIDTH - 290, 60 + i * 60, color=BLACK)

        self.draw_ui()

    def use_skill(self, player, enemies):
        if player.char_class == "warrior":
            if player.skill_cooldown > 0:
                self.add_message(f"Power Strike is on cooldown for {player.skill_cooldown} more turns.")
                return
            try:
                sword_sound.play()
            except NameError:
                pass
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                self.add_message("There are no enemies to attack.")
                return
            target = random.choice(alive_enemies)
            damage = player.attack * 2
            target.take_damage(damage)
            self.add_message(f"{player.name} uses Power Strike on {target.name} for {damage} damage!")
            player.skill_cooldown = 3
        elif player.char_class == "mage":
            if player.mana < 10:
                self.add_message("Not enough mana for Fireball.")
                return
            try:
                magic_sound.play()
            except NameError:
                pass
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
            try:
                arrow_sound.play()
            except NameError:
                pass
            alive_enemies = [e for e in enemies if e.is_alive()]
            if not alive_enemies:
                self.add_message("There are no enemies to attack.")
                return
            self.add_message(f"{player.name} uses Double Shot!")
            for _ in range(2):
                target = random.choice(alive_enemies)
                damage = player.attack
                target.take_damage(damage)
                self.add_message(f"{player.name} shoots {target.name} for {damage} damage.")
            player.skill_cooldown = 2
        self.next_turn()

    def game_over_screen(self):
        if wood_background:
            screen.blit(wood_background, (0, 0))
        else:
            screen.fill(BLACK)
        self.draw_text("Game Over", SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100, color=BLACK)

        menu_button = Button(SCREEN_WIDTH // 2 - 95, SCREEN_HEIGHT // 2, "Main Menu", UI_ELEMENTS["button_blue"], UI_ELEMENTS["button_blue_hover"])
        menu_button.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            if menu_button.handle_event(event):
                self.reset_game()
                self.game_state = "main_menu"

if __name__ == "__main__":
    game = Game()
    game.main_loop()
