import json, os, sys, uuid, re
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class Merge:
    """ This program aims to
        (1) Merge data/backend_reviews/location/*.txt into corpora/location.txt
        (2) Merge data/backend_stars_reviews/location/*.txt into all_stars/all_stars.txt
        (3) Merge data/sentiment_statistics/location/opinion/location_*.json into data/processed_sentiment_statistics/opinion_statistics.json
        (4) Merge data/sentiment_statistics/location/pos_tagged/location_*.json into data/processed_sentiment_statistics/pos_tagged_statistics.json """

    def __init__(self):
        self.src_br = "data/backend_reviews/"
        self.src_sbr = "data/starred_backend_reviews/"
        self.src_ss = "data/sentiment_statistics/"

        self.dst_c = "data/corpora/"
        self.dst_cs = "data/corpora/starred/"
        self.dst_pss = "data/processed_sentiment_statistics/"
        self.dst_l = "data/lexicon/"
        self.dst_log = "data/log.txt"

    def walk_backend_reviews(self):
        """ load and merge all reviews in data/backend_reviews/ """
        print "(1) Merge Backend_Reviews"
        for dirpath, dir_list, file_list in os.walk(self.src_br):
            print "Walking into directory: " + str(dirpath)

            corpus = []
            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                        break
                    else:
                        file_cnt += 1
                        # print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            corpus.append(file.read())

                if str(f) != ".DS_Store":
                    filename = re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+)\_", file_list[0]).group(1)
                    filename = filename + ".txt"
                    self.render_corpus(corpus, filename)

            else:
                print "No file is found"
                print "-"*80

        print "Mergin Backend_Reviews Completed"
        print "-"*80

    def render_corpus(self, corpus, filename):
        """ save corpus into corpora/location.txt | E.g., london_01~20.txt -> london.txt """

        print "Saving data to: " + self.dst_c + "\033[1m" + str(filename) + "\033[0m"
        review_cnt = 0
        corpus_length = len(corpus)
        f_corpus = open(self.dst_c + "/" + filename, 'w+') # c stands for corpus
        for review in corpus:
            review_cnt += 1
            f_corpus.write(review)

            sys.stdout.write("\rStatus: %s / %s"%(review_cnt, corpus_length))
            sys.stdout.flush()

        print "\n" + "-"*50

    def walk_starred_backend_reviews(self):
        """ load and merge all reviews in data/starred_backend_reviews/ into one single file named 'starred_backend_reviews.txt' """
        print "(2) Merge Starred_Backend_Reviews"

        starred_backend_reviews = []
        for dirpath, dir_list, file_list in os.walk(self.src_sbr):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath+ "/"+ f)
                        break
                    else:
                        file_cnt += 1
                        # print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            starred_backend_reviews.append(file.read())
            else:
                print "No file is found"

            print "-"*50
        self.render_starred_corpus(starred_backend_reviews)

    def render_starred_corpus(self, starred_backend_reviews):
        """ all starred_backend_reviews in all location_01~20.txt -> data/corpora/starred/starred_reviews.txt """

        print "Saving data to: " + self.dst_cs + "\033[1m" + "starred_corpus.txt" + "\033[0m"
        review_cnt = 0
        corpus_length = len(starred_backend_reviews)
        f_starred_reviews = open(self.dst_cs + "starred_corpus.txt", 'w+')
        for review in starred_backend_reviews:
            review_cnt += 1
            f_starred_reviews.write(review)

            sys.stdout.write("\rStatus: %s / %s"%(review_cnt, corpus_length))
            sys.stdout.flush()

        print "\n" + "-"*80

    def walk_sentiment_statistics(self):
        """ (1) open and append *.json in data/sentiment_statistics/location/opinion/
                into 1. opinion_sentiment_statistics 2. locational_opinion_sentiment_statisitcs
            (2) open and append *.json in data/sentiment_statistics/location/pos_tagged
                into 1. pos_tagged_sentiment_statistics 2. locational_pos_tagged_sentiment_statistics """

        print "(3) Merge Sentiment_Statistics"
        opinion_sentiment_statistics, pos_tagged_sentiment_statistics = [], []
        for dirpath, dir_list, file_list in os.walk(self.src_ss):
            print "Walking into:", dirpath

            # opinion
            if "opinion" in dirpath:
                if len(file_list) > 0:
                    locational_opinion_sentiment_statistics = []
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m" + "\n" + "-"*50
                    for f in file_list:
                        if f == ".DS_Store":
                            print "Removing " + dirpath + "/" + str(f)
                            os.remove(dirpath + "/" + f)
                            break
                        else:
                            # print "Appending " + str(dirpath) + "/" + str(f) + " into sentiment_statistics"
                            json_data = json.load(open(dirpath + "/" + f))
                            locational_opinion_sentiment_statistics.append(json_data)
                            opinion_sentiment_statistics.append(json_data)

                    self.merge_opinion_sentiment_statistics(locational_opinion_sentiment_statistics, "locational")
                else:
                    print "No file is found"
            # pos_tagged
            elif "pos_tagged" in dirpath:
                if len(file_list) > 0:
                    locational_pos_tagged_sentiment_statistics = []
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m" + "\n" + "-"*50
                    for f in file_list:
                        if f == ".DS_Store":
                            print "Removing " + dirpath + "/" + str(f)
                            os.remove(dirpath + "/" + f)
                            break
                        else:
                            # print "Appending " + str(dirpath) + "/" + str(f) + " into sentiment_statistics"
                            json_data = json.load(open(dirpath + "/" + f))
                            locational_pos_tagged_sentiment_statistics.append(json_data)
                            pos_tagged_sentiment_statistics.append(json_data)

                    self.merge_pos_tagged_sentiment_statistics(locational_pos_tagged_sentiment_statistics, "locational")
                else:
                    print "No file is found"
            else:
                """ Not in the directory where 'opinion' or 'pos_tagged' is found """
                print "-"*50
                pass

        self.merge_opinion_sentiment_statistics(opinion_sentiment_statistics, "overall")
        self.merge_pos_tagged_sentiment_statistics(pos_tagged_sentiment_statistics, "overall")

    def merge_opinion_sentiment_statistics(self, opinion_statistics_list, list_type):
        """ accumulate the count for every sentiment word in every location
        E.g., list[0] = {"good":1, "great":2}, list[1] = {"good":3, "great":4} -> sentiment_statistics = {"good":4, "great":6} """

        ## positive
        if list_type == "locational":
            print "Merging locational opinion_sentiment_statistics' positive counts"
            location = opinion_statistics_list[0]["location"]
        elif list_type == "overall":
            print "Merging overall opinion_sentiment_statistics' positive counts"
        else:
            print "Sentiment_statistics' list_type error"

        #print opinion_statistics_list[0]["sentiment_statistics"]["positive_statistics"]
        count_list = np.zeros(len(opinion_statistics_list[0]["sentiment_statistics"]["positive_statistics"]))
        index = 0
        length = len(opinion_statistics_list)
        for statistics in opinion_statistics_list:

            stemmed_word_list, word_list = [], []
            index += 1
            for i in xrange(len(statistics["sentiment_statistics"]["positive_statistics"])):
                stemmed_word_list.append(statistics["sentiment_statistics"]["positive_statistics"][i]['stemmed_word'])
                word_list.append(statistics["sentiment_statistics"]["positive_statistics"][i]['word'])
                count_list[i] += (np.asarray(statistics["sentiment_statistics"]["positive_statistics"][i]['count']))

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        # Putting them back to dictionary
        print "\nPutting positive_statistics back to dictionary"
        word_dict_list = []
        index = 0
        length = len(stemmed_word_list)
        for i in xrange(len(stemmed_word_list)):

            index += 1
            word_dict = {"stemmed_word": stemmed_word_list[i], "word": word_list[i], "count": int(count_list[i])}
            word_dict_list.append(word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        # Sorting by count
        positive_sentiment_statistics = sorted(word_dict_list, key=itemgetter('count'), reverse = True)

        print "\n" + "-"*50

        ## negative
        if list_type == "locational":
            print "Merging locational opinion_sentiment_statistics' negative counts"
        elif list_type == "overall":
            print "Merging overall opinion_sentiment_statistics' negative counts"
        else:
            print "Sentiment_statistics' list_type error"
            raise

        count_list = np.zeros(len(opinion_statistics_list[0]["sentiment_statistics"]["negative_statistics"]))
        index = 0
        length = len(opinion_statistics_list)
        for statistics in opinion_statistics_list:

            stemmed_word_list, word_list = [], []
            index += 1
            for i in xrange(len(statistics["sentiment_statistics"]["negative_statistics"])):
                stemmed_word_list.append(statistics["sentiment_statistics"]["negative_statistics"][i]['stemmed_word'])
                word_list.append(statistics["sentiment_statistics"]["negative_statistics"][i]['word'])
                count_list[i] += (np.asarray(statistics["sentiment_statistics"]["negative_statistics"][i]['count']))

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        # Putting them back to dictionary
        print "\nPutting negative_statistics back to dictionary"
        word_dict_list = []
        index = 0
        length = len(stemmed_word_list)
        for i in xrange(len(stemmed_word_list)):

            index += 1
            word_dict = {"stemmed_word": stemmed_word_list[i], "word": word_list[i], "count": int(count_list[i])}
            word_dict_list.append(word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        #Sorting by count
        negative_sentiment_statistics = sorted(word_dict_list, key=itemgetter('count'), reverse = True)

        print "\n" + "-"*80

        positive_statistics = [word_dict for word_dict in positive_sentiment_statistics if word_dict.get('count') > 20]
        negative_statistics = [word_dict for word_dict in negative_sentiment_statistics if word_dict.get('count') > 20]

        if list_type == "locational":
            self.save_opinion_sentiment_statistics(location, positive_statistics, negative_statistics)
        elif list_type == "overall":
            self.save_opinion_sentiment_statistics(None, positive_statistics, negative_statistics)
        else:
            print "Sentiment_statistics' list_type error"
            raise

    def save_opinion_sentiment_statistics(self, location, positive_statistics, negative_statistics):
        """ put keys in order and render json file """

        # if location is not None
        if location:
            print "Saving opinion positive_sentiment_statistics to:", "\033[1m" + self.dst_pss + location + "_opinion_positive.json" "\033[0m"
        else:
            print "Saving opinion positive_sentiment_statistics to:", "\033[1m" + self.dst_l + "processed_opinion_positive.json" "\033[0m"

        index = 0
        length = len(positive_statistics)
        ordered_dict_list = []
        for word_dict in positive_statistics:
            index += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = index
            ordered_dict["count"] = word_dict["count"]
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict_list.append(NoIndent(ordered_dict))

        if location:
            f_opinion_positive = open(self.dst_pss + location + "_opinion_positive.json", 'w+')
        else:
            f_opinion_positive = open(self.dst_l + "processed_opinion_positive.json", "w+")
        f_opinion_positive.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        # if location is not None
        if location:
            print "Saving opinion negative_sentiment_statistics to:", "\033[1m" + self.dst_pss + location + "_opinion_negative.json" "\033[0m"
        else:
            print "Saving opinion negative_sentiment_statistics to:", "\033[1m" + self.dst_l + "processed_opinion_negative.json" "\033[0m"

        index = 0
        length = len(negative_statistics)
        ordered_dict_list = []
        for word_dict in negative_statistics:
            index += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = index
            ordered_dict["count"] = word_dict["count"]
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict_list.append(NoIndent(ordered_dict))

        if location:
            f_opinion_negative = open(self.dst_pss + location + "_opinion_negative.json", 'w+')
        else:
            f_opinion_negative = open(self.dst_l + "processed_opinion_negative.json", "w+")
        f_opinion_negative.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "-"*80

    def merge_pos_tagged_sentiment_statistics(self, pos_tagged_statistics_list, list_type):
        """ accumulate the count for every sentiment word in every location
        E.g., list[0] = {"good":1, "great":2}, list[1] = {"good":3, "great":4} -> sentiment_statistics = {"good":4, "great":6} """

        if list_type == "locational":
            print "Merging locational pos_tagged_sentiment_statistics' counts"
            location = pos_tagged_statistics_list[0]["location"]
        elif list_type == "overall":
            print "Merging overall pos_tagged_sentiment_statistics' counts"
        else:
            print "Sentiment_statistics' list_type error"

        count_list = np.zeros(len(pos_tagged_statistics_list[0]["sentiment_statistics"]))
        index = 0
        length = len(pos_tagged_statistics_list)
        for statistics in pos_tagged_statistics_list:

            stemmed_word_list, word_list = [], []
            index += 1
            for i in xrange(len(statistics["sentiment_statistics"])):
                stemmed_word_list.append(statistics["sentiment_statistics"][i]['stemmed_word'])
                word_list.append(statistics["sentiment_statistics"][i]['word'])
                count_list[i] += (np.asarray(statistics["sentiment_statistics"][i]['count']))

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        # Putting them back to dictionary
        print "\nPutting pos_tagged_sentiment_statistics back to dictionary"
        word_dict_list = []
        index = 0
        length = len(stemmed_word_list)
        for i in xrange(len(stemmed_word_list)):

            index += 1
            word_dict = {"stemmed_word": stemmed_word_list[i], "word": word_list[i], "count": int(count_list[i])}
            word_dict_list.append(word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        # Sorting by count
        pos_tagged_sentiment_statistics = sorted(word_dict_list, key=itemgetter('count'), reverse = True)

        print "\n" + "-"*80

        pos_tagged_sentiment_statistics = [word_dict for word_dict in pos_tagged_sentiment_statistics if word_dict.get('count') > 20]

        if list_type == "locational":
            self.save_pos_tagged_sentiment_statistics(location, pos_tagged_sentiment_statistics)
        elif list_type == "overall":
            self.save_pos_tagged_sentiment_statistics(None, pos_tagged_sentiment_statistics)
        else:
            print "Sentiment_statistics' list_type error"
            raise

    def save_pos_tagged_sentiment_statistics(self, location, pos_tagged_sentiment_statistics):
        """ put keys in order and render json file """

        # if location is not None
        if location:
            print "Saving pos_tagged sentiment_statistics to:", "\033[1m" + self.dst_pss + location + "_pos_tagged.json" "\033[0m"
        else:
            print "Saving pos_tagged sentiment_statistics to:", "\033[1m" + self.dst_l + "processed_pos_tagged_lexicon.json" "\033[0m"

        index = 0
        length = len(pos_tagged_sentiment_statistics)
        ordered_dict_list = []
        for word_dict in pos_tagged_sentiment_statistics:
            index += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = index
            ordered_dict["count"] = word_dict["count"]
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict_list.append(NoIndent(ordered_dict))

        if location:
            f_pos_tagged = open(self.dst_pss + location + "_pos_tagged.json", 'w+')
        else:
            f_pos_tagged = open(self.dst_l + "processed_pos_tagged_lexicon.json", "w+")
        f_pos_tagged.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "-"*80

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_c)
        dir2 = os.path.dirname(self.dst_cs)
        dir3 = os.path.dirname(self.dst_pss)
        dir4 = os.path.dirname(self.dst_l)

        print "Checking destination directories"
        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            print "Creating directory: " + dir2
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            print "Creating directory: " + dir3
            os.makedirs(dir3)
        if not os.path.exists(dir4):
            print "Creating directory: " + dir4
            os.makedirs(dir4)

        print "-"*80

    def run(self):
        self.create_dirs()
        self.walk_backend_reviews()
        self.walk_starred_backend_reviews()
        self.walk_sentiment_statistics()

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
    merge = Merge()
    merge.run()

