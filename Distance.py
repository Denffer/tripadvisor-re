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

            sys.stdout.write("\rStatus: %s / %s"%(index+1, vocab_size))
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

    def get_top_cosine(self):
        """ calculate cosine distance get top** sentiment_words """

        print "Calculating Cosine Similarity between queries and every positive word"
        positive_cosine_similarity_list = []
        for query in self.queries:
            cosine_similarity_list = []
            for index in xrange(len(self.positive)):
                cosine_similarity_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cosine_similarity_list)), key=lambda k: cosine_similarity_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    positive_word =  self.positive[index]
                    word_dict = {"word": positive_word, "cosine_similarity": cosine_similarity_list[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, cosine_similarity_list[index]
            positive_cosine_similarity_list.append({"query": query, "top10_positive_cosine_similarity": word_dict_list})

        print "-"*70
        print "Calculating Cosine Similarity between queries and every negative word"
        negative_cosine_similarity_list = []
        for query in self.queries:
            cosine_similarity_list = []
            for index in xrange(len(self.negative)):
                cosine_similarity_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(cosine_similarity_list)), key=lambda k: cosine_similarity_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    negative_word =  self.negative[index]
                    word_dict = {"word": negative_word, "cosine_similarity": cosine_similarity_list[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, cosine_similarity_list[index]
            negative_cosine_similarity_list.append({"query": query, "top10_negative_cosine_similarity": word_dict_list})

        print "-"*70

        return positive_cosine_similarity_list, negative_cosine_similarity_list

    def get_top_dot(self):
        """ calculate dot product get top** sentiment_words """

        print "Calculating Dot Product between queries and every positive word"
        positive_dot_product_list = []
        for query in self.queries:
            dot_product_list = []
            for index in xrange(len(self.positive)):
                dot_product_list.append(np.dot(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(dot_product_list)), key=lambda k: dot_product_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    positive_word =  self.positive[index]
                    word_dict = {"word": positive_word, "dot_product": dot_product_list[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, dot_product_list[index]
            positive_dot_product_list.append({"query": query, "top10_positive_dot_product": word_dict_list})

        print "-"*70
        print "Calculating Dot Product between queries and every negative word"
        negative_dot_product_list = []
        for query in self.queries:
            dot_product_list = []
            for index in xrange(len(self.negative)):
                dot_product_list.append(np.dot(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(dot_product_list)), key=lambda k: dot_product_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    negative_word =  self.negative[index]
                    word_dict = {"word": negative_word, "dot_product": dot_product_list[index]}
                    word_dict_list.append(word_dict)
                    #print positive_word, cosine_similarity[index]
            negative_dot_product_list.append({"query": query, "top10_negative_dot_product": word_dict_list})

        print "-"*70

        return positive_dot_product_list, negative_dot_product_list

    def render(self):
        """ save every cosine_list for top1~5 as json file"""
        self.get_source()
        self.get_sentiment_statistics()
        positive_cosine_similarity_list, negative_cosine_similarity_list = self.get_top_cosine()
        positive_dot_product_list, negative_dot_product_list = self.get_top_dot()

        print "Putting both cosine_similarity and dot_product in order"
        #lexicon_ordered_dict = OrderedDict()

        entire_ordered_dict_list = []
        for p_cosine_query, n_cosine_query, p_dot_query, n_dot_query in zip(positive_cosine_similarity_list, negative_cosine_similarity_list, positive_dot_product_list, negative_dot_product_list):
            query_ordered_dict = OrderedDict()
            query_ordered_dict["query"] = p_cosine_query["query"] # n_cosine_query will also fit

            # positive cosine
            positive_cosine_ordered_dict_list = []
            index = 0
            for p_cosine_dict in p_cosine_query["top10_positive_cosine_similarity"]:

                index += 1
                p_word_dict = OrderedDict()
                p_word_dict["cosine_similarity"] = p_cosine_dict["cosine_similarity"]
                p_word_dict["index"] = index
                p_word_dict["count"] = p_cosine_dict["word"]["count"]
                p_word_dict["stemmed_word"] = p_cosine_dict["word"]["stemmed_word"]
                p_word_dict["word"] = p_cosine_dict["word"]["word"]
                p_word_dict["strength"] = p_cosine_dict["word"]["strength"]
                p_word_dict["polarity"] = p_cosine_dict["word"]["polarity"]
                positive_cosine_ordered_dict_list.append(NoIndent(p_word_dict))

            query_ordered_dict["top10_positive_cosine_similarity"] = positive_cosine_ordered_dict_list

            # negative cosine
            negative_cosine_ordered_dict_list = []
            index = 0
            for n_cosine_dict in n_cosine_query["top10_negative_cosine_similarity"]:

                index += 1
                n_word_dict = OrderedDict()
                n_word_dict["cosine_similarity"] = n_cosine_dict["cosine_similarity"]
                n_word_dict["index"] = index
                n_word_dict["count"] = n_cosine_dict["word"]["count"]
                n_word_dict["stemmed_word"] = n_cosine_dict["word"]["stemmed_word"]
                n_word_dict["word"] = n_cosine_dict["word"]["word"]
                n_word_dict["strength"] = n_cosine_dict["word"]["strength"]
                n_word_dict["polarity"] = n_cosine_dict["word"]["polarity"]
                negative_cosine_ordered_dict_list.append(NoIndent(n_word_dict))

            query_ordered_dict["top10_negative_cosine_similarity"] = negative_cosine_ordered_dict_list

            # positive dot
            positive_dot_ordered_dict_list = []
            index = 0
            for p_dot_dict in p_dot_query["top10_positive_dot_product"]:

                index += 1
                p_word_dict = OrderedDict()
                p_word_dict["dot_product"] = p_dot_dict["dot_product"]
                p_word_dict["index"] = index
                p_word_dict["count"] = p_dot_dict["word"]["count"]
                p_word_dict["stemmed_word"] = p_dot_dict["word"]["stemmed_word"]
                p_word_dict["word"] = p_dot_dict["word"]["word"]
                p_word_dict["strength"] = p_dot_dict["word"]["strength"]
                p_word_dict["polarity"] = p_dot_dict["word"]["polarity"]
                positive_dot_ordered_dict_list.append(NoIndent(p_word_dict))

            query_ordered_dict["top10_positive_dot_product"] = positive_dot_ordered_dict_list

            # negative dot
            negative_dot_ordered_dict_list = []
            index = 0
            for n_dot_dict in n_dot_query["top10_negative_dot_product"]:

                index += 1
                n_word_dict = OrderedDict()
                n_word_dict["dot_product"] = n_dot_dict["dot_product"]
                n_word_dict["index"] = index
                n_word_dict["count"] = n_dot_dict["word"]["count"]
                n_word_dict["stemmed_word"] = n_dot_dict["word"]["stemmed_word"]
                n_word_dict["word"] = n_dot_dict["word"]["word"]
                n_word_dict["strength"] = n_dot_dict["word"]["strength"]
                n_word_dict["polarity"] = n_dot_dict["word"]["polarity"]
                negative_dot_ordered_dict_list.append(NoIndent(n_word_dict))

            query_ordered_dict["top10_negative_dot_product"] = negative_dot_ordered_dict_list
            
            # finish one query
            entire_ordered_dict_list.append(query_ordered_dict)

	f = open(self.dst, "w")
        f.write(json.dumps(entire_ordered_dict_list, indent = 4, cls=NoIndentEncoder))
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
    lexiconMaker2 = LexiconMaker2()
    lexiconMaker2.render()

