import configparser

from pymongo import MongoClient

from create_topics import create_and_store_topics
from load_tweets import load_tweets
from topics import Topic

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    if config['tweets']['load_tweets'].lower() == "true":
        load_tweets()

    if config['topics']['create_topics'].lower() == "true":
        create_and_store_topics()

    client = MongoClient(config['database']['host'], int(config['database']['port']))
    db = client[config['database']['db']]
    topic_collection = db[config['topics']['topic_collection_name']]

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
            if current_result > result and current_result > 0.7:
                result = current_result
                assign_cluster = cluster
        if assign_cluster is None:
            topic_clusters += [topic]
        else:
            assign_cluster.merge_with(topic)
    for topic in topic_clusters:
        print(topic.relevant_words)
