import sys, os, json, uuid
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import numpy as np
from scipy import spatial

class LexiconMaker2:
    """ This program aims to
    (1) calculate nearest 100 dot product (or cosine similarity) sentiment words for star_1~5
    (2) render enhanced_lexicon.json
    """

    def __init__(self):
        self.src_ss = "data/lexicon/sentiment_statistics.json"
        self.src = "data/line/vectors200_stars/corpus_stars.txt"
        self.dst = "./data/lexicon/lexicon2.json"

        self.topN = 10
        self.queries = ["star_1", "star_2", "star_3", "star_4", "star_5"]
        self.positive = []
        self.negative = []
        self.vocab_size = 0
        self.dimension_size = 0

	self.unique_words = {}
        self.vectors200 = []
        self.positive_vectors200 = []
        self.negative_vectors200 = []
        self.lexicon = []

    def get_source(self):
	""" first call readline() to read thefirst line of vectors200 file to get vocab_size and dimension_size """

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

            sys.stdout.write("\rStatus: %s / %s"%(index, vocab_size))
            sys.stdout.flush()

        f_src.close()
        print "\n" + "-"*70

    def get_sentiment_statistics(self):
	""" open sentiment_statistics.json file and load dictionary """

        print "Loading data from " + "\033[1m" + self.src_ss + "\033[0m"
        with open(self.src_ss, 'r') as f_ss:
            sentiment_statistics = json.load(f_ss)

        self.positive = sentiment_statistics["positive_statistics"]
        index = 0
        for word_dict in self.positive:
            index += 1
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    word_dict["index"] = index
                    # length of self.vectors200 equals to that of self.unique_words
                    self.positive_vectors200.append(self.vectors200[value])

        self.negative = sentiment_statistics["negative_statistics"]
        index = 0
        for word_dict in self.negative:
            index += 1
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    word_dict["index"] = index
                    # length of self.vectors200 equals to that of self.unique_words
                    self.negative_vectors200.append(self.vectors200[value])

        print "-"*70

    def get_top_sentiment_words(self):
        """ calculate cosine distance get top** sentiment_words """

        self.get_sentiment_statistics()

        print "Calculating Cosine Similarity between queries and every positive word"
        positive_cosine_similarities_list = []
        for query in self.queries:
            cosine_similarities = []
            for index in xrange(len(self.positive)):
                cosine_similarities.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cosine_similarities)), key=lambda k: cosine_similarities[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    positive_word =  self.positive[index]
                    word_dict = {"word": positive_word, "cosine_similarity": cosine_similarities[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, cosine_similarities[index]
            positive_cosine_similarities_list.append({"query": query, "top10_positive_cosine_similarities": word_dict_list})

        print "-"*70
        print "Calculating Cosine Similarity between queries and every negative word"
        negative_cosine_similarities_list = []
        for query in self.queries:
            cosine_similarities = []
            for index in xrange(len(self.negative)):
                cosine_similarities.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cosine_similarities)), key=lambda k: cosine_similarities[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    negative_word =  self.negative[index]
                    word_dict = {"word": negative_word, "cosine_similarity": cosine_similarities[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, cosine_similarities[index]
            negative_cosine_similarities_list.append({"query": query, "top10_negative_cosine_similarities": word_dict_list})

        print "-"*70

        return positive_cosine_similarities_list, negative_cosine_similarities_list

    def render(self):
        """ save every cosine_list for top1~5 as json file"""
        self.get_source()
        positive, negative = self.get_top_sentiment_words()

        print "Putting both cosine_similarities in order"
        #lexicon_ordered_dict = OrderedDict()

        positive_ordered_dict_list = []
        for p_query, n_query in zip(positive, negative):
            query_ordered_dict = OrderedDict()
            query_ordered_dict["query"] = p_query["query"] # n_query will also fit

            cosine_ordered_dict_list = []
            index = 0
            for p_cosine_dict, n_cosine_dict in zip(p_query["top10_positive_cosine_similarities"], n_query["top10_negative_cosine_similarities"]):
                cosine_ordered_dict = OrderedDict()

                index += 1
                p_word_dict = OrderedDict()
                p_word_dict["cosine_similarity"] = p_cosine_dict["cosine_similarity"]
                p_word_dict["index"] = index
                p_word_dict["count"] = p_cosine_dict["word"]["count"]
                p_word_dict["stemmed_word"] = p_cosine_dict["word"]["stemmed_word"]
                p_word_dict["word"] = p_cosine_dict["word"]["word"]
                p_word_dict["strength"] = p_cosine_dict["word"]["strength"]
                p_word_dict["polarity"] = p_cosine_dict["word"]["polarity"]
                cosine_ordered_dict["positive_sentiment_word"] = NoIndent(p_word_dict)

                n_word_dict = OrderedDict()
                n_word_dict["cosine_similarity"] = n_cosine_dict["cosine_similarity"]
                n_word_dict["index"] = index
                n_word_dict["count"] = n_cosine_dict["word"]["count"]
                n_word_dict["stemmed_word"] = n_cosine_dict["word"]["stemmed_word"]
                n_word_dict["word"] = n_cosine_dict["word"]["word"]
                n_word_dict["strength"] = n_cosine_dict["word"]["strength"]
                n_word_dict["polarity"] = n_cosine_dict["word"]["polarity"]
                cosine_ordered_dict["negative_sentiment_word"] = NoIndent(n_word_dict)

                cosine_ordered_dict_list.append(cosine_ordered_dict)

            query_ordered_dict["top10_cosine_similiarity"] = cosine_ordered_dict_list
            positive_ordered_dict_list.append(query_ordered_dict)

	f = open(self.dst, "w")
        f.write(json.dumps(positive_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

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
    lexiconMaker2 = LexiconMaker2()
    lexiconMaker2.render()

