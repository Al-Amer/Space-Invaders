import curses

# --- Base Screen Dimensions ---
SCREEN_HEIGHT = 45
SCREEN_WIDTH = 80

# --- Menu Definitions ---
MAIN_MENU_ITEMS = ["START GAME", "LOAD GAME", "SCOREBOARD",
                   "ACHIEVEMENTS", "SHOP", "KEYBINDINGS", "QUIT"]
PAUSE_MENU_ITEMS = ["RESUME", "SAVE GAME",
                    "KEYBINDINGS", "RESTART LEVEL", "QUIT TO MAIN MENU"]
AUTH_MENU_ITEMS = ["LOGIN", "REGISTER", "QUIT"]

# --- Game Settings ---
CURRENCY_NAME = "Galactic Coins"

# --- Color Pair Identifiers ---
PAIR_MENU_SELECTED = 1
PAIR_MENU_NORMAL = 2
PAIR_ENEMY_CRASH = 3
PAIR_SCORE_LEVEL = 10
PAIR_PLAYER_SHIP = 11
PAIR_PLAYER_PROJECTILE = 12
PAIR_OBSTACLE = 13
PAIR_BOSS = 14
PAIR_HEALTH_FULL = 15
PAIR_HEALTH_MED = 16
PAIR_HEALTH_LOW = 17


def init_colors():
    curses.start_color()
    curses.init_pair(PAIR_MENU_SELECTED,
                     curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(PAIR_MENU_NORMAL, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(PAIR_ENEMY_CRASH, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(PAIR_SCORE_LEVEL, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.init_pair(PAIR_PLAYER_SHIP, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(PAIR_PLAYER_PROJECTILE,
                     curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(PAIR_OBSTACLE, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(PAIR_BOSS, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    curses.init_pair(PAIR_HEALTH_FULL, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(PAIR_HEALTH_MED, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(PAIR_HEALTH_LOW, curses.COLOR_RED, curses.COLOR_BLACK)


def get_enemy_colors():
    colors = [
        (curses.COLOR_GREEN, 20), (curses.COLOR_BLUE, 21), (curses.COLOR_MAGENTA, 22),
        (curses.COLOR_CYAN, 23), (curses.COLOR_RED, 24)
    ]
    for color, pair_num in colors:
        try:
            curses.init_pair(pair_num, color, curses.COLOR_BLACK)
        except:
            pass
    return colors
