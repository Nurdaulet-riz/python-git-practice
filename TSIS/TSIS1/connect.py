import psycopg2
from config import load_config


def connect():
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        return conn
    except Exception as error:
        print("Connection error:", error)
        return None
