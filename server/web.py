from flask import Flask

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    return ""


@app.route('/registration', methods=['POST'])
def registration():
    return ""


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