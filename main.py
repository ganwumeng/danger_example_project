from flask import Flask, request, jsonify
import sqlite3
import hashlib
import os

app = Flask(__name__)

conn = sqlite3.connect('vulnerable.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
conn.commit()

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    hashed_pw = hashlib.md5(password.encode()).hexdigest()

    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed_pw}')"
    
    try:
        cursor.execute(query)
        conn.commit()
        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.values.get('username')
    password = request.values.get('password')

    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashlib.md5(password.encode()).hexdigest()}'"
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            session_id = hashlib.md5(f"{username}{os.urandom(4)}".encode()).hexdigest()
            return jsonify({"message": "登录成功", "session": session_id})
        else:
            check_user = f"SELECT * FROM users WHERE username = '{username}'"
            cursor.execute(check_user)
            if cursor.fetchone():
                return jsonify({"error": "密码错误"}), 401
            else:
                return jsonify({"error": "用户不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    user_id = request.form.get('user_id')
    os.system(f"rm /tmp/user_{user_id}.data")
    return jsonify({"message": "用户数据已删除"})

@app.route('/search')
def search_user():
    keyword = request.args.get('keyword')
    try:
        query = f"SELECT * FROM users WHERE username LIKE '%{keyword}%'"
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
