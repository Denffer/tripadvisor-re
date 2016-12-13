import matplotlib, json, os, sys, linecache, re, scipy
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerLine2D
import numpy as np
from Distance import Distance

class Evaluate:
    """ This program take vectors2 as input and draw them by matplotlib """
    def __init__(self):
        self.src = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src = "data/ranking/" + self.filename + ".json"
        self.dst = "data/graphic_output/sk/"

        self.step = 0.5
        self.json_data = []
        self.attraction_name = ""

    def get_json_data(self):
        """ get json """
        print "Loading data from " + "\033[1m" + self.src + "\033[0m"
        with open(self.src) as f:
            self.json_data = json.load(f)

    def get_sk(self):
        """ Get spearmanr & kendalltau """
        rankings = []
        original_rankings = []
        for attraction_dict in self.json_data["cosine_ranking"]:
        #for attraction_dict in self.json_data["dot_ranking"]:
            rankings.append(attraction_dict["ranking"])
            original_rankings.append(attraction_dict["original_ranking"])

        spearmanr = scipy.stats.spearmanr(rankings, original_rankings).correlation
        kendalltau = scipy.stats.kendalltau(rankings, original_rankings).correlation

        return spearmanr, kendalltau

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory:", self.dst
            os.makedirs(dir1)

    def render(self):
        """ Draw matched vectors2 with unique_words and sentiment_words """

        self.create_dirs()

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig = plt.figure()
        plt.xlabel("Lambda")
        plt.ylabel("Spearmanr & Kendalltau")
        #plt.xlabel('Lambda', fontsize=14)
        #ax.set_xlim(-0.05, 1.1)
        #ax.set_ylim(-0.05, 1.1)

        lambdas = [float(x)/2 for x in range(0, 3)]
        #lambdas = [float(x)/20 for x in range(0, 21)]

        for l in lambdas:
            distance = Distance("data/line/vectors200/" + self.filename + ".txt", l)
            distance.render()

            self.get_json_data()
            spearmanr, kendalltau = self.get_sk()
            print "S:", spearmanr
            print "K:", kendalltau

            try:
                line1, = plt.plot( l, spearmanr, 'bo', label='Spearmanr')
                line2, = plt.plot( l, kendalltau, 'go', label='Kendalltau')

                #ax.plot(l, spearmanr, 'bo', label='Spearmanr')
                #ax.plot(l, kendalltau, 'go', label='Kendalltau')
                plt.text( l+0.001, spearmanr+0.001, str(spearmanr), fontsize=8)
                plt.text( l+0.001, kendalltau+0.001, str(kendalltau), fontsize=8)
            except:
                print 'Error'
                self.PrintException()

            #sys.stdout.write("\rStatus: %s / %s"%(r,))

        # set legend # aka indicator
        # plt.legend(handles=[line1, line2], loc=2)
        plt.legend(handles = [line1, line2], loc='best', numpoints=1)
        plt.title(self.filename)
        print "-"*80
        filename = self.filename + ".png"
        print "Saving", "\033[1m" + filename + "\033[0m", "to", self.dst
        fig.savefig(self.dst + filename)
        #plt.savefig(self.dst + filename)
        plt.show()

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print '    Exception in ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

if __name__ == '__main__':
    evaluate = Evaluate()
    evaluate.render()

