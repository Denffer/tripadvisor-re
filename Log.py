import json, os, sys, uuid, re
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class Log:
    """ This program aims to
        (1) Calculate the parameters needed by other programs
        (2) (to be added) """

    def __init__(self):
        self.src_fr = "data/frontend_reviews/"
        #self.src_ss = "data/sentiment_statistics/"

        self.frontend_reviews = []
        self.dst_log_dir = "data/"
        self.dst_log = "data/log.txt"

    def get_frontend_reviews(self):
        """ Get avg_sentiment_counts and avg_word_counts from frontend reviews """

        for dirpath, dir_list, file_list in os.walk(self.src_fr):
            print "Walking into:", dirpath

            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"
                for f in file_list:
                    if f == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                    else:
                        self.frontend_reviews.append(json.load(open(dirpath+"/"+f)))
            else:
                print "No file is found"
            print "-"*80

    def render(self):
        """ save avg_words_count_per_review & avg_sentiment_count_per_review in data/log.txt """
        total_review_count = 0.0
        total_opinion_positive_count = 0.0
        total_opinion_negative_count = 0.0
        total_pos_tagged_sentiment_count = 0.0
        total_word_count = 0.0
        total_nearest_opinion_sentiment_distance = 0.0
        total_nearest_pos_tagged_sentiment_distance = 0.0

        for entity in self.frontend_reviews:
            total_review_count += entity["review_count"]
            total_opinion_positive_count += entity["avg_opinion_positive_count"]
            total_opinion_negative_count += entity["avg_opinion_negative_count"]
            total_pos_tagged_sentiment_count += entity["avg_pos_tagged_sentiment_count"]
            total_word_count += entity["avg_word_count"]
            total_nearest_opinion_sentiment_distance += entity["avg_nearesti_opinion_sentiment_distance"]
            total_nearest_pos_tagged_sentiment_distance += entity["avg_nearesti_pos_tagged_sentiment_distance"]

        avg_review_count = total_review_count / len(self.frontend_reviews)
        avg_opinion_positive_count = total_opinion_positive_count / len(self.frontend_reviews)
        avg_opinion_negative_count = total_opinion_negative_count / len(self.frontend_reviews)
        avg_pos_tagged_sentiment_count = total_pos_tagged_sentiment_count / len(self.frontend_reviews)
        avg_word_count = total_word_count / len(self.frontend_reviews)
        avg_nearest_opinion_sentiment_distance = total_nearest_opinion_sentiment_distance / len(self.frontend_reviews)
        avg_nearest_pos_tagged_sentiment_distance = total_nearest_pos_tagged_sentiment_distance / len(self.frontend_reviews)

        total_review_count = 0
        with open(self.dst_log, "r") as log_file:
            text = log_file.readline()
            total_review_count = re.search("[0-9]+", text).group(0)

        with open(self.dst_log, "w") as log_file:
            log_file.write("Total review count: " + str(total_review_count))
            log_file.write("\nAverage review count per entity: " + str(avg_review_count))
            log_file.write("\nAverage review count per entity: " + str(avg_review_count))
            log_file.write("\nAverage opinion positive sentiment word count per review: " + str(avg_opinion_positive_count))
            log_file.write("\nAverage opinion negative sentiment word count per review: " + str(avg_opinion_negative_count))
            log_file.write("\nAverage pos_tagged sentiment word count per review: " + str(avg_pos_tagged_sentiment_count))
            log_file.write("\nAverage word count per review: " + str(avg_word_count))
            log_file.write("\nAverage nearest opinion_sentiment distance: " + str(avg_nearest_opinion_sentiment_distance))
            log_file.write("\nAverage nearest pos_tagged_sentiment distance: " + str(avg_nearest_pos_tagged_sentiment_distance))


    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_log_dir)
        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

        print "-"*80

class NoIndent(object):
    def __init__(self, value):
        self.value = value

class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in self._replacement_map.iteritems():
            result = result.replace('"@@%s@@"' % (k,), v)
        return result

if __name__ == '__main__':
    log = Log()
    log.create_dirs()
    log.get_frontend_reviews()
    log.render()

