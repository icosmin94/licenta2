class Topic:
    def __init__(self, start_datetime="", stop_datetime="", relevant_words=[], relevant_tweets=[]):
        self.start_datetime = start_datetime
        self.stop_datetime = stop_datetime
        self.relevant_words = relevant_words
        self.relevant_tweets = relevant_tweets

    @staticmethod
    def create_topic(entries):
        topic = Topic()
        topic.__dict__.update(entries)
        return topic



