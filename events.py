import json
import operator

import time

import datetime
from pymongo import MongoClient
from topics import Topic
from tweet import Tweet


def process_events(username):
    with open('../users/' + username + '/config.json') as data_file:
        config = json.load(data_file)

    merge_threshold = float(config['events']['merge_threshold'])

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    topic_collection = db[config['topics']['topic_collection_name']]
    tweets_collection = db[config['tweets']['collection_name']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    date_hour_list = date_hour_collection.find_one()['dates']
    date_hour_list.sort()
    granularity = float(config['events']['granularity'])

    start = time.time()
    topics_cursor = topic_collection.find({'username': username})
    topics = []
    for topic in topics_cursor:
        topics += [Topic.create_topic(topic)]

    topic_clusters = []
    print("Finished reading topics")

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
    print("Finished assigning topics to clusters")
    result = {}
    index = 0
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

        max_value = max(values)
        occurrences = 0
        for value in values:
            if float(value) > max_value/10:
                occurrences += 1
        if occurrences/values.__len__() < granularity:
            result[str(index)] = {}
            result[str(index)]['x'] = [date_hour.isoformat() for date_hour in date_hour_list]
            result[str(index)]['y'] = values
            result[str(index)]['title'] = ', '.join([word_tuple[0] for word_tuple in cluster.relevant_words])
            index += 1

    end = time.time()
    result['username'] = username
    event_collection = db['events']
    event_collection.remove({"username": username})
    event_collection.insert_one(result)
    print("Merging topics took: ", end - start)


def get_events(username):

    with open('../users/' + username + '/config.json') as data_file:
        config = json.load(data_file)

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    event_collection = db['events']
    result = event_collection.find_one({"username": username})
    result.pop('_id', None)
    result.pop('username', None)
    return result

