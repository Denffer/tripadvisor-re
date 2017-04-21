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
        self.src_cooccur = "data/glove/cooccur/" + self.filename + ".txt"
        self.src_frontend = "data/frontend_reviews/" + self.filename + "/"
        self.src_opinion_lexicon = "data/lexicon/processed_opinion_positive_lexicon.json"
        self.src_pos_tagged_lexicon = "data/lexicon/processed_pos_tagged_lexicon.json"
        self.dst = "data/ranking/" + self.filename + "/"

        self.unique_words = {}
        self.opinion_sentiment_words, pos_tagged_sentiment_words = [], []
        self.entities = []
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

    def get_entities(self):
        """ extract (1) entity_name (2) entity_mentioned_count (3) reranked_ranking (4) original_ranking """

        print "Loading entity_names from: " + self.src_frontend
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
                            entity = json.load(file)
                            # entity_al => entity append location E.g. Happy-Temple_Bangkok
                            entity_name = entity["entity_name"].lower() + "_" + entity["location"].lower()
                            entity_mentioned_count = entity["total_entity_count"]
                            #  original_ranking = int(entity["original_ranking"])
                            reranked_ranking = int(entity["reranked_ranking"])
                            original_ranking = int(entity["original_ranking"])
                            self.entities.append({
                                "entity_name": entity_name, "entity_mentioned_count": entity_mentioned_count,
                                "reranked_ranking": reranked_ranking, "original_ranking": original_ranking})
            else:
                print "No file is found"
                print "-"*80

        print "-"*80

    def get_opinion_lexicon(self):
        """ get all sentiment_words for baseline2 """

        with open(self.src_opinion_lexicon) as f:
            opinion_lexicon = json.load(f)
        self.opinion_sentiment_words = opinion_lexicon

    def get_pos_tagged_lexicon(self):
        """ get all sentiment_words for baseline3 """

        with open(self.src_pos_tagged_lexicon) as f:
            pos_tagged_lexicon = json.load(f)
        self.pos_tagged_sentiment_words = pos_tagged_lexicon

    def get_baseline1(self):
        """ baseline1 ranks the entities by the frequency of entity_mentioned_count """

        print "Processing Baseline1 ..."
        self.entities = sorted(self.entities, key=lambda k: k['entity_mentioned_count'], reverse = True)

        ranking_by_mentioned_count = 0
        for entity_dict in self.entities:
            ranking_by_mentioned_count += 1
            entity_dict.update({"ranking_by_mentioned_count": ranking_by_mentioned_count})

    def get_baseline2(self):
        """ baseline2 ranks the entities by the sum of entity_cooccur_opinion_sentiment_words """

        print "Processing Baseline2 ..."
        sentiment_indices = []
        for sentiment_dict in self.opinion_sentiment_words:
            try:
                sentiment_indices.append(self.unique_words[sentiment_dict["stemmed_word"]])
            except:
                pass

        for entity_dict in self.entities:
            try:
                # look for the index of entity_al in unique_words
                entity_index = self.unique_words[entity_dict["entity_name"]]
                cooccur_sum = 0

                for sentiment_index in sentiment_indices:
                    cooccur_sum += self.cooccur_matrix[entity_index][sentiment_index]

                entity_dict.update({"opinion_cooccur_sum": cooccur_sum})
            except:
                entity_dict.update({"opinion_cooccur_sum": 0})

        self.entities = sorted(self.entities, key=lambda k: k['opinion_cooccur_sum'], reverse = True)
        rank = 0
        for entity_dict in self.entities:
            rank += 1
            entity_dict.update({"ranking_by_opinion_cooccur_sum": rank})

        #pprint.pprint(self.entities)

    def get_baseline3(self):
        """ baseline3 ranks the entities by the sum of entity_cooccur_pos_tagged_sentiment_words """

        print "Processing Baseline3 ..."
        sentiment_indices = []
        for sentiment_dict in self.pos_tagged_sentiment_words:
            try:
                sentiment_indices.append(self.unique_words[sentiment_dict["stemmed_word"]])
            except:
                pass

        for entity_dict in self.entities:
            try:
                # look for the index of entity_al in unique_words
                entity_index = self.unique_words[entity_dict["entity_name"]]
                cooccur_sum = 0

                for sentiment_index in sentiment_indices:
                    cooccur_sum += self.cooccur_matrix[entity_index][sentiment_index]

                entity_dict.update({"pos_tagged_cooccur_sum": cooccur_sum})
            except:
                entity_dict.update({"pos_tagged_cooccur_sum": 0})

        self.entities = sorted(self.entities, key=lambda k: k['pos_tagged_cooccur_sum'], reverse = True)
        rank = 0
        for entity_dict in self.entities:
            rank += 1
            entity_dict.update({"ranking_by_pos_tagged_cooccur_sum": rank})

        #pprint.pprint(self.entities)

    def get_baseline4(self):
        """ baseline4 ranks the entities by the cosine_similarity between entity_cooccur_matrix_row and opinion_sentiment_words_cooccur_matrix_row """

        print "Processing Baseline4 ..."
        sentiment_matrix_rows = []
        for sentiment_dict in self.opinion_sentiment_words:
            try:
                sentiment_index = self.unique_words[sentiment_dict["stemmed_word"]]
                sentiment_matrix_rows.append(self.cooccur_matrix[sentiment_index])
            except:
                pass

        for entity_dict in self.entities:
            try:
                # look for the index of entity_al in unique_words
                entity_index = self.unique_words[entity_dict["entity_name"]]
                entity_matrix_row = self.cooccur_matrix[entity_index]
                cosine_sum = 0
                for sentiment_matrix_row in sentiment_matrix_rows:
                    cosine_sum += 1-spatial.distance.cosine(entity_matrix_row, sentiment_matrix_row)

                entity_dict.update({"opinion_cosine_sum":cosine_sum})
            except:
                entity_dict.update({"opinion_cosine_sum":0})


        self.entities = sorted(self.entities, key=lambda k: k['opinion_cosine_sum'], reverse = True)
        rank = 0
        for entity_dict in self.entities:
            rank += 1
            entity_dict.update({"ranking_by_opinion_cosine_sum": rank})

        #pprint.pprint(self.entities)

    def get_baseline5(self):
        """ baseline5 ranks the entities by the cosine_similarity between entity_cooccur_matrix_row and pos_tagged_sentiment_words_cooccur_matrix_row """

        print "Processing Baseline5 ..."
        sentiment_matrix_rows = []
        for sentiment_dict in self.pos_tagged_sentiment_words:
            try:
                sentiment_index = self.unique_words[sentiment_dict["stemmed_word"]]
                sentiment_matrix_rows.append(self.cooccur_matrix[sentiment_index])
            except:
                pass

        for entity_dict in self.entities:
            try:
                # look for the index of entity_al in unique_words
                entity_index = self.unique_words[entity_dict["entity_name"]]
                entity_matrix_row = self.cooccur_matrix[entity_index]
                cosine_sum = 0
                for sentiment_matrix_row in sentiment_matrix_rows:
                    cosine_sum += 1-spatial.distance.cosine(entity_matrix_row, sentiment_matrix_row)

                entity_dict.update({"pos_tagged_cosine_sum":cosine_sum})
            except:
                entity_dict.update({"pos_tagged_cosine_sum":0})


        self.entities = sorted(self.entities, key=lambda k: k['pos_tagged_cosine_sum'], reverse = True)
        rank = 0
        for entity_dict in self.entities:
            rank += 1
            entity_dict.update({"ranking_by_pos_tagged_cosine_sum": rank})

        #pprint.pprint(self.entities)

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
        self.get_entities()
        self.get_opinion_lexicon()
        self.get_pos_tagged_lexicon()
        self.get_baseline1()
        self.get_baseline2()
        self.get_baseline3()
        #  self.get_baseline4()
        #  self.get_baseline5()
        self.create_dirs()

        # reorder self.entities by original_ranking
        # self.entities = sorted(self.entities, key=lambda k: k['original_ranking'])
        # reorder self.entities by reranked_ranking
        self.entities = sorted(self.entities, key=lambda k: k['reranked_ranking'])

        baseline_ordered_dict = OrderedDict()
        baseline_ordered_dict["method"] = "Baseline"
        baseline_ordered_dict["location"] = self.filename

        ordered_entities = []
        for entity_dict in self.entities:
            ordered_dict = OrderedDict()
            ordered_dict['entity_name'] = entity_dict['entity_name']
            ordered_dict['reranked_ranking'] = entity_dict['reranked_ranking']
            ordered_dict['original_ranking'] = entity_dict['original_ranking']
            # (1)
            ordered_dict['entity_mentioned_count'] = entity_dict['entity_mentioned_count']
            ordered_dict['ranking_by_mentioned_count'] = entity_dict['ranking_by_mentioned_count']
            # (2)
            ordered_dict['opinion_cooccur_sum'] = entity_dict['opinion_cooccur_sum']
            ordered_dict['ranking_by_opinion_cooccur_sum'] = entity_dict['ranking_by_opinion_cooccur_sum']
            # (3)
            ordered_dict['pos_tagged_cooccur_sum'] = entity_dict['pos_tagged_cooccur_sum']
            ordered_dict['ranking_by_pos_tagged_cooccur_sum'] = entity_dict['ranking_by_pos_tagged_cooccur_sum']

            ordered_entities.append(ordered_dict)

        baseline_ordered_dict["Baseline_Ranking"] = ordered_entities

        # Writing to data/ranking/Amsterdam_baseline
        #print "Writing to " + "\033[1m" + str(self.dst) + self.filename + "_Baseline.json" + "\033[0m"
        print "Writing to " + "\033[1m" + str(self.dst) + "baseline.json" + "\033[0m"
        f = open(self.dst + "baseline.json", "w")
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

