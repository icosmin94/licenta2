import configparser
import re
from pymongo import MongoClient
from tweet import *


def create_tweet(tweet_line):
    parts = re.split(r'[,"\[\]]+', tweet_line)
    print(parts)
    author = parts[1]
    age = parts[2]
    gender = parts[3]
    latitude = parts[4]
    longitude = parts[5]
    date_time = parts[parts.__len__()-1]
    date_time_parts = re.split('[TZ\n]+', date_time)
    raw_text = re.sub(r'\\', '', tweet_line[tweet_line.index(parts[6]): tweet_line.index(date_time) - 1])

    #print(re.sub(r'[!?.\\<>\[\]()/*:+~=;^\']+', '', raw_text).lower())
    tweet = Tweet(author, age, gender, latitude, longitude, date_time_parts[0], date_time_parts[1], raw_text, 0, {})
    print(tweet.__dict__)

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    tweetsFile = config['default']['tweets_file']
    print(tweetsFile)

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]

    i = 0
    with open(tweetsFile) as fp:
        for line in fp:
            i += 1
            if i > 1:
                create_tweet(line)
