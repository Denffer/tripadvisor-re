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
    """ This program aims to
    (1) compute / sum topN sentiment_words with nearest cosine similarity for the given queries (entity_name) in data/distance/location/...
    (2) compute the rankings of the queries (entity_name)
        data/ranking/location/...
    """

    def __init__(self, argv1, argv2):
        self.src_line = argv1 # E.g., data/line/norm_vectors200/Amsterdam.txt
        self.location = re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+)\.txt", self.src_line).group(1)
        self.src_word2vec = "data/word2vec/" + self.location + ".txt"

        self.threshold = 0
        #self.threshold = float(argv2)
        self.src_opinion = "data/lexicon/processed_opinion_positive_lexicon.json"
        self.src_1star = "data/lexicon/1_star.json"
        self.src_2star = "data/lexicon/2_star.json"
        self.src_3star = "data/lexicon/3_star.json"
        self.src_4star = "data/lexicon/4_star.json"
        self.src_5star = "data/lexicon/5_star.json"
        self.src_fr = "data/frontend_reviews/" + self.location + "/"
        self.src_processed_ss = "data/processed_sentiment_statistics/"

        self.dst_distance = "data/distance/" + self.location + "/"
        self.dst_ranking = "data/ranking/" + self.location + "/"

        self.topN = 300
        self.queries = []

        self.entity_reranked_ranking_dict = {}
        self.entity_reranked_score_dict = {}
        self.entity_original_ranking_dict = {}
        self.entity_location_dict = {}
        self.entity_name_dict = {}

        self.verbose = 0

    def get_line_source(self):
	""" first call readline() to read thefirst line of vectors200 file to get vocab_size and dimension_size """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_line + "\033[0m"
        f_src = open(self.src_line, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')

        if self.verbose:
            print "Building index ..."

        line_unique_words, line_embeddings = {}, []
        for index in range(0, int(vocab_size)):
            line = f_src.readline().split(' ')
            # {"good":1, "attraciton":2, "Tokyo": 3}
            line_unique_words[line[0]]=index
            line_embeddings.append([float(i) for i in line[1:-1]])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index+1, vocab_size))
                sys.stdout.flush()

        f_src.close()
        if self.verbose:
            print "\n" + "-"*70

        return line_unique_words, line_embeddings

    def get_word2vec_source(self):
	""" first call readline() to read thefirst line of vectors200 file to get vocab_size and dimension_size """

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_word2vec + "\033[0m"
        f_src = open(self.src_word2vec, "r")
        vocab_size, dimension_size = f_src.readline().split(' ')

        if self.verbose:
            print "Building index ..."

        word2vec_unique_words, word2vec_embeddings = {}, []
        for index in range(0, int(vocab_size)):
            line = f_src.readline().split(' ')
            # {"good":1, "attraciton":2, "Tokyo": 3}
            word2vec_unique_words[line[0]]=index
            word2vec_embeddings.append([float(i) for i in line[1:-1]])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index+1, vocab_size))
                sys.stdout.flush()

        f_src.close()
        if self.verbose:
            print "\n" + "-"*70

        return word2vec_unique_words, word2vec_embeddings

    def get_entities(self):
        """ load data from frontend_review and extract information  """
        if self.verbose:
            print "Loading the entity_names from: " + self.src_fr

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
                            entity = json.load(file)
                            # entity_al => entity 'a'ppend 'l'ocation E.g. Happy-Temple_Bangkok
                            entity_al = entity["entity_name"].lower() + "_" + entity["location"].lower()
                            # get reranked_ranking
                            reranked_ranking = entity["reranked_ranking"]
                            self.entity_reranked_ranking_dict.update({entity_al: reranked_ranking})
                            # get reranked_score # E.g., 4.9
                            reranked_score = entity["avg_rating_stars"]
                            self.entity_reranked_score_dict.update({entity_al: reranked_score})
                            # get original_ranking
                            original_ranking = entity["original_ranking"]
                            self.entity_original_ranking_dict.update({entity_al: original_ranking})
                            # get entity_name
                            entity_name = entity["entity_name"]
                            self.entity_name_dict.update({entity_al: entity_name})
            else:
                print "No file is found"
                print "-"*80

        if self.verbose:
            print "-"*80

    def get_opinion_sentiment(self, unique_words, embeddings):
	""" (1) load sentiment_words from data/lexicon/processed_opinion_positive_lexicon.json
            (2) return sentiment_words and sentiment_embedding by the given embeddings
            (3) the given embeddings could be from Line or Word2Vec """

        with open(self.src_opinion, 'r') as f:
            opinion_lexicon = json.load(f)

        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src_opinion + "\033[0m"
            print "Processing words in opinion lexicon"

        opinion_sentiment_words, opinion_sentiment_embeddings = [], []
        cnt = 0
        length = len(unique_words.keys())
        for key, value in unique_words.iteritems():
            cnt += 1
            for word_dict in opinion_lexicon:
                if word_dict["stemmed_word"] == key.decode("utf-8"):
                    opinion_sentiment_words.append(word_dict)
                    opinion_sentiment_embeddings.append(embeddings[value])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        if self.verbose:
            print "\n" + "-"*70
        return opinion_sentiment_words, opinion_sentiment_embeddings

    def get_star_sentiment(self, source, unique_words, embeddings):
	""" open data/lexicon/5_star.json and load sentiment words """

        if self.verbose:
            print "Loading data from " + "\033[5m" + source + "\033[0m"
            print "Processing star lexicon"

        with open(source, 'r') as f:
            json_data = json.load(f)

        star_lexicon = json_data["topN_sentiment_words"]
        star_sentiment_words, star_sentiment_embeddings = [], []
        cnt = 0
        length = len(unique_words.keys())
        for key, value in unique_words.iteritems():
            cnt += 1
            for word_dict in star_lexicon:
                if word_dict["stemmed_word"] == key:
                    star_sentiment_words.append(word_dict)
                    star_sentiment_embeddings.append(embeddings[value])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        if self.verbose:
            print "\n" + "-"*70
        return star_sentiment_words, star_sentiment_embeddings

    def get_topN_sentiment_words(self, sentiment_type, unique_words, embeddings, sentiment_words, sentiment_words_embeddings):
        """ (1) calculate cosine similarity (2) get topN sentiment words with the highest cosine similarity"""

        if self.verbose:
            print "Calculating Cosine Similarity between queries and every sentiment word in opinion_lexicon"

        processed_entities = []
        for query in self.queries:
            cos_sim_list = []

            # cosine_similarity ranges from -1 ~ 1
            for index in xrange(len(sentiment_words)):
                try:
                    #print embeddings[unique_words[query]]
                    #print sentiment_words_embeddings[unique_words[query]]
                    cos_sim_list.append(1-spatial.distance.cosine(embeddings[unique_words[query]], sentiment_words_embeddings[index]))
                except:
                    # No match
                    pass

            if self.verbose:
                print "Generating top" + str(self.topN) + " sentiment words with " + "\033[1m" + query + "\033[0m"
            # sorting indices # indices is the plural form of index
            sorted_indices = sorted(range(len(cos_sim_list)), key=lambda k: cos_sim_list[k], reverse=True)

            # this get the locational sentiment_statistics # E.g., Amsterdam
            sentiment_statistics = self.get_locational_sentiment_statistics(sentiment_type)

            word_dict_list = []
            for i, index in enumerate(sorted_indices):
                try:
                    word_dict = {
                        "stemmed_word": sentiment_words[index]["stemmed_word"],
                        "word": sentiment_words[index]["word"],
                        "locational_frequency": sentiment_statistics[sentiment_words[index]["stemmed_word"]]["count"],
                        "norm_locational_frequency": sentiment_statistics[sentiment_words[index]["stemmed_word"]]["norm_count"],
                        "total_frequency": sentiment_words[index]["count"],
                        "cos_sim": cos_sim_list[index],
                        "cosineXfrequency_score": cos_sim_list[index] * sentiment_statistics[sentiment_words[index]["stemmed_word"]]["count"],
                        "cosineXnorm_frequency_score": cos_sim_list[index] * sentiment_statistics[sentiment_words[index]["stemmed_word"]]["norm_count"]
                            }
                    #print word_dict
                    word_dict_list.append(word_dict)
                except:
                    pass
                    #print "ya"
                #print word_dict

            #print word_dict_list
            cos_sim_list = [float(word_dict["cos_sim"]) for word_dict in word_dict_list if float(word_dict["cos_sim"]) >= self.threshold]
            #print cos_sim_list
            sum_cosine_score = sum(cos_sim_list)

            # (1) top3 avg
            top3_avg_cosine_score = max(cos_sim_list[:3])/len(cos_sim_list[:3])
            # (2) top10 avg
            top10_avg_cosine_score = max(cos_sim_list[:10])/len(cos_sim_list[:10])
            # (3) top50 avg
            top50_avg_cosine_score = max(cos_sim_list[:50])/len(cos_sim_list[:50])
            # (4) top100 avg
            top100_avg_cosine_score = max(cos_sim_list[:100])/len(cos_sim_list[:100])
            # (5) top_all avg
            top_all_avg_cosine_score = max(cos_sim_list[:])/len(cos_sim_list[:])

            # remove count <= 0
            refined_word_dict_list = [word_dict for word_dict in word_dict_list if float(word_dict["locational_frequency"]) >= 0]
            # cutting threshold
            refined_word_dict_list = [word_dict for word_dict in word_dict_list if float(word_dict["cos_sim"]) >= self.threshold]

            # (1) top3 cosine X norm_frequency
            top3 = refined_word_dict_list[:3]
            top3_sum_cXnf = sum([float(word_dict["cosineXnorm_frequency_score"]) for word_dict in top3])
            # (2) top10 cosine X norm_frequency
            top10 = refined_word_dict_list[:10]
            top10_sum_cXnf = sum([float(word_dict["cosineXnorm_frequency_score"]) for word_dict in top10])
            # (3) top50 cosine X norm_frequency
            top50 = refined_word_dict_list[:50]
            top50_sum_cXnf = sum([float(word_dict["cosineXnorm_frequency_score"]) for word_dict in top50])
            # (4) top100 cosine X norm_frequency
            top100 = refined_word_dict_list[:100]
            top100_sum_cXnf = sum([float(word_dict["cosineXnorm_frequency_score"]) for word_dict in top100])
            # (5) top100 cosine X norm_frequency
            top_all = refined_word_dict_list[:]
            top_all_sum_cXnf = sum([float(word_dict["cosineXnorm_frequency_score"]) for word_dict in top_all])

            # sum_z_scoreXnorm_frequency_score
            # (1) top3
            top3 = word_dict_list[:3]
            top3_mean = np.mean([float(word_dict["cos_sim"]) for word_dict in top3])
            top3_std = np.std([float(word_dict["cos_sim"]) for word_dict in top3])
            top3_sum_zXnf = sum([(((float(w["cos_sim"])-top3_mean)/top3_std) * float(w["cos_sim"]) * w['norm_locational_frequency']) for w in top3 if float(w["cos_sim"]) >= self.threshold])
            # (2) top10
            top10 = word_dict_list[:10]
            top10_mean = np.mean([float(word_dict["cos_sim"]) for word_dict in top10])
            top10_std = np.std([float(word_dict["cos_sim"]) for word_dict in top10])
            top10_sum_zXnf = sum([(((float(w["cos_sim"])-top10_mean)/top10_std) * float(w["cos_sim"]) * w['norm_locational_frequency']) for w in top10 if float(w["cos_sim"]) >= self.threshold])
            # (3) top50
            top50 = word_dict_list[:50]
            top50_mean = np.mean([float(word_dict["cos_sim"]) for word_dict in top50])
            top50_std = np.std([float(word_dict["cos_sim"]) for word_dict in top50])
            top50_sum_zXnf = sum([(((float(w["cos_sim"])-top50_mean)/top50_std) * float(w["cos_sim"]) * w['norm_locational_frequency']) for w in top50 if float(w["cos_sim"]) >= self.threshold])
            # (4) top100
            top100 = word_dict_list[:100]
            top100_mean = np.mean([float(word_dict["cos_sim"]) for word_dict in top100])
            top100_std = np.std([float(word_dict["cos_sim"]) for word_dict in top100])
            top100_sum_zXnf = sum([(((float(w["cos_sim"])-top100_mean)/top100_std) * float(w["cos_sim"]) * w['norm_locational_frequency']) for w in top100 if float(w["cos_sim"]) >= self.threshold])
            # (5) top_all
            top_all = word_dict_list[:]
            top_all_mean = np.mean([float(word_dict["cos_sim"]) for word_dict in top_all])
            top_all_std = np.std([float(word_dict["cos_sim"]) for word_dict in top_all])
            top_all_sum_zXnf = sum([(((float(w["cos_sim"])-top_all_mean)/top_all_std) * float(w["cos_sim"]) * w['norm_locational_frequency']) for w in top_all if float(w["cos_sim"]) >= self.threshold])

            #  # avg
            #  print "top3_avg_cosine_score :", top3_avg_cosine_score
            #  print "top10_avg_cosine_score :", top10_avg_cosine_score
            #  print "top50_avg_cosine_score :", top50_avg_cosine_score
            #  print "top100_avg_cosine_score :", top100_avg_cosine_score
            #  print "top_all_avg_cosine_score :", top_all_avg_cosine_score
            #  # sum
            #  print "top3 sum cosine_similarity * norm_locational_frequency = score :", top3_sum_cXnf
            #  print "top10 sum cosine_similarity * norm_locational_frequency = score :", top10_sum_cXnf
            #  print "top50 sum cosine_similarity * norm_locational_frequency = score :", top50_sum_cXnf
            #  print "top100 sum cosine_similarity * norm_locational_frequency = score :", top100_sum_cXnf
            #  print "top_all sum cosine_similarity * norm_locational_frequency = score :", top_all_sum_cXnf
            #  #  sum_zscoreXnorm_frequency_score
            #  print "top3 sum z_score * norm_locational_frequency = score :", top3_sum_zXnf
            #  print "top10 sum z_score * norm_locational_frequency = score :", top10_sum_zXnf
            #  print "top50 sum z_score * norm_locational_frequency = score :", top50_sum_zXnf
            #  print "top100 sum z_score * norm_locational_frequency = score :", top100_sum_zXnf
            #  print "top_all sum z_score * norm_locational_frequency = score :", top_all_sum_zXnf

            processed_entities.append({"query": query,
                "sentiment_type": sentiment_type,
                "topN_sentiment_words": refined_word_dict_list,
                # avg
                "top3_avg_cosine_score": top3_avg_cosine_score,
                "top10_avg_cosine_score": top10_avg_cosine_score,
                "top50_avg_cosine_score": top50_avg_cosine_score,
                "top100_avg_cosine_score": top100_avg_cosine_score,
                "top_all_avg_cosine_score": top_all_avg_cosine_score,
                # sum
                "top3_sum_cosineXnorm_frequency_score": top3_sum_cXnf,
                "top10_sum_cosineXnorm_frequency_score": top10_sum_cXnf,
                "top50_sum_cosineXnorm_frequency_score": top50_sum_cXnf,
                "top100_sum_cosineXnorm_frequency_score": top100_sum_cXnf,
                "top_all_sum_cosineXnorm_frequency_score": top_all_sum_cXnf,
                #  sum_zscoreXnorm_frequency_score
                "top3_sum_z_scoreXnorm_frequency_score": top3_sum_zXnf,
                "top10_sum_z_scoreXnorm_frequency_score": top10_sum_zXnf,
                "top50_sum_z_scoreXnorm_frequency_score": top50_sum_zXnf,
                "top100_sum_z_scoreXnorm_frequency_score": top100_sum_zXnf,
                "top_all_sum_z_scoreXnorm_frequency_score": top_all_sum_zXnf
                })

            if self.verbose:
                print "-"*70

        return processed_entities

    def get_locational_sentiment_statistics(self, statistics_type):
        """ get sentiment_statistic for a particular location | return frequencies of sentiment words """

        if "opinion" in statistics_type:
            target_filename = self.location + "_opinion_positive.json"
        elif "star" in statistics_type:
            target_filename = self.location + "_pos_tagged.json"
        else:
            raise
            print "Unknown sentiment statistics type"

        if self.verbose:
            print "Searching for: " + "\033[1m" + target_filename + "\033[0m" + " in " + self.src_processed_ss

        locational_sentiment_statistics = []
        for dirpath, dir_list, file_list in os.walk(self.src_processed_ss):
            #print "Walking into directory: " + str(dirpath)

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
                        if target_filename in f:
                            # print "Loading locational_sentiment_sentiment_statistics from " + dirpath + str(f)
                            with open(dirpath + "/" + f) as file:
                                json_data = json.load(file)
                            locational_sentiment_statistics = json_data
                        else:
                            #print "No match"
                            pass
            else:
                print "No file is found"

        if self.verbose:
            print "Normalizing frequencies ..."
        count_list = []
        for word_dict in locational_sentiment_statistics:
            count_list.append(word_dict["count"])
        norm_count_list = [( (float(c)-min(count_list)) / (max(count_list)-min(count_list)) ) for c in count_list]

        sentiment_dict = {}
        for word_dict, norm_count in zip(locational_sentiment_statistics, norm_count_list):
            sentiment_dict[word_dict["stemmed_word"]] = {"count": word_dict["count"], "norm_count": norm_count}

        #print sentiment_dict
        return sentiment_dict

    def renderDistance(self, entities, embedding_type, sentiment_type):
        """ save to data/distance/ """

        if self.verbose:
            print "Putting Cosine word dicts in order"
        entity_ordered_dicts = []

        sorted_entities = sorted(entities, key=lambda k: k['top_all_sum_cosineXnorm_frequency_score'], reverse = True)
        ranking = 0
        length = len(sorted_entities)
        for ranking_dict in sorted_entities:
            ranking += 1
            entity_ordered_dict = OrderedDict()
            entity_ordered_dict['computed_ranking'] = ranking
            entity_ordered_dict['embedding_type'] = embedding_type
            entity_ordered_dict['sentiment_tpye'] = sentiment_type
            entity_ordered_dict["query"] = ranking_dict["query"]
            entity_ordered_dict['location'] = self.location
            entity_ordered_dict['entity_name'] = self.entity_name_dict[ranking_dict['query']]
            entity_ordered_dict['reranked_score'] = self.entity_reranked_score_dict[ranking_dict['query']]
            entity_ordered_dict['reranked_ranking'] = self.entity_reranked_ranking_dict[ranking_dict['query']]
            entity_ordered_dict['original_ranking'] = self.entity_original_ranking_dict[ranking_dict['query']]
            entity_ordered_dict["cosine_threshold"] = self.threshold
            entity_ordered_dict["sentiment_type"] = ranking_dict["sentiment_type"]

            refined_word_dict_list = []
            index = 0
            for word_dict in ranking_dict["topN_sentiment_words"]:
                index += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = index
                ordered_dict["cos_sim"] = word_dict["cos_sim"]
                ordered_dict["loc_freq"] = word_dict["locational_frequency"]
                #ordered_dict["norm_loc_freq"] = word_dict["norm_locational_frequency"]
                ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
                ordered_dict["word"] = word_dict["word"]
                ordered_dict["total_freq"] = word_dict["total_frequency"]
                refined_word_dict_list.append(NoIndent(ordered_dict))

            entity_ordered_dict["topN_sentiment_words"] = refined_word_dict_list
            # append one query(entity) after another
            entity_ordered_dicts.append(entity_ordered_dict)

        # Writing to data/distance/New_York_City_line_star1.json
        print "Writing data to", "\033[1m" + str(self.dst_distance) + embedding_type + "_" + sentiment_type +".json \033[0m"
        f = open(self.dst_distance + embedding_type + "_" + sentiment_type + ".json", "w")
        f.write(json.dumps(entity_ordered_dicts, indent = 4, cls=NoIndentEncoder))

        if self.verbose:
            print "-"*80

    def renderRanking(self, entities, embedding_type, sentiment_type):
        """ put entities in orderedDict and save to data/ranking/ """

        if self.verbose:
            print "Ranking queries ..."
        ranking_dict_list = []
        for ranking_dict in entities:

            ranking_dict_list.append({
                "entity_name": ranking_dict["query"],
                "top3_avg_cosine_score": ranking_dict["top3_avg_cosine_score"],
                "top10_avg_cosine_score": ranking_dict["top10_avg_cosine_score"],
                "top50_avg_cosine_score": ranking_dict["top50_avg_cosine_score"],
                "top100_avg_cosine_score": ranking_dict["top100_avg_cosine_score"],
                "top_all_avg_cosine_score": ranking_dict["top_all_avg_cosine_score"],

                "top3_sum_cosineXnorm_frequency_score": ranking_dict["top3_sum_cosineXnorm_frequency_score"],
                "top10_sum_cosineXnorm_frequency_score": ranking_dict["top10_sum_cosineXnorm_frequency_score"],
                "top50_sum_cosineXnorm_frequency_score": ranking_dict["top50_sum_cosineXnorm_frequency_score"],
                "top100_sum_cosineXnorm_frequency_score": ranking_dict["top100_sum_cosineXnorm_frequency_score"],
                "top_all_sum_cosineXnorm_frequency_score": ranking_dict["top_all_sum_cosineXnorm_frequency_score"],

                "top3_sum_z_scoreXnorm_frequency_score": ranking_dict["top3_sum_z_scoreXnorm_frequency_score"],
                "top10_sum_z_scoreXnorm_frequency_score": ranking_dict["top10_sum_z_scoreXnorm_frequency_score"],
                "top50_sum_z_scoreXnorm_frequency_score": ranking_dict["top50_sum_z_scoreXnorm_frequency_score"],
                "top100_sum_z_scoreXnorm_frequency_score": ranking_dict["top100_sum_z_scoreXnorm_frequency_score"],
                "top_all_sum_z_scoreXnorm_frequency_score": ranking_dict["top_all_sum_z_scoreXnorm_frequency_score"],
                })

        # Avg
        # (1) Sort by top3_avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top3_avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top3_avg_cosine_score_ranking"] = rank
        # (2) Sort by top10_avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top10_avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top10_avg_cosine_score_ranking"] = rank
        # (3) Sort by top50_avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top50_avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top50_avg_cosine_score_ranking"] = rank
        # (4) Sort by top100_avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top100_avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top100_avg_cosine_score_ranking"] = rank
        # (5) Sort by top_all_avg_cosine_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top_all_avg_cosine_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top_all_avg_cosine_score_ranking"] = rank

        # sum_cosineXnorm_frequency_score
        # (1) Sort by sum_cosineXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top3_sum_cosineXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top3_sum_cosineXnorm_frequency_score_ranking"] = rank
        # (2) Sort by sum_cosineXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top10_sum_cosineXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top10_sum_cosineXnorm_frequency_score_ranking"] = rank
        # (3) By sort by sum_cosineXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top50_sum_cosineXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top50_sum_cosineXnorm_frequency_score_ranking"] = rank
        # (4) By sort by sum_cosineXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top100_sum_cosineXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top100_sum_cosineXnorm_frequency_score_ranking"] = rank
        # (5) By sort by sum_cosineXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top_all_sum_cosineXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top_all_sum_cosineXnorm_frequency_score_ranking"] = rank

        # sum_z_scoreXnorm_frequency_score
        # (1) By sort by top3_sum_z_scoreXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top3_sum_z_scoreXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top3_sum_z_scoreXnorm_frequency_score_ranking"] = rank
        # (2) By sort by top10_sum_z_scoreXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top10_sum_z_scoreXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top10_sum_z_scoreXnorm_frequency_score_ranking"] = rank
        # (3) By sort by top50_sum_z_scoreXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top50_sum_z_scoreXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top50_sum_z_scoreXnorm_frequency_score_ranking"] = rank
        # (4) By sort by top100_sum_z_scoreXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top100_sum_z_scoreXnorm_frequency_score'], reverse = True)
        rank = 0
        for rank_dict in ranking_dict_list:
            rank += 1
            rank_dict["top100_sum_z_scoreXnorm_frequency_score_ranking"] = rank
        # (5) By sort by top_all_sum_z_scoreXnorm_frequency_score # derive sorted_ranking_list from a the unsorted ranking_list
        ranking_dict_list = sorted(ranking_dict_list, key=lambda k: k['top_all_sum_z_scoreXnorm_frequency_score'], reverse = True)
        rank = 0
        for ranking_dict in ranking_dict_list:
            rank += 1
            ranking_dict["top_all_sum_z_scoreXnorm_frequency_score_ranking"] = rank

        # putting them in ordered_dict
        entity_ordered_dict = OrderedDict()
        entity_ordered_dict['embedding_type'] = embedding_type
        entity_ordered_dict['sentiment_tpye'] = sentiment_type
        entity_ordered_dict['threshold'] = self.threshold

        ordered_dicts = []
        computed_ranking = 0
        for ranking_dict in ranking_dict_list:
            computed_ranking += 1
            #print ranking_dict
            ordered_dict = OrderedDict()
            ordered_dict['entity_name'] = self.entity_name_dict[ranking_dict['entity_name']]
            ordered_dict['computed_ranking'] = computed_ranking
            ordered_dict['reranked_ranking'] = self.entity_reranked_ranking_dict[ranking_dict['entity_name']]
            ordered_dict['reranked_score'] = self.entity_reranked_score_dict[ranking_dict['entity_name']]
            ordered_dict['original_ranking'] = self.entity_original_ranking_dict[ranking_dict['entity_name']]

            # sum_cosineXnorm_frequency
            ordered_dict['top3_sum_cosineXnorm_frequency_score_ranking'] = ranking_dict["top3_sum_cosineXnorm_frequency_score_ranking"]
            ordered_dict['top3_sum_cosineXnorm_frequency_score'] = ranking_dict['top3_sum_cosineXnorm_frequency_score']
            ordered_dict['top10_sum_cosineXnorm_frequency_score_ranking'] = ranking_dict["top10_sum_cosineXnorm_frequency_score_ranking"]
            ordered_dict['top10_sum_cosineXnorm_frequency_score'] = ranking_dict['top10_sum_cosineXnorm_frequency_score']
            ordered_dict['top50_sum_cosineXnorm_frequency_score_ranking'] = ranking_dict["top50_sum_cosineXnorm_frequency_score_ranking"]
            ordered_dict['top50_sum_cosineXnorm_frequency_score'] = ranking_dict['top50_sum_cosineXnorm_frequency_score']
            ordered_dict['top100_sum_cosineXnorm_frequency_score_ranking'] = ranking_dict["top100_sum_cosineXnorm_frequency_score_ranking"]
            ordered_dict['top100_sum_cosineXnorm_frequency_score'] = ranking_dict['top100_sum_cosineXnorm_frequency_score']
            ordered_dict['top_all_sum_cosineXnorm_frequency_score_ranking'] = ranking_dict["top_all_sum_cosineXnorm_frequency_score_ranking"]
            ordered_dict['top_all_sum_cosineXnorm_frequency_score'] = ranking_dict['top_all_sum_cosineXnorm_frequency_score']

            # sum_z_scoreXnorm_frequency
            ordered_dict['top3_sum_z_scoreXnorm_frequency_score_ranking'] = ranking_dict["top3_sum_z_scoreXnorm_frequency_score_ranking"]
            ordered_dict['top3_sum_z_scoreXnorm_frequency_score'] = ranking_dict['top3_sum_z_scoreXnorm_frequency_score']
            ordered_dict['top10_sum_z_scoreXnorm_frequency_score_ranking'] = ranking_dict["top10_sum_z_scoreXnorm_frequency_score_ranking"]
            ordered_dict['top10_sum_z_scoreXnorm_frequency_score'] = ranking_dict['top10_sum_z_scoreXnorm_frequency_score']
            ordered_dict['top50_sum_z_scoreXnorm_frequency_score_ranking'] = ranking_dict["top50_sum_z_scoreXnorm_frequency_score_ranking"]
            ordered_dict['top50_sum_z_scoreXnorm_frequency_score'] = ranking_dict['top50_sum_z_scoreXnorm_frequency_score']
            ordered_dict['top100_sum_z_scoreXnorm_frequency_score_ranking'] = ranking_dict["top100_sum_z_scoreXnorm_frequency_score_ranking"]
            ordered_dict['top100_sum_z_scoreXnorm_frequency_score'] = ranking_dict['top100_sum_z_scoreXnorm_frequency_score']
            ordered_dict['top_all_sum_z_scoreXnorm_frequency_score_ranking'] = ranking_dict["top_all_sum_z_scoreXnorm_frequency_score_ranking"]
            ordered_dict['top_all_sum_z_scoreXnorm_frequency_score'] = ranking_dict['top_all_sum_z_scoreXnorm_frequency_score']

            # Avg
            ordered_dict['top3_avg_cosine_score_ranking'] = ranking_dict["top3_avg_cosine_score_ranking"]
            ordered_dict['top3_avg_cosine_score'] = ranking_dict['top3_avg_cosine_score']
            ordered_dict['top10_avg_cosine_score_ranking'] = ranking_dict["top10_avg_cosine_score_ranking"]
            ordered_dict['top10_avg_cosine_score'] = ranking_dict['top10_avg_cosine_score']
            ordered_dict['top50_avg_cosine_score_ranking'] = ranking_dict["top50_avg_cosine_score_ranking"]
            ordered_dict['top50_avg_cosine_score'] = ranking_dict['top50_avg_cosine_score']
            ordered_dict['top100_avg_cosine_score_ranking'] = ranking_dict["top100_avg_cosine_score_ranking"]
            ordered_dict['top100_avg_cosine_score'] = ranking_dict['top100_avg_cosine_score']
            ordered_dict['top_all_avg_cosine_score_ranking'] = ranking_dict["top_all_avg_cosine_score_ranking"]
            ordered_dict['top_all_avg_cosine_score'] = ranking_dict['top_all_avg_cosine_score']
            #print ordered_dict
            ordered_dicts.append(ordered_dict)

        entity_ordered_dict['Entity_Rankings'] = ordered_dicts


        #FIXME remove location # Writing to data/ranking/New_York_City/New_York_City_line_opinion
        print "Writing data to " + "\033[1m" + str(self.dst_ranking) + embedding_type + "_" + sentiment_type + ".json \033[0m"
        f = open(self.dst_ranking + embedding_type + "_" + sentiment_type + ".json", "w")
        f.write(json.dumps(entity_ordered_dict, indent = 4, cls=NoIndentEncoder))

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

    def run(self):
        """ run the entire program """
        self.create_dirs()
        line_unique_words, line_embeddings = self.get_line_source()
        word2vec_unique_words, word2vec_embeddings = self.get_word2vec_source()

        self.get_entities()
        self.queries = self.entity_name_dict.keys()

        # (1) opinion
        opinion_sentiment_words, opinion_sentiment_embeddings = self.get_opinion_sentiment(line_unique_words, line_embeddings)
        # line x opinion
        entities = self.get_topN_sentiment_words("opinion", line_unique_words, line_embeddings, opinion_sentiment_words, opinion_sentiment_embeddings)
        self.renderDistance(entities, "line", "opinion")
        self.renderRanking(entities, "line", "opinion")
        # word2vec x opinion
        entities = self.get_topN_sentiment_words("opinion", word2vec_unique_words, word2vec_embeddings, opinion_sentiment_words, opinion_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "opinion")
        self.renderRanking(entities, "word2vec", "opinion")

        # (2) 5_star
        star5_sentiment_words, star5_sentiment_embeddings = self.get_star_sentiment(self.src_5star, line_unique_words, line_embeddings)
        # line x 5_star
        entities = self.get_topN_sentiment_words("star", line_unique_words, line_embeddings, star5_sentiment_words, star5_sentiment_embeddings)
        self.renderDistance(entities, "line", "star5")
        self.renderRanking(entities, "line", "star5")
        # word2vec x 5_star
        entities = self.get_topN_sentiment_words("star", word2vec_unique_words, word2vec_embeddings, star5_sentiment_words, star5_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "star5")
        self.renderRanking(entities, "word2vec", "star5")

        # (3) 4_star
        star4_sentiment_words, star4_sentiment_embeddings = self.get_star_sentiment(self.src_4star, line_unique_words, line_embeddings)
        # line x 4_star
        entities = self.get_topN_sentiment_words("star", line_unique_words, line_embeddings, star4_sentiment_words, star4_sentiment_embeddings)
        self.renderDistance(entities, "line", "star4")
        self.renderRanking(entities, "line", "star4")
        # word2vec x 4_star
        entities = self.get_topN_sentiment_words("star", word2vec_unique_words, word2vec_embeddings, star4_sentiment_words, star4_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "star4")
        self.renderRanking(entities, "word2vec", "star4")

        # (4) 3_star
        star3_sentiment_words, star3_sentiment_embeddings = self.get_star_sentiment(self.src_3star, line_unique_words, line_embeddings)
        # line x 3_star
        entities = self.get_topN_sentiment_words("star", line_unique_words, line_embeddings, star3_sentiment_words, star3_sentiment_embeddings)
        self.renderDistance(entities, "line", "star3")
        self.renderRanking(entities, "line", "star3")
        # word2vec x 3_star
        entities = self.get_topN_sentiment_words("star", word2vec_unique_words, word2vec_embeddings, star3_sentiment_words, star3_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "star3")
        self.renderRanking(entities, "word2vec", "star3")

        # (5) 2_star
        star2_sentiment_words, star2_sentiment_embeddings = self.get_star_sentiment(self.src_2star, line_unique_words, line_embeddings)
        # line x 2_star
        entities = self.get_topN_sentiment_words("star", line_unique_words, line_embeddings, star2_sentiment_words, star2_sentiment_embeddings)
        self.renderDistance(entities, "line", "star2")
        self.renderRanking(entities, "line", "star2")
        # word2vec x 2_star
        entities = self.get_topN_sentiment_words("star", word2vec_unique_words, word2vec_embeddings, star2_sentiment_words, star2_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "star2")
        self.renderRanking(entities, "word2vec", "star2")

        # (1) 1_star
        star1_sentiment_words, star1_sentiment_embeddings = self.get_star_sentiment(self.src_1star, line_unique_words, line_embeddings)
        # line x 1_star
        entities = self.get_topN_sentiment_words("star", line_unique_words, line_embeddings, star1_sentiment_words, star1_sentiment_embeddings)
        self.renderDistance(entities, "line", "star1")
        self.renderRanking(entities, "line", "star1")
        # word2vec x 1_star
        entities = self.get_topN_sentiment_words("star", word2vec_unique_words, word2vec_embeddings, star1_sentiment_words, star1_sentiment_embeddings)
        self.renderDistance(entities, "word2vec", "star1")
        self.renderRanking(entities, "word2vec", "star1")

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

