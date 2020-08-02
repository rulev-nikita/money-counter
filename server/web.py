import hashlib
import secrets
from flask import Flask, request, make_response, jsonify
from sql_code import get_token, check_user_exists, create_user, get_user

app = Flask(__name__)


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data["login"]
    password = data["password"]
    user = get_user(login)    
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
    if check_user_exists(login):
        return make_response(
            jsonify(err="User alredy exists"), 
            400
        )

    salt = secrets.token_hex(8)
    pass_hash = hash_password(password, salt)
    token = secrets.token_hex(64)
    create_user(login, pass_hash, salt, token)
    return jsonify(token=token)


@app.route('/addCategory', methods=['POST'])
def add_category():
    return ""


@app.route('/removeCategory', methods=['POST'])
def remove_category():
    return ""


@app.route('/categories', methods=['GET'])
def categories():
    return ""


@app.route('/csv', methods=['GET'])
def csv():
    return ""


@app.route('/expenses', methods=['POST'])
def expenses():
    return ""


if __name__ == '__main__':
    app.run(debug=True)