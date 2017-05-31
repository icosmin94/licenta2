import configparser
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
import time
from pymongo import MongoClient
from tweet import *
import json


def create_and_store_tweets(task_nr):
    print("Started task", task_number, "processing:", tasks[task_nr][1].__len__(), "tweets")
    tweets = [create_tweet(tweet_line, contractions, stop_words, word_net_lemmatizer).__dict__ for tweet_line in tasks[task_nr][1]]
    tweets_collection.insert(tweets)
    print("Processed", tasks[task_nr][1].__len__(), "tweets")
    tasks[task_nr] = ()


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    tweetsFile = config['default']['tweets_file']

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]

    tweets_collection = db[config['tweets']['collection_name']]
    tweets_collection.drop()
    batch_size = int(config['tweets']['batch_size'])
    concurrent_tasks = int(config['tweets']['concurrent_tasks'])
    executor = ThreadPoolExecutor(max_workers=concurrent_tasks)
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
    tasks = []
    lines = []
    futures = []
    start = time.time()
    with open(tweetsFile) as fp:
        for line in fp:
            line_number += 1
            if line_number > 1:
                tweets_in_batch += 1
                lines += [line]
                if tweets_in_batch == batch_size:
                    submitted_lines = lines[:]
                    tasks += [(task_number, submitted_lines)]
                    futures += [executor.submit(create_and_store_tweets, task_number)]
                    tweets_in_batch = 0
                    lines = []
                    task_number += 1
                    if task_number % concurrent_tasks == 0:
                        for future in futures:
                            future.result()
                        futures = []

    if lines.__len__() > 0:
        submitted_lines = lines[:]
        tasks += [(task_number, submitted_lines)]
        futures += [executor.submit(create_and_store_tweets, task_number)]

    for future in futures:
        future.result()
    futures = []
    end = time.time()

    print("Processing tweets took: ", end-start)

