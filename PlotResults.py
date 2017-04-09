import os, json, re, sys, matplotlib
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np

class ToExcel:
    """ This program aims to
        (1) take data/results/location as input
        (2) render into data/graphic_output/
    """

    def __init__(self):
        self.src = "data/results/"
        self.dst_name = "Reranked_NDCG5_Results.xlsx"
        self.dst_dir = "data/graphic_output/"
        self.locations_ndcg5 = []
        self.locations_ndcg10 = []
        self.locations_ndcg20 = []

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
                        location_name = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+).json", f).group(1)
                        with open(dirpath +"/"+ f) as file:
                            json_data = json.load(file)
                            # ndcg5
                            b1_list, b2_list, avg_list, cXnf_list, zXnf_list = self.get_ndcg5(json_data)
                            self.locations_ndcg5.append({'location_name':location_name, 'b1_list': b1_list, 'b2_list': b2_list,
                                'avg_list': avg_list, 'zXnf_list': zXnf_list, 'cXnf_list': cXnf_list
                                })
                            # ndcg10
                            b1_list, b2_list, avg_list, cXnf_list, zXnf_list = self.get_ndcg10(json_data)
                            self.locations_ndcg10.append({'location_name':location_name, 'b1_list': b1_list, 'b2_list': b2_list,
                                'avg_list': avg_list, 'zXnf_list': zXnf_list, 'cXnf_list': cXnf_list
                                })
                            # ndcg20
                            b1_list, b2_list, avg_list, cXnf_list, zXnf_list = self.get_ndcg20(json_data)
                            self.locations_ndcg20.append({'location_name':location_name, 'b1_list': b1_list, 'b2_list': b2_list,
                                'avg_list': avg_list, 'zXnf_list': zXnf_list, 'cXnf_list': cXnf_list
                                })

            else:
                print "No file is found"
        print "-"*80

    def get_ndcg5(self, json_data):
        """ proces input json data dict->list """

        b1_list = [json_data["b1_ndcg@5"], json_data["b1_ndcg@5"], json_data["b1_ndcg@5"], json_data["b1_ndcg@5"], json_data["b1_ndcg@5"], json_data["b1_ndcg@5"]]
        b2_list = [json_data["b2_ndcg@5"], json_data["b2_ndcg@5"], json_data["b2_ndcg@5"], json_data["b2_ndcg@5"], json_data["b2_ndcg@5"], json_data["b2_ndcg@5"]]
        avg_list = [
                json_data["top3_avg_ndcg@5"],
                json_data["top5_avg_ndcg@5"],
                json_data["top20_avg_ndcg@5"],
                json_data["top50_avg_ndcg@5"],
                json_data["top100_avg_ndcg@5"],
                json_data["top_all_avg_ndcg@5"]
            ]
        cXnf_list = [
                json_data["top3_sum_cXnf_ndcg@5"],
                json_data["top5_sum_cXnf_ndcg@5"],
                json_data["top20_sum_cXnf_ndcg@5"],
                json_data["top50_sum_cXnf_ndcg@5"],
                json_data["top100_sum_cXnf_ndcg@5"],
                json_data["top_all_sum_cXnf_ndcg@5"]
            ]
        zXnf_list = [
                json_data["top3_sum_zXnf_ndcg@5"],
                json_data["top5_sum_zXnf_ndcg@5"],
                json_data["top20_sum_zXnf_ndcg@5"],
                json_data["top50_sum_zXnf_ndcg@5"],
                json_data["top100_sum_zXnf_ndcg@5"],
                json_data["top_all_sum_zXnf_ndcg@5"]
            ]

        return b1_list, b2_list, avg_list, cXnf_list, zXnf_list

    def get_ndcg10(self, json_data):
        """ proces input json data dict->list """

        b1_list = [json_data["b1_ndcg@10"], json_data["b1_ndcg@10"], json_data["b1_ndcg@10"], json_data["b1_ndcg@10"], json_data["b1_ndcg@10"], json_data["b1_ndcg@10"]]
        b2_list = [json_data["b2_ndcg@10"], json_data["b2_ndcg@10"], json_data["b2_ndcg@10"], json_data["b2_ndcg@10"], json_data["b2_ndcg@10"], json_data["b2_ndcg@10"]]
        avg_list = [
                json_data["top3_avg_ndcg@10"],
                json_data["top5_avg_ndcg@10"],
                json_data["top20_avg_ndcg@10"],
                json_data["top50_avg_ndcg@10"],
                json_data["top100_avg_ndcg@10"],
                json_data["top_all_avg_ndcg@10"]
            ]
        cXnf_list = [
                json_data["top3_sum_cXnf_ndcg@10"],
                json_data["top5_sum_cXnf_ndcg@10"],
                json_data["top20_sum_cXnf_ndcg@10"],
                json_data["top50_sum_cXnf_ndcg@10"],
                json_data["top100_sum_cXnf_ndcg@10"],
                json_data["top_all_sum_cXnf_ndcg@10"]
            ]
        zXnf_list = [
                json_data["top3_sum_zXnf_ndcg@10"],
                json_data["top5_sum_zXnf_ndcg@10"],
                json_data["top20_sum_zXnf_ndcg@10"],
                json_data["top50_sum_zXnf_ndcg@10"],
                json_data["top100_sum_zXnf_ndcg@10"],
                json_data["top_all_sum_zXnf_ndcg@10"]
            ]

        return b1_list, b2_list, avg_list, cXnf_list, zXnf_list

    def get_ndcg20(self, json_data):
        """ proces input json data dict->list """

        b1_list = [json_data["b1_ndcg@20"], json_data["b1_ndcg@20"], json_data["b1_ndcg@20"], json_data["b1_ndcg@20"], json_data["b1_ndcg@20"], json_data["b1_ndcg@20"]]
        b2_list = [json_data["b2_ndcg@20"], json_data["b2_ndcg@20"], json_data["b2_ndcg@20"], json_data["b2_ndcg@20"], json_data["b2_ndcg@20"], json_data["b2_ndcg@20"]]
        avg_list = [
                json_data["top3_avg_ndcg@20"],
                json_data["top5_avg_ndcg@20"],
                json_data["top20_avg_ndcg@20"],
                json_data["top50_avg_ndcg@20"],
                json_data["top100_avg_ndcg@20"],
                json_data["top_all_avg_ndcg@20"]
            ]
        cXnf_list = [
                json_data["top3_sum_cXnf_ndcg@20"],
                json_data["top5_sum_cXnf_ndcg@20"],
                json_data["top20_sum_cXnf_ndcg@20"],
                json_data["top50_sum_cXnf_ndcg@20"],
                json_data["top100_sum_cXnf_ndcg@20"],
                json_data["top_all_sum_cXnf_ndcg@20"]
            ]
        zXnf_list = [
                json_data["top3_sum_zXnf_ndcg@20"],
                json_data["top5_sum_zXnf_ndcg@20"],
                json_data["top20_sum_zXnf_ndcg@20"],
                json_data["top50_sum_zXnf_ndcg@20"],
                json_data["top100_sum_zXnf_ndcg@20"],
                json_data["top_all_sum_zXnf_ndcg@20"]
            ]

        return b1_list, b2_list, avg_list, cXnf_list, zXnf_list

    def get_average(self, locations):
        """ get average ndcg for all """
        # get avg b1_list # suppose to add up 25 and divide by 25
        sum_b1_list = np.zeros(6)
        for location in locations:
            sum_b1_list += np.asarray(location["b1_list"])
        avg_b1_list = sum_b1_list/len(locations)

        sum_b2_list = np.zeros(6)
        for location in locations:
            sum_b2_list += np.asarray(location["b2_list"])
        avg_b2_list = sum_b2_list/len(locations)

        sum_avg_list = np.zeros(6)
        for location in locations:
            sum_avg_list += np.asarray(location["avg_list"])
        avg_avg_list = sum_avg_list/len(locations)

        sum_cXnf_list = np.zeros(6)
        for location in locations:
            sum_cXnf_list += np.asarray(location["cXnf_list"])
        avg_cXnf_list = sum_cXnf_list/len(locations)

        sum_zXnf_list = np.zeros(6)
        for location in locations:
            sum_zXnf_list += np.asarray(location["zXnf_list"])
        avg_zXnf_list = sum_zXnf_list/len(locations)


        return {"avg_b1_list": avg_b1_list, "avg_b2_list": avg_b2_list,
                "avg_avg_list": avg_avg_list, "avg_cXnf_list": avg_cXnf_list, "avg_zXnf_list": avg_zXnf_list}

    def plot_ndcg(self, locations_ndcg5_avg, at_N):
        """ Draw | TopN as x-axis | NDCG Value as y-axis """

        self.create_dir()

        print "Plotting ndcg" + str(at_N) + "..."
        fig = plt.figure()
        matplotlib.rcParams['axes.unicode_minus'] = False

        xs = [3, 5, 20, 50, 100, 150]
        plt.xlabel("TopN")
        plt.ylabel("Average NDCG@" + str(at_N) + " Value")
        #plt.ylim([0, 1.1])
        line1 = plt.plot( xs, locations_ndcg5_avg["avg_b1_list"], 'bo-', label='Baseline1')
        line2 = plt.plot( xs, locations_ndcg5_avg["avg_b2_list"], 'go-', label='Baseline2')
        line3 = plt.plot( xs, locations_ndcg5_avg["avg_avg_list"], 'ro-', label='Avg')
        line4 = plt.plot( xs, locations_ndcg5_avg["avg_cXnf_list"], 'yo-', label='Sum_cXnf')
        line5 = plt.plot( xs, locations_ndcg5_avg["avg_zXnf_list"], 'mo-', label='Sum_zXnf')
            #plt.text( x+0.001, y1+0.001, "(" + "%.3f"%x + ", " +  "%.3f"%y1 + ")", fontsize=8)

        # set legend # aka indicator
        plt.legend(handles = [line1[0], line2[0], line3[0], line4[0], line5[0]], loc='best', numpoints=1)
        #plt.title(location["location_name"])

        print "Saving", "\033[1m" + "Avg_ndcg" + str(at_N) + ".png" + "\033[0m", "to", self.dst_dir
        fig.savefig(self.dst_dir + "AVG_ndcg" + str(at_N) + ".png")
        fig.show()

    def create_dir(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_dir)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def run(self):
        self.get_source()
        # return a dictionary
        self.locations_ndcg5_avg = self.get_average(self.locations_ndcg5)
        self.plot_ndcg(self.locations_ndcg5_avg, 5)
        self.locations_avg_ndcg10 = self.get_average(self.locations_ndcg10)
        self.plot_ndcg(self.locations_avg_ndcg10, 10)
        self.locations_avg_ndcg20 = self.get_average(self.locations_ndcg20)
        self.plot_ndcg(self.locations_avg_ndcg20, 20)

        print "Done"

if __name__ == '__main__':
    website = ToExcel()
    website.run()

