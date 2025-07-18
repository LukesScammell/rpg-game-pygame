import os
import pygame

def load_sprite(path, size=None):
    """Load a sprite with optional scaling."""
    sprite = pygame.image.load(path).convert_alpha()
    if size:
        sprite = pygame.transform.scale(sprite, size)
    return sprite

def load_ui_elements(ui_folder, scale=2):
    """
    Dynamically loads all UI elements from a folder.
    Applies scaling and returns a dictionary with semantic keys.
    """
    # You can rename these to whatever you want
    ui_map = {
        "ui_element_005": "panel",
        "ui_element_028": "button_blue",
        "ui_element_029": "button_blue_hover",
        # Add more mappings here as needed
    }

    elements = {}
    for file in os.listdir(ui_folder):
        if file.endswith(".png") and file.startswith("ui_element_"):
            key = os.path.splitext(file)[0]  # e.g., ui_element_028
            if key in ui_map:
                image_path = os.path.join(ui_folder, file)
                sprite = load_sprite(image_path)
                if scale != 1:
                    w, h = sprite.get_size()
                    sprite = pygame.transform.scale(sprite, (w * scale, h * scale))
                elements[ui_map[key]] = sprite
    return elements
