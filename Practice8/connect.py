import psycopg2
from config import load_config

def connect():
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        print("connection succesfully!")
        return conn
    
    except Exception as error:
        print("connection error", error)
        return None