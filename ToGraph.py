import os, json, re, sys, matplotlib
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np

class ToGraph:
    """ This program aims to
        (1) take data/results/ as input (2) render into data/graphic_output/
    """

    def __init__(self):
        self.src = "data/results/"
        self.dst_dir = "data/graphic_output/"
        self.location_names = []
        self.lineXopinion_cXnf_at5 = []
        self.lineXstar5_cXnf_at5 = []
        self.lineXstar4_cXnf_at5 = []
        self.lineXstar3_cXnf_at5 = []
        self.lineXstar2_cXnf_at5 = []
        self.lineXstar1_cXnf_at5 = []
        self.word2vecXopinion_cXnf_at5 = []
        self.baseline1_at5 = []
        self.baseline2_at5 = []

    def get_source(self):
        """ load data from data/results/ """
        for dirpath, dir_list, file_list in os.walk("data/results/"):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + "/" +f)
                    else:
                        print "Appending " + "\033[1m" + str(f) + "\033[0m" + " into source"
                        self.location_names.append(re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+).json", f).group(1))
                        with open(dirpath +"/"+ f) as file:
                            json_data = json.load(file)
                            # ndcg5
                            self.lineXopinion_cXnf_at5.append(json_data["lineXopinion_top_all_sum_cXnf_ndcg@5"])
                            self.lineXstar5_cXnf_at5.append(json_data["lineXstar5_top_all_sum_cXnf_ndcg@5"])
                            self.lineXstar4_cXnf_at5.append(json_data["lineXstar4_top_all_sum_cXnf_ndcg@5"])
                            self.lineXstar3_cXnf_at5.append(json_data["lineXstar3_top_all_sum_cXnf_ndcg@5"])
                            self.lineXstar2_cXnf_at5.append(json_data["lineXstar2_top_all_sum_cXnf_ndcg@5"])
                            self.lineXstar1_cXnf_at5.append(json_data["lineXstar1_top_all_sum_cXnf_ndcg@5"])
                            self.word2vecXopinion_cXnf_at5.append(json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@5"])
                            self.baseline1_at5.append(json_data["b1_ndcg@5"])
                            self.baseline2_at5.append(json_data["b2_ndcg@5"])
                            #  # ndcg10
                            #  self.lineXopinion_cXnf_at10.append(json_data["lineXopinion_top_all_sum_cXnf_ndcg@10"])
                            #  self.lineXstar5_cXnf_at10.append(json_data["lineXstar5_top_all_sum_cXnf_ndcg@10"])
                            #  self.lineXstar4_cXnf_at10.append(json_data["lineXstar4_top_all_sum_cXnf_ndcg@10"])
                            #  self.lineXstar3_cXnf_at10.append(json_data["lineXstar3_top_all_sum_cXnf_ndcg@10"])
                            #  self.lineXstar2_cXnf_at10.append(json_data["lineXstar2_top_all_sum_cXnf_ndcg@10"])
                            #  self.lineXstar1_cXnf_at10.append(json_data["lineXstar1_top_all_sum_cXnf_ndcg@10"])
                            #  self.word2vecXopinion_cXnf_at10.append(json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@10"])
                            #  self.baseline1_at10.append(json_data["b1_ndcg@10"])
                            #  self.baseline2_at10.append(json_data["b2_ndcg@10"])
                            #  # ndcg20
                            #  self.lineXopinion_cXnf_at20.append(json_data["lineXopinion_top_all_sum_cXnf_ndcg@20"])
                            #  self.lineXstar5_cXnf_at20.append(json_data["lineXstar5_top_all_sum_cXnf_ndcg@20"])
                            #  self.lineXstar4_cXnf_at20.append(json_data["lineXstar4_top_all_sum_cXnf_ndcg@20"])
                            #  self.lineXstar3_cXnf_at20.append(json_data["lineXstar3_top_all_sum_cXnf_ndcg@20"])
                            #  self.lineXstar2_cXnf_at20.append(json_data["lineXstar2_top_all_sum_cXnf_ndcg@20"])
                            #  self.lineXstar1_cXnf_at20.append(json_data["lineXstar1_top_all_sum_cXnf_ndcg@20"])
                            #  self.word2vecXopinion_cXnf_at20.append(json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@20"])
                            #  self.baseline1_at20.append(json_data["b1_ndcg@20"])
                            #  self.baseline2_at20.append(json_data["b2_ndcg@20"])

            else:
                print "No file is found"
        print "-"*80

    def plot_ndcg(self):
        """ Draw | TopN as x-axis | NDCG Value as y-axis """


        print "Plotting ndcg" + str(5) + "..."
        fig = plt.figure()
        matplotlib.rcParams['axes.unicode_minus'] = False

        xs = [i for i in range(1, 26)]
        plt.xlabel("Cities")
        plt.ylabel("NDCG@" + str(5) + " Value")
        #plt.ylim([0, 1.1])
        line1 = plt.plot( xs, self.lineXopinion_cXnf_at5, color='navy', ls='-', label='lineXopinion_cXnf_at5')
        line2 = plt.plot( xs, self.lineXstar5_cXnf_at5, color='green', ls='-', label='lineXstar5_cXnf_at5')
        line3 = plt.plot( xs, self.lineXstar4_cXnf_at5, color='moccasin', ls='-', label='lineXstar4_cXnf_at5')
        line4 = plt.plot( xs, self.lineXstar3_cXnf_at5, color='orchid', ls='-', label='lineXstar3_cXnf_at5')
        line5 = plt.plot( xs, self.lineXstar2_cXnf_at5, color='lawngreen', ls='-', label='lineXstar2_cXnf_at5')
        line6 = plt.plot( xs, self.lineXstar1_cXnf_at5, color='peru', ls='-', label='lineXstar1_cXnf_at5')
        line7 = plt.plot( xs, self.word2vecXopinion_cXnf_at5, color='teal', ls='-', label='word2vecXopinion_cXnf_at5')
        line8 = plt.plot( xs, self.baseline1_at5, color='red', ls='-', label='Baseline1')
        line9 = plt.plot( xs, self.baseline1_at5, color='yellow', ls='-', label='Baseline2')
        #  line3 = plt.plot( xs, locations_ndcg5_avg["avg_avg_list"], 'ro-', label='Avg')
        #  line4 = plt.plot( xs, locations_ndcg5_avg["avg_cXnf_list"], 'yo-', label='Sum_cXnf')
        #plt.text( x+0.001, y1+0.001, "(" + "%.3f"%x + ", " +  "%.3f"%y1 + ")", fontsize=8)

        # set legend # aka indicator
        plt.legend(handles = [line1[0], line2[0], line3[0], line4[0], line5[0], line6[0], line7[0], line8[0], line9[0]], loc='best', numpoints=1)
        #plt.title(location["location_name"])

        print "Saving", "\033[1m" + "ndcg" + str(5) + ".png" + "\033[0m", "to", self.dst_dir
        fig.savefig(self.dst_dir + "ndcg" + str(5) + ".png")
        fig.show()

    def create_dir(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_dir)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def run(self):
        self.get_source()
        self.create_dir()
        # return a dictionary
        self.plot_ndcg()

        print "Done"

if __name__ == '__main__':
    graph = ToGraph()
    graph.run()

