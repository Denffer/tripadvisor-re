import json, os, sys, uuid, re
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class Merger:
    """ This program aims to
        (1) Merge data/backend_reviews/*.txt into corpus.txt
        (2) Merge data/sentiment_statistics/*.json into sentiment_statistics.json  """

    def __init__(self):
        self.src_br = "data/backend_reviews/"
        self.src_ss = "data/sentiment_statistics/"

        self.dst_corpora = "data/corpora/"
        self.dst_ss = "data/line/sentiment_statistics.json"

    def get_corpora(self):
        """ load all reviews in data/backend_reviews/ and merge them """
        corpus = []
        for dirpath, dir_list, file_list in os.walk(self.src_br):
            print "Walking into directory: " + str(dirpath)

            corpus = []
            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + str(file_list)

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) != ".DS_Store":
                        file_cnt += 1
                        print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            corpus.append(file.read())

                filename = re.sub('\_[0-9]+', '', file_list[0])
                self.render_corpus(corpus, filename)

            else:
                print "No file is found"
                print "-"*80

    def render_corpus(self, corpus, filename):
        """ london1~20.txt -> london.txt | bangkok1~20.txt -> london.txt """

        print "Saving data to: " + self.dst_corpora + "\033[1m" + str(filename) + "\033[0m"
        review_cnt = 0
        corpus_length = len(corpus)
        f_corpus = open(self.dst_corpora + "/" + filename, 'w+') # br stands for backend_review
        for review in corpus:
            review_cnt += 1
            f_corpus.write(review)

            sys.stdout.write("\rStatus: %s / %s"%(review_cnt, corpus_length))
            sys.stdout.flush()

        print "\n" + "-"*80

    def get_sentiment_statistics(self):
        """ open and append *.json in data/sentiment_statistics into sentiment_statistics.json """

        src_files = []
        sentiment_statistics = []
        for dirpath, dir_list, file_list in os.walk(self.src_ss):
            print "Loading data from:", dirpath

            file_cnt = 0
            length = len(file_list)
            for f in file_list:
                if f != ".DS_Store":
                    file_cnt += 1
                    print "Opening " + str(dirpath) + str(f) + " into sentiment_statistics"
                    sentiment_statistics.append(json.load(open(dirpath+f)))

        #print sentiment_statistics
        return sentiment_statistics

    def get_merged_sentiment_statistics(self):
        """ accumulate the count for every sentiment word
        E.g. list[0] = {"good":1, "great":2}, list[1] = {"good":3, "great":4} -> sentiment_statistics = {"good":4, "great":6}
        """
        sentiment_statistics = self.get_sentiment_statistics()

        print "Merging sentiment_statistics' counts"

        count_list = np.zeros(len(sentiment_statistics[0]))
        ss_cnt = 0
        ss_length = len(sentiment_statistics)
        for statistics in sentiment_statistics:

            sentiment_word_list = []
            stemmed_sentiment_word_list = []
            ss_cnt += 1
            for i in xrange(len(statistics)):
                sentiment_word_list.append(statistics[i]['word'])
                stemmed_sentiment_word_list.append(statistics[i]['stemmed_word'])
                count_list[i] += (np.asarray(statistics[i]['count']))

            sys.stdout.write("\rStatus: %s / %s"%(ss_cnt, ss_length))
            sys.stdout.flush()

        """ Putting them back to dictionary """
        sentiment_word_dict_list = []
        swl_cnt = 0
        swl_length = len(sentiment_word_list)
        for i in xrange(len(sentiment_word_list)):

            swl_cnt += 1
            sentiment_word_dict = {"stemmed_word": stemmed_sentiment_word_list[i], "word": sentiment_word_list[i], "count": int(count_list[i])}
            sentiment_word_dict_list.append(sentiment_word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(swl_cnt, swl_length))
            sys.stdout.flush()

        #Sorting by count
        sentiment_statistics = sorted(sentiment_word_dict_list, key=itemgetter('count'), reverse = True)
        return sentiment_statistics

    def save_sentiment_statistics(self):
        """ put keys in order and render json file """

        sentiment_statistics = self.get_merged_sentiment_statistics()
        print "\nSaving data to:", self.dst_ss[:10] + "\033[1m" + self.dst_ss[10:] + "\033[0m"

        ss_cnt = 0
        ss_length = len(sentiment_statistics)
        ordered_dict_list = []
        for word_dict in sentiment_statistics:
            ss_cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = ss_cnt
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]
            ordered_dict["count"] = word_dict["count"]
            ordered_dict_list.append(NoIndent(ordered_dict))

        f_ss = open(self.dst_ss, 'w+')
        f_ss.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "Done"

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_corpora)
        dir2 = os.path.dirname(self.dst_ss)

        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)

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
    merger.save_sentiment_statistics()

