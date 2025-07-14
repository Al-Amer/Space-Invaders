import curses


class Projectile:
    def __init__(self, x, y, char=".", color_pair=None, dy=1, dx=0):
        self.x = float(x)
        self.y = float(y)
        self.char = char
        self.color_pair = color_pair if color_pair else 0
        self.dy = dy  # Vertical speed/direction
        self.dx = dx  # Horizontal speed/direction

    def move(self, direction_multiplier=1):
        self.y += self.dy * direction_multiplier
        self.x += self.dx * direction_multiplier

    def draw(self, game_window):
        draw_y, draw_x = int(self.y), int(self.x)
        if draw_y >= 0:
            try:
                color = curses.color_pair(
                    self.color_pair) if self.color_pair else 0
                game_window.addstr(draw_y, draw_x, self.char, color)
            except curses.error:
                pass

    def is_off_screen(self, window_height, window_width):
        return not (1 <= self.y < window_height - 1 and 1 <= self.x < window_width - 1)
