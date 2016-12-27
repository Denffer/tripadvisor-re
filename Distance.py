import sys, os, json, uuid, re, linecache
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
        self.tuning_lambda = float(argv2)
        self.src_lexicon = "data/lexicon/enhanced_lexicon.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src_fr = "data/frontend_reviews/" + self.filename + "/"

        self.verbose = 1
        self.dst_dc = "data/distance/" + self.filename + "/cosine/" + self.filename + "-lambda" + str(float(argv2)) + ".json"
        self.dst_dd = "data/distance/" + self.filename + "/dot/" + self.filename + "-lambda" + str(float(argv2)) + ".json"
        self.dst_rc = "data/ranking/" + self.filename + "/cosine/" + self.filename + "-lambda" + str(float(argv2)) + ".json"
        self.dst_rd = "data/ranking/" + self.filename + "/dot/" + self.filename + "-lambda" + str(float(argv2)) + ".json"
        self.cosine_flag = 1
        self.dot_flag = 1

        self.topN = 200
        self.topN_max = 5
        self.queries = []
        self.extreme_positive, self.strong_positive, self.moderate_positive = [], [], []
        self.extreme_negative, self.strong_negative, self.moderate_negative = [], [], []
        self.vocab_size = 0
        self.dimension_size = 0

        self.attractions, self.attractions2 = {}, {}
	self.unique_words = {}
        self.vectors200 = []
        self.extreme_positive_vectors200, self.strong_positive_vectors200, self.moderate_positive_vectors200 = [], [], []
        self.extreme_negative_vectors200, self.strong_negative_vectors200, self.moderate_negative_vectors200 = [], [], []

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
                            # attraction_ranking = attraction["ranking"]
                            reranked_ranking = attraction["reranked_ranking"]
                            self.attractions.update({attraction_al: reranked_ranking})
                            original_ranking = attraction["original_ranking"]
                            self.attractions2.update({attraction_al: original_ranking})
            else:
                if self.verbose:
                    print "No file is found"
                    print "-"*80

        if self.verbose:
            print "-"*80
        #print self.attractions
        return self.attractions

    def get_lexicon(self):
	""" open data/lexicon/enhanced_lexicon.json and load extreme_positive & strong_positive & moderate_positive """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_lexicon + "\033[0m"
        with open(self.src_lexicon, 'r') as f_ss:
            sentiment_statistics = json.load(f_ss)

        positive = sentiment_statistics["positive"]

        print "Processing positive"
        cnt = 0
        length = len(self.unique_words.keys())
        for key, value in self.unique_words.iteritems():
            cnt += 1
            # (1) extreme_positive
            for word_dict in positive["extreme_positive"]:
                if word_dict["stemmed_word"] == key:
                    self.extreme_positive.append(word_dict)
                    self.extreme_positive_vectors200.append(self.vectors200[value])
            # (2) strong_positive
            for word_dict in positive["strong_positive"]:
                if word_dict["stemmed_word"] == key:
                    self.strong_positive.append(word_dict)
                    self.strong_positive_vectors200.append(self.vectors200[value])
            # (3) moderate_positive
            for word_dict in positive["moderate_positive"]:
                if word_dict["stemmed_word"] == key:
                    self.moderate_positive.append(word_dict)
                    self.moderate_positive_vectors200.append(self.vectors200[value])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        negative = sentiment_statistics["negative"]

        print "\nProcessing negative"
        cnt = 0
        length = len(self.unique_words.keys())
        for key, value in self.unique_words.iteritems():
            cnt += 1
            # (1) extreme_negative
            for word_dict in negative["extreme_negative"]:
                if word_dict["stemmed_word"] == key:
                    self.extreme_negative.append(word_dict)
                    self.extreme_negative_vectors200.append(self.vectors200[value])
            # (2) strong_negative
            for word_dict in negative["strong_negative"]:
                if word_dict["stemmed_word"] == key:
                    self.strong_negative.append(word_dict)
                    self.strong_negative_vectors200.append(self.vectors200[value])
            # (3) moderate_negative
            for word_dict in negative["moderate_negative"]:
                if word_dict["stemmed_word"] == key:
                    self.moderate_negative.append(word_dict)
                    self.moderate_negative_vectors200.append(self.vectors200[value])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        if self.verbose:
            print "\n" + "-"*70

    def get_cosine_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ cos_sim stands for cosine_similarity """

        if self.verbose:
            print "Calculating Cosine Similarity between queries and every positive word"

        positive_cosine_topN = []
        for query in self.queries:
            extreme_cos_sim_list, strong_cos_sim_list, moderate_cos_sim_list = [], [],[]
            # cosine_similarity ranges from -1 ~ 1
            for index in xrange(len(self.extreme_positive)):
                extreme_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.extreme_positive_vectors200[index]))
            for index in xrange(len(self.strong_positive)):
                strong_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.strong_positive_vectors200[index]))
            for index in xrange(len(self.moderate_positive)):
                moderate_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.moderate_positive_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            extreme_sorted_index = sorted(range(len(extreme_cos_sim_list)), key=lambda k: extreme_cos_sim_list[k], reverse=True)
            strong_sorted_index = sorted(range(len(strong_cos_sim_list)), key=lambda k: strong_cos_sim_list[k], reverse=True)
            moderate_sorted_index = sorted(range(len(moderate_cos_sim_list)), key=lambda k: moderate_cos_sim_list[k], reverse=True)

            extreme_word_dict_list = []
            for i, index in enumerate(extreme_sorted_index):
                if i < self.topN:
                    extreme_word_dict = {"word": self.extreme_positive[index], "cos_sim": extreme_cos_sim_list[index]}
                    extreme_word_dict_list.append(extreme_word_dict)

            strong_word_dict_list = []
            for i, index in enumerate(strong_sorted_index):
                if i < self.topN:
                    strong_word_dict = {"word": self.strong_positive[index], "cos_sim": strong_cos_sim_list[index]}
                    strong_word_dict_list.append(strong_word_dict)

            moderate_word_dict_list = []
            for i, index in enumerate(moderate_sorted_index):
                if i < self.topN:
                    moderate_word_dict = {"word": self.moderate_positive[index], "cos_sim": moderate_cos_sim_list[index]}
                    moderate_word_dict_list.append(moderate_word_dict)

            extreme_topN_cos_sim_list = [float(extreme_word_dict["cos_sim"]) for extreme_word_dict in extreme_word_dict_list]
            strong_topN_cos_sim_list = [float(strong_word_dict["cos_sim"]) for strong_word_dict in strong_word_dict_list]
            moderate_topN_cos_sim_list = [float(moderate_word_dict["cos_sim"]) for moderate_word_dict in moderate_word_dict_list]

            # calculate the score out of topN cosine similarity
            #cos_score =  self.tuning_lambda * max(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list) / len(topN_cos_sim_list)
            extreme_cos_score =  self.tuning_lambda * sum(extreme_topN_cos_sim_list[:self.topN_max])/len(extreme_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(extreme_topN_cos_sim_list)/len(extreme_topN_cos_sim_list)
            strong_cos_score =  self.tuning_lambda * sum(strong_topN_cos_sim_list[:self.topN_max])/len(strong_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(strong_topN_cos_sim_list)/len(strong_topN_cos_sim_list)
            moderate_cos_score =  self.tuning_lambda * sum(moderate_topN_cos_sim_list[:self.topN_max])/len(moderate_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(moderate_topN_cos_sim_list)/len(moderate_topN_cos_sim_list)

            # generate cosine score
            #cos_score = extreme_cos_score * 1 + strong_cos_score * 0.5 + moderate_cos_score * 0.3
            cos_score = extreme_cos_score
            print "positive cosine score:", cos_score

            positive_cosine_topN.append({"query": query,
                "extreme_positive_topN_cosine_similarity": extreme_word_dict_list,
                "strong_positive_topN_cosine_similarity": strong_word_dict_list,
                "moderate_positive_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score})

        if self.verbose:
            print "-"*70
            print "Calculating Cosine Similarity between queries and every negative word"

        negative_cosine_topN = []
        for query in self.queries:
            extreme_cos_sim_list, strong_cos_sim_list, moderate_cos_sim_list = [], [],[]
            # cosine_similarity ranges from -1 ~ 1
            for index in xrange(len(self.extreme_negative)):
                extreme_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.extreme_negative_vectors200[index]))
            for index in xrange(len(self.strong_negative)):
                strong_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.strong_negative_vectors200[index]))
            for index in xrange(len(self.moderate_negative)):
                moderate_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.moderate_negative_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            extreme_sorted_index = sorted(range(len(extreme_cos_sim_list)), key=lambda k: extreme_cos_sim_list[k], reverse=True)
            strong_sorted_index = sorted(range(len(strong_cos_sim_list)), key=lambda k: strong_cos_sim_list[k], reverse=True)
            moderate_sorted_index = sorted(range(len(moderate_cos_sim_list)), key=lambda k: moderate_cos_sim_list[k], reverse=True)

            extreme_word_dict_list = []
            for i, index in enumerate(extreme_sorted_index):
                if i < self.topN:
                    extreme_word_dict = {"word": self.extreme_negative[index], "cos_sim": extreme_cos_sim_list[index]}
                    extreme_word_dict_list.append(extreme_word_dict)

            strong_word_dict_list = []
            for i, index in enumerate(strong_sorted_index):
                if i < self.topN:
                    strong_word_dict = {"word": self.strong_negative[index], "cos_sim": strong_cos_sim_list[index]}
                    strong_word_dict_list.append(strong_word_dict)

            moderate_word_dict_list = []
            for i, index in enumerate(moderate_sorted_index):
                if i < self.topN:
                    moderate_word_dict = {"word": self.moderate_negative[index], "cos_sim": moderate_cos_sim_list[index]}
                    moderate_word_dict_list.append(moderate_word_dict)

            extreme_topN_cos_sim_list = [float(extreme_word_dict["cos_sim"]) for extreme_word_dict in extreme_word_dict_list]
            strong_topN_cos_sim_list = [float(strong_word_dict["cos_sim"]) for strong_word_dict in strong_word_dict_list]
            moderate_topN_cos_sim_list = [float(moderate_word_dict["cos_sim"]) for moderate_word_dict in moderate_word_dict_list]

            # calculate the score out of topN cosine similarity
            #cos_score =  self.tuning_lambda * max(topN_cos_sim_list) + (1-self.tuning_lambda) * sum(topN_cos_sim_list) / len(topN_cos_sim_list)
            extreme_cos_score =  self.tuning_lambda * sum(extreme_topN_cos_sim_list[:self.topN_max])/len(extreme_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(extreme_topN_cos_sim_list)/len(extreme_topN_cos_sim_list)
            strong_cos_score =  self.tuning_lambda * sum(strong_topN_cos_sim_list[:self.topN_max])/len(strong_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(strong_topN_cos_sim_list)/len(strong_topN_cos_sim_list)
            moderate_cos_score =  self.tuning_lambda * sum(moderate_topN_cos_sim_list[:self.topN_max])/len(moderate_topN_cos_sim_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(moderate_topN_cos_sim_list)/len(moderate_topN_cos_sim_list)

            # generate cosine score
            #cos_score = extreme_cos_score * 1 + strong_cos_score * 0.5 + moderate_cos_score * 0.3
            cos_socre = extreme_cos_score
            print "negative cosine score:", cos_score

            negative_cosine_topN.append({"query": query,
                "extreme_negative_topN_cosine_similarity": extreme_word_dict_list,
                "strong_negative_topN_cosine_similarity": strong_word_dict_list,
                "moderate_negative_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score})

        if self.verbose:
            print "-"*70

        return positive_cosine_topN, negative_cosine_topN

    def get_dot_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ dot_prod stands for dot_product """

        if self.verbose:
            print "Calculating Dot Product between queries and every positive word"

        positive_dot_topN = []
        for query in self.queries:
            extreme_dot_prod_list, strong_dot_prod_list, moderate_dot_prod_list = [], [],[]
            # dot_similarity ranges from -1 ~ 1
            for index in xrange(len(self.extreme_positive)):
                extreme_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.extreme_positive_vectors200[index]))
            for index in xrange(len(self.strong_positive)):
                strong_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.strong_positive_vectors200[index]))
            for index in xrange(len(self.moderate_positive)):
                moderate_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.moderate_positive_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            extreme_sorted_index = sorted(range(len(extreme_dot_prod_list)), key=lambda k: extreme_dot_prod_list[k], reverse=True)
            strong_sorted_index = sorted(range(len(strong_dot_prod_list)), key=lambda k: strong_dot_prod_list[k], reverse=True)
            moderate_sorted_index = sorted(range(len(moderate_dot_prod_list)), key=lambda k: moderate_dot_prod_list[k], reverse=True)

            extreme_word_dict_list = []
            for i, index in enumerate(extreme_sorted_index):
                if i < self.topN:
                    extreme_word_dict = {"word": self.extreme_positive[index], "dot_prod": extreme_dot_prod_list[index]}
                    extreme_word_dict_list.append(extreme_word_dict)

            strong_word_dict_list = []
            for i, index in enumerate(strong_sorted_index):
                if i < self.topN:
                    strong_word_dict = {"word": self.strong_positive[index], "dot_prod": strong_dot_prod_list[index]}
                    strong_word_dict_list.append(strong_word_dict)

            moderate_word_dict_list = []
            for i, index in enumerate(moderate_sorted_index):
                if i < self.topN:
                    moderate_word_dict = {"word": self.moderate_positive[index], "dot_prod": moderate_dot_prod_list[index]}
                    moderate_word_dict_list.append(moderate_word_dict)

            extreme_topN_dot_prod_list = [float(extreme_word_dict["dot_prod"]) for extreme_word_dict in extreme_word_dict_list]
            strong_topN_dot_prod_list = [float(strong_word_dict["dot_prod"]) for strong_word_dict in strong_word_dict_list]
            moderate_topN_dot_prod_list = [float(moderate_word_dict["dot_prod"]) for moderate_word_dict in moderate_word_dict_list]

            # calculate the score out of topN dot similarity
            #dot_prod =  self.tuning_lambda * max(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list) / len(topN_dot_prod_list)
            extreme_dot_prod =  self.tuning_lambda * sum(extreme_topN_dot_prod_list[:self.topN_max])/len(extreme_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(extreme_topN_dot_prod_list)/len(extreme_topN_dot_prod_list)
            strong_dot_prod =  self.tuning_lambda * sum(strong_topN_dot_prod_list[:self.topN_max])/len(strong_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(strong_topN_dot_prod_list)/len(strong_topN_dot_prod_list)
            moderate_dot_prod =  self.tuning_lambda * sum(moderate_topN_dot_prod_list[:self.topN_max])/len(moderate_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(moderate_topN_dot_prod_list)/len(moderate_topN_dot_prod_list)

            # generate dot score
            #dot_score = extreme_dot_prod * 1 + strong_dot_prod * 0.5 + moderate_dot_prod * 0.3
            dot_score = extreme_dot_prod
            print "positive dot score:", dot_score

            positive_dot_topN.append({"query": query,
                "extreme_positive_topN_dot_product": extreme_word_dict_list,
                "strong_positive_topN_dot_product": strong_word_dict_list,
                "moderate_positive_topN_dot_product": moderate_word_dict_list,
                "dot_score": dot_score})

        if self.verbose:
            print "-"*70
            print "Calculating Dot Product between queries and every negative word"

        negative_dot_topN = []
        for query in self.queries:
            extreme_dot_prod_list, strong_dot_prod_list, moderate_dot_prod_list = [], [],[]
            # dot_similarity ranges from -1 ~ 1
            for index in xrange(len(self.extreme_negative)):
                extreme_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.extreme_negative_vectors200[index]))
            for index in xrange(len(self.strong_negative)):
                strong_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.strong_negative_vectors200[index]))
            for index in xrange(len(self.moderate_negative)):
                moderate_dot_prod_list.append(np.dot(self.vectors200[self.unique_words[query]], self.moderate_negative_vectors200[index]))

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            extreme_sorted_index = sorted(range(len(extreme_dot_prod_list)), key=lambda k: extreme_dot_prod_list[k], reverse=True)
            strong_sorted_index = sorted(range(len(strong_dot_prod_list)), key=lambda k: strong_dot_prod_list[k], reverse=True)
            moderate_sorted_index = sorted(range(len(moderate_dot_prod_list)), key=lambda k: moderate_dot_prod_list[k], reverse=True)

            extreme_word_dict_list = []
            for i, index in enumerate(extreme_sorted_index):
                if i < self.topN:
                    extreme_word_dict = {"word": self.extreme_negative[index], "dot_prod": extreme_dot_prod_list[index]}
                    extreme_word_dict_list.append(extreme_word_dict)

            strong_word_dict_list = []
            for i, index in enumerate(strong_sorted_index):
                if i < self.topN:
                    strong_word_dict = {"word": self.strong_negative[index], "dot_prod": strong_dot_prod_list[index]}
                    strong_word_dict_list.append(strong_word_dict)

            moderate_word_dict_list = []
            for i, index in enumerate(moderate_sorted_index):
                if i < self.topN:
                    moderate_word_dict = {"word": self.moderate_negative[index], "dot_prod": moderate_dot_prod_list[index]}
                    moderate_word_dict_list.append(moderate_word_dict)

            extreme_topN_dot_prod_list = [float(extreme_word_dict["dot_prod"]) for extreme_word_dict in extreme_word_dict_list]
            strong_topN_dot_prod_list = [float(strong_word_dict["dot_prod"]) for strong_word_dict in strong_word_dict_list]
            moderate_topN_dot_prod_list = [float(moderate_word_dict["dot_prod"]) for moderate_word_dict in moderate_word_dict_list]

            # calculate the score out of topN dot similarity
            #dot_prod =  self.tuning_lambda * max(topN_dot_prod_list) + (1-self.tuning_lambda) * sum(topN_dot_prod_list) / len(topN_dot_prod_list)
            extreme_dot_prod =  self.tuning_lambda * sum(extreme_topN_dot_prod_list[:self.topN_max])/len(extreme_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(extreme_topN_dot_prod_list)/len(extreme_topN_dot_prod_list)
            strong_dot_prod =  self.tuning_lambda * sum(strong_topN_dot_prod_list[:self.topN_max])/len(strong_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(strong_topN_dot_prod_list)/len(strong_topN_dot_prod_list)
            moderate_dot_prod =  self.tuning_lambda * sum(moderate_topN_dot_prod_list[:self.topN_max])/len(moderate_topN_dot_prod_list[:self.topN_max]) + (1-self.tuning_lambda) * sum(moderate_topN_dot_prod_list)/len(moderate_topN_dot_prod_list)

            # generate dot score
            #dot_score = extreme_dot_prod * 1 + strong_dot_prod * 0.5 + moderate_dot_prod * 0.3
            dot_score = extreme_dot_prod
            print "Negative dot score:", dot_score

            negative_dot_topN.append({"query": query,
                "extreme_negative_topN_dot_product": extreme_word_dict_list,
                "strong_negative_topN_dot_product": strong_word_dict_list,
                "moderate_negative_topN_dot_product": moderate_word_dict_list,
                "dot_score": dot_score})

        if self.verbose:
            print "-"*70
        return positive_dot_topN, negative_dot_topN

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_dc)
        dir2 = os.path.dirname(self.dst_dd)
        dir3 = os.path.dirname(self.dst_rc)
        dir4 = os.path.dirname(self.dst_rd)

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

    def render(self):
        """ save every cosine_list for top1~5 as json file"""
        self.get_source()
        self.get_lexicon()
        self.queries = self.get_attractions().keys()
        self.create_dirs()

        if self.cosine_flag:
            positive_cosine_topN, negative_cosine_topN = self.get_cosine_topN()

            if self.verbose:
                print "Putting Cosine word dicts in order"
            query_ordered_dict_list = []

            cnt = 0
            length = len(positive_cosine_topN)
            for p_cos_word_dict, n_cos_word_dict in zip(positive_cosine_topN, negative_cosine_topN):
                cnt += 1
                query_ordered_dict = OrderedDict()
                query_ordered_dict["query"] = p_cos_word_dict["query"]
                query_ordered_dict["lambda"] = self.tuning_lambda

                # (1) extreme positive cosine
                extreme_positive_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in p_cos_word_dict["extreme_positive_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    extreme_positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["extreme_positive_topN_cosine_similarity"] = extreme_positive_cosine_word_dict_list

                # (2) strong positive cosine
                strong_positive_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in p_cos_word_dict["strong_positive_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    strong_positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["strong_positive_topN_cosine_similarity"] = strong_positive_cosine_word_dict_list

                # (3) moderate positive cosine
                moderate_positive_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in p_cos_word_dict["moderate_positive_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    moderate_positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["moderate_positive_topN_cosine_similarity"] = moderate_positive_cosine_word_dict_list


                # (4) negative cosine
                extreme_negative_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in n_cos_word_dict["extreme_negative_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    extreme_negative_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["extreme_negative_topN_cosine_similarity"] = extreme_negative_cosine_word_dict_list

                strong_negative_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in n_cos_word_dict["strong_negative_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    strong_negative_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["strong_negative_topN_cosine_similarity"] = strong_negative_cosine_word_dict_list

                moderate_negative_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in n_cos_word_dict["moderate_negative_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    moderate_negative_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["moderate_negative_topN_cosine_similarity"] = moderate_negative_cosine_word_dict_list

                # append one query after another
                query_ordered_dict_list.append(query_ordered_dict)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()
            print ""
        else:
            # passing cosine
            pass

        if self.cosine_flag:
            if self.verbose:
                # Writing to data/distance/cosine/location_lambda05.json
                print "Writing data to " + "\033[1m" + str(self.dst_dc) + "\033[0m"

            f = open(self.dst_dc, "w")
            f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

            if self.verbose:
                print "-"*80

        # dot
        if self.dot_flag:
            positive_dot_topN, negative_dot_topN = self.get_dot_topN()
            query_ordered_dict_list = []

            cnt = 0
            length = len(positive_dot_topN)
            for p_dot_word_dict, n_dot_word_dict in zip(positive_dot_topN, negative_dot_topN):
                cnt += 1
                query_ordered_dict = OrderedDict()
                query_ordered_dict["query"] = p_dot_word_dict["query"]
                query_ordered_dict["lambda"] = self.tuning_lambda

                # (1) extreme positive dot
                extreme_positive_dot_word_dict_list = []
                index = 0
                for dot_word_dict in p_dot_word_dict["extreme_positive_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    extreme_positive_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["extreme_positive_topN_dot_product"] = extreme_positive_dot_word_dict_list

                # (2) strong positive dot
                strong_positive_dot_word_dict_list = []
                index = 0
                for dot_word_dict in p_dot_word_dict["strong_positive_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    strong_positive_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["strong_positive_topN_dot_product"] = strong_positive_dot_word_dict_list

                # (3) moderate positive dot
                moderate_positive_dot_word_dict_list = []
                index = 0
                for dot_word_dict in p_dot_word_dict["moderate_positive_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    moderate_positive_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["moderate_positive_topN_dot_product"] = moderate_positive_dot_word_dict_list

                # (4) extreme negative dot
                extreme_negative_dot_word_dict_list = []
                index = 0
                for dot_word_dict in n_dot_word_dict["extreme_negative_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    extreme_negative_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["extreme_negative_topN_dot_product"] = extreme_negative_dot_word_dict_list

                # (5) strong negative dot
                strong_negative_dot_word_dict_list = []
                index = 0
                for dot_word_dict in n_dot_word_dict["strong_negative_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    strong_negative_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["strong_negative_topN_dot_product"] = strong_negative_dot_word_dict_list

                # (6) moderate negative dot
                moderate_negative_dot_word_dict_list = []
                index = 0
                for dot_word_dict in n_dot_word_dict["moderate_negative_topN_dot_product"]:

                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["dot_product"] = dot_word_dict["dot_prod"]
                    ordered_dict["count"] = dot_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = dot_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = dot_word_dict["word"]["word"]
                    moderate_negative_dot_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["moderate_negative_topN_dot_product"] = moderate_negative_dot_word_dict_list

                # append one query after another
                query_ordered_dict_list.append(query_ordered_dict)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()
            print ""
        else:
            # passing dot
            pass

        if self.dot_flag:
            if self.verbose:
                # Writing to data/distance/dot/location_lambda05.json
                print "Writing to " + "\033[1m" + str(self.dst_dd) + "\033[0m"

            f = open(self.dst_dd, "w")
            f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

            if self.verbose:
                print "-"*80


        """"""""""""""""""""""""
        """  Ranking   Here  """
        """"""""""""""""""""""""
        # (1) cos_ranking
        if self.cosine_flag:
            location_ordered_dict = OrderedDict()
            location_ordered_dict['lambda'] = self.tuning_lambda
            if self.verbose:
                print "Ranking queries according to cosine score"
            score_list = []
            for p_cos_word_dict, n_cos_word_dict in zip(positive_cosine_topN, negative_cosine_topN):
                #score = p_cos_word_dict["cos_score"]
                score = p_cos_word_dict["cos_score"] #- n_cos_word_dict["cos_score"]
                score_list.append({"attraction_name": p_cos_word_dict["query"], "score": score})

            # derive ranking_list from a the unsorted score_list
            ranking_list = sorted(score_list, key=lambda k: k['score'], reverse = True)

            processed_ranking_list = []
            ranking = 0
            for rank_dict in ranking_list:
                ranking += 1
                rank_ordered_dict = OrderedDict()
                rank_ordered_dict['attraction_name'] = rank_dict['attraction_name']
                rank_ordered_dict['computed_ranking'] = str(ranking)
                rank_ordered_dict['reranked_ranking'] = self.attractions[rank_dict['attraction_name']]
                rank_ordered_dict['original_ranking'] = self.attractions2[rank_dict['attraction_name']]
                rank_ordered_dict['score'] = rank_dict['score']
                processed_ranking_list.append(rank_ordered_dict)
            location_ordered_dict['cosine_ranking'] = processed_ranking_list

            # Writing to data/ranking/cosine/location/Amsterdam_lambda04
            if self.verbose:
                print "Writing to " + "\033[1m" + str(self.dst_rc) + "\033[0m"
            f = open(self.dst_rc, "w")
            f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))
        else:
            pass

        # (2) dot_ranking
        if self.dot_flag:
            location_ordered_dict = OrderedDict()
            location_ordered_dict['lambda'] = self.tuning_lambda

            if self.verbose:
                print "Ranking queries according to dot score"
            score_list = []
            for p_dot_word_dict, n_dot_word_dict in zip(positive_dot_topN, negative_dot_topN):
                #score = p_dot_word_dict["dot_score"]
                score = p_dot_word_dict["dot_score"] #- n_dot_word_dict["dot_score"]
                score_list.append({"attraction_name": p_dot_word_dict["query"], "score": score})

            # derive ranking_list from a the unsorted score_list
            ranking_list = sorted(score_list, key=lambda k: k['score'], reverse = True)

            processed_ranking_list = []
            ranking = 0
            for rank_dict in ranking_list:
                ranking += 1
                rank_ordered_dict = OrderedDict()
                rank_ordered_dict['attraction_name'] = rank_dict['attraction_name']
                rank_ordered_dict['computed_ranking'] = str(ranking)
                rank_ordered_dict['reranked_ranking'] = self.attractions[rank_dict['attraction_name']]
                rank_ordered_dict['original_ranking'] = self.attractions2[rank_dict['attraction_name']]
                rank_ordered_dict['score'] = rank_dict['score']
                processed_ranking_list.append(rank_ordered_dict)
            location_ordered_dict['dot_ranking'] = processed_ranking_list

            # Writing to data/ranking/cosine/location/Amsterdam_lambda04
            if self.verbose:
                print "Writing to " + "\033[1m" + str(self.dst_rd) + "\033[0m"
            f = open(self.dst_rd, "w")
            f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))

        else:
            pass

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

