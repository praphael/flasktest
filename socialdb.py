from enum import Enum

class DB(Enum):
    sqlite = 1
    postgres = 2

supportedDBs = { "sqlite" : DB.sqlite, "postgres" : DB.postgres }

def getConnection(db):
    if db == DB.sqlite:
        import sqlite3
        conn = sqlite3.connect("social.db")
    elif db == DB.postgres:
        import psycopg
        conn = psycopg.connect("host=127.0.0.1 port=5432 dbname=social user=ec2-user")
    else:
        raise Exception(f"unsupported database '{db}'")
    
    return conn
