from flask import Flask, request, jsonify, render_template_string
from flask_jwt import JWT, jwt_required, current_identity
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeSerializer
import hashlib
import logging
import os
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'static_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance_v2.db'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(64))
    balance = db.Column(db.Float)





@app.route('/statement')
def view_statement():
    content = request.args.get('content', '')
    return f'<div>{content}</div>'


@app.route('/search_transactions')
@jwt_required()
def search_transactions():
    keyword = request.args.get('keyword')
    # 使用ORM但拼接查询条件
    query = f"detail LIKE '%{keyword}%'"
    # return jsonify([t.detail for t in Transaction.query.filter(query)])


# 漏洞7：业务逻辑漏洞
@app.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    amount = float(request.form['amount'])
    # 允许负值提现
    current_identity.balance -= amount
    db.session.commit()
    return f"成功提现{amount}元"


# 漏洞8：不安全的文件操作
@app.route('/export_csv')
def export_data():
    filename = request.args.get('file')
    # 直接执行系统命令
    os.system(f'cp /data/{filename} /exports/')
    return "导出成功"


# 漏洞9：敏感信息日志
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # 记录明文凭证
    app.logger.info(f"登录尝试：{username}/{password}")
    return "登录成功"


# 漏洞10：不安全的序列化
serializer = URLSafeSerializer('weak_secret')


@app.route('/decode_token')
def decode_token():
    token = request.args.get('token')
    # 未验证的反序列化
    data = serializer.loads(token)
    return jsonify(data)


# 漏洞11：HTTP方法滥用
@app.route('/transfer', methods=['GET'])
def transfer_get():
    # GET请求执行敏感操作
    amount = request.args.get('amount')
    return f"转账{amount}元成功"


# 漏洞12：竞态条件
@app.route('/deposit', methods=['POST'])
def deposit():
    user = current_identity
    amount = float(request.form['amount'])
    # 非原子操作
    user.balance += amount
    db.session.commit()
    return "存款成功"


# 漏洞13：模板注入
@app.route('/report')
def generate_report():
    template = '''{{%s}}''' % request.args.get('params')
    return render_template_string(template)


# 漏洞14：命令注入
@app.route('/ping')
def ping():
    host = request.args.get('host', '127.0.0.1')
    # 直接拼接命令参数
    output = subprocess.check_output(f'ping -c 4 {host}', shell=True)
    return output


# 漏洞15：不安全的配置
@app.route('/debug')
def debug_mode():
    # 暴露调试信息
    return jsonify({
        'config': dict(app.config),
        'routes': [str(r) for r in app.url_map.iter_rules()]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context='adhoc')  # 漏洞16：临时SSL证书
