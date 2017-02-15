try:
    import simplejson as json
except ImportError:
    import json
import sys, os, uuid, re, linecache
from sklearn.metrics.pairwise import cosine_similarity
from collections import OrderedDict
import numpy as np
from scipy import spatial

class Methodology:
    """ This program renders
    (1) topN positive sentiment_words with nearest cosine similarity for the given queries (attraction_name)
        data/distance/location/...
    (2) rankings of the queries (attraction_name)
        data/ranking/location/...
    """

    def __init__(self, argv1, argv2):
        self.src = argv1
        self.threshold = float(argv2)
        self.src_enhanced_lexicon = "data/lexicon/enhanced_lexicon.json"
        self.src_lexicon = "data/lexicon/sentiment_statistics.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src_fr = "data/frontend_reviews/" + self.filename + "/"
        self.src_ss = "data/sentiment_statistics/"
        self.src_lss = "data/location_sentiment_statistics/"

        self.dst_distance = "data/distance/" + self.filename + "/"
        self.dst_ranking = "data/ranking/" + self.filename + "/"

        self.positive_minus_negative_flag = 0

        self.topN = 500
        self.queries = []
        self.positive = []
        self.positive_vectors200 = []
        self.extreme_positive, self.strong_positive, self.moderate_positive = [], [], []
        self.extreme_negative, self.strong_negative, self.moderate_negative = [], [], []
        self.positive_cosine_topN, self.negative_cosine_topN = [], []

        self.attractions, self.attractions2 = {}, {}
	self.unique_words = {}
        self.vectors200 = []
        self.extreme_positive_vectors200, self.strong_positive_vectors200, self.moderate_positive_vectors200 = [], [], []
        self.extreme_negative_vectors200, self.strong_negative_vectors200, self.moderate_negative_vectors200 = [], [], []

        self.verbose = 1

    def get_source(self):
	""" first call readline() to read thefirst line of vectors200 file to get vocab_size and dimension_size """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src + "\033[0m"
        f_src = open(self.src, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')

        if self.verbose:
            print "Building Index"
        for index in range(0, int(vocab_size)):
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
                print "No file is found"
                print "-"*80

        print "-"*80
        #print self.attractions
        return self.attractions

    def get_lexicon(self):
	""" open data/lexicon/sentiment_statistics.json and load extreme_positive & strong_positive & moderate_positive """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_lexicon + "\033[0m"
        with open(self.src_lexicon, 'r') as f:
            lexicon = json.load(f)

        positive = lexicon["positive_statistics"]
        print "Processing positive"
        cnt = 0
        length = len(self.unique_words.keys())
        for key, value in self.unique_words.iteritems():
            cnt += 1
            for word_dict in positive:
                if word_dict["stemmed_word"] == key.decode("utf-8"):
                    self.positive.append(word_dict)
                    self.positive_vectors200.append(self.vectors200[value])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        if self.verbose:
            print "\n" + "-"*70


    def get_positive_cosine_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ cos_sim stands for cosine_similarity """

        if self.verbose:
            print "Calculating Cosine Similarity between queries and every positive word"

        for query in self.queries:
            positive_cos_sim_list = []

            # cosine_similarity ranges from -1 ~ 1
            for index in xrange(len(self.positive)):
                try:
                    positive_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.positive_vectors200[index]))
                except:
                    pass
                    print "No match"

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            # sorting index
            positive_sorted_index = sorted(range(len(positive_cos_sim_list)), key=lambda k: positive_cos_sim_list[k], reverse=True)

            sentiment_statistics = self.get_location_sentiment_statistics(query)
            #print sentiment_statistics

            word_dict_list = []
            for i, index in enumerate(positive_sorted_index):
                try:
                    positive_word_dict = {
                            "stemmed_word": self.positive[index]["stemmed_word"],
                            "word": self.positive[index]["word"],
                            "location_count": sentiment_statistics[self.positive[index]["stemmed_word"]],
                            "total_count": self.positive[index]["count"],
                            "cos_sim": positive_cos_sim_list[index],
                            "cosineXfrequency_score": positive_cos_sim_list[index] * sentiment_statistics[self.positive[index]["stemmed_word"]]
                            }
                    word_dict_list.append(positive_word_dict)
                except:
                    pass
                #print word_dict

            cosine_score_list = [float(word_dict["cos_sim"]) for word_dict in word_dict_list]
            #print cosine_score_list
            max_cosine_score = max(cosine_score_list)
            avg_cosine_score = sum(cosine_score_list)/len(cosine_score_list)
            sum_cosine_score = sum([float(word_dict["cos_sim"]) for word_dict in word_dict_list if float(word_dict["cos_sim"]) >= self.threshold])

            # remove count = 0
            refined_word_dict_list = [word_dict for word_dict in word_dict_list if float(word_dict["location_count"]) >= 0]
            # cutting threshold
            refined_word_dict_list = [word_dict for word_dict in word_dict_list if float(word_dict["cos_sim"]) >= self.threshold]
            # methodology score
            sum_cosineXfrequency_score = sum([float(word_dict["cosineXfrequency_score"]) for word_dict in refined_word_dict_list])
            # calculate the score out of topN cosine similarity

            # generate cosine score
            print "max_cosine_score :", max_cosine_score
            print "avg_cosine_score :", avg_cosine_score
            print "sum_cosine_score :", sum_cosine_score
            print "cosine_similarity * location_count = score :", sum_cosineXfrequency_score

            self.positive_cosine_topN.append({"query": query,
                "positive_topN_cosine_similarity": refined_word_dict_list,
                "max_cosine_score": max_cosine_score,
                "avg_cosine_score": avg_cosine_score,
                "sum_cosine_score": sum_cosine_score,
                "sum_cosineXfrequency_score": sum_cosineXfrequency_score
                })

            print "-"*70

    def get_location_sentiment_statistics(self, query):
        """ get sentiment_statistic for a particular location | return frequencies of sentiment words """

        location = re.search("_([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+)", query).group(1)
        location = location.replace("-","_")
        print "Searching for: " + "\033[1m" + location + ".json" + "\033[0m" + " in " + self.src_lss

        sentiment_statistics = []
        for dirpath, dir_list, file_list in os.walk(self.src_lss):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                # print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                        break
                    else:
                        if location in f.lower():
                            print "Loading location_sentiment_sentiment_statistics from " + dirpath + str(f)
                            with open(dirpath + "/" + f) as file:
                                json_data = json.load(file)
                            sentiment_statistics = json_data["positive_statistics"]
                        else:
                            #print "No match"
                            pass
            else:
                print "No file is found"

        sentiment_dict = {}
        for word_dict in sentiment_statistics:
            sentiment_dict[word_dict["stemmed_word"]] = word_dict["count"]

        return sentiment_dict

    def get_enhanced_lexicon(self):
	""" open data/lexicon/enhanced_lexicon.json and load extreme_positive & strong_positive & moderate_positive """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_enhanced_lexicon + "\033[0m"
        with open(self.src_enhanced_lexicon, 'r') as f:
            enhanced_lexicon = json.load(f)

        positive = enhanced_lexicon["positive"]

        print "Processing positive"
        cnt = 0
        length = len(self.unique_words.keys())
        for key, value in self.unique_words.iteritems():
            cnt += 1
            # (1) extreme_positive
            for word_dict in positive["extreme_positive"]:
                if word_dict["stemmed_word"] == key.decode("utf-8"):
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

        negative = enhanced_lexicon["negative"]

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

        for query in self.queries:
            extreme_cos_sim_list, strong_cos_sim_list, moderate_cos_sim_list = [], [],[]

            # cosine_similarity ranges from -1 ~ 1
            for index in xrange(len(self.extreme_positive)):
                extreme_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.extreme_positive_vectors200[index]))
            for index in xrange(len(self.strong_positive)):
                strong_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.strong_positive_vectors200[index]))
            for index in xrange(len(self.moderate_positive)):
                moderate_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.moderate_positive_vectors200[index]))

            print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            # sorting index
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

            # cutting threshold
            extreme_topN_cos_sim_list = [float(extreme_word_dict["cos_sim"]) for extreme_word_dict in extreme_word_dict_list if float(extreme_word_dict["cos_sim"]) >= self.threshold]
            strong_topN_cos_sim_list = [float(strong_word_dict["cos_sim"]) for strong_word_dict in strong_word_dict_list if float(strong_word_dict["cos_sim"]) >= self.threshold]
            moderate_topN_cos_sim_list = [float(moderate_word_dict["cos_sim"]) for moderate_word_dict in moderate_word_dict_list if float(moderate_word_dict["cos_sim"]) >= self.threshold]

            # calculate the score out of topN cosine similarity
            extreme_cos_score = sum(extreme_topN_cos_sim_list)
            strong_cos_score = sum(strong_topN_cos_sim_list)
            moderate_cos_score = sum(moderate_topN_cos_sim_list)

            # generate cosine score
            cos_score = extreme_cos_score
            #cos_score = extreme_cos_score + strong_cos_score + moderate_cos_score
            print "positive cosine score:", cos_score

            self.positive_cosine_topN.append({"query": query,
                "extreme_positive_topN_cosine_similarity": extreme_word_dict_list,
                "strong_positive_topN_cosine_similarity": strong_word_dict_list,
                "moderate_positive_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score,
                })

        print "-"*70
        print "Calculating Cosine Similarity between queries and every negative word"

        self.negative_cosine_topN = []
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

            # cutting threshold
            extreme_topN_cos_sim_list = [float(extreme_word_dict["cos_sim"]) for extreme_word_dict in extreme_word_dict_list if float(extreme_word_dict["cos_sim"]) >= self.threshold]
            strong_topN_cos_sim_list = [float(strong_word_dict["cos_sim"]) for strong_word_dict in strong_word_dict_list if float(strong_word_dict["cos_sim"]) >= self.threshold]
            moderate_topN_cos_sim_list = [float(moderate_word_dict["cos_sim"]) for moderate_word_dict in moderate_word_dict_list if float(moderate_word_dict["cos_sim"]) >= self.threshold]

            # calculate the score out of topN cosine similarity
            extreme_cos_score = sum(extreme_topN_cos_sim_list)
            strong_cos_score = sum(strong_topN_cos_sim_list)
            moderate_cos_score = sum(moderate_topN_cos_sim_list)

            # generate cosine score
            cos_score = extreme_cos_score
            #cos_score = extreme_cos_score + strong_cos_score + moderate_cos_score
            print "negative cosine score:", cos_score

            self.negative_cosine_topN.append({"query": query,
                "extreme_negative_topN_cosine_similarity": extreme_word_dict_list,
                "strong_negative_topN_cosine_similarity": strong_word_dict_list,
                "moderate_negative_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score})

        if self.verbose:
            print "-"*70

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_distance)
        dir2 = os.path.dirname(self.dst_ranking)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            print "Creating directory: " + dir2
            os.makedirs(dir2)

    def renderDistance(self):
        """ save to data/distance/ """

        if self.verbose:
            print "Putting Cosine word dicts in order"
        query_ordered_dict_list = []

        cnt = 0
        length = len(self.positive_cosine_topN)
        for p_cos_word_dict, n_cos_word_dict in zip(self.positive_cosine_topN, self.negative_cosine_topN):
            cnt += 1
            query_ordered_dict = OrderedDict()
            query_ordered_dict['method'] = "CosineThreshold"
            query_ordered_dict["query"] = p_cos_word_dict["query"]
            query_ordered_dict["cosine_threshold"] = self.threshold

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

            # (4) extreme negative cosine
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

            # (5) strong negative cosine
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

            # (6) moderate negative cosine
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
            # Writing to data/distance/New_York_City_Threshold.json
            print "Writing data to " + "\033[1m" + str(self.dst_distance) + self.filename + "-Threshold" + str(self.threshold) + ".json""\033[0m"

        f = open(self.dst_distance + self.filename + "-Threshold" + str(self.threshold) + ".json", "w")
        f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        if self.verbose:
            print "-"*80

    def renderRanking(self):
        """ save to data/ranking/ """

        location_ordered_dict = OrderedDict()
        location_ordered_dict['method'] = "CosineThreshold"
        location_ordered_dict['threshold'] = self.threshold
        location_ordered_dict['topN'] = self.topN

        if self.verbose:
            print "Ranking queries according to cosine score"
        score_list = []
        for p_cos_word_dict, n_cos_word_dict in zip(self.positive_cosine_topN, self.negative_cosine_topN):
            if self.positive_minus_negative_flag:
                score = p_cos_word_dict["cos_score"] - n_cos_word_dict["cos_score"]
            else:
                score = p_cos_word_dict["cos_score"]
            score_list.append({"attraction_name": p_cos_word_dict["query"], "score": score})

         # derive ranking_list from a the unsorted score_list
        ranking_list = sorted(score_list, key=lambda k: k['score'], reverse = True)

        ordered_dicts = []
        ranking = 0
        for rank_dict in ranking_list:
            ranking += 1
            ordered_dict = OrderedDict()
            ordered_dict['attraction_name'] = rank_dict['attraction_name']
            ordered_dict['computed_ranking'] = ranking
            ordered_dict['cosineXfrequency_score'] = rank_dict['cosineXfrequency_score']
            ordered_dict['max_score'] = rank_dict['max_score']
            ordered_dict['avg_score'] = rank_dict['avg_score']
            ordered_dict['sum_score'] = rank_dict['sum_score']
            ordered_dict['reranked_ranking'] = self.attractions[rank_dict['attraction_name']]
            ordered_dict['original_ranking'] = int(self.attractions2[rank_dict['attraction_name']])
            ordered_dicts.append(ordered_dict)

        location_ordered_dict['cosine_threshold_ranking'] = ordered_dicts

        # Writing to data/ranking/New_York_City/New_York_City_Threshold0.25
        if self.verbose:
            print "Writing to " + "\033[1m" + str(self.dst_ranking) + self.filename + "-Threshold" + str(self.threshold) + ".json""\033[0m"
        f = open(self.dst_ranking + self.filename + "-Threshold" + str(self.threshold) + ".json", "w")
        f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))

    def renderPositiveDistance(self):
        """ save to data/distance/ """

        if self.verbose:
            print "Putting Cosine word dicts in order"
        query_ordered_dict_list = []

        sorted_positive_cosine_topN = sorted(self.positive_cosine_topN, key=lambda k: k['sum_cosineXfrequency_score'], reverse = True)
        ranking = 0
        length = len(sorted_positive_cosine_topN)
        for p_cos_word_dict in sorted_positive_cosine_topN:
            ranking += 1
            query_ordered_dict = OrderedDict()
            query_ordered_dict['ranking'] = ranking
            query_ordered_dict['method'] = "CosineThreshold"
            query_ordered_dict["query"] = p_cos_word_dict["query"]
            query_ordered_dict["cosine_threshold"] = self.threshold

            # (1) positive cosine (from sentiment_statistics)
            positive_cosine_word_dict_list = []
            index = 0
            for cosine_word_dict in p_cos_word_dict["positive_topN_cosine_similarity"]:
                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                ordered_dict["location_count"] = cosine_word_dict["location_count"]
                ordered_dict["stemmed_word"] = cosine_word_dict["stemmed_word"]
                ordered_dict["word"] = cosine_word_dict["word"]
                ordered_dict["total_count"] = cosine_word_dict["total_count"]
                positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

            query_ordered_dict["positive_topN_cosine_similarity"] = positive_cosine_word_dict_list

            # append one query after another
            query_ordered_dict_list.append(query_ordered_dict)

        if self.verbose:
            # Writing to data/distance/New_York_City_Threshold.json
            print "Writing data to " + "\033[1m" + str(self.dst_distance) + self.filename + "-Threshold" + str(self.threshold) + ".json""\033[0m"

        f = open(self.dst_distance + self.filename + "-Threshold" + str(self.threshold) + ".json", "w")
        f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        if self.verbose:
            print "-"*80

    def renderPositiveRanking(self):
        """ save to data/ranking/ """

        location_ordered_dict = OrderedDict()
        location_ordered_dict['method'] = "CosineThreshold"
        location_ordered_dict['threshold'] = self.threshold

        if self.verbose:
            print "Ranking queries according to cosine score"
        ranking_dict_list = []
        for ranking_dict in self.positive_cosine_topN:

            ranking_dict_list.append({
                "attraction_name": ranking_dict["query"],
                "sum_cosineXfrequency_score": ranking_dict["sum_cosineXfrequency_score"],
                "sum_cosine_score": ranking_dict["sum_cosine_score"],
                "max_cosine_score": ranking_dict["max_cosine_score"],
                "avg_cosine_score": ranking_dict["avg_cosine_score"]
                })

        # (1) By sort by sum_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['sum_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["sum_cosine_score_ranking"] = rank
        # (2) By sort by max_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['max_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["max_cosine_score_ranking"] = rank
        # (3) By sort by avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["avg_cosine_score_ranking"] = rank
        # (4) By sort by sum_cosineXfrequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['sum_cosineXfrequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["sum_cosineXfrequency_score_ranking"] = rank

        ordered_dicts = []
        for rank_dict in ranking_dict_list:
            ordered_dict = OrderedDict()
            ordered_dict['attraction_name'] = rank_dict['attraction_name']
            ordered_dict['reranked_ranking'] = self.attractions[rank_dict['attraction_name']]
            ordered_dict['original_ranking'] = int(self.attractions2[rank_dict['attraction_name']])
            ordered_dict['computed_ranking'] = rank_dict["sum_cosineXfrequency_score_ranking"]
            ordered_dict['sum_cosineXfrequency_score'] = rank_dict['sum_cosineXfrequency_score']
            ordered_dict['sum_cosine_score_ranking'] = rank_dict["sum_cosine_score_ranking"]
            ordered_dict['sum_cosine_score'] = rank_dict['sum_cosine_score']
            ordered_dict['max_cosine_score_ranking'] = rank_dict["max_cosine_score_ranking"]
            ordered_dict['max_cosine_score'] = rank_dict['max_cosine_score']
            ordered_dict['avg_cosine_score_ranking'] = rank_dict["avg_cosine_score_ranking"]
            ordered_dict['avg_cosine_score'] = rank_dict['avg_cosine_score']
            #print ordered_dict
            ordered_dicts.append(ordered_dict)


        location_ordered_dict['CosineThreshold_Ranking'] = ordered_dicts

        # Writing to data/ranking/New_York_City/New_York_City_Threshold0.25
        if self.verbose:
            print "Writing to " + "\033[1m" + str(self.dst_ranking) + self.filename + "-Threshold" + str(self.threshold) + ".json""\033[0m"
        f = open(self.dst_ranking + self.filename + "-Threshold" + str(self.threshold) + ".json", "w")
        f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))


    def run(self):
        """ run the entire program """
        self.get_source()
        #self.get_enhanced_lexicon()
        self.get_lexicon()
        self.queries = self.get_attractions().keys()
        self.create_dirs()

        #self.get_cosine_topN()
        self.get_positive_cosine_topN()
        #self.renderDistance()
        self.renderPositiveDistance()
        #self.renderRanking()
        self.renderPositiveRanking()

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
    methodology = Methodology(sys.argv[1], sys.argv[2])
    methodology.run()

