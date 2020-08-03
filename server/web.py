import hashlib
import secrets
from flask import Flask, request, make_response, jsonify, send_file
import sql_code as sql
import config
import datetime

from util import data_to_csv_file

app = Flask(__name__)


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data["login"]
    password = data["password"]
    user = sql.get_user(login=login)    
    if not user:
        return make_response(
            jsonify(err="User does not exists"), 
            404
        )
    pass_hash = hash_password(password, user["salt"])
    if pass_hash != user["password"]:
        return make_response(
            jsonify(err="Wrong password"), 
            400
        )
    return jsonify(token=user["token"])


@app.route('/registration', methods=['POST'])
def registration():
    data = request.json
    login = data["login"]
    password = data["password"]
    if sql.check_user_exists(login):
        return make_response(
            jsonify(err="User alredy exists"), 
            400
        )

    salt = secrets.token_hex(8)
    pass_hash = hash_password(password, salt)
    token = secrets.token_hex(64)
    sql.create_user(login, pass_hash, salt, token)
    user = sql.get_user(login=login)
    for c in config.basic_categories:
        sql.add_category(user["id"], c)
    return jsonify(token=token)


@app.route('/addCategory', methods=['POST'])
def add_category():
    data = request.json
    token = data.get("token", "")
    user = sql.get_user(token=token)
    if not token or not user:
        return make_response(
            jsonify(err="Invalid token"), 
            400
        )
    category = data.get("category")
    if not category:
        return make_response(
            jsonify(err="category should be provided"), 
            400
        )
    sql.add_category(user["id"], category)
    return "", 200

@app.route('/removeCategory', methods=['POST'])
def remove_category():
    data = request.json
    token = data.get("token", "")
    user = sql.get_user(token=token)
    if not token or not user:
        return make_response(
            jsonify(err="Invalid token"), 
            400
        )
    category = data.get("category")
    if not category:
        return make_response(
            jsonify(err="category should be provided"), 
            400
        )
    sql.del_category(user["id"], category)
    return "", 200

@app.route('/categories', methods=['GET'])
def categories():
    token = request.args.get("token", "")
    user = sql.get_user(token=token)
    if not token or not user:
        return make_response(
            jsonify(err="Invalid token"), 
            400
        )
    res = sql.show_categories(user["id"])
    print(res, user["id"])
    return jsonify(list(map(lambda x: x[0], res)))

@app.route('/csv', methods=['GET'])
def csv():
    token = request.args.get("token", "")
    user = sql.get_user(token=token)
    if not token or not user:
        return make_response(
            jsonify(err="Invalid token"), 
            400
        )
    data = sql.data_for_export(user["id"])
    name = data_to_csv_file(user["id"], data)
    return send_file(name)

@app.route('/expenses', methods=['POST'])
def expenses():
    data = request.json
    token = data.get("token", "")
    user = sql.get_user(token=token)
    if not token or not user:
        return make_response(
            jsonify(err="Invalid token"), 
            400
        )
    category = data.get("category")
    value = data.get("value")
    description = data.get("description", "")
    time = data.get("time")
    if not category or not time or not value:
        return make_response(
            jsonify(err="category, value, time should be provided"), 
            400
        )
    try: 
        datetime.datetime.strptime(time, "%d.%m.%Y").date()
    except ValueError:
        return make_response(
            jsonify(err="Wrong date format. '%d.%m.%Y' should be provided"),
            400
        )
    try:
        value = float(value)
    except ValueError:
        return make_response(
            jsonify(err="Wrong value. should be number"),
            400
        )
    print(user["id"], category, value, description, time)
    sql.add_expenses(user["id"], category, value, description, time)
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)