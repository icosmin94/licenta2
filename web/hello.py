import configparser

from flask import Flask, redirect, url_for, request, render_template, make_response
import json

from pymongo import MongoClient

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = json.loads(request.form['jsonData'])
        if data['action'] == 'login':
            return render_template('login_form.html')
        if data['action'] == 'signup':
            return render_template('signup_form.html')
    else:
        return render_template('index.html')


@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    users = db['users']
    data = json.loads(request.form['jsonData'])
    if data['action'] == 'login':
        form_fields = data['form']
        login_id = ""
        login_password = ""
        for field in form_fields:
            if field['name'] == 'login_id':
                login_id = field['value']
            if field['name'] == 'login_password':
                login_password = field['value']
    if data['action'] == 'signup':
        form_fields = data['form']
        signup_email=""
        signup_username=""
        signup_password=""
        for field in form_fields:
            if field['name'] == 'signup_email':
                signup_email = field['value']
            if field['name'] == 'signup_username':
                signup_username = field['value']
            if field['name'] == 'signup_password':
                signup_password = field['value']
        result = users.find_one({"$or": [{'user_name': signup_username}, {'user_email': signup_email}]})
        if result is None:
            users.insert_one({'user_name': signup_username, 'user_email': signup_email, 'password': signup_password})
            return render_template('response.html', message="ok")
        else:
            return render_template('response.html', message="error")

    return render_template('response.html', message="hfdh")

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config/config.ini')
    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    users = db['users']
    users.drop()

    app.run(debug=True, port=8000)
