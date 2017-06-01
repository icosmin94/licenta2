import configparser
from load_tweets import load_tweets

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    if config['tweets']['load_tweets'].lower() == "true":
        load_tweets()
