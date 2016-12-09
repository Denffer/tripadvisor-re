import sys, os, json, uuid, re
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import numpy as np
from scipy import spatial

class Distance:
    """ This program aims to calculate
    (1) 10 positive and negative sentiment words with nearest dot product
    (2) 10 positive and negative sentiment words with nearest cosine similarity
        for the given queries
    """

    def __init__(self, argv1, argv2):
        self.src = argv1
        self.src_ss = "data/lexicon/enhanced_lexicon.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src_fr = "data/frontend_reviews/" + self.filename + "/"
        #self.dst_d = "./data/distance/" + self.filename + ".json"
        self.dst_d = "./data/distance/" + self.filename + "/" + self.filename + "_lambda" + str(argv2).replace(".","") + ".json"

        self.tuning_lambda = float(argv2)
        self.dst_r = "./data/ranking/" + self.filename + ".json"
        self.dst_rl = "./data/ranking/" + self.filename + "/" + self.filename + "_lambda" + str(argv2).replace(".","") + ".json"
        self.verbose = 0

        self.topN = 200
        self.queries = []
        self.positive_statistics = []
        self.negative_statistics = []
        self.vocab_size = 0
        self.dimension_size = 0

	self.unique_words = {}
        self.vectors200 = []
        self.positive_vectors200 = []
        self.negative_vectors200 = []
        self.attractions = {}

    def get_source(self):
	""" first call readline() to read thefirst line of vectors200 file to get vocab_size and dimension_size """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src + "\033[0m"
        f_src = open(self.src, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')
        self.vocab_size = int(vocab_size)
        self.dimension_size = int(dimension_size)

        if self.verbose:
            print "Building Index"
        for index in range(0, self.vocab_size):
            line = f_src.readline().split(' ')
            # {"good":1, "attraciton":2, "Tokyo": 3}
            self.unique_words[line[0]]=index
            self.vectors200.append([float(i) for i in line[1:-1]])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index+1, vocab_size))
                sys.stdout.flush()

        f_src.close()
        if self.verbose:
            print "\n" + "-"*70

    def get_attractions(self):
        """ get attraction_names as queries """

        attraction_names = []
        if self.verbose:
            print "Loading attraction_names from: " + self.src_fr
        for dirpath, dir_list, file_list in os.walk(self.src_fr):
            if self.verbose:
                print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                if self.verbose:
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        if self.verbose:
                            print "Removing " + dirpath + str(f)
                        os.remove(dirpath+ "/"+ f)
                        break
                    else:
                        file_cnt += 1
                        if self.verbose:
                            print "Merging " + str(dirpath) + str(f)
                        with open(dirpath + f) as file:
                            attraction = json.load(file)
                            # attraction_al => attraction append location E.g. Happy-Temple_Bangkok
                            attraction_al = attraction["attraction_name"].lower() + "_" + attraction["location"].lower()
                            attraction_ranking = attraction["ranking"]
                            self.attractions.update({attraction_al: attraction_ranking})
            else:
                if self.verbose:
                    print "No file is found"
                    print "-"*80

        if self.verbose:
            print "-"*80
        #print self.attractions
        return self.attractions

    def get_sentiment_statistics(self):
	""" open sentiment_statistics.json file and load dictionary """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_ss + "\033[0m"
        with open(self.src_ss, 'r') as f_ss:
            sentiment_statistics = json.load(f_ss)

        positive_statistics = sentiment_statistics["positive"]
        """ E.g. {"index": 1, "count": 3, "stemmed_word": "good", "word": ["good"]} """
        for word_dict in positive_statistics:
            # Only put positive word matched in unique_words into self.negative_statistics
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    self.positive_statistics.append(word_dict)
                    self.positive_vectors200.append(self.vectors200[value])

        negative_statistics = sentiment_statistics["negative"]
        """ E.g. {"index": 1, "count": 4, "stemmed_word": "bad", "word": ["bad"]} """
        for word_dict in negative_statistics:
            # Only put negative word matched in unique_words into self.negative_statistics
            for key, value in self.unique_words.iteritems():
                if word_dict["stemmed_word"] == key:
                    self.negative_statistics.append(word_dict)
                    self.negative_vectors200.append(self.vectors200[value])

        if self.verbose:
            print "-"*70

    def get_cosine_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ cos_sim stands for cosine_similarity """

        if self.verbose:
            print "Calculating Cosine Similarity between queries and every positive word"

        positive_cosine_topN = []
        for query in self.queries:
            cos_sim_list = []
            for index in xrange(len(self.positive_statistics)):
                # cosine_similarity ranges from -1 ~ 1
                cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            sorted_index = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.positive_statistics[index], "cos_sim": cos_sim_list[index]}
                    word_dict_list.append(word_dict)

            topN_cos_sim_list = [float(word_dict["cos_sim"]) for word_dict in word_dict_list]
            # calculate the score out of topN cosine similarity
            topN_cos_sim_list = sorted(topN_cos_sim_list)
            cos_score =  self.tuning_lambda * sum(topN_cos_sim_list[:3])/len(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list)/len(topN_cos_sim_list)
            # cos_score =  self.tuning_lambda * max(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list) / len(topN_cos_sim_list)
            positive_cosine_topN.append({"query": query, "positive_topN_cosine_similarity": word_dict_list, "cos_score": cos_score})

        if self.verbose:
            print "-"*70
            print "Calculating Cosine Similarity between queries and every negative word"

        negative_cosine_topN = []
        for query in self.queries:
            cos_sim_list = []
            for index in xrange(len(self.negative_statistics)):
                # cosine_similarity ranges from -1 ~ 1
                cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            sorted_index = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.negative_statistics[index], "cos_sim": cos_sim_list[index]}
                    word_dict_list.append(word_dict)

            topN_cos_sim_list = [float(word_dict["cos_sim"]) for word_dict in word_dict_list]
            # calculate the score out of topN cosine similarity
            topN_cos_sim_list = sorted(topN_cos_sim_list)
            cos_score =  self.tuning_lambda * sum(topN_cos_sim_list[:3])/len(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list)/len(topN_cos_sim_list)
            # cos_score =  self.tuning_lambda * max(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list) / len(topN_cos_sim_list)
            negative_cosine_topN.append({"query": query, "negative_topN_cosine_similarity": word_dict_list, "cos_score": cos_score})

        if self.verbose:
            print "-"*70
        return positive_cosine_topN, negative_cosine_topN

    def get_dot_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ dot_prod stands for dot_product """

        if self.verbose:
            print "Calculating Dot Product between queries and every positive word"

        # positive dot
        positive_dot_topN = []
        for query in self.queries:
            dot_prod_list = []
            for index in xrange(len(self.positive_statistics)):
                dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            sorted_index = sorted(range(len(dot_prod_list)), key=lambda k: dot_prod_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.positive_statistics[index], "dot_prod": dot_prod_list[index]}
                    word_dict_list.append(word_dict)

            topN_dot_prod_list = [float(word_dict["dot_prod"]) for word_dict in word_dict_list]
            topN_dot_prod_list = sorted(topN_dot_prod_list)
            dot_score =  self.tuning_lambda * sum(topN_dot_prod_list[:3])/len(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list)/len(topN_dot_prod_list)
            # dot_score =  self.tuning_lambda * max(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list) / len(topN_dot_prod_list)
            positive_dot_topN.append({"query": query, "positive_topN_dot_product": word_dict_list, "dot_score": dot_score})

        if self.verbose:
            print "-"*70
            print "Calculating Dot Product between queries and every negative word"

        # negative dot
        negative_dot_topN = []
        for query in self.queries:
            dot_prod_list = []
            for index in xrange(len(self.negative_statistics)):
                dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.negative_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"

            sorted_index = sorted(range(len(dot_prod_list)), key=lambda k: dot_prod_list[k], reverse=True)
            word_dict_list = []
            for i, index in enumerate(sorted_index):
                if i < self.topN:
                    word_dict = {"word": self.negative_statistics[index], "dot_prod": dot_prod_list[index]}
                    word_dict_list.append(word_dict)

            topN_dot_prod_list = [float(word_dict["dot_prod"]) for word_dict in word_dict_list]
            topN_dot_prod_list = sorted(topN_dot_prod_list)
            dot_score =  self.tuning_lambda * sum(topN_dot_prod_list[:3])/len(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list)/len(topN_dot_prod_list)
            # dot_score =  self.tuning_lambda * max(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list) / len(topN_dot_prod_list)
            negative_dot_topN.append({"query": query, "negative_topN_dot_product": word_dict_list, "dot_score": dot_score})

        if self.verbose:
            print "-"*70
        return positive_dot_topN, negative_dot_topN

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_d)
        dir2 = os.path.dirname(self.dst_r)
        dir3 = os.path.dirname(self.dst_rl)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            print "Creating directory: " + dir2
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            print "Creating directory: " + dir3
            os.makedirs(dir3)

    def render(self):
        """ save every cosine_list for top1~5 as json file"""
        self.get_source()
        self.get_sentiment_statistics()
        self.queries = self.get_attractions().keys()
        self.create_dirs()

        positive_cosine_topN, negative_cosine_topN = self.get_cosine_topN()
        positive_dot_topN, negative_dot_topN = self.get_dot_topN()

        if self.verbose:
            print "Putting all dictionaries in order"

        query_ordered_dict_list = []
        for p_cos_word_dict, n_cos_word_dict, p_dot_word_dict, n_dot_word_dict in zip(positive_cosine_topN, negative_cosine_topN, positive_dot_topN, negative_dot_topN):
            query_ordered_dict = OrderedDict()
            query_ordered_dict["query"] = p_cos_word_dict["query"]

            # positive cosine
            positive_cosine_word_dict_list = []
            index = 0
            for cosine_word_dict in p_cos_word_dict["positive_topN_cosine_similarity"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                ordered_dict["count"] = cosine_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = cosine_word_dict["word"]["word"]
                positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["positive_topN_cosine_similarity"] = positive_cosine_word_dict_list

            # negative cosine
            negative_cosine_word_dict_list = []
            index = 0
            for cosine_word_dict in n_cos_word_dict["negative_topN_cosine_similarity"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                ordered_dict["count"] = cosine_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = cosine_word_dict["word"]["word"]
                negative_cosine_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["negative_topN_cosine_similarity"] = negative_cosine_word_dict_list

            # positive dot
            positive_dot_word_dict_list = []
            index = 0
            for dot_word_dict in p_dot_word_dict["positive_topN_dot_product"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                ordered_dict["count"] = dot_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = dot_word_dict["word"]["word"]
                positive_dot_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["positive_topN_dot_product"] = positive_dot_word_dict_list

            # negative dot
            negative_dot_word_dict_list = []
            index = 0
            for dot_word_dict in n_dot_word_dict["negative_topN_dot_product"]:

                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                ordered_dict["count"] = dot_word_dict["word"]["count"]
                ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                ordered_dict["word"] = dot_word_dict["word"]["word"]
                negative_dot_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["negative_topN_dot_product"] = negative_dot_word_dict_list

            # append one query after another
            query_ordered_dict_list.append(query_ordered_dict)

        if self.verbose:
            print "Writing to " + "\033[1m" + str(self.dst_d) + "\033[0m"
	f = open(self.dst_d, "w")
        f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))
        if self.verbose:
            print "-"*80

        if self.verbose:
            print "Ranking queries according to average cosine_similarity and dot_product"
        outer_ordered_dict = OrderedDict() #FIXME positive - negative

        # (1) cos_score
        score_list = []
        for p_cos_word_dict, n_cos_word_dict in zip(positive_cosine_topN, negative_cosine_topN):
            #score = p_cos_word_dict["cos_score"]
            score = p_cos_word_dict["cos_score"] - n_cos_word_dict["cos_score"]
            score_list.append({"attraction_name": p_cos_word_dict["query"], "score": score})

        # derive ranking_list from a the unsorted score_list
        ranking_list = sorted(score_list, key=lambda k: k['score'], reverse = True)

        processed_ranking_list = []
        ranking = 0
        for rank_dict in ranking_list:
            ranking += 1
            rank_ordered_dict = OrderedDict()
            rank_ordered_dict['attraction_name'] = rank_dict['attraction_name']
            rank_ordered_dict['ranking'] = ranking
            rank_ordered_dict['original_ranking'] = self.attractions[rank_dict['attraction_name']]
            rank_ordered_dict['score'] = rank_dict['score']
            processed_ranking_list.append(rank_ordered_dict)
        outer_ordered_dict['cosine_ranking'] = processed_ranking_list

        # (2) dot_score
        score_list = []
        for p_dot_word_dict, n_dot_word_dict in zip(positive_dot_topN, negative_dot_topN):
            #score = p_dot_word_dict["dot_score"]
            score = p_dot_word_dict["dot_score"] - n_dot_word_dict["dot_score"]
            score_list.append({"attraction_name": p_dot_word_dict["query"], "score": score})

        # derive ranking_list from a the unsorted score_list
        ranking_list = sorted(score_list, key=lambda k: k['score'], reverse = True)

        processed_ranking_list = []
        ranking = 0
        for rank_dict in ranking_list:
            ranking += 1
            rank_ordered_dict = OrderedDict()
            rank_ordered_dict['attraction_name'] = rank_dict['attraction_name']
            rank_ordered_dict['ranking'] = ranking
            rank_ordered_dict['original_ranking'] = self.attractions[rank_dict['attraction_name']]
            rank_ordered_dict['score'] = rank_dict['score']
            processed_ranking_list.append(rank_ordered_dict)
        outer_ordered_dict['dot_ranking'] = processed_ranking_list

        # Writing to data/ranking/Amsterdam.json
        if self.verbose:
            print "Writing to " + "\033[1m" + str(self.dst_r) + "\033[0m"
        f = open(self.dst_r, "w")
        f.write(json.dumps(outer_ordered_dict, indent = 4, cls=NoIndentEncoder))

        # Writing to data/ranking/location/Amsterdam_lambda04
        if self.verbose:
            print "Writing to " + "\033[1m" + str(self.dst_rl) + "\033[0m"
        f = open(self.dst_rl, "w")
        f.write(json.dumps(outer_ordered_dict, indent = 4, cls=NoIndentEncoder))

        print "-"*80
        if self.verbose:
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
    distance = Distance(sys.argv[1], sys.argv[2])
    distance.render()

