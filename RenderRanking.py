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
        self.src = "data/ranking/"
        self.dst_g = "data/results/sk_graphic/"
        self.dst = "data/results/"

        self.window_size = 5
        self.min_count = 20

        self.cosine_source = []
        self.dot_source = []
        self.filename = ""
        self.cosine_flag = 1
        self.dot_flag = 1

    def get_cosine_ranking(self):
        """ load all json file in data/ranking/cosine/"""
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if "cosine" in dirpath:
                if len(file_list) > 0:
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                    file_cnt = 0
                    length = len(file_list)
                    ranking_dict_list = []
                    spearmanr_list, kendalltau_list = [], []

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
                                spearmanr_list.append(self.get_spearmanr(file_data))
                                kendalltau_list.append(self.get_kendalltau(file_data))

                    #  print "Ranking_dict_list: ", ranking_dict_list
                    #  print "Spearmanr_list:", spearmanr_list
                    #  print "Kendalltau_list", kendalltau_list
                    self.plot_cosine(ranking_dict_list, spearmanr_list, kendalltau_list, self.filename)
                    ndcg_list = self.get_ndcg_list(ranking_dict_list)
                    self.render_cosine(ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list, self.filename)
                else:
                    print "No file is found"
                    print "-"*80

    def get_dot_ranking(self):
        """ load all json file in data/ranking/dot/ """
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if "dot" in dirpath:
                if len(file_list) > 0:
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                    file_cnt = 0
                    length = len(file_list)
                    ranking_dict_list = []
                    spearmanr_list, kendalltau_list = [], []
                    for f in file_list:
                        # in case there is a goddamn .DS_Store file
                        if str(f) == ".DS_Store":
                            print "Removing " + dirpath + str(f)
                            os.remove(dirpath+ "/"+ f)
                        else:
                            file_cnt += 1
                            print "Merging " + str(dirpath) + "/" + str(f)

                            with open(dirpath +"/"+ f) as file:
                                self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                                file_data = json.loads(file.read())

                                ranking_dict_list.append(file_data)
                                spearmanr_list.append(self.get_spearmanr(file_data))
                                kendalltau_list.append(self.get_kendalltau(file_data))

                    #  print "Ranking_dict_list: ", ranking_dict_list
                    #  print "Spearmanr_list:", spearmanr_list
                    #  print "Kendalltau_list", kendalltau_list
                    self.plot_dot(ranking_dict_list, spearmanr_list, kendalltau_list, self.filename)
                    ndcg_list = self.get_ndcg_list(ranking_dict_list)
                    self.render_dot(ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list, self.filename)
                else:
                    print "No file is found"
                    print "-"*80

    def get_spearmanr(self, x):
        """ Get spearmanr correlation """
        # ranking_input will be [{"query":Happy-Temple_Bangkok, "lambda": 0.1, "extreme_positive_cos_sim:": 0.58 } * 20]
        computed_rankings = []
        reranked_rankings = []

        if self.cosine_flag and "cosine_ranking" in x:
            for attraction_dict in x["cosine_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                #original_rankings.append(attraction_dict["original_ranking"])

        if self.dot_flag and "dot_ranking" in x:
            for attraction_dict in x["dot_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                #original_rankings.append(attraction_dict["original_ranking"])

        spearmanr = scipy.stats.spearmanr(computed_rankings, reranked_rankings).correlation
        print "Spearmanr:", spearmanr
        return spearmanr

    def get_kendalltau(self, x):
        """ get kendalltau correlation """
        computed_rankings = []
        reranked_rankings = []

        if self.cosine_flag and "cosine_ranking" in x:
            for attraction_dict in x["cosine_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                #original_rankings.append(attraction_dict["original_ranking"])

        if self.dot_flag and "dot_ranking" in x:
            for attraction_dict in x["dot_ranking"]:
                computed_rankings.append(attraction_dict["computed_ranking"])
                reranked_rankings.append(attraction_dict["reranked_ranking"])
                #original_rankings.append(attraction_dict["original_ranking"])

        kendalltau = scipy.stats.kendalltau(computed_rankings, reranked_rankings).correlation
        print "kendalltau:", kendalltau
        return kendalltau

    def get_ndcg_list(self, ranking_dict_list):
        """ get g """

        computed_rankings_list = []
        reranked_rankings_list = []

        for ranking_dict in ranking_dict_list:
            computed_rankings = []
            reranked_rankings = []

            try:
                if "cosine_ranking" in ranking_dict:
                    for x in ranking_dict["cosine_ranking"]:
                        computed_rankings.append(x["computed_ranking"])
                        reranked_rankings.append(x["reranked_ranking"])
            except:
                pass

            try:
                if "dot_ranking" in ranking_dict:
                    for x in ranking_dict["dot_ranking"]:
                        computed_rankings.append(x["computed_ranking"])
                        reranked_rankings.append(x["reranked_ranking"])
            except:
                pass

            computed_rankings_list.append(computed_rankings)
            reranked_rankings_list.append(reranked_rankings)

        ndcg_list = []
        for computed_rankings, reranked_rankings in zip(computed_rankings_list, reranked_rankings_list):
            g = []
            for i, j in zip(computed_rankings, reranked_rankings):
                if int(j)-1 <= int(i) <= int(j)+1:
                    g.append(3)
                elif int(j)-2 <= int(i) <= int(j)+2:
                    g.append(2)
                elif int(j)-3 <= int(i) <= int(j)+3:
                    g.append(1)
                else:
                    g.append(0)
            ndcg_list.append(self.get_ndcg(g))

        #print ndcg_list
        return ndcg_list

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

    def plot_cosine(self, ranking_dict_list,spearmanr_list, kendalltau_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs(self.dst_g, filename, "cosine")

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Lambda")
        plt.ylabel("Spearmanr & Kendalltau")

        for ranking_dict, spearmanr_score, kendalltau_score in zip( ranking_dict_list, spearmanr_list, kendalltau_list):
            l = ranking_dict["lambda"]
            try:
                line1, = plt.plot( l, spearmanr_score, 'bo', label='Spearmanr')
                line2, = plt.plot( l, kendalltau_score, 'go', label='Kendalltau')

                plt.text( l+0.001, spearmanr_score+0.001, str(spearmanr_score), fontsize=8)
                plt.text( l+0.001, kendalltau_score+0.001, str(kendalltau_score), fontsize=8)
            except:
                print 'Error'
                self.PrintException()

        # set legend # aka indicator
        plt.legend(handles = [line1, line2], loc='best', numpoints=1)
        plt.title(filename)

        if self.cosine_flag:
            print "-"*80
            print "Saving", "\033[1m" + filename + ".png" + "\033[0m", "to", self.dst_g + filename + "/cosine/"
            fig.savefig(self.dst_g + filename + "/cosine/" + filename + ".png")
        else:
            pass

    def plot_dot(self, ranking_dict_list,spearmanr_list, kendalltau_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs(self.dst_g, filename, "dot")

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Lambda")
        plt.ylabel("Spearmanr & Kendalltau")

        for ranking_dict, spearmanr_score, kendalltau_score in zip( ranking_dict_list, spearmanr_list, kendalltau_list):
            l = ranking_dict["lambda"]
            try:
                line1, = plt.plot( l, spearmanr_score, 'bo', label='Spearmanr')
                #print type(line1)
                line2, = plt.plot( l, kendalltau_score, 'go', label='Kendalltau')

                plt.text( l+0.001, spearmanr_score+0.001, str(spearmanr_score), fontsize=8)
                plt.text( l+0.001, kendalltau_score+0.001, str(kendalltau_score), fontsize=8)
            except:
                print 'Error'
                self.PrintException()

        # set legend # aka indicator
        plt.legend(handles = [line1, line2], loc='best', numpoints=1)
        plt.title(filename)

        if self.dot_flag:
            print "-"*80
            print "Saving", "\033[1m" + filename + ".png" + "\033[0m", "to", self.dst_g + filename + "/dot/"
            fig.savefig(self.dst_g + filename + "/dot/" + filename + ".png")
            # plt.show()
        else:
            pass

    def render_cosine(self, ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs(self.dst, filename, "cosine")

        ordered_ranking_dict_list = []
        for ranking_dict, spearmanr, kendalltau, ndcg in zip(ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list):
            ordered_dict = OrderedDict()
            ordered_dict["lambda"] = ranking_dict["lambda"]
            ordered_dict["window_size"] = self.window_size
            ordered_dict["min_count"] = self.min_count
            ordered_dict["spearmanr"] = spearmanr
            ordered_dict["kendalltau"] = kendalltau
            ordered_dict["ndcg@5"] = ndcg[4]
            ordered_dict["ndcg@10"] = ndcg[9]
            ordered_dict["ndcg"] = NoIndent(ndcg)

            ordered_ranking_dict_list.append(ordered_dict)

        if self.cosine_flag:
            print "Saving", "\033[1m" + filename + ".json" + "\033[0m", "to", self.dst + filename + "/cosine/"
            with open(self.dst + filename + "/cosine/" + filename + ".json", "w") as f:
                f.write(json.dumps(ordered_ranking_dict_list, indent = 4, cls=NoIndentEncoder))
            print "-"*80
        else:
            pass

    def render_dot(self, ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in dot_source """

        self.create_dirs(self.dst, filename, "dot")

        ordered_ranking_dict_list = []
        for ranking_dict, spearmanr, kendalltau, ndcg in zip(ranking_dict_list, spearmanr_list, kendalltau_list, ndcg_list):
            ordered_dict = OrderedDict()
            ordered_dict["lambda"] = ranking_dict["lambda"]
            ordered_dict["window_size"] = self.window_size
            ordered_dict["min_count"] = self.min_count
            ordered_dict["spearmanr"] = spearmanr
            ordered_dict["kendalltau"] = kendalltau
            ordered_dict["ndcg@5"] = ndcg[4]
            ordered_dict["ndcg@10"] = ndcg[9]
            ordered_dict["ndcg"] = NoIndent(ndcg)

            ordered_ranking_dict_list.append(ordered_dict)

        if self.cosine_flag:
            print "Saving", "\033[1m" + filename + ".json" + "\033[0m", "to", self.dst + filename + "/dot/"
            with open(self.dst + filename + "/dot/" + filename + ".json", "w") as f:
                f.write(json.dumps(ordered_ranking_dict_list, indent = 4, cls=NoIndentEncoder))
            print "-"*80
        else:
            pass



    def run(self):
        """ plot cosine ranking and dot ranking according to the given flags """
        if self.cosine_flag:
            self.get_cosine_ranking()
        if self.dot_flag:
            self.get_dot_ranking()

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

