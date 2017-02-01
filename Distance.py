try:
    import simplejson as json
except ImportError:
    import json
import sys, os, uuid, re, linecache
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
        self.threshold = float(argv2)
        self.src_lexicon = "data/lexicon/enhanced_lexicon.json"
        self.src_sentiment_statistics = "data/lexicon/sentiment_statistics.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src_fr = "data/frontend_reviews/" + self.filename + "/"

        self.verbose = 1

        self.dst_distance = "data/distance/" + self.filename + "/" + self.filename + "-threshold" + str(float(argv2)) + ".json"
        self.dst_ranking = "data/ranking/" + self.filename + "/" + self.filename + "-threshold" + str(float(argv2)) + ".json"
        self.dst_distance_baseline = "data/distance/" + self.filename + "/baseline-" + self.filename + "-threshold" + str(float(argv2)) + "-baseline.json"
        self.dst_ranking_baseline = "data/ranking/" + self.filename + "/baseline-" + self.filename + "-threshold" + str(float(argv2)) + "-baseline.json"


        self.positive_minus_negative_flag = 0
        self.cosine_flag = 1
        self.dot_flag = 0

        self.topN = 500
        self.topN_max = 5
        self.queries = []
        self.baseline_positive_words = []
        self.extreme_positive, self.strong_positive, self.moderate_positive = [], [], []
        self.extreme_negative, self.strong_negative, self.moderate_negative = [], [], []
        self.vocab_size = 0
        self.dimension_size = 0

        self.attractions, self.attractions2 = {}, {}
	self.unique_words = {}
        self.vectors200 = []
        self.baseline_positive_vectors200 = []
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
                print "No file is found"
                print "-"*80

        print "-"*80
        #print self.attractions
        return self.attractions

    def get_sentiment_statistics(self):
	""" Open data/lexicon/sentiment_statistics.json and load positive """
        """ This is for the baseline """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_sentiment_statistics + "\033[0m"
        with open(self.src_sentiment_statistics, 'r') as f_ss:
            sentiment_statistics = json.load(f_ss)

        positive = sentiment_statistics["positive_statistics"]
        baseline_positive_dicts = []

        print "Processing Baseline Lexicon"
        cnt = 0
        length = len(self.unique_words.keys())
        for key, value in self.unique_words.iteritems():
            cnt += 1
            for word_dict in positive:
                if word_dict["stemmed_word"] == key.decode("utf-8"):
                    baseline_positive_dicts.append({"word_dict": word_dict, "vector200": self.vectors200[value]})

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        # siphon top500 frequency
        top_frequency_baseline_positive_dicts = sorted(baseline_positive_dicts, key=lambda k: k["word_dict"]['count'], reverse = True)[:500]

        #print baseline_positive_dicts
        """ index will exceed 500 because some of the words did not appear in this corpus"""
        for x_dict in top_frequency_baseline_positive_dicts:
            self.baseline_positive_words.append(x_dict["word_dict"])
            #print x_dict["word_dict"]
            self.baseline_positive_vectors200.append(x_dict["vector200"])

        print "\n" + "-"*70

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

    def get_baseline_cosine_topN(self):
        """ (1) calculate cosine similarity (2) get topN nearest sentiment_words """
        """ This is to calculate the baseline """

        print "Calculating Cosine Similarity between queries and every positive word (Baseline)"

        baseline_cosine_topN = []
        for query in self.queries:
            baseline_cos_sim_list = []

            for index in xrange(len(self.baseline_positive_words)):
                baseline_cos_sim_list.append(1-spatial.distance.cosine(self.vectors200[self.unique_words[query]], self.baseline_positive_vectors200[index]))

            print "Generating all baseline sentiment words with " + "\033[1m" + query + "\033[0m"
            baseline_sorted_index = sorted(range(len(baseline_cos_sim_list)), key=lambda k: baseline_cos_sim_list[k], reverse=True)

            baseline_word_dict_list = []
            for i, index in enumerate(baseline_sorted_index):
                # no threshold on topN
                baseline_word_dict = {"word": self.baseline_positive_words[index], "cos_sim": baseline_cos_sim_list[index]}
                baseline_word_dict_list.append(baseline_word_dict)

            # cutting threshold
            baseline_topN_cos_sim_list = [float(baseline_word_dict["cos_sim"]) for baseline_word_dict in baseline_word_dict_list if float(baseline_word_dict["cos_sim"]) >= self.threshold]

            # calculate the score out of topN cosine similarity
            baseline_positive_cos_score = sum(baseline_topN_cos_sim_list)

            print "baseline positive cosine score:", baseline_positive_cos_score

            baseline_cosine_topN.append({"query": query,
                "baseline_positive_topN_cosine_similarity": baseline_word_dict_list,
                "baseline_positive_cos_score": baseline_positive_cos_score
                })

        return baseline_cosine_topN

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
            #  cos_score = extreme_cos_score + strong_cos_score + moderate_cos_score
            print "positive cosine score:", cos_score

            positive_cosine_topN.append({"query": query,
                "extreme_positive_topN_cosine_similarity": extreme_word_dict_list,
                "strong_positive_topN_cosine_similarity": strong_word_dict_list,
                "moderate_positive_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score,
                })

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
            #  cos_score = extreme_cos_score + strong_cos_score + moderate_cos_score
            print "negative cosine score:", cos_score

            negative_cosine_topN.append({"query": query,
                "extreme_negative_topN_cosine_similarity": extreme_word_dict_list,
                "strong_negative_topN_cosine_similarity": strong_word_dict_list,
                "moderate_negative_topN_cosine_similarity": moderate_word_dict_list,
                "cos_score": cos_score})

        if self.verbose:
            print "-"*70

        return positive_cosine_topN, negative_cosine_topN

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_distance)
        dir2 = os.path.dirname(self.dst_ranking)
        dir3 = os.path.dirname(self.dst_distance_baseline)
        dir4 = os.path.dirname(self.dst_ranking_baseline)

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

    def render_baseline(self):
        if self.cosine_flag:
            baseline_positive_cosine_topN = self.get_baseline_cosine_topN()

            print "Putting Cosine word dicts in order"
            query_ordered_dict_list = []

            cnt = 0
            length = len(baseline_positive_cosine_topN)
            for baseline_cos_word_dict in baseline_positive_cosine_topN:
                cnt += 1
                query_ordered_dict = OrderedDict()
                query_ordered_dict["type"] = "baseline"
                query_ordered_dict["query"] = baseline_cos_word_dict["query"]
                query_ordered_dict["cosine_threshold"] = self.threshold

                # (1) baseline cosine
                baseline_positive_cosine_word_dict_list = []
                index = 0
                for cosine_word_dict in baseline_cos_word_dict["baseline_positive_topN_cosine_similarity"]:
                    index += 1
                    ordered_dict = OrderedDict()
                    ordered_dict["index"] = index
                    ordered_dict["cosine_similarity"] = cosine_word_dict["cos_sim"]
                    ordered_dict["count"] = cosine_word_dict["word"]["count"]
                    ordered_dict["stemmed_word"] = cosine_word_dict["word"]["stemmed_word"]
                    ordered_dict["word"] = cosine_word_dict["word"]["word"]
                    baseline_positive_cosine_word_dict_list.append(NoIndent(ordered_dict))

                query_ordered_dict["baseline_positive_topN_cosine_similarity"] = baseline_positive_cosine_word_dict_list

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
                # Writing to data/distance/location_threshold0.25-baseline.json
                print "Writing data to " + "\033[1m" + str(self.dst_distance_baseline) + "\033[0m"

            f = open(self.dst_distance_baseline, "w")
            f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

            if self.verbose:
                print "-"*80

        """"""""""""""""""""""""
        """  Ranking   Here  """
        """"""""""""""""""""""""
        # (1) cos_ranking
        if self.cosine_flag:
            location_ordered_dict = OrderedDict()
            location_ordered_dict['type'] = "baseline"
            location_ordered_dict['threshold'] = self.threshold
            location_ordered_dict['topN'] = len(self.baseline_positive_words)

            print "Ranking queries according to baseline cosine score"
            score_list = []
            for baseline_cos_word_dict in baseline_positive_cosine_topN:
                #if self.positive_minus_negative_flag:
                #    score = p_cos_word_dict["baseline_cos_score"] - n_cos_word_dict["baseline_positive_cos_score"]
                #else:
                score = baseline_cos_word_dict["baseline_positive_cos_score"]
                score_list.append({"attraction_name": baseline_cos_word_dict["query"], "score": score})

            # derive ranking_list from the unsorted score_list
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

            # Writing to data/ranking/location/Amsterdam_threshold0.25-baseline
            print "Writing to " + "\033[1m" + str(self.dst_ranking_baseline) + "\033[0m"
            print "-"*70
            f = open(self.dst_ranking_baseline, "w")
            f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))
        else:
            pass

    def render(self):
        """ save to data/distance/ & data/ranking/ """

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
                query_ordered_dict['type'] = "refined"
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
                print "Writing data to " + "\033[1m" + str(self.dst_distance) + "\033[0m"

            f = open(self.dst_distance, "w")
            f.write(json.dumps(query_ordered_dict_list, indent = 4, cls=NoIndentEncoder))

            if self.verbose:
                print "-"*80

        """"""""""""""""""""""""
        """  Ranking   Here  """
        """"""""""""""""""""""""
        # (1) cos_ranking
        if self.cosine_flag:
            location_ordered_dict = OrderedDict()
            location_ordered_dict['type'] = "refined"
            location_ordered_dict['threshold'] = self.threshold
            location_ordered_dict['topN'] = self.topN

            if self.verbose:
                print "Ranking queries according to cosine score"
            score_list = []
            for p_cos_word_dict, n_cos_word_dict in zip(positive_cosine_topN, negative_cosine_topN):
                if self.positive_minus_negative_flag:
                    score = p_cos_word_dict["cos_score"] - n_cos_word_dict["cos_score"]
                else:
                    score = p_cos_word_dict["cos_score"]
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

            # Writing to data/ranking/location/Amsterdam_threshold0.25
            if self.verbose:
                print "Writing to " + "\033[1m" + str(self.dst_ranking) + "\033[0m"
            f = open(self.dst_ranking, "w")
            f.write(json.dumps(location_ordered_dict, indent = 4, cls=NoIndentEncoder))
        else:
            pass

    def run(self):
        """ run the entire program """
        self.get_source()
        self.get_sentiment_statistics()
        self.get_lexicon()
        self.queries = self.get_attractions().keys()
        self.create_dirs()
        #self.render_baseline()
        self.render()

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
    distance.run()

