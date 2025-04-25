import sqlite3

def get_connection():
    return sqlite3.connect("shop.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        registered TEXT
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT,
        password TEXT,
        price INTEGER,
        is_sold INTEGER DEFAULT 0
    )
    """)

   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        account_id INTEGER,
        date TEXT,
        paid INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    )
    """)

  
    accounts_data = [
        ("aeg25qt6q_2574", "playerok.com/profile/AEG", 300),
        ("playerok_aeg2142", "playerok.com/profile/AEG", 400),
        ("Diamond90101", "Thomas98027300", 500),
        ("jujuleboss13", "inpi2Sb1", 600),
        ("wf6ju3bf5wc3", "qKnh6N9SLiMxyvXVX36d", 700),
        ("crazycatwastaken", "JX89pBI4Pb7", 800),
        ("jlcc6436427", "fhxL1wIaHoR4", 900),
        ("nmsukt191", "batzaza191", 1000),
        ("sheerheartattack420", "70games.net166", 1100),
        ("adtlix", "retii1337+", 1200),
        ("amandabrooks7t", "OXPRVkRFs91999", 1000),
        ("stickyman69", "floci1234567", 900),
    ]

    for login, password, price in accounts_data:
        cursor.execute("INSERT INTO accounts (login, password, price, is_sold) VALUES (?, ?, ?, 0)",
                       (login, password, price))

    conn.commit()
    conn.close()
