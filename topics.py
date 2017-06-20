from math import sqrt


class Topic:
    def __init__(self, start_datetime="", stop_datetime="", username=""):
        self.start_datetime = start_datetime
        self.stop_datetime = stop_datetime
        self.relevant_words = []
        self.relevant_tweets = []
        self.merge_count = 0
        self.username = username

    @staticmethod
    def create_topic(entries):
        topic = Topic()
        topic.__dict__.update(entries)
        return topic

    def cosine_similarity(self, other_topic):
        scalar_product = 0
        norm1 = 0
        norm2 = 0
        word_dict_1 = {}
        word_dict_2 = {}
        for word_tuple in self.relevant_words:
            word_dict_1[word_tuple[0]] = word_tuple[1]
            norm1 += word_tuple[1] * word_tuple[1]

        for word_tuple in other_topic.relevant_words:
            word_dict_2[word_tuple[0]] = word_tuple[1]
            norm2 += word_tuple[1] * word_tuple[1]

        for word in word_dict_1:
            if word in word_dict_2:
                scalar_product += word_dict_1[word] * word_dict_2[word]

        return scalar_product/(sqrt(norm1) * sqrt(norm2))

    def merge_with(self, other_topic):
        self.merge_count += 1
        relevant_words_dict = {}
        topic_words_number = self.relevant_words.__len__()

        for word_tuple in self.relevant_words:
            relevant_words_dict[word_tuple[0]] = word_tuple[1]

        for word_tuple in other_topic.relevant_words:
            if word_tuple[0] in relevant_words_dict:
                relevant_words_dict[word_tuple[0]] = (relevant_words_dict[word_tuple[0]] *
                                                      self.merge_count + word_tuple[1]) / (self.merge_count + 1)
            else:
                relevant_words_dict[word_tuple[0]] = word_tuple[1]

        self.relevant_words = sorted(relevant_words_dict.items(), key=lambda x: x[1], reverse=True)[0:topic_words_number]
        relevant_tweets_map = {}
        for tweet_tuple in self.relevant_tweets + other_topic.relevant_tweets:
            if tweet_tuple[1] not in relevant_tweets_map:
                relevant_tweets_map[tweet_tuple[1]] = tweet_tuple[0]
        self.relevant_tweets = [(relevant_tweets_map[tweet], tweet) for tweet in relevant_tweets_map ]




