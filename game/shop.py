import curses
from . import config

SHOP_ITEMS = {
    "ship_colors": [
        {"name": "Default Cyan", "price": 0, "color_id": config.PAIR_PLAYER_SHIP},
        {"name": "Emerald Ghost", "price": 1500, "color_id": 30},
        {"name": "Ruby Raider", "price": 2000, "color_id": 31},
        {"name": "Golden Star", "price": 3000, "color_id": 32},
    ],
    "projectile_styles": [
        {"name": "Standard Bolt", "price": 0, "char": "."},
        {"name": "Laser Beam", "price": 2500, "char": "|"},
        {"name": "Star Shot", "price": 3500, "char": "*"},
        {"name": "Heavy Slug", "price": 5000, "char": "O"},
    ]
}


def init_shop_colors():
    """Initializes the custom color pairs for shop items."""
    try:
        curses.init_pair(30, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(31, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(32, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    except:
        pass


def buy_item(db, player_id, item_type, item_name):
    """Handles the logic for a player buying an item."""
    item_to_buy = None
    for item in SHOP_ITEMS.get(item_type, []):
        if item['name'] == item_name:
            item_to_buy = item
            break

    if not item_to_buy:
        return "Item not found."

    player_currency = db.get_player_currency(player_id)
    if player_currency < item_to_buy['price']:
        return "Not enough Galactic Coins."

    new_currency = player_currency - item_to_buy['price']
    db.update_player_currency(player_id, new_currency)
    db.update_player_cosmetic(player_id, item_type, item_name)

    return f"Purchase successful! You equipped {item_name}."


def get_player_cosmetics(db, player_id):
    """
    Loads the player's equipped cosmetics from the database
    and returns the actual data from SHOP_ITEMS.
    """
    equipped = db.get_player_cosmetics(player_id)
    ship_color = SHOP_ITEMS['ship_colors'][0]
    projectile_style = SHOP_ITEMS['projectile_styles'][0]

    for item in SHOP_ITEMS['ship_colors']:
        if item['name'] == equipped.get('ship_color_name'):
            ship_color = item
            break
    for item in SHOP_ITEMS['projectile_styles']:
        if item['name'] == equipped.get('projectile_style_name'):
            projectile_style = item
            break

    return {"ship_color_pair": ship_color['color_id'], "projectile_char": projectile_style['char']}
