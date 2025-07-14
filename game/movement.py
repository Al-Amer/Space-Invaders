import curses


def check_bounds(x, y, width, height, window_w, window_h):
    return (1 <= x <= window_w - 2 - width and
            4 <= y <= window_h - 2 - height)


def move_entity_left(entity, game_window):
    if entity.x > 1:
        entity.x -= 1


def move_entity_right(entity, game_window):
    _, w = game_window.getmaxyx()
    if entity.x < w - 2 - entity.width:
        entity.x += 1


def move_entity_up(entity, game_window):
    if entity.y > 27:
        entity.y -= 1


def move_entity_down(entity, game_window):
    h, _ = game_window.getmaxyx()
    if entity.y < h - 2 - entity.height:
        entity.y += 1


def move_entity_down_with_delay(entity):
    entity.frame_counter += 1
    if entity.frame_counter >= entity.move_delay:
        entity.y += 1
        entity.frame_counter = 0


def handle_entity_movement(key, entity, game_window):
    if key == curses.KEY_LEFT:
        move_entity_left(entity, game_window)
    elif key == curses.KEY_RIGHT:
        move_entity_right(entity, game_window)
    elif key == curses.KEY_UP:
        move_entity_up(entity, game_window)
    elif key == curses.KEY_DOWN:
        move_entity_down(entity, game_window)
