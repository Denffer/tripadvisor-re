import matplotlib, json, os, sys, linecache, re
import matplotlib.pyplot as plt
import numpy as np
from Distance import Distance

class Evaluate:
    """ This program take vectors2 as input and draw them by matplotlib """
    def __init__(self):
        self.src = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src).group(1)
        self.src = "data/ranking/" + self.filename + ".json"
        self.dst = "data/graphic_output/precision/" + self.filename + "/"

        self.step = 0.5
        self.json_data = []
        self.attraction_name = ""
        self.precision = 0

    def get_json_data(self):
        """ get json """
        print "Loading data from " + "\033[1m" + self.src + "\033[0m"
        with open(self.src) as f:
            self.json_data = json.load(f)

    def get_precision(self):
        """ Get precision """
        rankings = []
        original_rankings = []
        for attraction_dict in self.json_data["dot_ranking"]:
            rankings.append(attraction_dict["ranking"])
            original_rankings.append(attraction_dict["original_ranking"])

        matched_cnt = 0
        for r1, r2 in zip(rankings, original_rankings):
            if float(r1) == float(r2):
                matched_cnt += 1

        self.precision = float(matched_cnt) / float(len(rankings))

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
        fig, ax = plt.subplots()
        ax.set_xlim(-0.05, 1.1)
        ax.set_ylim(-0.05, 1.1)

        for x in range(0,110, self.step*10):
            tuning_lambda = float(x)/10
            distance = Distance("data/line/vectors200/" + self.filename + ".txt", tuning_lambda)
            distance.render()

            self.get_json_data()
            self.get_precision()

            try:
                ax.plot(self.tuning_lambda, self.precision, 'bo')
                plt.text( (self.tuning_lambda)+0.001, (self.precision)+0.001, str(self.precision), fontsize=8)
                plt.xlabel('Lambda', fontsize=14)
                plt.ylabel('Rerank', fontsize=14)
            except:
                print 'Error'
                self.PrintException()

            sys.stdout.write("\rStatus: %s / %s"%(r,))

        ax.set_title('Rerank on: ' + self.filename)
        print "-"*80
        filename = self.filename + ".png"
        print "Saving", "\033[1m" + filename + "\033[0m", "to", self.dst
        plt.savefig(self.dst + filename)
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

