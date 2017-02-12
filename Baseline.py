import matplotlib, json, os, sys, linecache, re
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial
from collections import OrderedDict
import pprint

class Baseline:
    """ This program calculate 3 baselines for comparison """
    def __init__(self):
        self.src_vectors200 = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src_vectors200).group(1)
        self.src_cooccur = "data/line/cooccur/" + self.filename + ".txt"
        self.src_frontend = "data/frontend_reviews/" + self.filename + "/"
        self.src_lexicon = "data/lexicon/sentiment_statistics.json"
        self.dst = "data/ranking/" + self.filename + "/"

        self.unique_words = {}
        self.sentiment_words = []
        self.attractions = []
        self.cooccur_matrix = np.zeros(shape=(1,1))
        self.baseline1, self.baseline2, self.baseline3 = [], [], []

    def get_unique_words(self):
        """ get a dictionary of all unique words """

        print "Loading data from:", "\033[1m" + self.src_vectors200 + "\033[0m"
        with open(self.src_vectors200) as f:
            next(f)
            index = 0
            for line in f:
                line = line.strip("\n").strip().split(" ")
                self.unique_words.update({line[0]:index})
                index += 1
        #print self.unique_words

    def get_cooccurrence_matrix(self):
        """ get cooccur_matrix """
        print "Constructing cooccurrence matrix"

        cooccur_lines = []
        with open(self.src_cooccur) as f:
            for line in f:
                cooccur_lines.append(line.strip("\n").strip().split(" "))

        cnt = 0
        length = len(cooccur_lines)
        vocab_size = len(self.unique_words)
        self.cooccur_matrix = np.zeros(shape=(vocab_size, vocab_size))
        for line in cooccur_lines:
            cnt += 1
            if line[0] and line[1] in self.unique_words:
                index1 = self.unique_words[line[0]]
                index2 = self.unique_words[line[1]]
                self.cooccur_matrix[index1][index2] = line[2]
                self.cooccur_matrix[index2][index1] = line[2]
            else:
                pass

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()
        print ""

    def get_attractions(self):
        """ get attraction_names and total_review_mentioned_count """

        print "Loading attraction_names from: " + self.src_frontend
        for dirpath, dir_list, file_list in os.walk(self.src_frontend):
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
                        print "Merging " + str(dirpath) + str(f)
                        with open(dirpath + f) as file:
                            attraction = json.load(file)
                            # attraction_al => attraction append location E.g. Happy-Temple_Bangkok
                            attraction_name = attraction["attraction_name"].lower() + "_" + attraction["location"].lower()
                            attraction_mentioned_count = attraction["total_attraction_name_mentioned_count"]
                            #  original_ranking = int(attraction["original_ranking"])
                            reranked_ranking = int(attraction["reranked_ranking"])
                            original_ranking = int(attraction["original_ranking"])
                            self.attractions.append({
                                "attraction_name": attraction_name, "attraction_mentioned_count": attraction_mentioned_count,
                                "reranked_ranking": reranked_ranking, "original_ranking": original_ranking})
            else:
                print "No file is found"
                print "-"*80

        print "-"*80
        #print self.attractions
        return self.attractions

    def get_sentiment_words(self):
        """ get all sentiment_words for baseline2 """

        with open(self.src_lexicon) as f:
            lexicon = json.load(f)

        self.sentiment_words = lexicon["positive_statistics"]

    def get_baseline1(self):
        """ baseline1 ranks the attractions by the frequency of total_attraction_name_mentioned_count """

        print "Rendering Baseline1 ..."
        self.attractions = sorted(self.attractions, key=lambda k: k['attraction_mentioned_count'], reverse = True)
        ranking_by_mentioned_count = 0
        for attraction_dict in self.attractions:
            ranking_by_mentioned_count += 1
            attraction_dict.update({"ranking_by_mentioned_count": ranking_by_mentioned_count})

        #pprint.pprint(self.attractions)

    def get_baseline2(self):
        """ baseline2 ranks the attractions by the sum of attraction_cooccur_sentiment_words """

        print "Rendering Baseline2 ..."
        sentiment_indices = []
        for sentiment_dict in self.sentiment_words:
            try:
                sentiment_indices.append(self.unique_words[sentiment_dict["stemmed_word"]])
            except:
                pass

        for attraction_dict in self.attractions:
            try:
                # look for the index of attraction_al in unique_words
                attraction_index = self.unique_words[attraction_dict["attraction_name"]]
                cooccur_sum = 0

                for sentiment_index in sentiment_indices:
                    cooccur_sum += self.cooccur_matrix[attraction_index][sentiment_index]

                attraction_dict.update({"cooccur_sum":cooccur_sum})
            except:
                attraction_dict.update({"cooccur_sum":0})

        self.attractions = sorted(self.attractions, key=lambda k: k['cooccur_sum'], reverse = True)
        rank = 0
        for attraction_dict in self.attractions:
            rank += 1
            attraction_dict.update({"ranking_by_cooccur_sum": rank})

        #pprint.pprint(self.attractions)

    def get_baseline3(self):
        """ baseline3 ranks the attractions by the cosine_similarity between attraction_cooccur_matrix_row and sentiment_words_cooccur_matrix_row """

        print "Rendering Baseline3 ..."
        sentiment_matrix_rows = []
        for sentiment_dict in self.sentiment_words:
            try:
                sentiment_index = self.unique_words[sentiment_dict["stemmed_word"]]
                sentiment_matrix_rows.append(self.cooccur_matrix[sentiment_index])
            except:
                pass

        for attraction_dict in self.attractions:
            try:
                # look for the index of attraction_al in unique_words
                attraction_index = self.unique_words[attraction_dict["attraction_name"]]
                attraction_matrix_row = self.cooccur_matrix[attraction_index]
                cosine_sum = 0
                for sentiment_matrix_row in sentiment_matrix_rows:
                    cosine_sum += 1-spatial.distance.cosine(attraction_matrix_row, sentiment_matrix_row)

                attraction_dict.update({"cosine_sum":cosine_sum})
            except:
                attraction_dict.update({"cosine_sum":0})


        self.attractions = sorted(self.attractions, key=lambda k: k['cosine_sum'], reverse = True)
        rank = 0
        for attraction_dict in self.attractions:
            rank += 1
            attraction_dict.update({"ranking_by_cosine_sum": rank})

        #pprint.pprint(self.attractions)

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory:", dst1
            os.makedirs(dir1)

    def render(self):
        """ Draw matched vectors2 with unique_words and sentiment_words """

        self.get_unique_words()
        self.get_cooccurrence_matrix()
        self.get_attractions()
        self.get_sentiment_words()
        self.get_baseline1()
        self.get_baseline2()
        # self.get_baseline3()
        self.create_dirs()

        # reorder self.attractions by original_ranking
        # reorder self.attractions by reranked_ranking
        #self.attractions = sorted(self.attractions, key=lambda k: k['original_ranking'])
        self.attractions = sorted(self.attractions, key=lambda k: k['reranked_ranking'])

        baseline_ordered_dict = OrderedDict()
        baseline_ordered_dict["method"] = "Baseline"

        ordered_attractions = []
        for attraction_dict in self.attractions:
            ordered_dict = OrderedDict()
            ordered_dict['attraction_name'] = attraction_dict['attraction_name']
            ordered_dict['reranked_ranking'] = attraction_dict['reranked_ranking']
            ordered_dict['original_ranking'] = attraction_dict['original_ranking']
            ordered_dict['attraction_mentioned_count'] = attraction_dict['attraction_mentioned_count']
            ordered_dict['ranking_by_mentioned_count'] = attraction_dict['ranking_by_mentioned_count']
            ordered_dict['cooccur_sum'] = attraction_dict['cooccur_sum']
            ordered_dict['ranking_by_cooccur_sum'] = attraction_dict['ranking_by_cooccur_sum']
            #  ordered_dict['cosine_sum'] = attraction_dict['cosine_sum']
            #  ordered_dict['ranking_by_cosine_sum'] = attraction_dict['ranking_by_cosine_sum']
            ordered_attractions.append(ordered_dict)

        baseline_ordered_dict["Baseline_Ranking"] = ordered_attractions

        # Writing to data/ranking/Amsterdam_baseline
        print "Writing to " + "\033[1m" + str(self.dst) + self.filename + "_Baseline.json" + "\033[0m"
        f = open(self.dst + self.filename + "_Baseline.json", "w")
        f.write(json.dumps(baseline_ordered_dict, indent = 4))
        print "Done"


    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print '    Exception in ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

if __name__ == '__main__':
    baseline = Baseline()
    baseline.render()

