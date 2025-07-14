import curses
import time
from . import config, shop, achievement

# --- HELPER FUNCTIONS ---


def get_secure_input(window, y, x, prompt, mask=True):
    window.keypad(True)
    curses.curs_set(1)
    window.addstr(y, x, prompt)
    text = ""
    while True:
        key = window.getch()
        if key in [curses.KEY_ENTER, 10, 13]:
            break
        elif key == 27:
            curses.curs_set(0)
            return None
        elif key == curses.KEY_BACKSPACE or key == 127:
            if len(text) > 0:
                text = text[:-1]
                window.addstr(y, x + len(prompt) + len(text), " ")
                window.move(y, x + len(prompt) + len(text))
        elif 32 <= key <= 126:
            text += chr(key)
            display_char = "*" if mask else chr(key)
            window.addstr(y, x + len(prompt) + len(text) - 1, display_char)
    curses.curs_set(0)
    return text


def _draw_fancy_border(win, title=""):
    win.clear()
    win.attron(curses.color_pair(config.PAIR_MENU_NORMAL))
    win.border()
    if title:
        win.addstr(0, (win.getmaxyx()[1] - len(title)) // 2, title)
    win.attroff(curses.color_pair(config.PAIR_MENU_NORMAL))


def _print_menu_items(win, selected_idx, items, y_offset=0):
    h, w = win.getmaxyx()
    for i, item in enumerate(items):
        y = h // 2 - len(items) // 2 + i + y_offset
        x = (w - len(item)) // 2
        attr = curses.color_pair(
            config.PAIR_MENU_SELECTED) if i == selected_idx else curses.A_NORMAL
        win.addstr(y, x, item, attr)

# --- AUTH MENUS ---


def auth_menu(window):
    current_row = 0
    window.keypad(True)
    while True:
        _draw_fancy_border(window, title=" T E R M I N A L   C O N F L I C T ")
        _print_menu_items(window, current_row, config.AUTH_MENU_ITEMS)
        window.refresh()
        key = window.getch()
        if key == curses.KEY_UP:
            current_row = (
                current_row - 1 + len(config.AUTH_MENU_ITEMS)) % len(config.AUTH_MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(config.AUTH_MENU_ITEMS)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return config.AUTH_MENU_ITEMS[current_row]
        elif key == 27:
            return "QUIT"


def login_screen(window, db):
    while True:
        _draw_fancy_border(window, title=" L O G I N ")
        h, w = window.getmaxyx()
        y_start = h//2 - 2
        username = get_secure_input(
            window, y_start, (w - 30)//2, "Username:     ", mask=False)
        if username is None:
            return None
        _draw_fancy_border(window, title=" L O G I N ")
        window.addstr(y_start, (w - 30)//2, f"Username:     {username}")
        password = get_secure_input(
            window, y_start + 1, (w - 30)//2, "Password:     ", mask=True)
        if password is None:
            continue
        player_data = db.get_player(username, password)
        if player_data:
            show_message("Login successful!", duration_seconds=2,
                         wait=False, position='bottom')
            return player_data
        else:
            show_message("Login failed. Please any key to retry.",
                         duration_seconds=0, wait=True, position='bottom')


def register_screen(window, db):
    while True:
        _draw_fancy_border(window, title=" R E G I S T E R ")
        h, w = window.getmaxyx()
        y_start = h//2 - 2
        username = get_secure_input(
            window, y_start, (w - 35)//2, "Choose Username:        ", mask=False)
        if username is None:
            return False
        _draw_fancy_border(window, title=" R E G I S T E R ")
        window.addstr(y_start, (w-35)//2,
                      f"Choose Username:        {username}")
        password = get_secure_input(
            window, y_start + 1, (w - 35)//2, "Choose Password:        ", mask=True)
        if password is None:
            continue
        _draw_fancy_border(window, title=" R E G I S T E R ")
        window.addstr(y_start, (w-35)//2,
                      f"Choose Username:        {username}")
        window.addstr(y_start + 1, (w-35)//2,
                      f"Choose Password:        {'*' * len(password)}")
        confirm_password = get_secure_input(
            window, y_start + 2, (w - 35)//2, "Confirm Password:       ", mask=True)

        if confirm_password is None:
            continue

        if password != confirm_password:
            show_message("Passwords do not match! Try again.",
                         duration_seconds=3, wait=False, position='bottom')
            continue

        if db.register_player(username, password):
            show_message("Registration successful! Please log in.",
                         duration_seconds=3, wait=False, position='bottom')
            return True
        else:
            show_message("Username already exists! Try again.",
                         duration_seconds=3, wait=False, position='bottom')


# --- CORE UI LOGIC ---
def menu_utils(window, current_row_idx, db_connected):
    items = config.MAIN_MENU_ITEMS[:]
    window.keypad(True)
    if not db_connected:
        items.insert(-1, "CONNECT TO DATABASE")
    while True:
        _draw_fancy_border(window, title=" M A I N   M E N U ")
        _print_menu_items(window, current_row_idx, items)
        window.refresh()
        key = window.getch()
        if key == curses.KEY_UP:
            current_row_idx = (current_row_idx - 1 + len(items)) % len(items)
        elif key == curses.KEY_DOWN:
            current_row_idx = (current_row_idx + 1) % len(items)
        elif key == 27:
            return "QUIT", current_row_idx
        elif key in [curses.KEY_ENTER, 10, 13]:
            return items[current_row_idx], current_row_idx


def pause_menu_utils(parent_win, current_row_idx=0):
    box_h, box_w = len(config.PAUSE_MENU_ITEMS) + 4, 30
    box_y, box_x = (curses.LINES - box_h) // 2, (curses.COLS - box_w) // 2
    pause_win = curses.newwin(box_h, box_w, box_y, box_x)
    pause_win.keypad(True)
    while True:
        _draw_fancy_border(pause_win, title=" P A U S E D ")
        _print_menu_items(pause_win, current_row_idx,
                          config.PAUSE_MENU_ITEMS, y_offset=1)
        pause_win.refresh()
        key = pause_win.getch()
        if key == curses.KEY_UP:
            current_row_idx = (
                current_row_idx - 1 + len(config.PAUSE_MENU_ITEMS)) % len(config.PAUSE_MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            current_row_idx = (current_row_idx +
                               1) % len(config.PAUSE_MENU_ITEMS)
        elif key == 27 or key == ord('p'):
            del pause_win
            return "RESUME", current_row_idx
        elif key in [curses.KEY_ENTER, 10, 13]:
            action = config.PAUSE_MENU_ITEMS[current_row_idx]
            if action == "KEYBINDINGS":
                show_keybindings()
                parent_win.touchwin()
                parent_win.refresh()
                continue
            del pause_win
            return action, current_row_idx


def show_message(message, duration_seconds=1.0, wait=False, position='center'):
    msg_box_w, msg_box_h = len(message) + 4, 3
    if position == 'bottom':
        msg_win_y = curses.LINES - msg_box_h - 1
    else:
        msg_win_y = (curses.LINES - msg_box_h) // 2
    msg_win_x = (curses.COLS - msg_box_w) // 2

    msg_win = curses.newwin(msg_box_h, msg_box_w, msg_win_y, msg_win_x)
    _draw_fancy_border(msg_win)
    msg_win.addstr(1, 2, message)
    msg_win.refresh()

    if wait:
        msg_win.keypad(True)
        msg_win.getch()
    elif duration_seconds > 0:
        time.sleep(duration_seconds)

    if msg_win:
        msg_win.clear()
        msg_win.refresh()
        del msg_win


def show_centered_message(parent_window, message, duration):
    box_h, box_w = 5, len(message) + 6
    msg_win_y, msg_win_x = (
        curses.LINES - box_h) // 2, (curses.COLS - box_w) // 2
    msg_win = curses.newwin(box_h, box_w, msg_win_y, msg_win_x)
    _draw_fancy_border(msg_win)
    msg_win.addstr(box_h // 2, (box_w - len(message)) // 2, message)
    msg_win.refresh()
    time.sleep(duration)

    if msg_win:
        msg_win.clear()
        msg_win.refresh()
        del msg_win

# --- FULLSCREEN ART WINDOWS ---


def _create_art_window(title, art_lines):
    win = curses.newwin(config.SCREEN_HEIGHT, config.SCREEN_WIDTH, (curses.LINES -
                        config.SCREEN_HEIGHT) // 2, (curses.COLS - config.SCREEN_WIDTH) // 2)
    win.keypad(True)
    _draw_fancy_border(win, title)
    win_h, win_w = win.getmaxyx()
    for i, line in enumerate(art_lines):
        start_row = 4
        parts = line.split('@@')
        line_text = parts[0]
        attr = curses.color_pair(int(parts[1])) if len(
            parts) > 1 else curses.A_NORMAL
        win.addstr(start_row + i, (win_w - len(line_text)) //
                   2, line_text, attr)
    footer = "<< < Press ESC to return > >>"
    win.addstr(win_h - 3, (win_w - len(footer)) // 2, footer)
    win.refresh()
    while win.getch() != 27:
        pass
    del win


def show_scoreboard(scores):
    title = "HALL OF FAME"
    art = [
        "---------------------------------------------",
        f" {'RANK':^6} | {'PLAYER':^15} | {'SCORE':^15} @@{config.PAIR_SCORE_LEVEL}",
        "---------------------------------------------",]
    for i, (name, score) in enumerate(scores):
        art.append(f" {i+1:^6} | {name:<15} | {score:<15}")
    art.append("---------------------------------------------")
    _create_art_window(title, art)


def show_keybindings():
    title = "KEYBINDINGS"
    art = [
        "---------------------------------------------",
        f"{'GAMEPLAY CONTROLS':^45}@@{config.PAIR_SCORE_LEVEL}",
        "---------------------------------------------",
        "      UP ARROW    :  Move Ship Up", "      DOWN ARROW  :  Move Ship Down",
        "      LEFT ARROW  :  Move Ship Left", "      RIGHT ARROW :  Move Ship Right", "",
        "      P           :  Pause Game", "      AUTO-FIRE   :  No key needed",
        "---------------------------------------------",
        f"{'MENU CONTROLS':^45}@@{config.PAIR_SCORE_LEVEL}",
        "---------------------------------------------",
        "      ENTER       :  Confirm Selection", "      ESC         :  Return / Back / Exit",
        "---------------------------------------------",]
    _create_art_window(title, art)


def show_achievements():
    title = "ACHIEVEMENTS"
    art = [
        f"STATUS | {'ACHIEVEMENT':<20}| {'DESCRIPTION':<36} | {'REWARD':>8}",
        "-----------------------------------------------------------------------",]
    ach_list = list(achievement.ACHIEVEMENTS.items())
    for key, data in ach_list:
        status = "[X]" if data["unlocked"] else "[ ]"
        name, desc = data['name'], data['desc']
        if len(desc) > 34:
            desc = desc[:31] + "..."
        reward = f"{data['reward']} GC"
        line = f"  {status:<4} | {name:<20}| {desc:<36} | {reward:>8}"
        art.append(line)
    _create_art_window(title, art)


def show_shop(db, player_id):
    win = curses.newwin(config.SCREEN_HEIGHT, config.SCREEN_WIDTH, (curses.LINES -
                        config.SCREEN_HEIGHT) // 2, (curses.COLS - config.SCREEN_WIDTH) // 2)
    win.keypad(True)
    shop.init_shop_colors()
    current_category, current_selection = "ship_colors", 0
    while True:
        _draw_fancy_border(win, title=" S H O P ")
        win_h, win_w = win.getmaxyx()
        player_currency = db.get_player_currency(player_id)
        currency_text = f"Your Galactic Coins: {player_currency}"
        win.addstr(2, (win_w - len(currency_text)) // 2, currency_text)
        ship_tab, proj_tab = " [Ship Colors] ", " [Projectile Styles] "
        ship_tab_x, proj_tab_x = win_w//2 - len(ship_tab) - 2, win_w//2 + 2
        if current_category == "ship_colors":
            win.attron(curses.color_pair(config.PAIR_MENU_SELECTED))
        win.addstr(4, ship_tab_x, ship_tab)
        win.attroff(curses.color_pair(config.PAIR_MENU_SELECTED))
        if current_category == "projectile_styles":
            win.attron(curses.color_pair(config.PAIR_MENU_SELECTED))
        win.addstr(4, proj_tab_x, proj_tab)
        win.attroff(curses.color_pair(config.PAIR_MENU_SELECTED))
        items = shop.SHOP_ITEMS[current_category]
        y_offset = 7
        for i, item in enumerate(items):
            item_text = f"{item['name']:<20} | Price: {item['price']:<5}"
            attr = curses.color_pair(
                config.PAIR_MENU_SELECTED) if i == current_selection else curses.A_NORMAL
            item_x = (win_w - len(item_text)) // 2
            if y_offset + i*2 < win_h - 2:
                win.addstr(y_offset + i*2, item_x, item_text, attr)
        footer = "<< < ARROWS to navigate | ENTER to buy | ESC to exit > >>"
        win.addstr(win_h - 2, (win_w - len(footer)) // 2, footer)
        key = win.getch()
        if key == curses.KEY_UP:
            current_selection = (current_selection - 1 +
                                 len(items)) % len(items)
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % len(items)
        elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
            current_category = "projectile_styles" if current_category == "ship_colors" else "ship_colors"
            current_selection = 0
        elif key in [curses.KEY_ENTER, 10, 13]:
            selected_item = items[current_selection]
            result = shop.buy_item(
                db, player_id, current_category, selected_item['name'])
            show_message(result, 2, wait=False, position='bottom')
        elif key == 27:
            break
    del win
