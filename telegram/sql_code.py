import sqlite3

import config



def add_category(user_id, category):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO categories (user_id, name) VALUES ({user_id}, "{category}");')
    conn.commit()
    conn.close()

def del_categories(user_id):
    print(user_id)
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM categories WHERE user_id = {user_id};')
    conn.commit()
    conn.close()
    print(2)

def show_categories(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT name FROM categories WHERE user_id = {user_id}')
    rows = cursor.fetchall()
    return rows 
    conn.commit()
    conn.close()


def data():
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM categories''')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.commit()
    conn.close()

def check_auth(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT DISTINCT user_id FROM categories WHERE user_id = {user_id}')
    row = cursor.fetchall()
    conn.commit()
    conn.close()
    if row:
        return True

#del_categories(332471895)
data()

#cursor.execute(f'SELECT * FROM categories WHERE')


# cursor.execute('''CREATE TABLE categories(
#    id INTEGER PRIMARY KEY,
#    user_id INTEGER,
#    name TEXT)''')

#cursor.execute('DROP TABLE categories')


# cursor.execute('PRAGMA table_info(categories)')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

#SELECT name FROM sqlite_master
# WHERE type='table'
# ORDER BY name;
