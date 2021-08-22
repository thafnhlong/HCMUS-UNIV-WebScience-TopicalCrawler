import model.baiviet as baiviet
import sqlite3
import config.env
from sqlite3 import Error
from utils.lock import synchronized

conn = None

def create_connection():
    global conn
    try:
        conn = sqlite3.connect(config.env.database_storage,check_same_thread=False)
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
        c.executescript(sql)
        return True
    except Error as e:
        print(e)
    return False

def create_schema():
    global conn
    sql_create_baiviet_table = baiviet.create_schema_bai_viet()+baiviet.create_indexes_bai_viet()

    return _create_table(sql_create_baiviet_table)
        
@synchronized    
def insert_value(table, value):
    global conn
    cur = conn.cursor()

    params = ""
    for i in range(len(value)):
        params+= "?,"
    params = params[:-1]

    cur.execute("insert into %s values (%s)"%(table,params), value)
    conn.commit()
    return cur.lastrowid


def fetch_value(sqlCommand, param=[]):
    global conn
    cur = conn.cursor()
    return cur.execute(sqlCommand,param)