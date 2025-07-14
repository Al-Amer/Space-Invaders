import json
import os
import hashlib
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# --- DATABASE CONFIGURATION (placeholders) ---
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"

LOCAL_DB_FILE = "gamedata.json"


class Database:
    def __init__(self):
        self.conn = None
        self.db_mode = "local"

    def connect(self):
        if PSYCOPG2_AVAILABLE:
            try:
                self.conn = psycopg2.connect(
                    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
                )
                self.db_mode = "postgres"
                self.create_tables()
            except psycopg2.OperationalError:
                self.db_mode = "local"
        if self.db_mode == "local":
            self.init_local_db()

    def is_connected(self):
        return self.db_mode == "postgres"

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_tables(self):
        if not self.is_connected():
            return
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL, currency INT DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS equipped_cosmetics (
                    player_id INT PRIMARY KEY REFERENCES players(id),
                    ship_color_name VARCHAR(50) DEFAULT 'Default Cyan',
                    projectile_style_name VARCHAR(50) DEFAULT 'Standard Bolt'
                );
                CREATE TABLE IF NOT EXISTS scores (
                    id SERIAL PRIMARY KEY, player_id INT REFERENCES players(id), score INT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_saves (
                    player_id INT PRIMARY KEY REFERENCES players(id), level INT, score INT, currency INT
                );
                CREATE TABLE IF NOT EXISTS player_achievements (
                    player_id INT REFERENCES players(id),
                    achievement_id VARCHAR(50) NOT NULL,
                    PRIMARY KEY (player_id, achievement_id)
                );
            """)
            self.conn.commit()

    def init_local_db(self):
        if not os.path.exists(LOCAL_DB_FILE) or os.path.getsize(LOCAL_DB_FILE) == 0:
            data = {"players": [], "scores": [], "saves": {},
                    "cosmetics": {}, "achievements": {}}
            with open(LOCAL_DB_FILE, 'w') as f:
                json.dump(data, f, indent=4)

    def register_player(self, username, password):
        password_hash = self._hash_password(password)
        if self.is_connected():
            try:
                with self.conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO players (username, password_hash, currency) VALUES (%s, %s, 0) RETURNING id", (username, password_hash))
                    player_id = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO equipped_cosmetics (player_id) VALUES (%s)", (player_id,))
                    self.conn.commit()
                return True
            except psycopg2.IntegrityError:
                self.conn.rollback()
                return False
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                if any(p['username'] == username for p in data['players']):
                    return False
                new_id = len(data.get('players', [])) + 1
                data.setdefault('players', []).append(
                    {"id": new_id, "username": username, "password_hash": password_hash, "currency": 0})
                data.setdefault('cosmetics', {})[str(new_id)] = {
                    "ship_color_name": "Default Cyan", "projectile_style_name": "Standard Bolt"}
                data.setdefault('achievements', {})[str(new_id)] = []
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
            return True

    def get_player(self, username, password):
        password_hash = self._hash_password(password)
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username FROM players WHERE username = %s AND password_hash = %s", (username, password_hash))
                return cur.fetchone()
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                for p in data['players']:
                    if p['username'] == username and p['password_hash'] == password_hash:
                        return p['id'], p['username']
            return None

    def get_player_currency(self, player_id):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT currency FROM players WHERE id = %s", (player_id,))
                result = cur.fetchone()
                return result[0] if result else 0
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                for p in data['players']:
                    if p['id'] == player_id:
                        return p.get('currency', 0)
        return 0

    def update_player_currency(self, player_id, new_amount):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "UPDATE players SET currency = %s WHERE id = %s", (new_amount, player_id))
                self.conn.commit()
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                for p in data['players']:
                    if p['id'] == player_id:
                        p['currency'] = new_amount
                        break
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

    def get_player_cosmetics(self, player_id):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT ship_color_name, projectile_style_name FROM equipped_cosmetics WHERE player_id = %s", (player_id,))
                res = cur.fetchone()
                return {"ship_color_name": res[0], "projectile_style_name": res[1]} if res else {}
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                return data.get('cosmetics', {}).get(str(player_id), {})

    def update_player_cosmetic(self, player_id, item_type, item_name):
        db_field = "ship_color_name" if item_type == "ship_colors" else "projectile_style_name"
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    f"UPDATE equipped_cosmetics SET {db_field} = %s WHERE player_id = %s", (item_name, player_id))
                self.conn.commit()
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                if str(player_id) in data.get('cosmetics', {}):
                    data['cosmetics'][str(player_id)][db_field] = item_name
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

    def save_high_score(self, player_id, score):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO scores (player_id, score) VALUES (%s, %s)", (player_id, score))
                self.conn.commit()
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                data.setdefault('scores', []).append(
                    {"player_id": player_id, "score": score})
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

    def get_high_scores(self):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT p.username, s.score FROM scores s JOIN players p ON s.player_id = p.id
                    ORDER BY s.score DESC LIMIT 10
                """)
                return cur.fetchall()
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                players = {p['id']: p['username']
                           for p in data.get('players', [])}
                scores = data.get('scores', [])
                scores.sort(key=lambda x: x['score'], reverse=True)
                return [(players.get(s['player_id'], "Unknown"), s['score']) for s in scores[:10]]

    def save_game_state(self, player_id, level, score, currency):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO game_saves (player_id, level, score, currency) VALUES (%s, %s, %s, %s)
                    ON CONFLICT (player_id) DO UPDATE SET level = EXCLUDED.level,
                    score = EXCLUDED.score, currency = EXCLUDED.currency;
                """, (player_id, level, score, currency))
                self.conn.commit()
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                data.setdefault('saves', {})[str(player_id)] = {
                    "level": level, "score": score, "currency": currency}
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

    def load_game_state(self, player_id):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT level, score, currency FROM game_saves WHERE player_id = %s", (player_id,))
                save = cur.fetchone()
                return {"level": save[0], "score": save[1], "currency": save[2]} if save else None
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                return data.get('saves', {}).get(str(player_id))

    def save_player_achievement(self, player_id, achievement_id):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO player_achievements (player_id, achievement_id) VALUES (%s, %s)
                    ON CONFLICT (player_id, achievement_id) DO NOTHING;
                """, (player_id, achievement_id))
                self.conn.commit()
        else:
            with open(LOCAL_DB_FILE, 'r+') as f:
                data = json.load(f)
                player_achievements = data.setdefault(
                    'achievements', {}).setdefault(str(player_id), [])
                if achievement_id not in player_achievements:
                    player_achievements.append(achievement_id)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)

    def get_player_achievements(self, player_id):
        if self.is_connected():
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT achievement_id FROM player_achievements WHERE player_id = %s", (player_id,))
                return [row[0] for row in cur.fetchall()]
        else:
            with open(LOCAL_DB_FILE, 'r') as f:
                data = json.load(f)
                return data.get('achievements', {}).get(str(player_id), [])
