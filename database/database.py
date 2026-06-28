import sqlite3

DB_PATH = "data/wordchain.db"


def connect():
    return sqlite3.connect(DB_PATH)


def setup_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            score INTEGER NOT NULL DEFAULT 0
        )
    """)

    score_columns = {
        "correct_words": "INTEGER NOT NULL DEFAULT 0",
        "wrong_words": "INTEGER NOT NULL DEFAULT 0",
        "repeated_words": "INTEGER NOT NULL DEFAULT 0",
        "hints_used": "INTEGER NOT NULL DEFAULT 0",
    }

    cursor.execute("PRAGMA table_info(scores)")
    existing_score_columns = [column[1] for column in cursor.fetchall()]

    for column_name, column_type in score_columns.items():
        if column_name not in existing_score_columns:
            cursor.execute(f"ALTER TABLE scores ADD COLUMN {column_name} {column_type}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id INTEGER PRIMARY KEY,
            game_language TEXT NOT NULL DEFAULT 'english',
            bot_language TEXT NOT NULL DEFAULT 'english',
            hint_cost INTEGER NOT NULL DEFAULT 10,
            correct_points INTEGER NOT NULL DEFAULT 5,
            wrong_points INTEGER NOT NULL DEFAULT -3,
            announcement_channel_id INTEGER,
            daily_announcement_time TEXT NOT NULL DEFAULT '00:00',
            timezone TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh'
        )
    """)

    conn.commit()
    conn.close()


def ensure_player(user_id, username):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO scores (
            user_id, username, score, correct_words, wrong_words, repeated_words, hints_used
        )
        VALUES (?, ?, 0, 0, 0, 0, 0)
    """, (user_id, username))

    cursor.execute("""
        UPDATE scores
        SET username = ?
        WHERE user_id = ?
    """, (username, user_id))

    conn.commit()
    conn.close()


def add_points(user_id, username, points, event_type=None):
    ensure_player(user_id, username)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE scores
        SET score = score + ?
        WHERE user_id = ?
    """, (points, user_id))

    if event_type == "correct":
        cursor.execute("UPDATE scores SET correct_words = correct_words + 1 WHERE user_id = ?", (user_id,))
    elif event_type == "wrong":
        cursor.execute("UPDATE scores SET wrong_words = wrong_words + 1 WHERE user_id = ?", (user_id,))
    elif event_type == "repeat":
        cursor.execute("UPDATE scores SET repeated_words = repeated_words + 1 WHERE user_id = ?", (user_id,))
    elif event_type == "hint":
        cursor.execute("UPDATE scores SET hints_used = hints_used + 1 WHERE user_id = ?", (user_id,))

    conn.commit()

    cursor.execute("SELECT score FROM scores WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()[0]

    conn.close()
    return score


def get_score(user_id, username):
    ensure_player(user_id, username)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM scores WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()[0]

    conn.close()
    return score


def get_stats(user_id, username):
    ensure_player(user_id, username)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score, correct_words, wrong_words, repeated_words, hints_used
        FROM scores
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "score": row[0],
        "correct_words": row[1],
        "wrong_words": row[2],
        "repeated_words": row[3],
        "hints_used": row[4],
    }


def get_leaderboard(limit=10):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, score
        FROM scores
        ORDER BY score DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def ensure_server_settings(guild_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO server_settings (guild_id)
        VALUES (?)
    """, (guild_id,))

    conn.commit()
    conn.close()


def get_server_settings(guild_id):
    ensure_server_settings(guild_id)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT game_language, bot_language, hint_cost, correct_points, wrong_points,
               announcement_channel_id, daily_announcement_time, timezone
        FROM server_settings
        WHERE guild_id = ?
    """, (guild_id,))

    row = cursor.fetchone()
    conn.close()

    return {
        "game_language": row[0],
        "bot_language": row[1],
        "hint_cost": row[2],
        "correct_points": row[3],
        "wrong_points": row[4],
        "announcement_channel_id": row[5],
        "daily_announcement_time": row[6],
        "timezone": row[7],
    }


def update_server_setting(guild_id, setting_name, setting_value):
    allowed_settings = {
        "game_language",
        "bot_language",
        "hint_cost",
        "correct_points",
        "wrong_points",
        "announcement_channel_id",
        "daily_announcement_time",
        "timezone",
    }

    if setting_name not in allowed_settings:
        raise ValueError(f"Invalid setting: {setting_name}")

    ensure_server_settings(guild_id)

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE server_settings SET {setting_name} = ? WHERE guild_id = ?",
        (setting_value, guild_id)
    )

    conn.commit()
    conn.close()