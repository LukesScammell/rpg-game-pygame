import pygame
from golden_ui_loader import load_ui_elements

# Load UI elements (assume scale=2 for consistency)
UI_ELEMENTS = load_ui_elements("ui_elements", scale=2)

class MainMenuUI:
    def __init__(self, screen, font, screen_width, screen_height):
        self.screen = screen
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Assets
        self.bg = UI_ELEMENTS.get("background")
        self.banner_panel = UI_ELEMENTS.get("panel")
        self.button_green = UI_ELEMENTS.get("button_green")
        self.button_blue = UI_ELEMENTS.get("button_blue")
        self.button_red = UI_ELEMENTS.get("button_red")
        self.icon_play = UI_ELEMENTS.get("icon_play")
        self.icon_options = UI_ELEMENTS.get("icon_options")
        self.icon_quit = UI_ELEMENTS.get("icon_quit")

    def draw(self):
        # Draw background
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((40, 40, 80))
        # Draw banner panel (centered right)
        if self.banner_panel:
            banner_rect = self.banner_panel.get_rect(center=(self.screen_width // 2 + 120, self.screen_height // 2 - 10))
            self.screen.blit(self.banner_panel, banner_rect)
        # Draw title text (centered in panel)
        self.draw_text("HEROES", self.screen_width // 2 + 120, self.screen_height // 2 - 60, size=64)
        self.draw_text("AND", self.screen_width // 2 + 120, self.screen_height // 2, size=32)
        self.draw_text("VILLAINS", self.screen_width // 2 + 120, self.screen_height // 2 + 50, size=64)
        # Draw buttons (vertically aligned left)
        self.draw_button(self.button_green, self.icon_play, "PLAY", self.screen_width // 2 - 120, self.screen_height // 2 - 60)
        self.draw_button(self.button_blue, self.icon_options, "OPTIONS", self.screen_width // 2 - 120, self.screen_height // 2 + 10)
        self.draw_button(self.button_red, self.icon_quit, "QUIT", self.screen_width // 2 - 120, self.screen_height // 2 + 80)

    def draw_text(self, text, x, y, size=48):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, button_img, icon_img, text, x, y):
        if button_img:
            self.screen.blit(button_img, (x, y))
        if icon_img:
            icon_rect = icon_img.get_rect()
            icon_rect.center = (x + 30, y + button_img.get_height() // 2)
            self.screen.blit(icon_img, icon_rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(x + 60, y + button_img.get_height() // 2 if button_img else y + 25))
        self.screen.blit(text_surface, text_rect)
