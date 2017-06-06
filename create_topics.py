import configparser
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


def compute_nmf(config, start_datetime, stop_datetime):
    idf = {}
    tweets = []
    nr_topics = int(config['topics']['nr_topics'])

    topics_list = []

    # get tweets from db
    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    topic_collection = db[config['topics']['topic_collection_name']]

    result = tweets_collection.find({'date_time':  {'$gte':  start_datetime, '$lt': stop_datetime}})
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
    index = 0
    for topic in topics:
        topic_object = Topic(start_datetime=start_datetime, stop_datetime=stop_datetime)
        values = topic.tolist()
        relevant_words = {}
        for i in range(0, values.__len__()):
            relevant_words[words[i]] = values[i]
        relevant_words = sorted(relevant_words.items(), key=lambda x: x[1], reverse=True)

        # add relevant words
        topic_object.relevant_words = relevant_words[0:9]
        relevant_tweets_per_topic = [(relevant_tweets[i][index], tweets[i]) for i in range(0, relevant_tweets.__len__())]
        relevant_tweets_per_topic = sorted(relevant_tweets_per_topic, key=lambda x: x[0], reverse=True)

        # add relevant tweet ids
        topic_object.relevant_tweets = list(
            map(lambda x: (x[0], x[1]._id), filter(lambda x: x[0] > 0.1, relevant_tweets_per_topic)))
        print(topic_object.relevant_words)
        topics_list += [topic_object.__dict__]
        index += 1

    topic_collection.insert(topics_list)

    print("Processed topics in time interval", start_datetime, "-", stop_datetime, "consisting of", tweets.__len__(),
          "tweets")


def create_and_store_topics():

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    if config['tweets']['load_tweets'].lower() == "true":
        load_tweets()

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    concurrent_tasks = int(config['default']['concurrent_tasks'])
    topic_collection = db[config['topics']['topic_collection_name']]
    topic_collection.drop()
    # add index on date-time
    topic_collection.create_index([("start_datetime", pymongo.ASCENDING)])
    executor = ProcessPoolExecutor(max_workers=concurrent_tasks)

    date_hour_dict = date_hour_collection.find_one()
    dates = []
    futures = []
    task_number = 0

    # date parsing
    for key in date_hour_dict:
        if key != "_id":
            dates += [key]
    dates.sort()
    date_hour_dict[dates[0]].sort()
    date_hour_dict[dates[dates.__len__() - 1]].sort(reverse=True)

    current_datetime_parts = re.split('-', dates[0])
    limit_datetime_parts = re.split('-', dates[dates.__len__() - 1])

    start_datetime = datetime.datetime(year=int(current_datetime_parts[0]), month=int(current_datetime_parts[1]),
                                       day=int(current_datetime_parts[2]),
                                       hour=int(date_hour_dict[dates[0]][0]))
    stop_datetime = start_datetime + datetime.timedelta(hours=1)
    limit_datetime = datetime.datetime(year=int(limit_datetime_parts[0]), month=int(limit_datetime_parts[1]),
                                       day=int(limit_datetime_parts[2]),
                                       hour=int(date_hour_dict[dates[dates.__len__() - 1]][0]))

    # start tf-idf and nmf
    start = time.time()
    while start_datetime <= limit_datetime:
        futures += [executor.submit(compute_nmf, config, start_datetime, stop_datetime)]

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