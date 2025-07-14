import curses
import time
import random
from . import ui, config, shop, achievement
from .player import Player
from .level import Level, LEVEL_CONFIG
from .enemy import Enemy, ShootingEnemy
from .obstacle import Obstacle


def start_game(game_window, db, player_id, username, saved_data):
    h, w = game_window.getmaxyx()
    unlocked_achievements = db.get_player_achievements(player_id)
    achievement.load_player_achievements(unlocked_achievements)

    if saved_data:
        start_level, initial_score, initial_currency = saved_data[
            'level'], saved_data['score'], saved_data['currency']
    else:
        start_level, initial_score, initial_currency = 1, 0, 0

    player_cosmetics = shop.get_player_cosmetics(db, player_id)
    player = Player(game_window, username, initial_currency, player_cosmetics)
    player.score = initial_score

    current_level_num = start_level
    game_running_state = "RUNNING"
    total_kills_run, total_obstacles_destroyed_run = 0, 0

    currency_checkpoints = {1: 0}
    if saved_data:
        currency_checkpoints[start_level] = initial_currency
    elif start_level > 1:
        currency_checkpoints[start_level] = 0

    while current_level_num <= len(LEVEL_CONFIG) and game_running_state == "RUNNING":

        player.health = player.max_health
        player.currency = currency_checkpoints.get(current_level_num, 0)

        currency_at_this_attempt_start = player.currency

        player.x, player.y = w // 2 - player.width // 2, h - player.height - 3

        level_stats = {"kills": 0,
                       "obstacles_destroyed": 0, "damage_taken": False}

        level_result_state, score_from_level, currency_from_level = run_level(
            game_window, player, current_level_num, db, player_id, level_stats, currency_at_this_attempt_start
        )

        player.score = score_from_level
        player.currency = currency_from_level

        if level_result_state == "LEVEL_COMPLETE":
            total_kills_run += level_stats["kills"]
            total_obstacles_destroyed_run += level_stats["obstacles_destroyed"]
            check_achievements(db, player_id, player, "level_end", level_num=current_level_num,
                               level_stats=level_stats, run_kills=total_kills_run, run_obstacles=total_obstacles_destroyed_run)

            current_level_num += 1
            if current_level_num <= len(LEVEL_CONFIG):
                currency_checkpoints[current_level_num] = player.currency
            game_running_state = "RUNNING"

        elif level_result_state == "LEVEL_RESTART":
            game_running_state = "RUNNING"

        elif level_result_state == "QUIT_TO_MENU":
            game_running_state = "QUIT_TO_MENU"
            return

    if current_level_num > len(LEVEL_CONFIG) and game_running_state == "RUNNING":
        check_achievements(db, player_id, player, "game_complete")
        db.update_player_currency(player_id, player.currency)
        db.save_high_score(player_id, player.score)
        ui.show_centered_message(game_window, "V I C T O R Y !", 4)


def run_level(game_window, player, level_number, db, player_id, level_stats, currency_at_this_attempt_start):
    level = Level(game_window, level_number)
    level_config = LEVEL_CONFIG[level_number]

    h, w = game_window.getmaxyx()
    game_window.keypad(True)
    game_window.timeout(50)

    game_window.clear()
    game_window.border()
    game_window.refresh()
    level_type_text = "B O S S   E N C O U N T E R" if level_config[
        "type"] == "boss" else "S U R V I V E"
    ui.show_centered_message(
        game_window, f"L E V E L {level_number}: {level_type_text}", 2)

    game_window.clear()
    game_window.border()
    game_window.refresh()
    for i in range(3, 0, -1):
        ui.show_centered_message(game_window, str(i), 0.7)

    active_projectiles, enemy_projectiles = [], []
    notifications = []
    last_shot_time, level_start_time = 0, time.time()
    time_remaining = None

    def add_notification(text, duration=3):
        notifications.append({'text': text, 'expires': time.time() + duration})

    while True:
        key = game_window.getch()

        if key == ord('p') or key == 27:
            game_window.timeout(-1)
            action, _ = ui.pause_menu_utils(game_window)
            game_window.timeout(50)

            if action == "RESTART LEVEL":
                return "LEVEL_RESTART", player.score, currency_at_this_attempt_start
            elif action == "QUIT TO MAIN MENU":
                return "QUIT_TO_MENU", player.score, player.currency
            elif action == "SAVE GAME":
                db.save_game_state(player_id, level.level_number,
                                   player.score, player.currency)
                add_notification("Game Saved!")

            game_window.clear()
            game_window.border()
            game_window.refresh()

        player.move(key, game_window)

        current_time = time.time()
        if current_time - last_shot_time >= 0.25:
            active_projectiles.extend(player.shoot())
            last_shot_time = current_time

        # --- UPDATE ENTITIES ---
        for proj in active_projectiles[:]:
            proj.move(direction_multiplier=-1)
        for proj in enemy_projectiles[:]:
            proj.move(direction_multiplier=1)
        for enemy in level.active_enemies[:]:
            enemy.move(game_window)
        for obstacle in level.active_obstacles[:]:
            obstacle.move(game_window)
        if level.boss:
            level.boss.move(game_window)
            new_projectiles = level.boss.use_ability()
            if new_projectiles:
                enemy_projectiles.extend(new_projectiles)
        for enemy in level.active_enemies[:]:
            if isinstance(enemy, ShootingEnemy):
                proj = enemy.shoot()
                if proj:
                    enemy_projectiles.append(proj)

        # --- DESPAWN OFF-SCREEN ---
        for entity in active_projectiles[:] + enemy_projectiles[:] + level.active_enemies[:] + level.active_obstacles[:]:
            if entity.y >= h - 2 or entity.y < 1:
                if isinstance(entity, Enemy) and entity.y >= h-2:
                    player.take_damage(10)
                    level_stats["damage_taken"] = True
                if entity in active_projectiles:
                    active_projectiles.remove(entity)
                elif entity in enemy_projectiles:
                    enemy_projectiles.remove(entity)
                elif entity in level.active_enemies:
                    level.active_enemies.remove(entity)
                elif entity in level.active_obstacles:
                    level.active_obstacles.remove(entity)

        # --- SPAWN NEW ENTITIES ---
        if level_config["type"] == "survival" and current_time - level_start_time < level_config["respawn_until"]:
            if len(level.active_enemies) < level_config["enemy_cap"] and random.random() < 0.05:
                if level_number > 1 and random.random() < 0.4:
                    level.active_enemies.append(
                        ShootingEnemy(game_window, level_number))
                else:
                    level.active_enemies.append(
                        Enemy(game_window, level_number))
            if len(level.active_obstacles) < level_config["obstacle_cap"] and random.random() < 0.07:
                level.active_obstacles.append(Obstacle(game_window))

        # --- COLLISIONS ---
        for proj in active_projectiles[:]:
            if proj not in active_projectiles:
                continue
            for obj in level.active_obstacles[:]:
                if obj.is_collision(proj.x, proj.y):
                    player.currency += obj.currency_value
                    level_stats["obstacles_destroyed"] += 1
                    level.active_obstacles.remove(obj)
                    if proj in active_projectiles:
                        active_projectiles.remove(proj)
                    break
            if proj not in active_projectiles:
                continue
            for enemy in level.active_enemies[:]:
                if enemy.is_collision(proj.x, proj.y):
                    if enemy.take_damage(1):
                        player.score += 10
                        player.currency += enemy.currency_value
                        level.active_enemies.remove(enemy)
                        level_stats["kills"] += 1
                        check_achievements(
                            db, player_id, player, "kill", add_notification_func=add_notification)
                    if proj in active_projectiles:
                        active_projectiles.remove(proj)
                    break
            if proj not in active_projectiles:
                continue
            if level.boss and level.boss.is_collision(proj.x, proj.y):
                if level.boss.take_damage(1):  # Player projectile damage is 1
                    if level.boss.health <= 0:
                        player.score += 500
                        player.currency += level.boss.currency_value
                        return "LEVEL_COMPLETE", player.score, player.currency
                if proj in active_projectiles:
                    active_projectiles.remove(proj)

        for obj in level.active_obstacles[:]:
            if obj.is_collision(player.x + player.width//2, player.y + player.height//2):
                player.take_damage(obj.damage)
                level_stats["damage_taken"] = True
                level.active_obstacles.remove(obj)
        for proj in enemy_projectiles[:]:
            if player.y <= proj.y < player.y + player.height and player.x <= proj.x < player.x + player.width:
                player.take_damage(15)
                level_stats["damage_taken"] = True
                enemy_projectiles.remove(proj)
        for enemy in level.active_enemies[:]:
            if enemy.y + 1 > player.y and enemy.x < player.x + player.width and enemy.x + enemy.width > player.x:
                player.take_damage(20)
                level_stats["damage_taken"] = True
                level.active_enemies.remove(enemy)

        # --- WIN/LOSS CONDITIONS ---
        if player.health <= 0:
            return "LEVEL_RESTART", player.score, currency_at_this_attempt_start

        if level_config["type"] == "survival":
            if current_time - level_start_time >= level_config["duration"]:
                return "LEVEL_COMPLETE", player.score, player.currency
        elif level_config["type"] == "boss":
            time_remaining = level_config["time_limit"] - \
                (current_time - level_start_time)
            if time_remaining <= 0:
                add_notification("OUT OF TIME!")
                game_window.refresh()
                time.sleep(1.5)
                return "LEVEL_RESTART", player.score, currency_at_this_attempt_start

        # --- DRAWING ---
        game_window.clear()
        game_window.border()
        for entity in active_projectiles + enemy_projectiles + level.active_enemies + level.active_obstacles:
            entity.draw(game_window)
        if level.boss:
            level.boss.draw(game_window)
        player.draw(game_window)
        # Pass time_remaining for boss levels
        level.display_hud(game_window, player, time_remaining)
        notifications = [
            n for n in notifications if n['expires'] > current_time]
        for i, n in enumerate(notifications):
            game_window.addstr(
                1 + i, (w - len(n['text'])) // 2, n['text'], curses.A_REVERSE)
        game_window.refresh()


def check_achievements(db, player_id, player, event_type, add_notification_func=None, **kwargs):
    achievements_unlocked_now = []
    if not achievement.ACHIEVEMENTS["GEN_RICH"]["unlocked"] and player.currency >= 1000:
        achievements_unlocked_now.append("GEN_RICH")
    if event_type == "level_end":
        level_num = kwargs.get("level_num")
        level_stats = kwargs.get("level_stats")
        run_kills = kwargs.get("run_kills")
        run_obstacles = kwargs.get("run_obstacles")
        if not achievement.ACHIEVEMENTS["GEN_KILLS_10"]["unlocked"] and run_kills >= 10:
            achievements_unlocked_now.append("GEN_KILLS_10")
        if not achievement.ACHIEVEMENTS["GEN_KILLS_50"]["unlocked"] and run_kills >= 50:
            achievements_unlocked_now.append("GEN_KILLS_50")
        if not achievement.ACHIEVEMENTS["GEN_DESTROYER"]["unlocked"] and run_obstacles >= 25:
            achievements_unlocked_now.append("GEN_DESTROYER")
        if not achievement.ACHIEVEMENTS["GEN_NO_HIT"]["unlocked"] and not level_stats["damage_taken"]:
            achievements_unlocked_now.append("GEN_NO_HIT")
        if level_num == 1:
            if not achievement.ACHIEVEMENTS["LVL1_COMPLETE"]["unlocked"]:
                achievements_unlocked_now.append("LVL1_COMPLETE")
            if not achievement.ACHIEVEMENTS["LVL1_PERFECT"]["unlocked"] and player.health == player.max_health:
                achievements_unlocked_now.append("LVL1_PERFECT")
        elif level_num == 2:
            if not achievement.ACHIEVEMENTS["LVL2_COMPLETE"]["unlocked"]:
                achievements_unlocked_now.append("LVL2_COMPLETE")
            if not achievement.ACHIEVEMENTS["LVL2_DODGER"]["unlocked"] and level_stats["obstacles_destroyed"] < 5:
                achievements_unlocked_now.append("LVL2_DODGER")
        elif level_num == 3:
            if not achievement.ACHIEVEMENTS["BOSS1_DEFEAT"]["unlocked"]:
                achievements_unlocked_now.append("BOSS1_DEFEAT")
        elif level_num == 4:
            if not achievement.ACHIEVEMENTS["LVL4_COMPLETE"]["unlocked"]:
                achievements_unlocked_now.append("LVL4_COMPLETE")
        elif level_num == 5:
            if not achievement.ACHIEVEMENTS["BOSS2_DEFEAT"]["unlocked"]:
                achievements_unlocked_now.append("BOSS2_DEFEAT")
    for ach_id in achievements_unlocked_now:
        if not achievement.ACHIEVEMENTS[ach_id]["unlocked"]:
            achievement.ACHIEVEMENTS[ach_id]["unlocked"] = True
            reward = achievement.ACHIEVEMENTS[ach_id]["reward"]
            player.currency += reward
            db.save_player_achievement(player_id, ach_id)
            if add_notification_func:
                add_notification_func(
                    f"Achievement: {achievement.ACHIEVEMENTS[ach_id]['name']} (+{reward} GC)")
