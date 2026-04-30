# This file works with PostgreSQL.
# It creates tables, saves game results, and reads the leaderboard.

import psycopg2
from psycopg2 import sql
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def get_connection(dbname=DB_NAME):
    # Connect to PostgreSQL database.
    # dbname is snake_db by default.
    return psycopg2.connect(
        dbname=dbname,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def create_database_if_missing():
    # Step 1: Try to connect to snake_db.
    # If it works, the database already exists.
    try:
        conn = get_connection()
        conn.close()
        return
    except Exception:
        # If connection fails, we will create the database below.
        pass

    # Step 2: Connect to the default PostgreSQL database.
    admin = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    # Autocommit is needed because CREATE DATABASE cannot run inside a normal transaction.
    admin.autocommit = True
    cur = admin.cursor()

    # Step 3: Check if snake_db exists.
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    # Step 4: If snake_db does not exist, create it.
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))

    # Step 5: Close connection.
    cur.close()
    admin.close()


def init_db():
    # This function prepares the database before the game starts.
    create_database_if_missing()

    conn = get_connection()
    cur = conn.cursor()

    # Create table for players.
    # Each username must be unique.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
        """
    )

    # Create table for game sessions.
    # It stores score, level, and date of the game.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id),
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
        """
    )

    # Save changes and close database connection.
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    # Remove spaces and limit username to 50 characters.
    # If username is empty, use "Player".
    username = username.strip()[:50] or "Player"

    conn = get_connection()
    cur = conn.cursor()

    # Step 1: Try to find this player in the database.
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()

    if row:
        # If player exists, take the player id.
        player_id = row[0]
    else:
        # If player does not exist, create a new player.
        cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


def save_result(username, score, level):
    # Save one finished game result.
    player_id = get_or_create_player(username)

    conn = get_connection()
    cur = conn.cursor()

    # Insert score and level into game_sessions table.
    cur.execute(
        "INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s, %s, %s)",
        (player_id, score, level),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_personal_best(username):
    # Find the best score for one player.
    conn = get_connection()
    cur = conn.cursor()

    # MAX finds the biggest score.
    # COALESCE returns 0 if the player has no games yet.
    cur.execute(
        """
        SELECT COALESCE(MAX(gs.score), 0)
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        WHERE p.username = %s
        """,
        (username,),
    )

    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best


def get_top_scores(limit=10):
    # Get the best results for the leaderboard.
    conn = get_connection()
    cur = conn.cursor()

    # Sort results by score, then by level, then by date.
    cur.execute(
        """
        SELECT p.username, gs.score, gs.level_reached, TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI')
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
        LIMIT %s
        """,
        (limit,),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
