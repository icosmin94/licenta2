import configparser
from concurrent.futures import ProcessPoolExecutor
import time
import pymongo
from nltk import WordNetLemmatizer, pprint
from pymongo import MongoClient
from tweet import *
import json


def merge_date_hour_dict(dict1, dict2):
    for date in dict2:
        if date in dict1:
            dict1[date] = list(set(dict1[date] + dict2[date]))
        else:
            dict1[date] = dict2[date]


def create_and_store_tweets(lines, contractions, stop_words, word_net_lemmatizer, config, task_number):
    print("Started task", task_number, ": processing:", lines.__len__(), "tweets")
    tweets = [create_tweet(tweet_line, contractions, stop_words, word_net_lemmatizer).__dict__ for tweet_line in lines]

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    tweets_collection.insert(tweets)

    date_hour_dict = {}

    for tweet in tweets:
        date_time = tweet['date_time']
        parts = re.split(' ', date_time.__str__())
        if parts[0] not in date_hour_dict:
            date_hour_dict[parts[0]] = set()
        date_hour_dict[parts[0]].add(re.split(r":", parts[1])[0])

    for entry in date_hour_dict:
        date_hour_dict[entry] = list(date_hour_dict[entry])

    print("Processed task", task_number, "with :", lines.__len__(), "tweets")

    return date_hour_dict


def load_tweets():

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    tweetsFile = config['default']['tweets_file']

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    tweets_collection = db[config['tweets']['collection_name']]
    tweets_collection.drop()
    # create index on date
    tweets_collection.create_index([("date_time", pymongo.ASCENDING)])

    batch_size = int(config['tweets']['batch_size'])
    concurrent_tasks = int(config['default']['concurrent_tasks'])
    executor = ProcessPoolExecutor(max_workers=concurrent_tasks)
    word_net_lemmatizer = WordNetLemmatizer()
    word_net_lemmatizer.lemmatize("dogs")

    # read stop words
    stop_words = []
    with open('./words/stop_words.txt') as sp:
        for line in sp:
            stop_words.extend([line.strip(" \n")])

    # read contractions file
    with open('./words/contractions.json') as contractions_file:
        contractions = json.load(contractions_file)

    line_number = 0
    tweets_in_batch = 0
    task_number = 0
    lines = []
    futures = []
    date_hour_dict = {}
    start = time.time()
    with open(tweetsFile) as fp:
        for line in fp:
            line_number += 1
            if line_number > 1:
                tweets_in_batch += 1
                lines += [line]
                if tweets_in_batch == batch_size:
                    submitted_lines = lines[:]

                    futures += [executor.submit(create_and_store_tweets, submitted_lines, contractions, stop_words,
                                                word_net_lemmatizer, config, task_number)]
                    tweets_in_batch = 0
                    lines = []
                    task_number += 1
                    if task_number % concurrent_tasks == 0:
                        for future in futures:
                            merge_date_hour_dict(date_hour_dict, future.result())
                        futures = []

    if lines.__len__() > 0:
        submitted_lines = lines[:]
        futures += [executor.submit(create_and_store_tweets, submitted_lines, contractions, stop_words,
                                    word_net_lemmatizer, config, task_number)]

    for future in futures:
        merge_date_hour_dict(date_hour_dict, future.result())

    date_hour_list = []
    for date in date_hour_dict:
        date_time = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        hours = date_hour_dict[date]
        for hour in hours:
            h_time = datetime.time(hour=int(hour))
            date_hour_list += [datetime.datetime.combine(date_time, h_time)]

    end = time.time()
    date_hour_collection = db[config['tweets']['date_hour_collection_name']]
    date_hour_collection.drop()
    date_hour_collection.insert({"dates": date_hour_list})

    print("Processing tweets took: ", end - start)

