import json, os, sys, uuid, re
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class Merger:
    """ This program aims to
        (1) Merge data/backend_reviews/location/*.txt into corpora/location.txt
        (2) Merge data/backend_stars_reviews/location/*.txt into corpus_all/corpus_all.txt
        (3) Merge data/sentiment_statistics/*.json into sentiment_statistics.json  """

    def __init__(self):
        self.src_br = "data/backend_reviews/"
        self.src_bsr = "data/backend_stars_reviews/"
        self.src_ss = "data/sentiment_statistics/"

        # sc stands for corpus_stars
        self.dst_cs = "data/corpus_stars/"
        self.corpus_stars = []
        self.dst_corpora = "data/corpora/"
        self.dst_ss = "data/lexicon/sentiment_statistics.json"

    def get_corpora(self):
        """ load all reviews in data/backend_reviews/ and merge them """
        print "Starting to load: " + self.src_br
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
                        print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            corpus.append(file.read())

                if str(f) != ".DS_Store":
                    filename = re.sub('\_[0-9]+', '', file_list[0])[:-4]
                    filename = filename + ".txt"
                    self.render_corpus(corpus, filename)

            else:
                print "No file is found"
                print "-"*80

    def render_corpus(self, corpus, filename):
        """ london1~20.txt -> london.txt | bangkok1~20.txt -> bangkok.txt """

        print "Saving data to: " + self.dst_corpora + "/" + "\033[1m" + str(filename) + "\033[0m"
        review_cnt = 0
        corpus_length = len(corpus)
        f_corpus = open(self.dst_corpora + "/" + filename, 'w+') # br stands for backend_review
        for review in corpus:
            review_cnt += 1
            f_corpus.write(review)

            sys.stdout.write("\rStatus: %s / %s"%(review_cnt, corpus_length))
            sys.stdout.flush()

        print "\n" + "-"*80

    def get_corpus_stars(self):
        """ load all reviews in data/backend_stats_reviews/ and merge them into one single file named 'corpus_stars.txt' """
        print "Starting to load: " + self.src_bsr
        for dirpath, dir_list, file_list in os.walk(self.src_bsr):
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
                        print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            self.corpus_stars.append(file.read())
            else:
                print "No file is found"
                print "-"*80

    def render_corpus_stars(self):
        """ all location1~20.txt -> corpus_stars.txt """

        print "Saving data to: " + self.dst_cs + "\033[1m" + "corpus_stars.txt" + "\033[0m"
        review_cnt = 0
        corpus_length = len(self.corpus_stars)
        f_corpus_stars = open(self.dst_cs + "corpus_stars.txt", 'w+') # br stands for backend_review
        for review in self.corpus_stars:
            review_cnt += 1
            f_corpus_stars.write(review)

            sys.stdout.write("\rStatus: %s / %s"%(review_cnt, corpus_length))
            sys.stdout.flush()

        print "\n" + "-"*80

    def get_sentiment_statistics(self):
        """ open and append *.json in data/sentiment_statistics into sentiment_statistics.json """

        sentiment_statistics = []
        for dirpath, dir_list, file_list in os.walk(self.src_ss):
            print "Walking into:", dirpath

            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"
                for f in file_list:
                    if f == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                        break
                    else:
                        print "Appending " + str(dirpath) + "/" + str(f) + " into sentiment_statistics"
                        sentiment_statistics.append(json.load(open(dirpath+"/"+f)))

            else:
                print "No file is found"
            print "-"*80
        #print sentiment_statistics
        return sentiment_statistics

    def get_merged_sentiment_statistics(self):
        """ accumulate the count for every sentiment word
        E.g. list[0] = {"good":1, "great":2}, list[1] = {"good":3, "great":4} -> sentiment_statistics = {"good":4, "great":6}
        """
        sentiment_statistics = self.get_sentiment_statistics()
        #print sentiment_statistics
        print "Merging sentiment_statistics' positive counts"

        count_list = np.zeros(len(sentiment_statistics[0]["positive_statistics"]))
        ss_cnt = 0
        ss_length = len(sentiment_statistics)
        for statistics in sentiment_statistics:

            positive_word_list = []
            stemmed_positive_word_list = []
            ss_cnt += 1
            for i in xrange(len(statistics["positive_statistics"])):
                positive_word_list.append(statistics["positive_statistics"][i]['word'])
                stemmed_positive_word_list.append(statistics["positive_statistics"][i]['stemmed_word'])
                count_list[i] += (np.asarray(statistics["positive_statistics"][i]['count']))

            strength = statistics["positive_statistics"][0]['strength']
            polarity = statistics["positive_statistics"][0]['polarity']

            sys.stdout.write("\rStatus: %s / %s"%(ss_cnt, ss_length))
            sys.stdout.flush()

        """ Putting them back to dictionary """
        print "\nPutting positive_statistics back to dictionary"
        positive_word_dict_list = []
        pwl_cnt = 0
        pwl_length = len(positive_word_list)
        for i in xrange(len(positive_word_list)):

            pwl_cnt += 1
            positive_word_dict = {"stemmed_word": stemmed_positive_word_list[i], "word": positive_word_list[i], "count": int(count_list[i]), "strength": strength, "polarity": polarity}
            positive_word_dict_list.append(positive_word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(pwl_cnt, pwl_length))
            sys.stdout.flush()

        #Sorting by count
        positive_statistics = sorted(positive_word_dict_list, key=itemgetter('count'), reverse = True)

        print "\n" + "-"*80
        print "Merging sentiment_statistics' negative counts"
        count_list = np.zeros(len(sentiment_statistics[0]["negative_statistics"]))
        ss_cnt = 0
        ss_length = len(sentiment_statistics)
        for statistics in sentiment_statistics:

            negative_word_list = []
            stemmed_negative_word_list = []
            ss_cnt += 1
            for i in xrange(len(statistics["negative_statistics"])):
                negative_word_list.append(statistics["negative_statistics"][i]['word'])
                stemmed_negative_word_list.append(statistics["negative_statistics"][i]['stemmed_word'])
                count_list[i] += (np.asarray(statistics["negative_statistics"][i]['count']))

            strength = statistics["negative_statistics"][0]['strength']
            polarity = statistics["negative_statistics"][0]['polarity']

            sys.stdout.write("\rStatus: %s / %s"%(ss_cnt, ss_length))
            sys.stdout.flush()

        """ Putting them back to dictionary """
        print "\nPutting negative_statistics back to dictionary"
        negative_word_dict_list = []
        nwl_cnt = 0
        nwl_length = len(negative_word_list)
        for i in xrange(len(negative_word_list)):

            nwl_cnt += 1
            negative_word_dict = {"stemmed_word": stemmed_negative_word_list[i], "word": negative_word_list[i], "count": int(count_list[i]), "strength": strength, "polarity": polarity}
            negative_word_dict_list.append(negative_word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(nwl_cnt, nwl_length))
            sys.stdout.flush()

        print "\n" + "-"*80
        #Sorting by count
        negative_statistics = sorted(negative_word_dict_list, key=itemgetter('count'), reverse = True)

	positive_statistics[:] = [dictionary for dictionary in positive_statistics if dictionary.get('count') > 10]
	negative_statistics[:] = [dictionary for dictionary in negative_statistics if dictionary.get('count') > 10]

        return positive_statistics, negative_statistics

    def save_sentiment_statistics(self):
        """ put keys in order and render json file """

        positive_statistics, negative_statistics = self.get_merged_sentiment_statistics()
        print "Saving data to:", "\033[1m" + self.dst_ss + "\033[0m"

        ps_cnt = 0
        ps_length = len(positive_statistics)
        positive_ordered_dict_list = []
        for word_dict in positive_statistics:
            ps_cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = ps_cnt
            ordered_dict["count"] = word_dict["count"]
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict["strength"] = word_dict["strength"]
            ordered_dict["polarity"] = word_dict["polarity"]
            positive_ordered_dict_list.append(NoIndent(ordered_dict))

        ns_cnt = 0
        ns_length = len(negative_statistics)
        negative_ordered_dict_list = []
        for word_dict in negative_statistics:
            ns_cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = ns_cnt
            ordered_dict["count"] = word_dict["count"]
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict["strength"] = word_dict["strength"]
            ordered_dict["polarity"] = word_dict["polarity"]
            negative_ordered_dict_list.append(NoIndent(ordered_dict))

        ss_ordered_dict = OrderedDict()
        ss_ordered_dict["positive_statistics"] = positive_ordered_dict_list
        ss_ordered_dict["negative_statistics"] = negative_ordered_dict_list

        f_ss = open(self.dst_ss, 'w+')
        f_ss.write( json.dumps( ss_ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "Done"

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_corpora)
        dir2 = os.path.dirname(self.dst_cs)
        dir3 = os.path.dirname(self.dst_ss)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            print "Creating directory: " + dir2
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            print "Creating directory: " + dir3
            os.makedirs(dir3)

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
    merger = Merger()
    merger.create_dirs()
    merger.get_corpora()
    merger.get_corpus_stars()
    merger.render_corpus_stars()
    merger.save_sentiment_statistics()
