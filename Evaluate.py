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
        self.filename = re.search("data\/ranking\/([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)", self.src).group(1) # E.g. New_York_City
        self.dst = "data/results/"

        self.baseline1_data = {}
        self.methodology_data = []

        baseline1_kendalltau, baseline1_ndcg = [], []
        baseline2_kendalltau, baseline2_ndcg = [], []
        baseline3_kendalltau, baseline3_ndcg = [], []
        methodology_kendalltau, methodology_ndcg = [], []

    def get_source(self):
        """ load all json file in data/ranking/location/location-Threshold.json """
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                computed_vs_reranked_kendalltau_list, computed_vs_original_kendalltau_list = [], []

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
                                print "Initializing Baseline from", str(dirpath) + str(f)
                                self.baseline_data = file_data["baseline_ranking"]
                            elif file_data["method"] == "CosineThreshold":
                                print "Initializing Methodology from", str(dirpath) + str(f)
                                self.methodology_data = file_data["cosine_threshold_ranking"]
                            else:
                                print "No match for Baseline or CosineThreshold"
                                pass

            else:
                print "No file is found"
            print "-"*80

    def get_baseline1(self):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_mentioned_count """

        print "Processing baseline1"
        original_rankings, baseline1_rankings = [], []
        for attraction_dict in self.baseline_data:
            original_rankings.append(attraction_dict["reranked_ranking"])
            baseline1_rankings.append(attraction_dict["ranking_by_mentioned_count"])

        baseline1_kendalltau = self.get_kendalltau(original_rankings, baseline1_rankings)
        baseline1_ndcg = self.get_ndcg(original_rankings, baseline1_rankings)

        print "-"*80
        return baseline1_kendalltau, baseline1_ndcg

    def get_baseline2(self):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_cooccur_sum """

        print "Processing baseline2"
        original_rankings, baseline2_rankings = [], []
        for attraction_dict in self.baseline_data:
            original_rankings.append(attraction_dict["reranked_ranking"])
            baseline2_rankings.append(attraction_dict["ranking_by_cooccur_sum"])

        baseline2_kendalltau = self.get_kendalltau(original_rankings, baseline2_rankings)
        baseline2_ndcg = self.get_ndcg(original_rankings, baseline2_rankings)

        print "-"*80
        return baseline2_kendalltau, baseline2_ndcg

    def get_baseline3(self):
        """ get NDCG & Kendalltau between original_rankings and rankings_by_cooccur_sum """

        print "Processing baseline3"
        original_rankings, baseline3_rankings = [], []
        for attraction_dict in self.baseline_data:
            original_rankings.append(attraction_dict["reranked_ranking"])
            baseline3_rankings.append(attraction_dict["ranking_by_cosine_sum"])

        baseline3_kendalltau = self.get_kendalltau(original_rankings, baseline3_rankings)
        baseline3_ndcg = self.get_ndcg(original_rankings, baseline3_rankings)

        print "-"*80
        return baseline3_kendalltau, baseline3_ndcg

    def get_methodology(self):
        """ get NDCG & Kendalltau between original_rankings and computed_rankings """

        print "Processing methodology"
        original_rankings, computed_rankings = [], []
        self.methodology_data = sorted(self.methodology_data, key=lambda k: k['reranked_ranking'])
        for attraction_dict in self.methodology_data:
            #original_rankings.append(attraction_dict["original_ranking"])
            original_rankings.append(attraction_dict["reranked_ranking"])
            computed_rankings.append(attraction_dict["computed_ranking"])

        methodology_kendalltau = self.get_kendalltau(original_rankings, computed_rankings)
        methodology_ndcg = self.get_ndcg(original_rankings, computed_rankings)

        print "-"*80
        return methodology_kendalltau, methodology_ndcg

    def get_kendalltau(self, ranking_list1, ranking_list2):
        """ get kendalltau for two input lists """

        print "Computing Kendalltau ..."
        print "List1:", ranking_list1
        print "List2:", ranking_list2
        kendalltau = scipy.stats.kendalltau(ranking_list1, ranking_list2).correlation

        print kendalltau
        print "-"*30
        return kendalltau

    def get_ndcg(self, ranking_list1, ranking_list2):
        """ get ndcg for two input lists """

        print "Computing NDCG ..."
        print "List1:", ranking_list1
        print "List2:", ranking_list2

        g = []
        for r1, r2 in zip(ranking_list1, ranking_list2):
            if int(r1)<5:
                if int(r2)<=5:
                    g.append(4)
                else:
                    g.append(0)
            elif 5 < int(r1) <= 10:
                if 5 < int(r2) <= 10:
                    g.append(3)
                else:
                    g.append(0)
            elif 10 < int(r1) <= 15:
                if 10 < int(r2) <= 15:
                    g.append(2)
                else:
                    g.append(0)
            elif 15 < int(r1) <= 20:
                if 15 < int(r2) <= 20:
                    g.append(1)
                else:
                    g.append(0)
            else:
                g.append(0)

        print "G:", g
        ndcg = map(div, self.get_dcg(g), self.get_dcg(sorted(g, reverse=True)))
        print "NDCG:", ndcg

        return ndcg

    def get_dcg(self, r):
        return reduce(lambda dcgs, dg: dcgs + [dg+dcgs[-1]], map(lambda(rank, g): (2**g-1)/log(rank+2,2),enumerate(r)), [0])[1:]

    def create_dirs(self, dst, location):
        """ create the directory if not exist """
        dir1 = os.path.dirname(dst + location + "/")

        if not os.path.exists(dir1):
            print "Creating directory:", dir1
            os.makedirs(dir1)

    def render(self):
        """Render kendalltau and NDCG according to baseline1, baseline2, baseline3, methodology """

        self.create_dirs(self.dst, self.filename)

        ordered_dict = OrderedDict()
        ordered_dict["b1_kendalltau"] = self.baseline1_kendalltau
        ordered_dict["b2_kendalltau"] = self.baseline2_kendalltau
        ordered_dict["b3_kendalltau"] = self.baseline3_kendalltau
        ordered_dict["m_kendalltau"] = self.methodology_kendalltau
        ordered_dict["b1_ndcg@10"] = self.baseline1_ndcg[9]
        ordered_dict["b2_ndcg@10"] = self.baseline2_ndcg[9]
        ordered_dict["b3_ndcg@10"] = self.baseline3_ndcg[9]
        ordered_dict["m_ndcg@10"] = self.methodology_ndcg[9]


        print "Saving", "\033[1m" + self.filename + ".json" + "\033[0m", "to", self.dst
        with open(self.dst + "/" + self.filename + ".json", "w") as f:
            f.write(json.dumps(ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def run(self):
        """ plot cosine ranking and dot ranking according to the given flags """
        self.get_source()
        self.baseline1_kendalltau, self.baseline1_ndcg = self.get_baseline1()
        self.baseline2_kendalltau, self.baseline2_ndcg = self.get_baseline2()
        self.baseline3_kendalltau, self.baseline3_ndcg = self.get_baseline3()
        self.methodology_kendalltau, self.methodology_ndcg = self.get_methodology()

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

