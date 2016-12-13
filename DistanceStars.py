import sys, os, json, uuid, re, pprint
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import numpy as np
from scipy import spatial

class DistanceStars:
    """ This program aims to calculate
    (1) 10 positive and negative sentiment words with nearest dot product
    (2) 10 positive and negative sentiment words with nearest cosine similarity
        for star_1 & star_2 & star_3 & star_4 & star_5 &
    """

    def __init__(self):
        """ initialize values """
        """ data/line/vectors200/All_Stars.txt should be given as sys.argv[1] """
        self.src = sys.argv[1]
        self.src_ss = "data/lexicon/sentiment_statistics.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)

        self.dst_d = "data/distance/" + self.filename + "/"

        self.topN = 200
        self.queries = {"star_1":1, "star_2":2, "star_3":3, "star_4":4, "star_5":5}
        self.positive_statistics = []
        self.negative_statistics = []
        self.vocab_size = 0
        self.dimension_size = 0

	self.unique_words = {}
        self.vectors200 = []
        self.positive_vectors200 = []
        self.negative_vectors200 = []

    def get_source(self):
	""" first call readline() to read the first line of vectors200 file to get vocab_size and dimension_size """

        print "Loading data from " + "\033[1m" + self.src + "\033[0m"

        f_src = open(self.src, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')
        self.vocab_size = int(vocab_size)
        self.dimension_size = int(dimension_size)

        print "Building Index"
        for index in range(0, self.vocab_size):
            line = f_src.readline().split(' ')
            # {"good":1, "attraciton":2, "Tokyo": 3}
            self.unique_words[line[0]]=index
            self.vectors200.append([float(i) for i in line[1:-1]])

            sys.stdout.write("\rStatus: %s / %s"%(index+1, self.vocab_size))
            sys.stdout.flush()

        f_src.close()
        print "\n" + "-"*70

    def get_sentiment_statistics(self):
	""" open sentiment_statistics.json file and load dictionary """

        print "Loading data from " + "\033[1m" + self.src_ss + "\033[0m"
        with open(self.src_ss, 'r') as f_ss:
            sentiment_statistics = json.load(f_ss)

        positive_statistics = sentiment_statistics["positive_statistics"]
        """ E.g. {"index": 1, "count": 3, "stemmed_word": "good", "word": ["good"]} """
        for word_dict in positive_statistics:
            # Only put positive word matched in unique_words into self.negative_statistics
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    self.positive_statistics.append(word_dict)
                    self.positive_vectors200.append(self.vectors200[value])

        negative_statistics = sentiment_statistics["negative_statistics"]
        """ E.g. {"index": 1, "count": 4, "stemmed_word": "bad", "word": ["bad"]} """
        for word_dict in negative_statistics:
            # Only put negative word matched in unique_words into self.negative_statistics
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    self.negative_statistics.append(word_dict)
                    self.negative_vectors200.append(self.vectors200[value])

        print "-"*70

    def get_cosine_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ cos_sim stands for cosine_similarity """

        print "Calculating " + "\033[1m" + "Cosine" + "\033[0m" + " Similarity between queries and every " + "\033[1m" + "positive" + "\033[0m" + " word"

        positive_cosine_topN = []
        for query in self.queries:
            cos_sim_list = []
            for index in xrange(len(self.positive_statistics)):
                # cosine_similarity ranges from -1 ~ 1
                cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.positive_statistics[index], "cos_sim": cos_sim_list[index]}
                    word_dict_list.append(word_dict)

            positive_cosine_topN.append({"query": query, "positive_topN_cosine_similarity": word_dict_list})

        print "-"*70
        print "Calculating " + "\033[1m" + "Cosine" + "\033[0m" + " Similarity between queries and every " + "\033[1m" + "negative" + "\033[0m" + " word"

        negative_cosine_topN = []
        for query in self.queries:
            cos_sim_list = []
            for index in xrange(len(self.negative_statistics)):
                # cosine_similarity ranges from -1 ~ 1
                cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.negative_statistics[index], "cos_sim": cos_sim_list[index]}
                    word_dict_list.append(word_dict)

            negative_cosine_topN.append({"query": query, "negative_topN_cosine_similarity": word_dict_list})

        print "-"*70
        return positive_cosine_topN, negative_cosine_topN

    def get_dot_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ dot_prod stands for dot_product """

        print "Calculating " + "\033[1m" + "Dot" + "\033[0m" + " Product between queries and every " + "\033[1m" + "positive" + "\033[0m" + " word"

        # positive dot
        positive_dot_topN = []
        for query in self.queries:
            dot_prod_list = []
            for index in xrange(len(self.positive_statistics)):
                dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(dot_prod_list)), key=lambda k: dot_prod_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.positive_statistics[index], "dot_prod": dot_prod_list[index]}
                    word_dict_list.append(word_dict)

            positive_dot_topN.append({"query": query, "positive_topN_dot_product": word_dict_list})

        print "-"*70
        print "Calculating " + "\033[1m" + "Dot" + "\033[0m" + " Product between queries and every " + "\033[1m" + "negative" + "\033[0m" + " word"

        # negative dot
        negative_dot_topN = []
        for query in self.queries:
            dot_prod_list = []
            for index in xrange(len(self.negative_statistics)):
                dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(dot_prod_list)), key=lambda k: dot_prod_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.negative_statistics[index], "dot_prod": dot_prod_list[index]}
                    word_dict_list.append(word_dict)

            negative_dot_topN.append({"query": query, "negative_topN_dot_product": word_dict_list})

        print "-"*70
        return positive_dot_topN, negative_dot_topN

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_d)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def render(self):
        """ save every cosine_list for top1~5 as json file"""
        self.get_source()
        self.get_sentiment_statistics()
        self.create_dirs()

        positive_cosine_topN, negative_cosine_topN = self.get_cosine_topN()
        positive_dot_topN, negative_dot_topN = self.get_dot_topN()

        print "Putting all dictionaries in order"

        for p_cos_word_dict, n_cos_word_dict, p_dot_word_dict, n_dot_word_dict in zip(positive_cosine_topN, negative_cosine_topN, positive_dot_topN, negative_dot_topN):
            query_ordered_dict = OrderedDict()
            query_ordered_dict["query"] = p_cos_word_dict["query"]

            # (1) positive cosine
            positive_cosine_word_dict_list = []
            index = 0
            for cosine_word_dict in p_cos_word_dict["positive_topN_cosine_similarity"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cos_sim"] = cosine_word_dict["cos_sim"]
                ordered_dict["count"] = cosine_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = cosine_word_dict["word"]["word"]
                positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["positive_topN_cosine_similarity"] = positive_cosine_word_dict_list

            # (2) negative cosine
            negative_cosine_word_dict_list = []
            index = 0
            for cosine_word_dict in n_cos_word_dict["negative_topN_cosine_similarity"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cos_sim"] = cosine_word_dict["cos_sim"]
                ordered_dict["count"] = cosine_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = cosine_word_dict["word"]["word"]
                negative_cosine_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["negative_topN_cosine_similarity"] = negative_cosine_word_dict_list

            # (3) positive dot
            positive_dot_word_dict_list = []
            index = 0
            for dot_word_dict in p_dot_word_dict["positive_topN_dot_product"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["dot"] = dot_word_dict["dot_prod"]
                ordered_dict["count"] = dot_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = dot_word_dict["word"]["word"]
                positive_dot_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["positive_topN_dot_product"] = positive_dot_word_dict_list

            # (4) negative dot
            negative_dot_word_dict_list = []
            index = 0
            for dot_word_dict in n_dot_word_dict["negative_topN_dot_product"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["dot"] = dot_word_dict["dot_prod"]
                ordered_dict["count"] = dot_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = dot_word_dict["word"]["word"]
                negative_dot_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["negative_topN_dot_product"] = negative_dot_word_dict_list

            print "Writing to " + "\033[1m" + str(self.dst_d) + query_ordered_dict["query"] + ".json" + "\033[0m"
            f = open(self.dst_d + query_ordered_dict["query"] + ".json", "w")
            f.write(json.dumps(query_ordered_dict, indent = 4, cls=NoIndentEncoder))

        print "-"*80
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
    distanceStars = DistanceStars()
    distanceStars.render()

