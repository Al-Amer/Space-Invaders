import curses
import random
import time
import math
from . import config
from .movement import move_entity_down_with_delay
from .projectile import Projectile


class Enemy:
    def __init__(self, game_window, level):
        _, w = game_window.getmaxyx()
        self.enemy_types = ["~(8)~", "<=O=>", "<-*->",
                            "(-=0=-)", "(=^*^=)", "(-*T*-)"]
        self.sprite = random.choice(self.enemy_types)
        self.width = len(self.sprite)
        self.y = 2
        self.x = random.randint(1, w - self.width - 2)

        self.frame_counter = 0
        self.move_delay = 8

        self.health = 4
        self.currency_value = 4 * level

        config.get_enemy_colors()
        self.enemy_color_attr = curses.color_pair(
            random.choice([20, 21, 22, 23, 24]))

    def draw(self, game_window):
        try:
            game_window.addstr(self.y, self.x, self.sprite,
                               self.enemy_color_attr)
        except curses.error:
            pass

    def move(self, game_window):
        move_entity_down_with_delay(self)

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def is_collision(self, proj_x, proj_y):
        return self.y <= proj_y < self.y + 1 and self.x <= proj_x < self.x + self.width


class ShootingEnemy(Enemy):
    def __init__(self, game_window, level):
        super().__init__(game_window, level)
        self.health = 4
        self.y = random.randint(2, 6)
        self.move_delay = 12
        self.direction = random.choice([-1, 1])
        self.last_shot_time = time.time()
        self.shoot_interval = random.uniform(3, 6)

    def move(self, game_window):
        h, w = game_window.getmaxyx()
        self.frame_counter += 1
        if self.frame_counter >= self.move_delay:
            self.x += self.direction
            if self.x <= 1 or self.x >= w - self.width - 2:
                self.direction *= -1
            self.frame_counter = 0

    def shoot(self):
        if time.time() - self.last_shot_time > self.shoot_interval:
            self.last_shot_time = time.time()
            proj_x = self.x + self.width // 2
            proj_y = self.y + 1
            return Projectile(proj_x, proj_y, char="v")
        return None


class Boss(Enemy):
    def __init__(self, game_window, level):
        super().__init__(game_window, level)
        self.boss_color = curses.color_pair(config.PAIR_BOSS)
        self.direction = 1
        self.move_delay = 8
        self.y = 3
        self.max_health = 100
        self.health = self.max_health

    def draw(self, game_window):
        for i, line in enumerate(self.sprite):
            try:
                game_window.addstr(self.y + i, self.x, line, self.boss_color)
            except curses.error:
                pass
        h, w = game_window.getmaxyx()
        health_bar_width = w // 2
        health_percentage = self.health / self.max_health if self.max_health > 0 else 0
        current_health_width = int(health_bar_width * health_percentage)
        health_bar_y = 1
        health_bar_x = (w - health_bar_width) // 2
        game_window.addstr(health_bar_y, health_bar_x,
                           f"BOSS HP: [{'#' * current_health_width}{' ' * (health_bar_width - current_health_width)}]")

    def move(self, game_window):
        h, w = game_window.getmaxyx()
        self.frame_counter += 1
        if self.frame_counter >= self.move_delay:
            self.x += self.direction
            if self.x <= 1 or self.x >= w - self.width - 2:
                self.direction *= -1
            self.frame_counter = 0

    def is_collision(self, proj_x, proj_y):
        return self.y <= proj_y < self.y + len(self.sprite) and self.x <= proj_x < self.x + self.width


class BossLevel3(Boss):
    def __init__(self, game_window, level):
        super().__init__(game_window, level)
        self.sprite = ["<{\\__/}>", "{(0.0)}", "()_V_()"]
        self.width = max(len(s) for s in self.sprite)
        self.max_health = 220  # Previously 300
        self.health = self.max_health
        self.currency_value = 100
        self.last_ability_time = time.time()
        self.ability_cooldown = 2.0

    def use_ability(self):
        projectiles = []
        if time.time() - self.last_ability_time > self.ability_cooldown:
            self.last_ability_time = time.time()
            proj_y = self.y + len(self.sprite)
            center_x = self.x + self.width // 2

            ability = random.choice([1, 2, 3])
            if ability == 1:
                projectiles.append(Projectile(center_x - 3, proj_y, char="v"))
                projectiles.append(Projectile(center_x, proj_y, char="V"))
                projectiles.append(Projectile(center_x + 3, proj_y, char="v"))
            elif ability == 2:
                projectiles.append(Projectile(
                    center_x, proj_y, char="v", dy=1, dx=-0.5))
                projectiles.append(Projectile(
                    center_x, proj_y, char="v", dy=1, dx=0.5))
            elif ability == 3:
                projectiles.append(Projectile(
                    center_x, proj_y, char="!", dy=1.5))
        return projectiles


class BossLevel5(Boss):
    def __init__(self, game_window, level):
        super().__init__(game_window, level)
        self.sprite = ["/MMMMM\\", "|(o|o)|", "\\|VVV|/"]
        self.width = max(len(s) for s in self.sprite)
        self.max_health = 350  # Previously 500
        self.health = self.max_health
        self.currency_value = 100
        self.last_ability_time = time.time()
        self.ability_cooldown = 1.7

    def use_ability(self):
        projectiles = []
        if time.time() - self.last_ability_time > self.ability_cooldown:
            self.last_ability_time = time.time()
            proj_y = self.y + len(self.sprite)
            center_x = self.x + self.width // 2

            ability = random.choice([1, 2, 3, 4, 5])
            if ability == 1:
                for i in range(-2, 3):
                    projectiles.append(Projectile(
                        center_x + i * 3, proj_y, char="*"))
            elif ability == 2:
                for i in range(8):
                    angle = 2 * math.pi * i / 8
                    projectiles.append(Projectile(
                        center_x, self.y+1, char="o", dy=math.sin(angle), dx=math.cos(angle)))
            elif ability == 3:
                for i in range(1, 10):
                    projectiles.append(Projectile(
                        self.x-i, self.y+1, char="-", dy=0, dx=-1))
                    projectiles.append(Projectile(
                        self.x+self.width+i-1, self.y+1, char="-", dy=0, dx=1))
            elif ability == 4:
                for i in range(-1, 2):
                    projectiles.append(Projectile(
                        center_x, proj_y, char=">", dy=1, dx=i*0.3))
            elif ability == 5:
                for i in range(3):
                    projectiles.append(Projectile(
                        center_x - 2 + i * 2, proj_y + i*0.5, char="|"))
        return projectiles
