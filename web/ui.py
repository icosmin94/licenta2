import os
from shutil import copyfile, copy

from flask import Flask, redirect, url_for, request, render_template, make_response, session, jsonify

import json

from pymongo import MongoClient

from create_topics import create_and_store_topics
from events import merge_topics, get_events
from load_tweets import load_tweets

app = Flask(__name__)


@app.route('/logout', methods=['POST'])
def logout():
    progress_tracker.pop(session.get('user_name'), None)
    session.pop('user_name', None)
    return render_template('response.html', message="ok")


@app.route('/pagina')
def pagina():
    return render_template('pagina.html')


@app.route('/results')
def results():
    return render_template('results.html', user=session['user_name'])


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
            return render_template('pagina.html')


@app.route('/merge_topics', methods=['POST'])
def merge_topics_call():
    params = json.loads(request.form['jsonData'])
    merge_topics(session.get('user_name'), params, progress_tracker)
    return render_template('response.html', message="ok")


@app.route('/show_events', methods=['POST'])
def show_events_call():
    params = json.loads(request.form['jsonData'])
    result = get_events(session.get('user_name'), params)
    return jsonify(result)


@app.route('/create_topics', methods=['POST'])
def create_topics_call():
    params = json.loads(request.form['jsonData'])
    create_and_store_topics(session.get('user_name'), params, progress_tracker)
    return render_template('response.html', message="ok")


@app.route('/load_tweets', methods=['POST'])
def load_tweets_call():
    if request.files['upload'].filename == '':
        return render_template('response.html', message="notok")
    f = request.files['upload']
    filename = "../users/" + session.get('user_name') + "/files/"+f.filename
    print('Saving file')
    f.save(filename)
    params = json.loads(request.form['jsonData'])
    print("Calling load_tweets")
    load_tweets(session.get('user_name'), filename, params, progress_tracker)
    return render_template('response.html', message="ok")


@app.route('/create_session', methods=['POST'])
def create_session():
    sessions = db['sessions']
    result = sessions.find_one({'user_name': session.get('user_name')})
    if result is None:
        sessions.insert_one({'user_name': session.get('user_name'), 'counter': 1, 'sessions': ['Session 1']})
        sessions_list = ['Session 1']
    else:
        sessions.remove({'user_name': session.get('user_name')})
        sessions_list = result['sessions'] + ['Session ' + str(result['counter'] + 1)]
        sessions.insert_one(
            {'user_name': session.get('user_name'), 'counter': result['counter'] + 1,
             'sessions': sessions_list})
    return jsonify({'sessions': sessions_list})


@app.route('/show_session', methods=['POST'])
def show_session():
    sessions = db['sessions']
    result = sessions.find_one({'user_name': session.get('user_name')})
    if result is None:
        sessions_list = []
    else:
        sessions_list = result['sessions']
        data = json.loads(request.form['jsonData'])
        if data['action'] == 'delete':
            sessions_list.remove(data['id'])
            clean_up(session.get('user_name'), data['id'])
            result['sessions'] = sessions_list
            sessions.remove({'user_name': session.get('user_name')})
            sessions.insert_one(result)
            progress_tracker[session.get('user_name')] = 100
    return jsonify({'sessions': sessions_list})


def clean_up(username, session_number):
    progress_tracker[session.get('user_name')] = 5
    tweets_collection.remove({'username': username, 'session': session_number})
    progress_tracker[session.get('user_name')] = 40
    date_hour_collection.remove({'username': username, 'session': session_number})
    topic_collection.remove({'username': username, 'session': session_number})
    progress_tracker[session.get('user_name')] = 80
    event_collection.remove({'username': username, 'session': session_number})
    progress_tracker[session.get('user_name')] = 95
    print("Deleting data for user:", username, " session:", session_number)


@app.route('/board', methods=['POST', 'GET'])
def board():
    return render_template('new_board.html', user=session['user_name'])


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


@app.route('/get_progress', methods=['POST'])
def get_progress():
    if session.get('user_name') in progress_tracker:
        print(progress_tracker[session.get('user_name')])
        return jsonify(str(progress_tracker[session.get('user_name')])[0:4])
    else:
        return jsonify(0)


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
        result = users.find_one(
            {"$and": [{"$or": [{'user_name': login_id}, {'user_email': login_id}]}, {'password': login_password}]})
        if result is None:
            return render_template('response.html', message="=error")
        else:
            session['user_name'] = result['user_name']
            progress_tracker[result['user_name']] = 0
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
            progress_tracker[signup_username] = 0
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
    tweets_collection = db[config['tweets']['collection_name']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    topic_collection = db[config['topics']['topic_collection_name']]
    event_collection = db['events']

    progress_tracker = {}
    app.secret_key = "igiogyufo8g5re4wa6w9uh809y6r74s46zi7do8n,-9=u,u8jhub5d64w 53a5cs5e87rv7b896n98709m09m087y0880m" \
                     "t685ndb8d d6b8r98r7nr5rb685d8d6dfuiufbnklb7opn8ym5bi87gkunk7ynit9pytd6d4sb6d86vonpmo89k;hbykdxyr"
    app.run(debug=True, port=8000, threaded=True)
