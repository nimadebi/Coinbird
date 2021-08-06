import sqlite3
from sqlite3 import Error

db = "coinlist.db"

def create_connection():
    db_file = r"" + db
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_table():
    sql_create_coins_table = """ CREATE TABLE IF NOT EXISTS coins (
                                        coin text UNIQUE PRIMARY KEY,
                                        signal text NOT NULL
                                    ); """

    conn = create_connection()

    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(sql_create_coins_table)
        except Error as e:
            print(e)
    else:
        print("Error! Cannot create the db connection")


def add_coin(coin_ticker):
    conn = create_connection()
    with conn:
        sql = ''' INSERT or IGNORE INTO coins(coin, signal)
                      VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (coin_ticker, ""))
        conn.commit()


def remove_coin(coin_ticker):
    conn = create_connection()
    with conn:
        sql = 'DELETE FROM coins WHERE coin=?'
        cur = conn.cursor()
        cur.execute(sql, (coin_ticker,))
        conn.commit()

def query_all_coins():
    conn = create_connection()

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM coins")

        rows = cur.fetchall()
        return rows

def update_signal(coin_ticker, signal):
    conn = create_connection()

    with conn:
        sql = ''' UPDATE coins SET signal = ? WHERE coin = ?'''
        cur = conn.cursor()
        cur.execute(sql, (signal, coin_ticker))
        conn.commit()
