# We import psycopg2 to work with PostgreSQL.
import psycopg2

# We import database settings from config.py.
from config import DB_CONFIG


def get_connection():
    # This function connects Python to the database.
    # **DB_CONFIG sends all settings to psycopg2.
    return psycopg2.connect(**DB_CONFIG)
