import configparser
import os
from shutil import copyfile, copy

import time
from flask import Flask, redirect, url_for, request, render_template, make_response, session, jsonify

import json
from pprint import pprint

from pymongo import MongoClient

from create_topics import create_and_store_topics
from events import process_events, get_events
from load_tweets import load_tweets

app = Flask(__name__)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_name', None)
    return render_template('response.html', message="ok")


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = json.loads(request.form['jsonData'])
        if data['action'] == 'login':
            return render_template('login_form.html')
        if data['action'] == 'signup':
            return render_template('signup_form.html')
    else:
        if session.get('user_name'):
            return redirect(url_for('board'))
        else:
            return render_template('index.html')


@app.route('/process_events', methods=['POST'])
def process_events_call():
    process_events(session.get('user_name'))
    return render_template('response.html', message="ok")


@app.route('/show_events', methods=['POST'])
def show_events_call():
    result = get_events(session.get('user_name'))
    return jsonify(result)


@app.route('/create_topics', methods=['POST'])
def create_topics_call():
    create_and_store_topics(session.get('user_name'))
    return render_template('response.html', message="ok")


@app.route('/load_tweets', methods=['POST'])
def load_tweets_call():
    if request.files['upload'].filename == '':
        return render_template('response.html', message="notok")
    f = request.files['upload']
    filename = "../users/" + session.get('user_name') + "/files/"+f.filename
    f.save(filename)
    load_tweets(session.get('user_name'), filename)
    return render_template('response.html', message="ok")


@app.route('/board', methods=['POST', 'GET'])
def board():
    return render_template('board.html', user=session['user_name'])


@app.route('/get_config', methods=['POST'])
def get_config():
    with open('../users/' + session.get('user_name') + '/config.json') as config_file:
        config = json.load(config_file)
    return jsonify(config)


@app.route('/set_config', methods=['POST'])
def set_config():
    data = json.loads(request.form['jsonData'])
    with open('../users/' + session.get('user_name') + '/config.json', 'w') as outfile:
        json.dump(data, outfile)
    return render_template('response.html', message="ok")


@app.route('/config', methods=['POST', 'GET'])
def config():
    config['user'] = session.get('user_name')
    return render_template('config.html', user=session['user_name'])


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
        result = users.find_one({"$and": [{"$or": [{'user_name': login_id}, {'user_email': login_id}]}, {'password': login_password}]})
        if result is None:
            return render_template('response.html', message="=error")
        else:
            session['user_name'] = result['user_name']
            return render_template('response.html', message="ok")
    if data['action'] == 'signup':
        form_fields = data['form']
        signup_email = ""
        signup_username = ""
        signup_password = ""
        for field in form_fields:
            if field['name'] == 'signup_email':
                signup_email = field['value']
            if field['name'] == 'signup_username':
                signup_username = field['value']
            if field['name'] == 'signup_password':
                signup_password = field['value']
        result = users.find_one({"$or": [{'user_name': signup_username}, {'user_email': signup_email},
                                         {'user_name': signup_email}, {'user_email': signup_username}]})
        if result is None:
            users.insert_one({'user_name': signup_username, 'user_email': signup_email, 'password': signup_password})
            session['user_name'] = signup_username
            if not os.path.exists("../users/" + signup_username):
                os.makedirs("../users/" + signup_username)
                os.chmod(os.path.abspath("../users/" + signup_username+"/"), 0o777)
                copy('../config/config.json', os.path.abspath("../users/" + signup_username+"/"))
            if not os.path.exists("../users/" + signup_username + "/files"):
                os.makedirs("../users/" + signup_username + "/files")
                os.chmod("../users/" + signup_username + "/files/", 0o777)
            return render_template('response.html', message="ok")
        else:
            return render_template('response.html', message="error")

    return render_template('response.html', message="error")

if __name__ == '__main__':
    with open('../config/config.json') as data_file:
        config = json.load(data_file)

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    users = db['users']

    app.secret_key = "igiogyufo8g5re4wa6w9uh809y6r74s46zi7do8n,-9=u,u8jhub5d64w 53a5cs5e87rv7b896n98709m09m087y0880m" \
                     "t685ndb8d d6b8r98r7nr5rb685d8d6dfuiufbnklb7opn8ym5bi87gkunk7ynit9pytd6d4sb6d86vonpmo89k;hbykdxyr"
    app.run(debug=True, port=8000, threaded=True)
