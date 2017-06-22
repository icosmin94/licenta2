import configparser
import json
from concurrent.futures import ProcessPoolExecutor
import re
import numpy as np
import time
import datetime

import pymongo
from scipy.sparse import csr_matrix
import math
from pymongo import MongoClient
from load_tweets import load_tweets
from topics import Topic
from tweet import Tweet
from sklearn.decomposition import NMF


def compute_nmf(config, start_datetime, stop_datetime, username):
    idf = {}
    tweets = []
    nr_topics = int(config['topics']['nr_topics'])
    topic_words_nr = int(config['topics']['topic_words_nr'])
    topics_list = []
    tweet_per_topic_number = int(config['topics']['tweet_per_topic'])
    tweet_threshold = int(config['topics']['tweet_threshold'])

    # get tweets from db
    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    topic_collection = db[config['topics']['topic_collection_name']]

    result = tweets_collection.find(
        {"$and": [{'date_time': {'$gte': start_datetime, '$lt': stop_datetime}}, {'username': username}]})
    for tweet in result:
        tweets += [Tweet.create_tweet(tweet)]

    # find word document frequency
    for tweet in tweets:
        for word in tweet.words_map:
            if word not in idf:
                idf[word] = 0
            idf[word] += 1

    words = list(idf.keys())
    word_indexes = {}
    index = 0
    for word in idf.keys():
        word_indexes[word] = index
        index += 1
    index = 0
    row = []
    col = []
    data = []

    # prepare the date for nmf model
    for tweet in tweets:
        for word in tweet.words_map:
            row += [index]
            col += [word_indexes[word]]
            data += [(tweet.words_map[word]/tweet.words_count) * math.log(tweets.__len__()/idf[word])]
        index += 1
    row = np.array(row)
    col = np.array(col)
    data = np.array(data)

    # apply nmf
    matrix = csr_matrix((data, (row, col)), shape=(tweets.__len__(), words.__len__()))
    nmf_model = NMF(n_components=nr_topics, init='nndsvd', random_state=0)
    relevant_tweets = nmf_model.fit_transform(matrix).tolist()
    topics = nmf_model.components_

    # extract topics and relevant tweets
    for topic in topics:
        topic_object = Topic(start_datetime=start_datetime, stop_datetime=stop_datetime, username=username)
        values = topic.tolist()
        relevant_words = {}
        for i in range(0, values.__len__()):
            relevant_words[words[i]] = values[i]
        relevant_words = sorted(relevant_words.items(), key=lambda x: x[1], reverse=True)

        # add relevant words
        topic_object.relevant_words = relevant_words[0:topic_words_nr]
        topics_list += [topic_object]

    # add relevant tweets
    index = 0
    for tweet_per_topic in relevant_tweets:
        tweet_topic_pairs = [(tweet_per_topic[i], i) for i in range(0, nr_topics)]
        tweet_topic_pairs = sorted(tweet_topic_pairs,  key=lambda x: x[0], reverse=True)
        for j in range(0, tweet_per_topic_number):
            if tweet_topic_pairs[j][0] > tweet_threshold:
                topics_list[tweet_topic_pairs[j][1]].relevant_tweets.append(
                    (tweet_topic_pairs[j][0], tweets[index]._id))

        index += 1
    topics_list = [topic.__dict__ for topic in topics_list]
    topic_collection.insert(topics_list)

    print("Processed topics in time interval", start_datetime, "-", stop_datetime, "consisting of", tweets.__len__(),
          "tweets")


def create_and_store_topics(username):

    with open('../users/' + username+'/config.json') as data_file:
        config = json.load(data_file)

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    concurrent_tasks = int(config['general']['concurrent_tasks'])
    topic_collection = db[config['topics']['topic_collection_name']]
    # add index on date-time and user_name
    topic_collection.create_index([("username", pymongo.ASCENDING)])
    topic_collection.remove({"username": username})
    executor = ProcessPoolExecutor(max_workers=concurrent_tasks)

    date_hour_list = date_hour_collection.find_one()['dates']
    date_hour_list.sort()
    futures = []
    task_number = 0

    start_datetime = date_hour_list[0]
    stop_datetime = start_datetime + datetime.timedelta(hours=1)
    limit_datetime = date_hour_list[date_hour_list.__len__() - 1]

    # start tf-idf and nmf
    start = time.time()
    while start_datetime <= limit_datetime:
        futures += [executor.submit(compute_nmf, config, start_datetime, stop_datetime, username)]

        start_datetime += datetime.timedelta(minutes=10)
        stop_datetime += datetime.timedelta(minutes=10)
        task_number += 1
        if task_number % concurrent_tasks == 0:
            for future in futures:
                future.result()
            futures = []

    for future in futures:
        future.result()
    end = time.time()

    print("Processing nmf took: ", end - start)
