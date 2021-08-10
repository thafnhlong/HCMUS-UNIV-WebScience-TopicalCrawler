import sqlite3
from sqlite3 import Error
import config.env

conn = None

def create_connection():
    global conn
    try:
        conn = sqlite3.connect(config.env.database_storage)
    except Error as e:
        print(e)
    
    return conn

def close_connection():
    global conn
    conn.close()

def _create_table(sql):
    global conn
    try:
        c = conn.cursor()
        c.execute(sql)
        return True
    except Error as e:
        print(e)
    return False

def create_schema():
    global conn
    sql_create_baiviet_table = """ CREATE TABLE IF NOT EXISTS baiviet (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        page_source text
                                    ); """
    return _create_table(sql_create_baiviet_table)
        
    
def insert_value(table, value):
    global conn
    cur = conn.cursor()
    cur.execute("insert into %s values (?, ?, ?)"%table, value)
    conn.commit()
    return cur.lastrowid


def fetch_value(sqlCommand, param=[]):
    global conn
    cur = conn.cursor()
    return cur.execute(sqlCommand,param)