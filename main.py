import sqlite3

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()
    return result is not None

print(login("admin' -- ", "any_password"))