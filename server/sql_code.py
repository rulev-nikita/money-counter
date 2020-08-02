import sqlite3

import config

def add_category(user_id, category):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO categories (user_id, name) VALUES (?, ?);''', (user_id, category,))
    conn.commit()
    conn.close()

def del_categories(user_id):        
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM categories WHERE user_id = ?;''', (user_id,))
    conn.commit()
    conn.close()

def show_categories(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM categories WHERE user_id = ?''', (user_id,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def check_auth(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT DISTINCT user_id FROM categories WHERE user_id = ?''', (user_id,))
    row = cursor.fetchall()
    conn.commit()
    conn.close()
    if row:
        return True

def add_expenses(user_id, name, value, description, time):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT id FROM categories WHERE name = ? AND user_id = ?''', (name, user_id,))
    category_id = cursor.fetchall()
    conn.commit()
    cursor.execute('''INSERT INTO expenses (category_id, description, value, "time") VALUES (?, ?, ?, ?)''', (category_id[0][0], description, value, time,))
    conn.commit()
    conn.close()

def data_for_export(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM expenses WHERE category_id IN (SELECT id FROM categories WHERE user_id = ?)''', (user_id,))
    data = cursor.fetchall()
    conn.commit()
    print(data)
    
    for i in range(len(data)):
        data[i] = list(data[i])
        print(data[i])
        print(data[i][1])
        cursor.execute('''SELECT name FROM categories WHERE user_id = ? and id = ?''', (user_id, data[i][1],))
        name = cursor.fetchall()
        data[i][1] = name[0][0]
        data[i].pop(0)
        conn.commit()
    print(data)
    conn.close()
    return data


def get_token(login, password):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT token FROM web_users WHERE login = ? AND password = ?''', (login, password,))
    token = cursor.fetchone()
    conn.commit()
    conn.close()
    return token

def check_user_exists(login):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(id) FROM web_users WHERE login = ?''', (login,))
    cnt = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return cnt != 0

def create_user(login, password, salt, token):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO web_users (login, password, salt, token, id)
        VALUES (?, ?, ?, ?, (SELECT MIN(id) - 1 FROM web_users));
        ''', (login, password, salt, token)
    )
    conn.commit()
    conn.close()

def get_user(login):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT login, password, salt, token, id
        FROM web_usres
        WHERE login = ?
        ''', (login,)
    )
    row = cursor.fetchone()
    user = {
        "login": login,
        "password": row[1],
        "salt": row[2],
        "token": row[3],
        "id": row[4],
    }
    conn.commit()
    conn.close()
    return user