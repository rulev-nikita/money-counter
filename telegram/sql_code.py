import sqlite3

import config



def add_category(user_id, category):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO categories (user_id, name, value, description) VALUES ({user_id}, "{category}");')
    conn.commit()
    conn.close()

def del_categories(user_id):        
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM categories WHERE user_id = {user_id};')
    conn.commit()
    conn.close()

def show_categories(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT name FROM categories WHERE user_id = {user_id}')
    rows = cursor.fetchall()
    print(rows) 
    conn.commit()
    conn.close()
    return rows

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

def add_expenses(user_id, name, value, description, time):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute(f'SELECT id FROM categories WHERE name = "{name}" AND user_id = {user_id}')
    category_id = cursor.fetchall()
    conn.commit()
    cursor.execute(f'INSERT INTO expenses (category_id, description, value, time) VALUES ({category_id[0][0]}, "{description}", {value}, "{time}")')
    conn.commit()
    conn.close()

def data_for_export(user_id):
    conn = sqlite3.connect(config.my_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    data = cursor.fetchall()
    conn.commit()
    print(data)
    
    for i in range(len(data)):
        data[i] = list(data[i])
        print(data[i])
        print(data[i][1])
        cursor.execute(f'SELECT name FROM categories WHERE user_id = {user_id} and id = {data[i][1]}')
        name = cursor.fetchall()
        data[i][1] = name[0][0]
        data[i].pop(0)
        conn.commit()
    
    print(data)
    conn.close()
    return data
#del_categories(332471895)
#data()

#cursor.execute(f'SELECT * FROM categories WHERE')

# conn = sqlite3.connect(config.my_db)
# cursor = conn.cursor()
# cursor.execute('''CREATE TABLE expenses(
#    id INTEGER PRIMARY KEY,
#    category_id INTEGER,
#    user_id INTEGER,
#    description TEXT)''')
# conn.commit()
# conn.close()

#cursor.execute('DROP TABLE expenses')


# cursor.execute('PRAGMA table_info(expenses)')
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

#SELECT name FROM sqlite_master
# WHERE type='table'
# ORDER BY name;
