import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        conn.commit()
        cur.close()
    except Exception as error:
        print("Database init error:", error)
    finally:
        if conn:
            conn.close()


def get_or_create_player(username):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO players(username)
            VALUES (%s)
            ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username
            RETURNING id;
            """,
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return player_id
    except Exception as error:
        print("Player save error:", error)
        return None
    finally:
        if conn:
            conn.close()


def save_game_session(username, score, level_reached):
    player_id = get_or_create_player(username)
    if player_id is None:
        return

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO game_sessions(player_id, score, level_reached)
            VALUES (%s, %s, %s);
            """,
            (player_id, score, level_reached)
        )
        conn.commit()
        cur.close()
    except Exception as error:
        print("Session save error:", error)
    finally:
        if conn:
            conn.close()


def get_personal_best(username):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COALESCE(MAX(gs.score), 0)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s;
            """,
            (username,)
        )
        best = cur.fetchone()[0]
        cur.close()
        return best
    except Exception as error:
        print("Personal best error:", error)
        return 0
    finally:
        if conn:
            conn.close()


def get_leaderboard(limit=10):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.username, gs.score, gs.level_reached,
                   TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI') AS played_at
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
            LIMIT %s;
            """,
            (limit,)
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Exception as error:
        print("Leaderboard error:", error)
        return []
    finally:
        if conn:
            conn.close()
