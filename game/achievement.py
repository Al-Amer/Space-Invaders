ACHIEVEMENTS = {
    # General Achievements
    "GEN_KILLS_10": {"name": "Rookie Slayer", "desc": "Defeat 10 enemies in a single run.", "unlocked": False, "reward": 75},
    "GEN_KILLS_50": {"name": "Veteran Slayer", "desc": "Defeat 50 enemies in a single run.", "unlocked": False, "reward": 200},
    "GEN_RICH": {"name": "Coin Collector", "desc": "Hold over 1000 currency at once.", "unlocked": False, "reward": 100},
    "GEN_DESTROYER": {"name": "Space Janitor", "desc": "Destroy 25 obstacles in a single run.", "unlocked": False, "reward": 150},
    "GEN_NO_HIT": {"name": "Untouchable", "desc": "Complete any survival level without taking damage.", "unlocked": False, "reward": 350},

    # Level-Specific Achievements
    "LVL1_COMPLETE": {"name": "Sector 1 Secure", "desc": "Survive the onslaught in Level 1.", "unlocked": False, "reward": 100},
    "LVL1_PERFECT": {"name": "Perfect Start", "desc": "Beat Level 1 with full health.", "unlocked": False, "reward": 150},

    "LVL2_COMPLETE": {"name": "Sector 2 Secure", "desc": "Survive the gauntlet in Level 2.", "unlocked": False, "reward": 200},
    "LVL2_DODGER": {"name": "Matrix Mode", "desc": "Survive Level 2 while destroying less than 5 obstacles.", "unlocked": False, "reward": 250},

    "BOSS1_DEFEAT": {"name": "Big Game Hunter", "desc": "Defeat the boss of Level 3.", "unlocked": False, "reward": 500},

    "LVL4_COMPLETE": {"name": "Sector 4 Secure", "desc": "Survive the chaos in Level 4.", "unlocked": False, "reward": 400},

    "BOSS2_DEFEAT": {"name": "Galaxy Saved!", "desc": "Defeat the final boss of Level 5.", "unlocked": False, "reward": 1000},
}


def load_player_achievements(unlocked_ids):
    """
    Updates the global ACHIEVEMENTS dictionary based on the list of
    unlocked achievement IDs for the current player.
    """
    for key, data in ACHIEVEMENTS.items():
        data['unlocked'] = True if key in unlocked_ids else False
