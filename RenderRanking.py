import matplotlib, json, os, sys, linecache, re, scipy, uuid
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
import numpy as np
from operator import div
from math import log
from collections import OrderedDict
from Distance import Distance

class RenderRanking:
    """ This program calculate spearmanr and kendalltau """
    def __init__(self):
        # data/ranking/cosine/ or data/ranking/dot/
        #self.src = "data/ranking/New_York_City/"
        self.src = sys.argv[1]
        self.dst_g = "data/results/sk_graphic/"
        self.dst = "data/results/"

        self.window_size = "2"
        self.min_count = "20"
        self.ranking_function = "1p"

        self.cosine_source = []
        self.filename = ""
        self.cosine_flag = 1

    def get_cosine_ranking(self):
        """ load all json file in data/ranking/cosine/"""
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                file_cnt = 0
                length = len(file_list)
                ranking_dict_list = []
                computed_vs_reranked_spearmanr_list, computed_vs_original_spearmanr_list = [], []
                computed_vs_reranked_kendalltau_list, computed_vs_original_kendalltau_list = [], []


                for f in file_list:
                    # in case there is a goddamn .DS_Store file
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + "/" + str(f)
                        os.remove(dirpath+ "/"+ f)
                    else:
                        file_cnt += 1
                        print "Merging " + str(dirpath) + "/" + str(f)

                        with open(dirpath +"/"+ f) as file:
                            self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                            file_data = json.loads(file.read())

                            ranking_dict_list.append(file_data)
                            s = self.get_spearmanr(file_data)
                            computed_vs_reranked_spearmanr_list.append(s[0])
                            computed_vs_original_spearmanr_list.append(s[1])
                            k = self.get_kendalltau(file_data)
                            computed_vs_reranked_kendalltau_list.append(k[0])
                            computed_vs_original_kendalltau_list.append(k[1])

                self.plot_cosine(ranking_dict_list, computed_vs_reranked_spearmanr_list, computed_vs_original_spearmanr_list, computed_vs_reranked_kendalltau_list, computed_vs_original_kendalltau_list, self.filename)

                #computed_vs_reranked_ndcg_list, computed_vs_original_ndcg_list
                cvrn_list, cvon_list = self.get_ndcg_list(ranking_dict_list)
                self.render_cosine(ranking_dict_list, computed_vs_reranked_spearmanr_list, computed_vs_original_spearmanr_list, computed_vs_reranked_kendalltau_list, computed_vs_original_kendalltau_list, cvrn_list, cvon_list, self.filename)
            else:
                print "No file is found"
                print "-"*80

    def get_spearmanr(self, x):
        """ Get spearmanr correlation """
        # ranking_input will be [{"query":Happy-Temple_Bangkok, "lambda": 0.1, "extreme_positive_cos_sim:": 0.58 } * 20]
        computed_rankings, reranked_rankings, original_rankings = [], [], []

        if self.cosine_flag and "cosine_ranking" in x:
            for attraction_dict in x["cosine_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                original_rankings.append(attraction_dict["original_ranking"])

        computed_vs_reranked_spearmanr = scipy.stats.spearmanr(computed_rankings, reranked_rankings).correlation
        computed_vs_original_spearmanr = scipy.stats.spearmanr(computed_rankings, original_rankings).correlation
        #print "Spearmanr:", spearmanr
        return computed_vs_reranked_spearmanr, computed_vs_original_spearmanr

    def get_kendalltau(self, x):
        """ get kendalltau correlation """
        computed_rankings, reranked_rankings, original_rankings = [], [], []

        if self.cosine_flag and "cosine_ranking" in x:
            for attraction_dict in x["cosine_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                original_rankings.append(attraction_dict["original_ranking"])

        computed_vs_reranked_kendalltau = scipy.stats.kendalltau(computed_rankings, reranked_rankings).correlation
        computed_vs_original_kendalltau = scipy.stats.kendalltau(computed_rankings, original_rankings).correlation
        #print "kendalltau:", kendalltau
        return computed_vs_reranked_kendalltau, computed_vs_original_kendalltau

    def get_ndcg_list(self, ranking_dict_list):
        """ get g """

        computed_rankings_list, reranked_rankings_list, original_rankings_list = [], [], []

        for ranking_dict in ranking_dict_list:
            computed_rankings, reranked_rankings, original_rankings = [], [], []

            try:
                if "cosine_ranking" in ranking_dict:
                    for x in ranking_dict["cosine_ranking"]:
                        computed_rankings.append(x["computed_ranking"])
                        reranked_rankings.append(x["reranked_ranking"])
                        original_rankings.append(x["original_ranking"])
            except:
                pass

            computed_rankings_list.append(computed_rankings)
            reranked_rankings_list.append(reranked_rankings)
            original_rankings_list.append(original_rankings)

        computed_vs_reranked_ndcg_list = []
        for computed_rankings, reranked_rankings in zip(computed_rankings_list, reranked_rankings_list):
            print "computed:", computed_rankings
            #reranked_rankings = [i for i in xrange(1,21)]
            print "reranked:", reranked_rankings
            g = []
            for i, j in zip(computed_rankings, reranked_rankings):
                if int(j)<5:
                    if int(i)<=5:
                        g.append(4)
                    else:
                        g.append(0)
                elif 5 < int(j) <= 10:
                    if 5 < int(i) <= 10:
                        g.append(3)
                    else:
                        g.append(0)
                elif 10 < int(j) <= 15:
                    if 10 < int(i) <= 15:
                        g.append(2)
                    else:
                        g.append(0)
                elif 15 < int(j) <= 20:
                    if 15 < int(i) <= 20:
                        g.append(1)
                    else:
                        g.append(0)
                else:
                    g.append(0)
            print "g:", g
            computed_vs_reranked_ndcg_list.append(self.get_ndcg(g))
            print "ndcg:", self.get_ndcg(g)
            print "-"*30

        computed_vs_original_ndcg_list = []
        for computed_rankings, original_rankings in zip(computed_rankings_list, original_rankings_list):
            print "computed:", computed_rankings
            #original_rankings = [i for i in xrange(1,21)]
            print "original:", original_rankings
            g = []
            for i, j in zip(computed_rankings, original_rankings):
                if int(j)<5:
                    if int(i)<=5:
                        g.append(4)
                    else:
                        g.append(0)
                elif 5 < int(j) <= 10:
                    if 5 < int(i) <= 10:
                        g.append(3)
                    else:
                        g.append(0)
                elif 10 < int(j) <= 15:
                    if 10 < int(i) <= 15:
                        g.append(2)
                    else:
                        g.append(0)
                elif 15 < int(j) <= 20:
                    if 15 < int(i) <= 20:
                        g.append(1)
                    else:
                        g.append(0)
                else:
                    g.append(0)
            print "g:", g
            print "ndcg:", self.get_ndcg(g)
            computed_vs_original_ndcg_list.append(self.get_ndcg(g))
            print "-"*30

        #print ndcg_list
        return computed_vs_reranked_ndcg_list, computed_vs_original_ndcg_list

    def get_dcg(self, r):
        return reduce(lambda dcgs, dg: dcgs + [dg+dcgs[-1]], map(lambda(rank, g): (2**g-1)/log(rank+2,2),enumerate(r)), [0])[1:]

    def get_ndcg(self, r):
        return map(div, self.get_dcg(r), self.get_dcg(sorted(r, reverse=True)))

    def create_dirs(self, dst, location, flag):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(dst + location + "/" + flag + "/")

        if not os.path.exists(dir1):
            print "Creating directory:", dir1
            os.makedirs(dir1)

    # computed = c, reranked = r, original = g, spearmanr = s, kendalltau = k
    def plot_cosine(self, ranking_dict_list, cvrs_list, cvos_list, cvrk_list, cvok_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs(self.dst_g, filename, "cosine")

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Lambda")
        plt.ylabel("Spearmanr & Kendalltau")

        for ranking_dict, spearmanr1, spearmanr2, kendalltau1,  kendalltau2 in zip( ranking_dict_list, cvrs_list, cvos_list, cvrk_list, cvok_list):
            #l = ranking_dict["lambda"]
            l = ranking_dict["threshold"]
            try:
                line1, = plt.plot( l, spearmanr1, 'bo', label='Computed_vs_Reranked_Spearmanr')
                line2, = plt.plot( l, kendalltau1, 'go', label='Computed_vs_Reranked_Kendalltau')
                line3, = plt.plot( l, spearmanr2, 'bx', label='Computed_vs_Original_Spearmanr')
                line4, = plt.plot( l, kendalltau2, 'gx', label='Computed_vs_Original_Kendalltau')

                plt.text( l+0.001, spearmanr1+0.001, str(spearmanr1), fontsize=8)
                plt.text( l+0.001, kendalltau1+0.001, str(kendalltau1), fontsize=8)
                plt.text( l+0.001, spearmanr2+0.001, str(spearmanr2), fontsize=8)
                plt.text( l+0.001, kendalltau2+0.001, str(kendalltau2), fontsize=8)
            except:
                print 'Error'
                self.PrintException()

        # set legend # aka indicator
        plt.legend(handles = [line1, line2, line3, line4], loc='best', numpoints=1)
        plt.title(filename)

        if self.cosine_flag:
            print "-"*80
            print "Saving", "\033[1m" + filename + "_w" + self.window_size + "_mc" + self.min_count + "_" + self.ranking_function +".png" + "\033[0m", "to", self.dst_g + filename + "/"
            fig.savefig(self.dst_g + filename + "_w" + self.window_size + "_mc" + self.min_count + "_" + self.ranking_function + ".png")
        else:
            pass

    # computed = c, reranked = r, original = g, spearmanr = s, kendalltau = k
    def render_cosine(self, ranking_dict_list, cvrs_list, cvos_list, cvrk_list, cvok_list, cvrn_list, cvon_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs(self.dst, filename, "cosine")

        ordered_ranking_dict_list = []
        for ranking_dict, spearmanr1, spearmanr2, kendalltau1, kendalltau2, ndcg1, ndcg2 in zip(ranking_dict_list, cvrs_list, cvos_list, cvrk_list, cvok_list, cvrn_list, cvon_list):
            ordered_dict = OrderedDict()
            #  ordered_dict["lambda"] = ranking_dict["lambda"]
            ordered_dict["threshold"] = ranking_dict["threshold"]
            ordered_dict["topN"] = ranking_dict["topN"]
            #ordered_dict["topN_max"] = ranking_dict["topN_max"]
            ordered_dict["window_size"] = self.window_size
            ordered_dict["min_count"] = self.min_count
            ordered_dict["ranking_function"] = self.ranking_function
            ordered_dict["computed_vs_reranked_spearmanr"] = spearmanr1
            ordered_dict["computed_vs_reranked_kendalltau"] = kendalltau1
            ordered_dict["computed_vs_original_spearmanr"] = spearmanr2
            ordered_dict["computed_vs_original_kendalltau"] = kendalltau2
            ordered_dict["computed_vs_reranked_ndcg@5"] = ndcg1[4]
            ordered_dict["computed_vs_reranked_ndcg@10"] = ndcg1[9]
            #ordered_dict["computed_vs_reranked_ndcg@15"] = ndcg1[14]
            #ordered_dict["computed_vs_reranked_ndcg@20"] = ndcg1[19]
            ordered_dict["computed_vs_original_ndcg@5"] = ndcg2[4]
            ordered_dict["computed_vs_original_ndcg@10"] = ndcg2[9]
            #ordered_dict["computed_vs_original_ndcg@15"] = ndcg2[14]
            #ordered_dict["computed_vs_original_ndcg@20"] = ndcg2[19]
            #ordered_dict["ndcg"] = NoIndent(ndcg)

            ordered_ranking_dict_list.append(ordered_dict)

        if self.cosine_flag:
            print "Saving", "\033[1m" + filename + "_w" + self.window_size + "_mc" + self.min_count + "_" + self.ranking_function +".json" + "\033[0m", "to", self.dst + filename + "/"
            with open(self.dst + filename + "/" + filename + "_w" + self.window_size + "_mc" + self.min_count + "_" + self.ranking_function + ".json", "w") as f:
                f.write(json.dumps(ordered_ranking_dict_list, indent = 4, cls=NoIndentEncoder))
            print "-"*80
        else:
            pass

    def run(self):
        """ plot cosine ranking and dot ranking according to the given flags """
        if self.cosine_flag:
            self.get_cosine_ranking()

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
    r = RenderRanking()
    r.run()

