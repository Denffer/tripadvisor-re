import os, json, re, sys, matplotlib
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt

class DistanceAnalysis:
    """ This program aims to
        (1) take data/distance/location as input
        (2) calculate S(p)=\sum_{i=1}^n p_{s_i}-mean(p_s)/std(p_s) * p_{s_i}
        (3) render into data/distance_analysis/
    """

    def __init__(self):
        self.src = sys.argv[1]
        self.topN = sys.argv[2]
        self.dst = "data/distance_analysis/"
        self.locations = []

    def walk_into_source(self):
        """ load data from data/distance/ """
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                attractions = []
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + "/" +f)
                    else:
                        print "Appending " + "\033[1m" + str(f) + "\033[0m" + " into json_data" + "\n" + "-"*50
                        location_name = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-Threshold", f).group(1)

                        with open(dirpath +"/"+ f) as file:
                            json_data = json.load(file)
                            attraction_ranking_list, attraction_name_list, reranked_score_list, attraction_distances_list, location_list = self.process_json_data(json_data)

                            var_list, std_list, total_frequency_list = self.run_analysis(attraction_distances_list)
                            #normalized_avg_z_score_list = self.normalize(avg_z_score_list)

                            for i in xrange(len(attraction_ranking_list)):
                                attractions.append({
                                    'attraction_ranking': attraction_ranking_list[i],
                                    'attraction_name': attraction_name_list[i],
                                    'location': location_list[i],
                                    'cosine_variance': var_list[i],
                                    'total_frequency': total_frequency_list[i],
                                    'reranked_score': reranked_score_list[i],
                                    'standard_deviation': std_list[i]
                                    })

                            #print location
                            self.plot(location_name, attractions)
                            self.render(location_name, attractions)
                            self.locations.append(attractions)
            else:
                print "No file is found"
                print "-"*65


    def process_json_data(self, json_data):
        """ proces input json data dict->list """

        print "Processing json data ..."
        attraction_ranking_list, attraction_name_list, reranked_score_list, attraction_distances_list = [], [], [], []
        location_list = []
        for attraction_dict in json_data:
            try:
                attraction_ranking_list.append(attraction_dict['computed_ranking'])
            except:
                print attraction_dict["query"]
            reranked_score_list.append(attraction_dict['reranked_score'])
            attraction_name_list.append(attraction_dict['query'])
            attraction_distances_list.append(attraction_dict['positive_topN_cosine_similarity'])
            location_list.append(attraction_dict['location'])

        return attraction_ranking_list, attraction_name_list, reranked_score_list, attraction_distances_list, location_list

    def normalize(self, avg_z_score_list):
        """ normalize avg_z_score_list """

        xs = avg_z_score_list
        xs = [ 2 * ( (float(x)-min(xs)) / (max(xs)-min(xs)) ) - 1 for x in xs]
        xs = [ float(x)/20 for x in xs]

        return xs

    def run_analysis(self, attraction_distances_list):
        """ run S(p)=\sum_{i=1}^n p_{s_i}-mean(p_s)/std(p_s) * p_{s_i} """

        print "Running analysis on Cosine_Similarity_dict_list ..."
        score_list, var_list, avg_z_score_list = [], [], []
        std_list = []
        total_frequency_list = []
        for attraction_distance_dict in attraction_distances_list:
            cosine_similarity_list = [x['cosine_similarity'] for x in attraction_distance_dict]
            frequency_list = [x['location_count'] for x in attraction_distance_dict]
            if self.topN == "all":
                cosine_similarity_list = cosine_similarity_list[:]
                frequency_list = frequency_list[:]
            else:
                cosine_similarity_list = cosine_similarity_list[:int(self.topN)]
                frequency_list = frequency_list[:int(self.topN)]

            # variance
            var = np.var(cosine_similarity_list)
            var_list.append(var)

            # standard deviation
            std = np.std(cosine_similarity_list)
            std_list.append(std)

            # sum frequency_list into total_frequency_list
            total_frequency_list.append(sum(frequency_list))


            #mean = np.mean(cosine_similarity_list)

            #  # score
            #  score = 0.0
            #  for cos_sim in cosine_similarity_list:
            #      score = score + ( ((cos_sim-mean)/std) * cos_sim )
            #sum([(((cos_sim-mean)/std) * cos_sim) for cos_sim in cosine_similarity_list])
            #
            #  score_list.append(score)
            #
            #  # z-score
            #  z_score = 0.0
            #  for cos_sim in cosine_similarity_list:
            #      z_score = z_score + ((cos_sim-mean)/std)
            #
            #  # print "length:", len(cosine_similarity_list)
            #  avg_z_score = z_score / len(cosine_similarity_list)
            #  avg_z_score_list.append(avg_z_score)

        #print score_list
        #return score_list, var_list, avg_z_score_list
        return var_list, std_list, total_frequency_list

    def create_render_dir(self, location_name):
        """ create the directory if not exist """
        dir1 = os.path.dirname(self.dst + "/" + location_name + "/")
        if not os.path.exists(dir1):
            print "Creating directory: " + dir1 + "/"
            os.makedirs(dir1)

    def create_plot_dir(self):
        """ create the directory if not exist """
        dir1 = os.path.dirname(self.dst)
        if not os.path.exists(dir1):
            print "Creating directory: " + dir1 + "/"
            os.makedirs(dir1)

    def plot(self, location_name, attractions):
        """ Draw | score as x-axis | var as y-axis """
        print location_name

        self.create_plot_dir()

        print "Plotting ..."
        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Reranked_Score")
        plt.ylabel("Total_Frequency")
        #plt.ylabel("Cosine Variance")
        #plt.ylabel("Cosine Variance / Avg_Z_Score")

        xs = []
        y1s = []
        y2s = []
        for attraction_dict in attractions:
            x = attraction_dict["reranked_score"]
            xs.append(x)
            y1 = attraction_dict["total_frequency"]
            y1s.append(y1)
            #  y1 = attraction_dict["cosine_variance"]
            #  y1s.append(y1)
            #y2 = attraction_dict["normalized_avg_z_score"]
            #y2s.append(y2)
            try:
                line1, = plt.plot( x, y1, 'bo', label='Total_Frequency / Reranked_score')
                #line2, = plt.plot( x, y2, 'go-', label='Avg_Z_Score / Score')
                # line2, = plt.plot( l, kendalltau2, 'gx', label='Computed_vs_Original_Kendalltau')

                plt.text( x+0.001, y1+0.001, "(" + "%.3f"%x + ", " +  "%.3f"%y1 + ")", fontsize=8)
                #plt.text( x+0.001, y2+0.001, "(" + str(x) + "," +  str(y2) + ")", fontsize=8)

            except:
                print 'Error'

        #line1, = plt.plot( xs, y1s, 'bo-', label='Cosine_Variance / Score')

        # set legend # aka indicator
        #plt.legend(handles = [line1, line2], loc='best', numpoints=1)
        plt.legend(handles = [line1], loc='best', numpoints=1)
        plt.title(location_name)

        print "Saving", "\033[1m" + location_name + "_top_" + str(self.topN) + ".png" + "\033[0m", "to", self.dst
        fig.savefig(self.dst + location_name + "_top_"+ str(self.topN) + ".png")
        #  fig.show()

    def plot_all(self):
        """ Draw | score as x-axis | var as y-axis """

        self.create_plot_dir()
        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Reranked_Score")
        plt.ylabel("Total_Frequency")
        #plt.ylabel("Standard_Deviation")
        #plt.ylabel("Cosine Variance / Avg_Z_Score")
        cmap = plt.get_cmap('jet')
        colors = cmap(np.linspace(0, 1, len(self.locations)))

        labels = []
        for attractions, color in zip(self.locations, colors):
            xs = []
            y1s = []
            y2s = []
            for attraction_dict in attractions:
                x = attraction_dict["reranked_score"]
                xs.append(x)
                y1 = attraction_dict["total_frequency"]
                y1s.append(y1)
                #y1 = attraction_dict["standard_deviation"]
                #y1s.append(y1)
                #y2 = attraction_dict["normalized_avg_z_score"]
                #y2s.append(y2)
                try:
                    #line1, = plt.plot( x, y1, 'bo', label='Standard_Deviation / Reranked_Score')
                    plt.plot( x, y1, c=color, marker='o', label=attraction_dict['location'])
                    #line2, = plt.plot( x, y2, 'go-', label='Avg_Z_Score / Score')
                    # line2, = plt.plot( l, kendalltau2, 'gx', label='Computed_vs_Original_Kendalltau')
                    #plt.legend(handles = line1, loc='best', numpoints=1)
                    #plt.text( x+0.001, y1+0.001, "(" + "%.3f"%x + "," +  "%.3f"%y1 + ")", fontsize=8)
                    #plt.text( x+0.001, y2+0.001, "(" + str(x) + "," +  str(y2) + ")", fontsize=8)

                except:
                    raise
                    print 'Error'
            #labels.append(attraction_dict['location'])
            #plt.legend(, loc='best', numpoints=1)

        #plt.legend(labels, loc='best', numpoints=1)
            #line1, = plt.plot( xs, y1s, 'bo-', label='Cosine_Variance / Score')

            # set legend # aka indicator
        #plt.legend(handles = lines, loc='best', numpoints=1)
            #plt.title(location_name)

        if self.topN == "all":
            print "Saving", "\033[1m" + "all_locations_top_" + str(self.topN) + ".png" + "\033[0m", "to", self.dst
            fig.savefig(self.dst + "all_locations_top_" +  str(self.topN) + ".png")
        else:
            print "Saving", "\033[1m" + "all_locations_top" + str(self.topN) + ".png" + "\033[0m", "to", self.dst
            fig.savefig(self.dst + "all_locations_top" +  str(self.topN) + ".png")
        #fig.show()

    def render(self, location_name, attractions):
        """ render location """

        self.create_render_dir(location_name)
        # sort location by score
        attractions = sorted(attractions, key=lambda k: k['attraction_ranking'])

        location_ordered_dict = OrderedDict()
        location_ordered_dict['location_name'] = location_name

        ordered_dict_list = []
        for attraction_dict in attractions:
            ordered_dict = OrderedDict()
            ordered_dict['attraction_ranking'] = attraction_dict['attraction_ranking']
            ordered_dict['attraction_name'] = attraction_dict['attraction_name']
            ordered_dict['cosine_variance'] = attraction_dict['cosine_variance']
            ordered_dict['reranked_score'] = attraction_dict['reranked_score']
            #ordered_dict['avg_z_score'] = attraction_dict['avg_z_score']
            #ordered_dict['avg_z_score'] = attraction_dict['avg_z_score']
            #ordered_dict['normalized_avg_z_score'] = attraction_dict['normalized_avg_z_score']
            ordered_dict_list.append(ordered_dict)

        location_ordered_dict['attractions'] = ordered_dict_list

        # Writing to data/distance_analysis/location/location_topN.json
        print "Saving", "\033[1m" + location_name + "_top_" + str(self.topN) + ".json" + "\033[0m", "to", self.dst + location_name
        f = open(self.dst + location_name + "/" + location_name + "_top_"+ str(self.topN) + ".json", "w")
        f.write(json.dumps(location_ordered_dict, indent = 4))

        print "-"*50 + "\n" + location_name + " Done" + "\n" + "-"*65

    def run(self):
        """ run the entire program """

        self.walk_into_source()
        self.plot_all()

if __name__ == '__main__':
    analysis = DistanceAnalysis()
    analysis.run()

