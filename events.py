import json
import operator

import time

import datetime

import copy
from pymongo import MongoClient
from topics import Topic
from tweet import Tweet


def merge_topics(username, params, progress_tracker):
    with open('../users/' + username + '/config.json') as data_file:
        config = json.load(data_file)

    config['events']['merge_threshold'] = params['merge_threshold']
    config['tweets']['threads_number'] = params['threads']
    session_number = params['session']

    with open('../users/' + username + '/config.json', 'w') as outfile:
        json.dump(config, outfile)

    progress_tracker[username] = 2
    merge_threshold = float(config['events']['merge_threshold'])

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    topic_collection = db[config['topics']['topic_collection_name']]
    tweets_collection = db[config['tweets']['collection_name']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    date_hour_list = date_hour_collection.find_one()['dates']
    date_hour_list.sort()
    # granularity = float(config['events']['granularity'])

    start = time.time()
    topics_cursor = topic_collection.find({'username': username, 'session': session_number})
    topics = []
    for topic in topics_cursor:
        topics += [Topic.create_topic(topic)]

    topic_clusters = []
    print("Finished reading topics")


    nr_topics = topics.__len__()

    for topic in topics:
        result = 0
        assign_cluster = None
        for cluster in topic_clusters:
            current_result = cluster.cosine_similarity(topic)
            if current_result > result and current_result > merge_threshold:
                result = current_result
                assign_cluster = cluster
        if assign_cluster is None:
            topic_clusters += [topic]
        else:
            assign_cluster.merge_with(topic)
        progress_tracker[username] = min(progress_tracker[username] + 50 / nr_topics,
                                         98.0)
    print("Finished assigning topics to clusters")
    result = {}
    index = 0
    topic_clusters_number = topic_clusters.__len__()

    for cluster in topic_clusters:
        topic_tweet_ids = [tweet_tuple[1] for tweet_tuple in cluster.relevant_tweets]
        tweets_cursor = tweets_collection.find({"_id": {"$in": topic_tweet_ids}})

        tweets = []
        for tweet in tweets_cursor:
            tweets += [Tweet.create_tweet(tweet)]
        tweets = sorted(tweets, key=operator.attrgetter('date_time'))
        date_hour_dict = {}
        for tweet in tweets:
            hour = datetime.time(hour=tweet.date_time.hour)
            date = tweet.date_time.date()
            date_hour = datetime.datetime.combine(date, hour)
            if date_hour not in date_hour_dict:
                date_hour_dict[date_hour] = 0
            date_hour_dict[date_hour] += 1

        values = [0] * date_hour_list.__len__()
        for date in date_hour_dict:
            values[date_hour_list.index(date)] = date_hour_dict[date]

        # max_value = max(values)
        # occurrences = 0
        # for value in values:
        #     if float(value) > max_value/10:
        #         occurrences += 1
        # if occurrences/values.__len__() < granularity:
        result[str(index)] = {}
        result[str(index)]['x'] = [date_hour.isoformat() for date_hour in date_hour_list]
        result[str(index)]['y'] = values
        result[str(index)]['title'] = ', '.join([word_tuple[0] for word_tuple in cluster.relevant_words])
        index += 1
        progress_tracker[username] = min(progress_tracker[username] + 50 / topic_clusters_number,
                                         98.0)

    end = time.time()
    result['username'] = username
    result['session'] = session_number
    event_collection = db['events']
    event_collection.remove({"username": username, 'session': session_number})
    event_collection.insert_one(result)
    print("Merging topics took: ", end - start)
    progress_tracker[username] = 100


def get_events(username, params):

    with open('../users/' + username + '/config.json') as data_file:
        config = json.load(data_file)

    config['events']['granularity'] = params['granularity']
    session_number = params['session']

    with open('../users/' + username + '/config.json', 'w') as outfile:
        json.dump(config, outfile)

    expected_granularity = float(config['events']['granularity'])
    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    event_collection = db['events']
    result = event_collection.find_one({"username": username, 'session': session_number})
    result.pop('_id', None)
    result.pop('username', None)
    result.pop('session', None)
    copy_result = copy.copy(result)

    for key in result:
        granularity = 0
        y = result[key]['y']
        maximum = max(y)
        for value in y:
            if value > maximum/10:
                granularity += 1
        if granularity/y.__len__() > expected_granularity:
            copy_result.pop(key, None)

    return copy_result

