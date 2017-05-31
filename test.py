import configparser
from pymongo import MongoClient
from tweet import *
import json


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    tweetsFile = config['default']['tweets_file']

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]

    # read stop words
    stop_words = []
    with open('./words/stop_words.txt') as sp:
        for line in sp:
            stop_words.extend([line.strip(" \n")])

    # read contractions file
    with open('./words/contractions.json') as contractions_file:
        contractions = json.load(contractions_file)

    line_number = 0
    with open(tweetsFile) as fp:
        for line in fp:
            line_number += 1
            if line_number > 1:
                create_tweet(line, contractions, stop_words)



