import curses
import locale
from game import ui, config, game_loop, database, shop, achievement

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    stdscr.keypad(True)

    config.init_colors()
    shop.init_shop_colors()
    config.get_enemy_colors()

    db = database.Database()
    db.connect()

    main_win = curses.newwin(config.SCREEN_HEIGHT, config.SCREEN_WIDTH,
                             (curses.LINES - config.SCREEN_HEIGHT) // 2,
                             (curses.COLS - config.SCREEN_WIDTH) // 2)
    main_win.keypad(True)

    player_info = None
    while not player_info:
        auth_choice = ui.auth_menu(main_win)

        if auth_choice == "LOGIN":
            player_info = ui.login_screen(main_win, db)
        elif auth_choice == "REGISTER":
            registration_success = ui.register_screen(main_win, db)
            if registration_success:
                player_info = ui.login_screen(main_win, db)
        elif auth_choice == "QUIT":
            return

    if player_info is None:
        return
    player_id, username = player_info

    current_selection = 0
    while True:
        main_win.clear()
        main_menu_choice, current_selection = ui.menu_utils(
            main_win, current_selection, db.is_connected())

        if main_menu_choice == "START GAME" or main_menu_choice == "LOAD GAME":
            save_data = None
            if main_menu_choice == "LOAD GAME":
                save_data = db.load_game_state(player_id)
                if not save_data:
                    ui.show_message("No saved game found!", 2,
                                    wait=True, position='bottom')
                    continue

            game_loop.start_game(main_win, db, player_id, username, save_data)

        elif main_menu_choice == "ACHIEVEMENTS":
            unlocked_ids = db.get_player_achievements(player_id)
            achievement.load_player_achievements(unlocked_ids)
            ui.show_achievements()
        elif main_menu_choice == "SCOREBOARD":
            scores = db.get_high_scores()
            ui.show_scoreboard(scores)
        elif main_menu_choice == "SHOP":
            ui.show_shop(db, player_id)
        elif main_menu_choice == "KEYBINDINGS":
            ui.show_keybindings()
        elif main_menu_choice == "QUIT":
            break


if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("Your terminal window might be too small.")
        print(
            f"A size of at least {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT} is recommended.")
    except Exception as e:
        import traceback
        print("An unexpected error occurred:")
        traceback.print_exc()
