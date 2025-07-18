import os
import pygame
from golden_ui_loader import load_ui_elements

class UIManager:
    def __init__(self, screen, font, screen_width, screen_height):
        self.screen = screen
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.elements = load_ui_elements(os.path.join(os.path.dirname(__file__), "ui_elements"), scale=2)
        # Common UI assets
        self.bg = self.elements.get("background")
        self.panel = self.elements.get("panel")
        self.button_green = self.elements.get("button_green")
        self.button_blue = self.elements.get("button_blue")
        self.button_red = self.elements.get("button_red")
        self.icon_play = self.elements.get("icon_play")
        self.icon_options = self.elements.get("icon_options")
        self.icon_quit = self.elements.get("icon_quit")

    def draw_background(self):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((40, 40, 80))

    def draw_panel(self, x, y, center=True):
        if self.panel:
            rect = self.panel.get_rect()
            if center:
                rect.center = (x, y)
            else:
                rect.topleft = (x, y)
            self.screen.blit(self.panel, rect)
            return rect
        return None

    def draw_button(self, button_img, icon_img, text, x, y):
        if button_img:
            self.screen.blit(button_img, (x, y))
        if icon_img:
            icon_rect = icon_img.get_rect()
            icon_rect.center = (x + 30, y + button_img.get_height() // 2)
            self.screen.blit(icon_img, icon_rect)
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(x + 60, y + button_img.get_height() // 2 if button_img else y + 25))
        self.screen.blit(text_surface, text_rect)

    def draw_text(self, text, x, y, size=48, color=(255,255,255), center=True):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    # Add more UI drawing methods as needed for other screens
