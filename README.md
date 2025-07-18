# Python RPG Adventure - Pygame Version

This file documents the development of a graphical RPG created with Pygame, with the help of a large language model. It tracks the game's evolution through different versions, detailing the features added at each stage and the prompts used to generate them.

This version was started by user **LukesScammell**.

## How to Play

1.  **Installation:**
    *   Make sure you have Python installed.
    *   Install the Pygame library by opening a terminal (like in VS Code) and running: `pip install pygame` or `py -m pip install pygame`

2.  **Running the Game:**
    *   Navigate to the game's directory in your terminal.
    *   Run the script using: `python rpg_pygame.py` or `py rpg_pygame.py`

3.  **Gameplay:**
    *   **Character Creation:** Follow the on-screen prompts to choose the number of heroes, their names, and their classes (Warrior, Mage, Archer).
    *   **Exploration:** Use the **W, A, S, D** keys to move your party through the dungeon.
    *   **Combat:** When you move into an enemy, combat begins. On a hero's turn, use the number keys:
        *   **(1) Attack:** Perform a basic attack on a random enemy.
        *   **(2) Skill:** Use your class's unique, more powerful skill.
    *   **Descending:** Find the stairs (a down arrow) to proceed to the next, more difficult dungeon level.
    *   **Winning:** Defeat the final boss (a dragon) on the last level to win the game.

4.  **(Optional) Sound:**
    *   For sound effects and music, create a folder named `assets` in the same directory as the game.
    *   Place the following sound files inside it: `music.ogg`, `sword.wav`, `magic.wav`, `arrow.wav`, `damage.wav`.

## Version History

### v1.6.1: Emoji Font Fix

*   **Prompt:** "it runs now, could you make a seperate readme file for the pygame version showing how to play and the versions if i update it with the prompts i gave you to make the feature and also the ui emojis arnt showing right in the pygame"
*   **Changes:**
    *   Updated the Pygame font handling to use "Segoe UI Emoji" to correctly display emoji icons on Windows.
    *   Added a fallback to the default font to prevent crashes if the specified font is not found.

### v1.6: Pygame GUI Implementation (by user)

*   **Prompt:** "can i run the game yet or is there anything i need to add and could you add to the readme all of the new versions that got added and explain that i made the pygame version"
*   **Changes:**
    *   The user, LukesScammell, initiated the creation of a new version of the RPG with a graphical user interface using the Pygame library.
    *   The initial `rpg_pygame.py` file was created, laying the foundation for the GUI.
    *   The emoji-based UI from the command-line version was carried over as a placeholder.
