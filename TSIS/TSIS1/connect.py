import psycopg2
from config import DB_CONFIG


def connect():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("Connection error:", e)
        return None