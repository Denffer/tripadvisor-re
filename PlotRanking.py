import matplotlib, json, os, sys, linecache, re, scipy
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
import numpy as np
from Distance import Distance

class PlotRanking:
    """ This program calculate spearmanr and kendalltau """
    def __init__(self):
        # data/ranking/cosine/ or data/ranking/dot/
        self.src = "data/ranking/"
        self.dst_c = "data/graphic_output/sk/cosine/"
        self.dst_d = "data/graphic_output/sk/dot/"

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
                    ranking_dicts_list = []
                    spearmanr_list, kendalltau_list = [], []

                    for f in file_list:
                        # in case there is a goddamn .DS_Store file
                        if str(f) == ".DS_Store":
                            print "Removing " + dirpath + "/" + str(f)
                            os.remove(dirpath+ "/"+ f)
                            break
                        else:
                            file_cnt += 1
                            print "Merging " + str(dirpath) + "/" + str(f)

                            with open(dirpath +"/"+ f) as file:
                                self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                                file_data = json.loads(file.read())

                                ranking_dicts_list.append(file_data)
                                spearmanr_list.append(self.get_spearmanr(file_data))
                                kendalltau_list.append(self.get_kendalltau(file_data))

                    #  print "Ranking_dict_list: ", ranking_dicts_list
                    #  print "Spearmanr_list:", spearmanr_list
                    #  print "Kendalltau_list", kendalltau_list
                    self.plot(ranking_dicts_list, spearmanr_list, kendalltau_list, self.filename)
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
                    ranking_dicts_list = []
                    spearmanr_list, kendalltau_list = [], []
                    for f in file_list:
                        # in case there is a goddamn .DS_Store file
                        if str(f) == ".DS_Store":
                            print "Removing " + dirpath + str(f)
                            os.remove(dirpath+ "/"+ f)
                            break
                        else:
                            file_cnt += 1
                            print "Merging " + str(dirpath) + "/" + str(f)

                            with open(dirpath +"/"+ f) as file:
                                self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                                file_data = json.loads(file.read())

                                ranking_dicts_list.append(file_data)
                                spearmanr_list.append(self.get_spearmanr(file_data))
                                kendalltau_list.append(self.get_kendalltau(file_data))

                    #  print "Ranking_dict_list: ", ranking_dicts_list
                    #  print "Spearmanr_list:", spearmanr_list
                    #  print "Kendalltau_list", kendalltau_list
                    self.plot(ranking_dicts_list, spearmanr_list, kendalltau_list, self.filename)

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
        return kendalltau

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_c)
        dir2 = os.path.dirname(self.dst_d)

        if not os.path.exists(dir1):
            print "Creating directory:", dir1
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            print "Creating directory:", dir2
            os.makedirs(dir2)

    def plot(self, ranking_dicts_list,spearmanr_list, kendalltau_list, filename):
        """ Draw spearmanr and kendalltau according to lambda in cosine_source"""

        self.create_dirs()

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Lambda")
        plt.ylabel("Spearmanr & Kendalltau")
        #ax.set_xlim(-0.05, 1.1)
        #ax.set_ylim(-0.05, 1.1)

        for ranking_dicts, spearmanr_score, kendalltau_score in zip( ranking_dicts_list, spearmanr_list, kendalltau_list):
            l = ranking_dicts["lambda"]
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

        if self.cosine_flag:
            print "-"*80
            print "Saving", "\033[1m" + filename + ".png" + "\033[0m", "to", self.dst_c
            fig.savefig(self.dst_c + filename + ".png")
            plt.show()
        else:
            pass

        if self.dot_flag:
            print "-"*80
            print "Saving", "\033[1m" + filename + ".png" + "\033[0m", "to", self.dst_d
            fig.savefig(self.dst_d + filename + ".png")
            plt.show()
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

if __name__ == '__main__':
    plot = PlotRanking()
    plot.run()

