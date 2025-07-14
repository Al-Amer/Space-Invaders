from .projectile import Projectile
import curses


class Player:
    def __init__(self, game_window, username, initial_currency, cosmetics):
        h, w = game_window.getmaxyx()

        self.username = username
        self.art = [
            "  /\\  ",
            " |==| ",
            "/_.._\\"
        ]
        self.height = len(self.art)
        self.width = max(len(line) for line in self.art)

        self.y = h - self.height - 3
        self.x = w // 2 - self.width // 2

        self.speed_x = 2
        self.speed_y = 1

        self.max_health = 100
        self.health = self.max_health
        self.score = 0
        self.currency = initial_currency

        self.ship_color_pair = cosmetics.get('ship_color_pair', 0)
        self.projectile_char = cosmetics.get('projectile_char', '.')
        self.projectile_color_pair = self.ship_color_pair

    def draw(self, game_window):
        h, w = game_window.getmaxyx()
        ship_color = curses.color_pair(self.ship_color_pair)
        for i, line in enumerate(self.art):
            target_y = self.y + i
            target_x = self.x
            if 0 <= target_y < h and 0 <= target_x + len(line) <= w:
                try:
                    game_window.addstr(target_y, target_x, line, ship_color)
                except curses.error:
                    pass

    def move(self, key, game_window):
        h, w = game_window.getmaxyx()
        bottom_boundary = h - 3 - self.height

        if key == curses.KEY_LEFT:
            self.x = max(1, self.x - self.speed_x)
        elif key == curses.KEY_RIGHT:
            self.x = min(w - self.width - 2, self.x + self.speed_x)
        elif key == curses.KEY_UP:
            self.y = max(1, self.y - self.speed_y)
        elif key == curses.KEY_DOWN:
            self.y = min(bottom_boundary, self.y + self.speed_y)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def shoot(self):
        projectile_y = self.y - 1
        projectile_left_x = self.x + 1
        projectile_right_x = self.x + self.width - 2

        left_projectile = Projectile(
            projectile_left_x, projectile_y, self.projectile_char, self.projectile_color_pair)
        right_projectile = Projectile(
            projectile_right_x, projectile_y, self.projectile_char, self.projectile_color_pair)

        return [left_projectile, right_projectile]
