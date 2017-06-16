import configparser
import json
import operator

import time

import datetime
from pymongo import MongoClient
import matplotlib.pyplot as plt
from create_topics import create_and_store_topics
from load_tweets import load_tweets
from topics import Topic
from tweet import Tweet

if __name__ == '__main__':

    with open('./config/config.json') as data_file:
        config = json.load(data_file)

    if config['tweets']['load_tweets'].lower() == "true":
        load_tweets()

    if config['topics']['create_topics'].lower() == "true":
        create_and_store_topics()

    merge_threshold = float(config['topics']['merge_threshold'])

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    topic_collection = db[config['topics']['topic_collection_name']]
    tweets_collection = db[config['tweets']['collection_name']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    date_hour_list = date_hour_collection.find_one()['dates']
    date_hour_list.sort()
    granularity = float(config['topics']['granularity'])

    start = time.time()
    topics_cursor = topic_collection.find()
    topics = []
    for topic in topics_cursor:
        topics += [Topic.create_topic(topic)]

    topic_clusters = []

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
    plot_index = 1
    for try_topic in topic_clusters:
        topic_tweet_ids = [tweet_tuple[1] for tweet_tuple in try_topic.relevant_tweets]
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
            plt.figure(plot_index, figsize=(12, 7))
            plt.plot([x for x in date_hour_list], values, marker='o', linestyle='--')
            plt.title([word_tuple[0] for word_tuple in try_topic.relevant_words].__str__(), fontsize=10)
            plt.xticks(fontsize=8)
            plt.xlabel('time', fontsize=10)
            plt.ylabel('tweets')
            plot_index += 1

    plt.show()
    end = time.time()
    print("Merging topics took: ", end - start)

