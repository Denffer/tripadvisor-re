import sys, os, json, uuid, re, pprint
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import numpy as np
from scipy import spatial

class MakeStarsLexicon:
    """ This program aims to calculate
    (1) top 500 sentiment words in pos_tagged_lexicon with nearest cosine similarity
        for star_1 & star_2 & star_3 & star_4 & star_5
    """

    def __init__(self):
        """ initialize values """
        self.src = sys.argv[1]  # input -> data/line/norm_vectors200/starred_corpus.txt
        self.src_pos_tagged = "data/lexicon/processed_pos_tagged_lexicon.json"

        self.dst = "data/lexicon/"

        self.topN = 500
        self.queries = {"1_star":1, "2_star":2, "3_star":3, "4_star":4, "5_star":5}
        self.vocab_size = 0
        self.dimension_size = 0

	self.unique_words = {}
        self.sentiment_word_dicts = []
        self.vectors200 = []

    def get_source(self):
	""" first call readline() to read the first line of vectors200 file to get vocab_size and dimension_size """

        print "(1) Loading data from " + "\033[1m" + self.src + "\033[0m"

        f_src = open(self.src, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')
        self.vocab_size = int(vocab_size)
        self.dimension_size = int(dimension_size)

        print "Building index ..."
        for index in range(0, self.vocab_size):
            line = f_src.readline().split(' ')
            # {"good":1, "attraciton":2, "Tokyo": 3}
            self.unique_words[line[0]]=index
            self.vectors200.append([float(i) for i in line[1:-1]])

            sys.stdout.write("\rStatus: %s / %s"%(index+1, self.vocab_size))
            sys.stdout.flush()

        f_src.close()
        print "\n" + "-"*70

    def get_processed_pos_tagged_lexicon(self):
	""" open processed_pos_tagged_lexicon.json and load dictionaries """

        print "(2) Loading data from " + "\033[1m" + self.src_pos_tagged + "\033[0m"
        with open(self.src_pos_tagged, 'r') as f:
            pos_tagged_lexicon = json.load(f)

        index = 0
        length = len(pos_tagged_lexicon)
        print "Building sentiment_word_dicts and vectors200 ..."
        for word_dict in pos_tagged_lexicon:
            index += 1
            """ E.g. word_dict = {"index": 1, "count": 3, "stemmed_word": "good", "word": ["good"]} """
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    self.sentiment_word_dicts.append(word_dict)
                    self.vectors200.append(self.vectors200[value])

            sys.stdout.write("\rStatus: %s / %s"%(index, length))
            sys.stdout.flush()

        print "\n" + "-"*70

    def get_topN_sentiment_words(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """

        print "(3) Calculating " + "\033[1m" + "Cosine Similarity" + "\033[0m" + " between queries and every " + "\033[1m" + "sentiment" + "\033[0m" + " word"
        star_cnt = 0 # loop 1_star to 5_star
        for query in self.queries:
            cos_sim_list = []
            for index in xrange(len(self.sentiment_word_dicts)):
                # cosine_similarity ranges from -1 ~ 1
                cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)
            topN_sentiment_words = []
            s = self.sentiment_word_dicts
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    sentiment_word = {"cos_sim": cos_sim_list[index], "count": s[index]["count"], "stemmed_word": s[index]["stemmed_word"], "word": s[index]["word"]}
                    topN_sentiment_words.append(sentiment_word)

            self.render(query, topN_sentiment_words)

        print "-"*50

    def render(self, query, topN_sentiment_words):
        """ save every sentiment_word_dict in sentiment_word_dicts for 1_star ~ 5_star """

        print "Constructing", "\033[1m" + str(query) + "\033[0m", "lexicon"

        query_ordered_dict = OrderedDict()
        query_ordered_dict["query"] = str(query)
        ordered_topN_sentiment_words = []
        index = 0
        for word_dict in topN_sentiment_words:

            index += 1
            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["cos_sim"] = word_dict["cos_sim"]
            orderedDict["count"] = word_dict["count"]
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            ordered_topN_sentiment_words.append(NoIndent(orderedDict))

        query_ordered_dict["topN_sentiment_words"] = ordered_topN_sentiment_words

        print "Saving lexicon to", str(self.dst), "\033[1m" + str(query) + ".json" + "\033[0m"
        f = open(self.dst + str(query) + ".json", "w")
        f.write(json.dumps(query_ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "-"*50


    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def run(self):
        """ run the entire program """
        self.get_source()
        self.get_processed_pos_tagged_lexicon()
        self.create_dirs()
        self.get_topN_sentiment_words()
        print "Done"

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
    process = MakeStarsLexicon()
    process.run()
