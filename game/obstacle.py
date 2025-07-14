import curses
import random
from . import config
from .movement import move_entity_down_with_delay


class Obstacle:
    def __init__(self, game_window):
        _, w = game_window.getmaxyx()
        self.obstacle_types = ["<->", "###", "oOo", "(@)"]
        self.sprite = random.choice(self.obstacle_types)
        self.width = len(self.sprite)

        self.y = 2
        self.x = random.randint(1, w - self.width - 2)

        self.frame_counter = 0
        self.move_delay = random.randint(2, 4)
        self.damage = 10
        self.color_attr = curses.color_pair(config.PAIR_OBSTACLE)

        self.currency_value = 2

    def draw(self, game_window):
        try:
            game_window.addstr(self.y, self.x, self.sprite, self.color_attr)
        except curses.error:
            pass

    def move(self, game_window):
        move_entity_down_with_delay(self)

    def is_collision(self, x, y):
        return self.y <= y < self.y + 1 and self.x <= x < self.x + self.width
