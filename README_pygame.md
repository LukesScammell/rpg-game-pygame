# Pygame RPG Adventure - Changelog

This document outlines the recent changes and development history of the Pygame RPG Adventure game.

## Version 1.1 - Bug Fixes (July 18, 2025)

This update addresses a critical bug that caused the game to crash with a "ValueError: cannot choose from an empty sequence" error during combat.

### Bug Fix: Combat Skill Crash

*   **Issue:** The game would crash if a player attempted to use the "Power Strike" (Warrior) or "Double Shot" (Archer) skill when no living enemies were left in the combat instance. The code did not check if there were valid targets before attempting to select one.
*   **Fix:** Added checks to the `use_skill` method in `rpg_pygame.py`. Before executing a skill that targets an enemy, the game now verifies that there is at least one living enemy available. If no valid targets exist, a message is displayed to the user, and the skill is not executed, preventing the crash.

---

## Development History

This section logs the user prompts that led to the recent updates.

### July 18, 2025

*   **User Prompt:** "could you look at my files and figure out the game and on line 800, 436, 554 and 658 on the rpg_pygame.py which says cannot choose from an empty sequence"
*   **User Prompt:** "could you generate the new changes as a new version on the pygame readme and show the prompts i used to get the new features and things"