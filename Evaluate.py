import json, os, sys, linecache, re, uuid, scipy
from scipy import stats
import numpy as np
from operator import div
from math import log
from collections import OrderedDict

class Evaluate:
    """ This program
        (1) takes data/ranking/location/location-Threshold.json & location-Baseline.json as inputs
        (2) calculates Kendalltau of both Threshold and Baseline with original ranking on tripadvisor
        (3) calculates NDCG@10 of both Threshold and Baseline with original ranking on tripadvisor
    """

    def __init__(self):
        # sample argv input : data/ranking/New_York_City/
        self.src = sys.argv[1]
        self.order = sys.argv[2]
        self.filename = re.search("data\/ranking\/([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)", self.src).group(1) # E.g. New_York_City
        self.dst = "data/results/"

        self.baseline1_data = {}
        self.methodology_data = []

        #  baseline1_kendalltau, baseline1_ndcg = [], []
        #  baseline2_kendalltau, baseline2_ndcg = [], []
        #  max_kendalltau, max_ndcg = [], []
        #  avg_kendalltau, avg_ndcg = [], []
        #  sum_kendalltau, sum_ndcg = [], []
        #  sum_cXf_kendalltau, sum_cXf_ndcg = [], []
        #  top3_kendalltau, top3_ndcg = [], []
        #  top5_kendalltau, top5_ndcg = [], []
        #  top10_kendalltau, top10_ndcg = [], []
        #  top50_kendalltau, top50_ndcg = [], []
        #  top100_kendalltau, top100_ndcg = [], []

    def get_source(self):
        """ load all json file in data/ranking/location/location-Threshold.json """
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            #print "Walking into directory: " + str(dirpath)

            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)

                ranking_dict_list = []
                for f in file_list:
                    # in case there is a goddamn .DS_Store file
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + "/" + str(f)
                        os.remove(dirpath+ "/"+ f)
                    else:
                        file_cnt += 1

                        with open(dirpath + "/" + f) as file:
                            file_data = json.loads(file.read())

                            if file_data["method"] == "Baseline":
                                #print "Initializing Baseline from", str(dirpath) + str(f)
                                self.baseline_data = file_data["Baseline_Ranking"]
                                # reorder according to input self.order
                                if self.order == "original":
                                    self.baseline_data = sorted(self.baseline_data, key=lambda k: k['original_ranking'])
                                elif self.order == "reranked":
                                    self.baseline_data = sorted(self.baseline_data, key=lambda k: k['reranked_ranking'])
                                else:
                                    raise
                            elif file_data["method"] == "CosineThreshold":
                                #print "Initializing Methodology from", str(dirpath) + str(f)
                                self.methodology_data = file_data["CosineThreshold_Ranking"]
                                # reorder according to input self.order
                                if self.order == "original":
                                    self.methodology_data = sorted(self.methodology_data, key=lambda k: k['original_ranking'])
                                elif self.order == "reranked":
                                    self.methodology_data = sorted(self.methodology_data, key=lambda k: k['reranked_ranking'])
                                else:
                                    raise
                            else:
                                print "No match for Baseline or CosineThreshold"
                                pass

            else:
                print "No file is found"
            print "-"*80

    def get_baseline1(self):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_mentioned_count """

        print "Processing: " + "\033[1m" + "baseline1" + "\033[0m"
        rankings, baseline1_rankings = [], []
        for attraction_dict in self.baseline_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            baseline1_rankings.append(attraction_dict["ranking_by_mentioned_count"])


        baseline1_kendalltau = self.get_kendalltau(rankings, baseline1_rankings)
        baseline1_ndcg = self.get_ndcg(rankings, baseline1_rankings)

        print "-"*80
        return baseline1_kendalltau, baseline1_ndcg

    def get_baseline2(self):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_cooccur_sum """

        print "Processing: " + "\033[1m" + "baseline2" + "\033[0m"
        rankings, baseline2_rankings = [], []
        for attraction_dict in self.baseline_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            baseline2_rankings.append(attraction_dict["ranking_by_cooccur_sum"])

        baseline2_kendalltau = self.get_kendalltau(rankings, baseline2_rankings)
        baseline2_ndcg = self.get_ndcg(rankings, baseline2_rankings)

        print "-"*80
        return baseline2_kendalltau, baseline2_ndcg

    def get_top3_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top3_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top3_avg_cosine_score_ranking"])

        top3_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top3_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top3_avg_kendalltau, top3_avg_ndcg

    def get_top5_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top5_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top5_avg_cosine_score_ranking"])

        top5_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top5_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top5_avg_kendalltau, top5_avg_ndcg

    def get_top20_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top20_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top20_avg_cosine_score_ranking"])

        top20_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top20_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top20_avg_kendalltau, top20_avg_ndcg

    def get_top50_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top50_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top50_avg_cosine_score_ranking"])

        top50_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top50_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top50_avg_kendalltau, top50_avg_ndcg

    def get_top100_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top100_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top100_avg_cosine_score_ranking"])

        top100_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top100_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top100_avg_kendalltau, top100_avg_ndcg

    def get_top_all_avg(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing: " + "\033[1m" + "top_all_avg_cosine" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top_all_avg_cosine_score_ranking"])

        top_all_avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        top_all_avg_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return top_all_avg_kendalltau, top_all_avg_ndcg

    #  def get_avg(self):
    #      """ get NDCG & Kendalltau between original_rankings and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "avg_cosine" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["avg_cosine_score_ranking"])
    #
    #      avg_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      avg_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return avg_kendalltau, avg_ndcg

    #  def get_sum(self):
    #      """ get NDCG & Kendalltau between original_rankings and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "sum_cosine" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["sum_cosine_score_ranking"])
    #
    #      sum_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      sum_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return sum_kendalltau, sum_ndcg

    #  def get_sum_cXf(self):
    #      """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "sum_cosineXfrequency" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["sum_cosineXfrequency_score_ranking"])
    #
    #      methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      methodology_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return methodology_kendalltau, methodology_ndcg

    def get_top3_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top3_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top3_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top5_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top5_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top5_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top20_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top20_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top20_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top50_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top50_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top50_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top100_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top100_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top100_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top_all_sum_cXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top_all_sum_cosineXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top_all_sum_cosineXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top3_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top3_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top3_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top5_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top5_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top5_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top20_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top20_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top20_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top50_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top50_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top50_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top100_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top100_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top100_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_top_all_sum_zXnf(self):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top_all_sum_z_scoreXnorm_frequency" + "\033[0m"
        rankings, computed_rankings = [], []
        for attraction_dict in self.methodology_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict["top_all_sum_z_scoreXnorm_frequency_score_ranking"])

        methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    #  def get_top5(self):
    #      """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "top5" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["sum_z_score_top5_ranking"])
    #
    #      methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      methodology_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return methodology_kendalltau, methodology_ndcg
    #
    #  def get_top50(self):
    #      """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "top50" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["sum_z_score_top50_ranking"])
    #
    #      methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      methodology_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return methodology_kendalltau, methodology_ndcg
    #
    #  def get_top100(self):
    #      """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """
    #
    #      print "Processing: " + "\033[1m" + "top100" + "\033[0m"
    #      rankings, computed_rankings = [], []
    #      for attraction_dict in self.methodology_data:
    #          if self.order == "original":
    #              rankings.append(attraction_dict["original_ranking"])
    #          elif self.order == "reranked":
    #              rankings.append(attraction_dict["reranked_ranking"])
    #          else:
    #              raise
    #          computed_rankings.append(attraction_dict["sum_z_score_top100_ranking"])
    #
    #      methodology_kendalltau = self.get_kendalltau(rankings, computed_rankings)
    #      methodology_ndcg = self.get_ndcg(rankings, computed_rankings)
    #
    #      print "-"*80
    #      return methodology_kendalltau, methodology_ndcg

    def get_kendalltau(self, ground_truth_rankings, comparing_rankings):
        """ get kendalltau for two input lists """

        print "Ground_Truth_Rankings:", ground_truth_rankings
        print "Comparing_Rankings:", comparing_rankings

        g = []
        for r1, r2 in zip(ground_truth_rankings, comparing_rankings):
            if int(r2)<=5:
                g.append(4)
            elif 5 < int(r2) <= 10:
                g.append(3)
            elif 10 < int(r2) <= 15:
                g.append(2)
            elif 15 < int(r2) <= 20:
                g.append(1)
            else:
                g.append(0)

        ground_truth_g = [4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1]
        #print "Ground Truth G:", ground_truth_g
        print "G:", g

        kendalltau = scipy.stats.kendalltau(ground_truth_rankings, comparing_rankings).correlation
        print kendalltau
        print "-"*30
        return kendalltau

    def get_ndcg(self, ground_truth_rankings, comparing_rankings):
        """ get ndcg for two input lists """

        print "Computing NDCG ..."
        print "Ground_Truth_Rankings:", ground_truth_rankings
        print "Comparing_Rankings:", comparing_rankings

        g = []
        for r1, r2 in zip(ground_truth_rankings, comparing_rankings):
            if int(r2)<=5:
                g.append(4)
            elif 5 < int(r2) <= 10:
                g.append(3)
            elif 10 < int(r2) <= 15:
                g.append(2)
            elif 15 < int(r2) <= 20:
                g.append(1)
            else:
                g.append(0)

        ground_truth_g = [4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1]
        #print "Ground Truth G:", ground_truth_g
        print "G:", g
        try:
            ndcg = map(div, self.get_dcg(g), self.get_dcg(sorted(g, reverse=True)))
        except:
            ndcg = [0]*20
        print "NDCG:", ndcg

        return ndcg

    def get_dcg(self, r):
        return reduce(lambda dcgs, dg: dcgs + [dg+dcgs[-1]], map(lambda(rank, g): (2**g-1)/log(rank+2,2),enumerate(r)), [0])[1:]

    def create_dirs(self, dst, location):
        """ create the directory if not exist """
        dir1 = os.path.dirname(dst + "/")

        if not os.path.exists(dir1):
            print "Creating directory:", dir1
            os.makedirs(dir1)

    def render(self):
        """Render kendalltau and NDCG according to baseline1, baseline2, baseline3, methodology """

        self.create_dirs(self.dst, self.filename)

        ordered_dict = OrderedDict()
        ordered_dict["b1_kendalltau"] = self.baseline1_kendalltau
        ordered_dict["b2_kendalltau"] = self.baseline2_kendalltau
        #ordered_dict["max_kendalltau"] = self.max_kendalltau
        #ordered_dict["avg_kendalltau"] = self.avg_kendalltau
        ordered_dict["top3_avg_kendalltau"] = self.top3_avg_kendalltau
        ordered_dict["top5_avg_kendalltau"] = self.top5_avg_kendalltau
        ordered_dict["top20_avg_kendalltau"] = self.top20_avg_kendalltau
        ordered_dict["top50_avg_kendalltau"] = self.top50_avg_kendalltau
        ordered_dict["top100_avg_kendalltau"] = self.top100_avg_kendalltau
        ordered_dict["top_all_avg_kendalltau"] = self.top_all_avg_kendalltau
        #ordered_dict["sum_kendalltau"] = self.sum_kendalltau
        #ordered_dict["sum_cXf_kendalltau"] = self.sum_cXf_kendalltau
        ordered_dict["top3_sum_cXnf_kendalltau"] = self.top3_sum_cXnf_kendalltau
        ordered_dict["top5_sum_cXnf_kendalltau"] = self.top5_sum_cXnf_kendalltau
        ordered_dict["top20_sum_cXnf_kendalltau"] = self.top20_sum_cXnf_kendalltau
        ordered_dict["top50_sum_cXnf_kendalltau"] = self.top50_sum_cXnf_kendalltau
        ordered_dict["top100_sum_cXnf_kendalltau"] = self.top100_sum_cXnf_kendalltau
        ordered_dict["top_all_sum_cXnf_kendalltau"] = self.top_all_sum_cXnf_kendalltau

        ordered_dict["top3_sum_zXnf_kendalltau"] = self.top3_sum_zXnf_kendalltau
        ordered_dict["top5_sum_zXnf_kendalltau"] = self.top5_sum_zXnf_kendalltau
        ordered_dict["top20_sum_zXnf_kendalltau"] = self.top20_sum_zXnf_kendalltau
        ordered_dict["top50_sum_zXnf_kendalltau"] = self.top50_sum_zXnf_kendalltau
        ordered_dict["top100_sum_zXnf_kendalltau"] = self.top100_sum_zXnf_kendalltau
        ordered_dict["top_all_sum_zXnf_kendalltau"] = self.top_all_sum_zXnf_kendalltau

        #  ordered_dict["top5_kendalltau"] = self.top5_kendalltau
        #  ordered_dict["top50_kendalltau"] = self.top50_kendalltau
        #  ordered_dict["top100_kendalltau"] = self.top100_kendalltau

        # ndcg@5
        ordered_dict["b1_ndcg@5"] = self.baseline1_ndcg[4]
        ordered_dict["b2_ndcg@5"] = self.baseline2_ndcg[4]

        ordered_dict["top3_avg_ndcg@5"] = self.top3_avg_ndcg[4]
        ordered_dict["top5_avg_ndcg@5"] = self.top5_avg_ndcg[4]
        ordered_dict["top20_avg_ndcg@5"] = self.top20_avg_ndcg[4]
        ordered_dict["top50_avg_ndcg@5"] = self.top50_avg_ndcg[4]
        ordered_dict["top100_avg_ndcg@5"] = self.top100_avg_ndcg[4]
        ordered_dict["top_all_avg_ndcg@5"] = self.top_all_avg_ndcg[4]

        ordered_dict["top3_sum_cXnf_ndcg@5"] = self.top3_sum_cXnf_ndcg[4]
        ordered_dict["top5_sum_cXnf_ndcg@5"] = self.top5_sum_cXnf_ndcg[4]
        ordered_dict["top20_sum_cXnf_ndcg@5"] = self.top20_sum_cXnf_ndcg[4]
        ordered_dict["top50_sum_cXnf_ndcg@5"] = self.top50_sum_cXnf_ndcg[4]
        ordered_dict["top100_sum_cXnf_ndcg@5"] = self.top100_sum_cXnf_ndcg[4]
        ordered_dict["top_all_sum_cXnf_ndcg@5"] = self.top_all_sum_cXnf_ndcg[4]

        ordered_dict["top3_sum_zXnf_ndcg@5"] = self.top3_sum_zXnf_ndcg[4]
        ordered_dict["top5_sum_zXnf_ndcg@5"] = self.top5_sum_zXnf_ndcg[4]
        ordered_dict["top20_sum_zXnf_ndcg@5"] = self.top20_sum_zXnf_ndcg[4]
        ordered_dict["top50_sum_zXnf_ndcg@5"] = self.top50_sum_zXnf_ndcg[4]
        ordered_dict["top100_sum_zXnf_ndcg@5"] = self.top100_sum_zXnf_ndcg[4]
        ordered_dict["top_all_sum_zXnf_ndcg@5"] = self.top_all_sum_zXnf_ndcg[4]

        # ndcg@10
        ordered_dict["b1_ndcg@10"] = self.baseline1_ndcg[9]
        ordered_dict["b2_ndcg@10"] = self.baseline2_ndcg[9]

        ordered_dict["top3_avg_ndcg@10"] = self.top3_avg_ndcg[9]
        ordered_dict["top5_avg_ndcg@10"] = self.top5_avg_ndcg[9]
        ordered_dict["top20_avg_ndcg@10"] = self.top20_avg_ndcg[9]
        ordered_dict["top50_avg_ndcg@10"] = self.top50_avg_ndcg[9]
        ordered_dict["top100_avg_ndcg@10"] = self.top100_avg_ndcg[9]
        ordered_dict["top_all_avg_ndcg@10"] = self.top_all_avg_ndcg[9]

        ordered_dict["top3_sum_cXnf_ndcg@10"] = self.top3_sum_cXnf_ndcg[9]
        ordered_dict["top5_sum_cXnf_ndcg@10"] = self.top5_sum_cXnf_ndcg[9]
        ordered_dict["top20_sum_cXnf_ndcg@10"] = self.top20_sum_cXnf_ndcg[9]
        ordered_dict["top50_sum_cXnf_ndcg@10"] = self.top50_sum_cXnf_ndcg[9]
        ordered_dict["top100_sum_cXnf_ndcg@10"] = self.top100_sum_cXnf_ndcg[9]
        ordered_dict["top_all_sum_cXnf_ndcg@10"] = self.top_all_sum_cXnf_ndcg[9]

        ordered_dict["top3_sum_zXnf_ndcg@10"] = self.top3_sum_zXnf_ndcg[9]
        ordered_dict["top5_sum_zXnf_ndcg@10"] = self.top5_sum_zXnf_ndcg[9]
        ordered_dict["top20_sum_zXnf_ndcg@10"] = self.top20_sum_zXnf_ndcg[9]
        ordered_dict["top50_sum_zXnf_ndcg@10"] = self.top50_sum_zXnf_ndcg[9]
        ordered_dict["top100_sum_zXnf_ndcg@10"] = self.top100_sum_zXnf_ndcg[9]
        ordered_dict["top_all_sum_zXnf_ndcg@10"] = self.top_all_sum_zXnf_ndcg[9]

        # ndcg@20
        ordered_dict["b1_ndcg@20"] = self.baseline1_ndcg[18]
        ordered_dict["b2_ndcg@20"] = self.baseline2_ndcg[18]

        ordered_dict["top3_avg_ndcg@20"] = self.top3_avg_ndcg[18]
        ordered_dict["top5_avg_ndcg@20"] = self.top5_avg_ndcg[18]
        ordered_dict["top20_avg_ndcg@20"] = self.top20_avg_ndcg[18]
        ordered_dict["top50_avg_ndcg@20"] = self.top50_avg_ndcg[18]
        ordered_dict["top100_avg_ndcg@20"] = self.top100_avg_ndcg[18]
        ordered_dict["top_all_avg_ndcg@20"] = self.top_all_avg_ndcg[18]

        ordered_dict["top3_sum_cXnf_ndcg@20"] = self.top3_sum_cXnf_ndcg[18]
        ordered_dict["top5_sum_cXnf_ndcg@20"] = self.top5_sum_cXnf_ndcg[18]
        ordered_dict["top20_sum_cXnf_ndcg@20"] = self.top20_sum_cXnf_ndcg[18]
        ordered_dict["top50_sum_cXnf_ndcg@20"] = self.top50_sum_cXnf_ndcg[18]
        ordered_dict["top100_sum_cXnf_ndcg@20"] = self.top100_sum_cXnf_ndcg[18]
        ordered_dict["top_all_sum_cXnf_ndcg@20"] = self.top_all_sum_cXnf_ndcg[18]

        ordered_dict["top3_sum_zXnf_ndcg@20"] = self.top3_sum_zXnf_ndcg[18]
        ordered_dict["top5_sum_zXnf_ndcg@20"] = self.top5_sum_zXnf_ndcg[18]
        ordered_dict["top20_sum_zXnf_ndcg@20"] = self.top20_sum_zXnf_ndcg[18]
        ordered_dict["top50_sum_zXnf_ndcg@20"] = self.top50_sum_zXnf_ndcg[18]
        ordered_dict["top100_sum_zXnf_ndcg@20"] = self.top100_sum_zXnf_ndcg[18]
        ordered_dict["top_all_sum_zXnf_ndcg@20"] = self.top_all_sum_zXnf_ndcg[18]

        print "Saving", "\033[1m" + self.filename + ".json" + "\033[0m", "to", self.dst
        with open(self.dst + "/" + self.filename + ".json", "w") as f:
            f.write(json.dumps(ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def run(self):
        """ plot cosine ranking and dot ranking according to the given flags """
        print "Ground truth is set to be: " + "\033[1m" + self.order + "\033[0m"
        self.get_source()
        self.baseline1_kendalltau, self.baseline1_ndcg = self.get_baseline1()
        self.baseline2_kendalltau, self.baseline2_ndcg = self.get_baseline2()

        self.top3_avg_kendalltau, self.top3_avg_ndcg = self.get_top3_avg()
        self.top5_avg_kendalltau, self.top5_avg_ndcg = self.get_top5_avg()
        self.top20_avg_kendalltau, self.top20_avg_ndcg = self.get_top20_avg()
        self.top50_avg_kendalltau, self.top50_avg_ndcg = self.get_top50_avg()
        self.top100_avg_kendalltau, self.top100_avg_ndcg = self.get_top100_avg()
        self.top_all_avg_kendalltau, self.top_all_avg_ndcg = self.get_top_all_avg()
        #self.avg_kendalltau, self.avg_ndcg = self.get_avg()
        #self.sum_kendalltau, self.sum_ndcg = self.get_sum()
        #self.sum_cXf_kendalltau, self.sum_cXf_ndcg = self.get_sum_cXf()

        self.top3_sum_cXnf_kendalltau, self.top3_sum_cXnf_ndcg = self.get_top3_sum_cXnf()
        self.top5_sum_cXnf_kendalltau, self.top5_sum_cXnf_ndcg = self.get_top5_sum_cXnf()
        self.top20_sum_cXnf_kendalltau, self.top20_sum_cXnf_ndcg = self.get_top20_sum_cXnf()
        self.top50_sum_cXnf_kendalltau, self.top50_sum_cXnf_ndcg = self.get_top50_sum_cXnf()
        self.top100_sum_cXnf_kendalltau, self.top100_sum_cXnf_ndcg = self.get_top100_sum_cXnf()
        self.top_all_sum_cXnf_kendalltau, self.top_all_sum_cXnf_ndcg = self.get_top_all_sum_cXnf()

        self.top3_sum_zXnf_kendalltau, self.top3_sum_zXnf_ndcg = self.get_top3_sum_zXnf()
        self.top5_sum_zXnf_kendalltau, self.top5_sum_zXnf_ndcg = self.get_top5_sum_zXnf()
        self.top20_sum_zXnf_kendalltau, self.top20_sum_zXnf_ndcg = self.get_top20_sum_zXnf()
        self.top50_sum_zXnf_kendalltau, self.top50_sum_zXnf_ndcg = self.get_top50_sum_zXnf()
        self.top100_sum_zXnf_kendalltau, self.top100_sum_zXnf_ndcg = self.get_top100_sum_zXnf()
        self.top_all_sum_zXnf_kendalltau, self.top_all_sum_zXnf_ndcg = self.get_top_all_sum_zXnf()
        #  self.top5_kendalltau, self.top5_ndcg = self.get_top5()
        #  self.top50_kendalltau, self.top50_ndcg = self.get_top50()
        #  self.top100_kendalltau, self.top100_ndcg = self.get_top100()

        self.render()

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print '    Exception in ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

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
    evaluate = Evaluate()
    evaluate.run()

