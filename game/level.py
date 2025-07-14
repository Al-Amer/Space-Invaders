import curses
from . import config

LEVEL_CONFIG = {
    1: {"type": "survival", "duration": 45, "enemy_cap": 5, "obstacle_cap": 4, "respawn_until": 40},
    2: {"type": "survival", "duration": 60, "enemy_cap": 8, "obstacle_cap": 6, "respawn_until": 55},
    3: {"type": "boss", "boss_class": "BossLevel3", "time_limit": 60},
    4: {"type": "survival", "duration": 75, "enemy_cap": 12, "obstacle_cap": 8, "respawn_until": 70},
    5: {"type": "boss", "boss_class": "BossLevel5", "time_limit": 90}
}


class Level:
    def __init__(self, game_window, level_number):
        self.game_window = game_window
        self.level_number = level_number
        self.level_data = LEVEL_CONFIG.get(level_number)
        self.active_enemies, self.active_obstacles = [], []
        self.boss = None

        if self.level_data.get("type") == "boss":
            from . import enemy
            boss_class = getattr(enemy, self.level_data["boss_class"])
            self.boss = boss_class(self.game_window, self.level_number)

    def display_hud(self, game_window, player, time_remaining=None):
        h, w = game_window.getmaxyx()
        hud_y_1, hud_y_2 = h - 3, h - 2
        if hud_y_1 < 0 or hud_y_2 < 0:
            return

        color = curses.color_pair(config.PAIR_SCORE_LEVEL)

        if time_remaining is not None:
            timer_text = f"TIME: {int(time_remaining)}"
            game_window.addstr(1, (w - len(timer_text)) // 2,
                               timer_text, curses.color_pair(config.PAIR_HEALTH_LOW))

        level_text = f"Level: {self.level_number}"
        score_text = f"Score: {player.score}"
        currency_text = f"GC: {player.currency}"

        game_window.addstr(hud_y_1, 2, level_text, color)
        game_window.addstr(hud_y_1, (w - len(score_text)) //
                           2, score_text, color)
        currency_x = w - len(currency_text) - 2
        if currency_x > 0:
            game_window.addstr(hud_y_1, currency_x, currency_text, color)

        health_text = f"Health: {player.health}/{player.max_health} "
        bar_width = w - len(health_text) - 5
        if bar_width < 0:
            bar_width = 0

        health_ratio = player.health / player.max_health if player.max_health > 0 else 0
        filled_width = int(bar_width * health_ratio)

        health_color_pair = config.PAIR_HEALTH_FULL
        if health_ratio < 0.6:
            health_color_pair = config.PAIR_HEALTH_MED
        if health_ratio < 0.3:
            health_color_pair = config.PAIR_HEALTH_LOW
        health_color = curses.color_pair(health_color_pair)

        game_window.addstr(hud_y_2, 2, health_text)
        if 2 + len(health_text) < w - 1:
            game_window.addstr(hud_y_2, 2 + len(health_text), '[' + (
                '#' * filled_width) + ('-' * (bar_width - filled_width)) + ']', health_color)
