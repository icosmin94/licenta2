class Tweet:

    def __init__(self, author, age, gender, latitude,
                 longitude, date, time, raw_text, words_count, words_map):

        self.author = author
        self.age = age
        self.gender = gender
        self.latitude = latitude
        self.longitude = longitude
        self.date = date
        self.time = time
        self.raw_text = raw_text
        self.words_count = words_count
        self.words_map = words_map
        self.tfIdfMap = {}

