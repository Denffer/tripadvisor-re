import json, os, sys, linecache, re, uuid, scipy
from scipy import stats
import numpy as np
from operator import div
from math import log
from collections import OrderedDict

class Evaluate:
    """ This program
        (1) takes data/ranking/location/parameter1_parameter2.json & baseline.json as inputs
        (2) calculates Kendalltau of the reranked rankings ( or original rankings )
        (3) calculates 1) NDCG@5 2) NDCG@10 3) NDCG@20 of the reranked rankings ( or original rankings )
    """

    def __init__(self):
        # sample argv input: data/ranking/New-York-City/ reranked | data/ranking/New-York-City original
        self.src = sys.argv[1]
        self.order = sys.argv[2]
        self.filename = re.search("data\/ranking\/([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+)", self.src).group(1) # E.g., New-York-City
        self.dst = "data/results/"

        self.methodology_data = []

    def get_baseline_source(self, target_filename):
        """ load all json file in data/ranking/location/baseline.json """
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
                    elif target_filename in f:
                        file_cnt += 1

                        with open(dirpath + "/" + f) as file:
                            file_data = json.loads(file.read())

                            #print "Initializing Baseline from", str(dirpath) + str(f)
                            self.baseline_data = file_data["Baseline_Ranking"]
                            # reorder according to input self.order
                            if self.order == "original":
                                self.baseline_data = sorted(self.baseline_data, key=lambda k: k['original_ranking'])
                            elif self.order == "reranked":
                                self.baseline_data = sorted(self.baseline_data, key=lambda k: k['reranked_ranking'])
                            else:
                                raise
            else:
                print "No file is found"
            print "-"*80

    def get_source(self, target_filename):
        """ load all json file in data/ranking/location/para1_para2.json """

        print "Loading data from: " + self.src
        source = []
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
                    elif target_filename in f:


                        file_cnt += 1
                        with open(dirpath + "/" + f) as file:
                            file_data = json.loads(file.read())

                            source = file_data["Entity_Rankings"]
                            # reorder according to input self.order
                            if self.order == "original":
                                source = sorted(source, key=lambda k: k['original_ranking'])
                            elif self.order == "reranked":
                                source = sorted(source, key=lambda k: k['reranked_ranking'])
                            else:
                                raise
                    else:
                        pass
            else:
                print "No target_file is found"

            print "-"*80
            return source

    def get_baselineN(self, source, parameter):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_mentioned_count """

        print "Processing: " + "\033[1m" + "baseline by " + str(parameter) + "\033[0m"
        rankings, baseline_rankings = [], []
        for attraction_dict in self.baseline_data:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            baseline_rankings.append(attraction_dict[parameter])

        kendalltau = self.get_kendalltau(rankings, baseline_rankings)
        ndcg = self.get_ndcg(rankings, baseline_rankings)

        print "-"*80
        return kendalltau, ndcg

    def get_topN_avg(self, source, n):
        """ get NDCG & Kendalltau between reranked_rankings ( or original_rankings ) and computed_rankings """

        print "Processing: " + "\033[1m" + "top" + n + "_avg_cosine_score_ranking" + "\033[0m"
        key = "top" + str(n) + "_avg_cosine_score_ranking"
        rankings, computed_rankings = [], []
        for attraction_dict in source:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict[key])

        kendalltau = self.get_kendalltau(rankings, computed_rankings)
        ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return kendalltau, ndcg

    def get_topN_sum_cXnf(self, source, n):
        """ get NDCG & Kendalltau between reranked_rankings ( or original_ranking ) and computed_rankings """

        print "Processing: " + "\033[1m" + "top" + n + "_sum_cosineXnorm_frequency" + "\033[0m"
        key = "top" + str(n) + "_sum_cosineXnorm_frequency_score_ranking"
        rankings, computed_rankings = [], []
        for attraction_dict in source:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict[key])

        kendalltau = self.get_kendalltau(rankings, computed_rankings)
        ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return kendalltau, ndcg

    def get_topN_sum_zXnf(self, source, n):
        """ get NDCG & Kendalltau between reranked_rankings(or original_ranking) and computed_rankings """

        print "Processing: " + "\033[1m" + "top" + n + "_sum_z_scoreXnorm_frequency" + "\033[0m"
        key = "top" + str(n) + "_sum_z_scoreXnorm_frequency_score_ranking"
        rankings, computed_rankings = [], []
        for attraction_dict in source:
            if self.order == "original":
                rankings.append(attraction_dict["original_ranking"])
            elif self.order == "reranked":
                rankings.append(attraction_dict["reranked_ranking"])
            else:
                raise
            computed_rankings.append(attraction_dict[key])

        kendalltau = self.get_kendalltau(rankings, computed_rankings)
        ndcg = self.get_ndcg(rankings, computed_rankings)

        print "-"*80
        return kendalltau, ndcg

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

    def render(self, result_dict):
        """Render kendalltau and NDCG according to baseline1, baseline2, baseline3, all methonds in methodology """

        self.create_dirs(self.dst, self.filename)
        baselines = result_dict["baselines"]

        # kendalltau
        ordered_dict = OrderedDict()
        ordered_dict["b1_kendalltau"] = baselines["baseline1_kendalltau"]
        ordered_dict["b2_kendalltau"] = baselines["baseline2_kendalltau"]
        ordered_dict["b3_kendalltau"] = baselines["baseline3_kendalltau"]
        ordered_dict["b1_ndcg@5"] = baselines["baseline1_ndcg"][4]
        ordered_dict["b2_ndcg@5"] = baselines["baseline2_ndcg"][4]
        ordered_dict["b3_ndcg@5"] = baselines["baseline3_ndcg"][4]
        ordered_dict["b1_ndcg@10"] = baselines["baseline1_ndcg"][9]
        ordered_dict["b2_ndcg@10"] = baselines["baseline2_ndcg"][9]
        ordered_dict["b3_ndcg@10"] = baselines["baseline3_ndcg"][9]
        ordered_dict["b1_ndcg@20"] = baselines["baseline1_ndcg"][19]
        ordered_dict["b2_ndcg@20"] = baselines["baseline2_ndcg"][19]
        ordered_dict["b3_ndcg@20"] = baselines["baseline3_ndcg"][19]

        for key in result_dict:
            if key != "baselines":
                ordered_dict[key+"_top_all_avg_kendalltau"] = result_dict[key]["top_all_avg_kendalltau"]
                ordered_dict[key+"_top_all_sum_cXnf_kendalltau"] = result_dict[key]["top_all_sum_cXnf_kendalltau"]
                ordered_dict[key+"_top_all_sum_zXnf_kendalltau"] = result_dict[key]["top_all_sum_zXnf_kendalltau"]

                # ndcg@5
                ordered_dict[key+"_top_all_avg_ndcg@5"] = result_dict[key]["top_all_avg_ndcg"][4]
                ordered_dict[key+"_top_all_sum_cXnf_ndcg@5"] = result_dict[key]["top_all_sum_cXnf_ndcg"][4]
                ordered_dict[key+"_top_all_sum_zXnf_ndcg@5"] = result_dict[key]["top_all_sum_zXnf_ndcg"][4]
                # ndcg@10
                ordered_dict[key+"_top_all_avg_ndcg@10"] = result_dict[key]["top_all_avg_ndcg"][9]
                ordered_dict[key+"_top_all_sum_cXnf_ndcg@10"] = result_dict[key]["top_all_sum_cXnf_ndcg"][9]
                ordered_dict[key+"_top_all_sum_zXnf_ndcg@10"] = result_dict[key]["top_all_sum_zXnf_ndcg"][9]
                # ndcg@20
                ordered_dict[key+"_top_all_avg_ndcg@20"] = result_dict[key]["top_all_avg_ndcg"][19]
                ordered_dict[key+"_top_all_sum_cXnf_ndcg@20"] = result_dict[key]["top_all_sum_cXnf_ndcg"][19]
                ordered_dict[key+"_top_all_sum_zXnf_ndcg@20"] = result_dict[key]["top_all_sum_zXnf_ndcg"][19]

        print "Saving", "\033[1m" + self.filename + ".json" + "\033[0m", "to", self.dst
        with open(self.dst + "/" + self.filename + ".json", "w") as f:
            f.write(json.dumps(ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def run(self):
        """ plot cosine ranking and dot ranking according to the given flags """
        print "Ground truth is set to be: " + "\033[1m" + self.order + "\033[0m"
        result_dict = {}

        baselines = {}
        # baseline
        source = self.get_baseline_source("baseline")
        baseline1_kendalltau, baseline1_ndcg = self.get_baselineN(source, "ranking_by_mentioned_count")
        baselines.update({"baseline1_kendalltau": baseline1_kendalltau, "baseline1_ndcg": baseline1_ndcg})
        baseline2_kendalltau, baseline2_ndcg = self.get_baselineN(source, "ranking_by_opinion_cooccur_sum")
        baselines.update({"baseline2_kendalltau": baseline2_kendalltau, "baseline2_ndcg": baseline2_ndcg})
        baseline3_kendalltau, baseline3_ndcg = self.get_baselineN(source, "ranking_by_pos_tagged_cooccur_sum")
        baselines.update({"baseline3_kendalltau": baseline3_kendalltau, "baseline3_ndcg": baseline3_ndcg})
        result_dict.update({"baselines": baselines})

        lineXopinion = {}
        # line x opinion
        source = self.get_source("line_opinion")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXopinion.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXopinion.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXopinion.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXopinion": lineXopinion})

        word2vecXopinion = {}
        # word2vec x opinion
        source = self.get_source("word2vec_opinion")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXopinion.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXopinion.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXopinion.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXopinion": word2vecXopinion})

        lineXstar1 = {}
        # line x star1
        source = self.get_source("line_star1")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXstar1.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXstar1.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXstar1.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXstar1": lineXstar1})

        word2vecXstar1 = {}
        # word2vec x star1
        source = self.get_source("word2vec_star1")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXstar1.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXstar1.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXstar1.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXstar1": word2vecXstar1})

        lineXstar2 = {}
        # line x star2
        source = self.get_source("line_star2")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXstar2.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXstar2.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXstar2.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXstar2": lineXstar2})

        word2vecXstar2 = {}
        # word2vec x star2
        source = self.get_source("word2vec_star2")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXstar2.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXstar2.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXstar2.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXstar2": word2vecXstar2})

        lineXstar3 = {}
        # line x star3
        source = self.get_source("line_star3")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXstar3.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXstar3.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXstar3.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXstar3": lineXstar3})

        word2vecXstar3 = {}
        # word2vec x star3
        source = self.get_source("word2vec_star3")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXstar3.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXstar3.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXstar3.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXstar3": word2vecXstar3})

        lineXstar4 = {}
        # line x star4
        source = self.get_source("line_star4")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXstar4.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXstar4.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXstar4.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXstar4": lineXstar4})

        word2vecXstar4 = {}
        # word2vec x star4
        source = self.get_source("word2vec_star4")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXstar4.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXstar4.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXstar4.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXstar4": word2vecXstar4})

        lineXstar5 = {}
        # line x star5
        source = self.get_source("line_star5")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        lineXstar5.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        lineXstar5.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        lineXstar5.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"lineXstar5": lineXstar5})

        word2vecXstar5 = {}
        # word2vec x star5
        source = self.get_source("word2vec_star5")
        kendalltau, ndcg = self.get_topN_avg(source, "_all")
        word2vecXstar5.update({"top_all_avg_kendalltau": kendalltau, "top_all_avg_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_cXnf(source, "_all")
        word2vecXstar5.update({"top_all_sum_cXnf_kendalltau": kendalltau, "top_all_sum_cXnf_ndcg": ndcg})
        kendalltau, ndcg = self.get_topN_sum_zXnf(source, "_all")
        word2vecXstar5.update({"top_all_sum_zXnf_kendalltau": kendalltau, "top_all_sum_zXnf_ndcg": ndcg})
        result_dict.update({"word2vecXstar5": word2vecXstar5})

        self.render(result_dict)

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

