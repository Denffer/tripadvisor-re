import matplotlib, json, os, sys, linecache, re
import matplotlib.pyplot as plt
import numpy as np

class Plot:
    """ This program take vectors2 as input and draw them by matplotlib """
    def __init__(self):
        self.src = sys.argv[1]
        self.src_rankings = sys.argv[2]
        self.dst_o = "data/graphic_output/"
        self.src_ss = "data/lexicon/enhanced_lexicon.json"
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.json", self.src).group(1)

        self.json_data = []
        self.unique_words = []
        self.vectors2 = []
        self.positive = []
        self.attractions = []

    def get_json_data(self):
        """ get json """
        print "Loading vectors2 from " + "\033[1m" + self.src + "\033[0m"
        with open(self.src) as f:
            self.json_data = json.load(f)

    def get_unique_words(self):
        """ Get unique_words"""
        for word_dict in self.json_data:
            self.unique_words.append(word_dict["word"])
        #print self.unique_words

    def get_vectors2(self):
        """ Get vectors2 """
        for word_dict in self.json_data:
            self.vectors2.append(eval(word_dict["vector2"]))

        for vector2 in self.vectors2:
            vectos2 = [float(f) for f in vector2]
        #print self.vectors2

    def get_lexicon(self):
        """ Get sentiment_statistics """
        with open(self.src_ss) as f:
            lexicon = json.load(f)

        self.positive = lexicon["positive"]["extreme_positive"]

    def get_rankings(self):
        """ load attraction_name from data/ranking/ and store it to a list """
        self.attractions = []

        with open(self.src_rankings) as f:
            rankings = json.load(f)

        for ranking_dict in rankings["cosine_ranking"]:
            self.attractions.append({
                "attraction_name": ranking_dict["attraction_name"],
                "c": str(ranking_dict["computed_ranking"]),
                "r": str(ranking_dict["reranked_ranking"]),
                "o": str(ranking_dict["original_ranking"])
                    })

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_o)

        if not os.path.exists(dir1):
            print "Creating directory:", self.dst_o
            os.makedirs(dir1)

    def render(self):
        """ Draw matched vectors2 with unique_words and sentiment_words """

        self.get_json_data()
        self.get_unique_words()
        self.get_vectors2()
        self.get_lexicon()
        self.get_rankings()

        self.create_dirs()

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig, ax = plt.subplots()
        #ax.set_xlim( -2.0, 1.1)
        #ax.set_ylim( -1.5, 1.5)
        ss_cnt = 0
        ss_length = len(self.positive)

        print "Matching and drawing"

        uw_length = len(self.unique_words)
        for i in xrange(len(self.unique_words)):
            for j in xrange(len(self.positive)):

                if self.unique_words[i] == self.positive[j]["stemmed_word"]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'bo')
                        # instead of printing stemmed word, print unstemmed word
                        plt.text( (self.vectors2[i][0])+0.002, (self.vectors2[i][1])+0.002, self.positive[j]["word"][0], fontsize=8)
                    except:
                        print 'Error word:', word_dict["stemmed_word"]
                        self.PrintException()

            for k in xrange(len(self.attractions)):
                if self.unique_words[i] == self.attractions[k]["attraction_name"]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'go', markersize=20)
                        plt.text( self.vectors2[i][0]+0.002, self.vectors2[i][1]+0.002,
                                "c:" + self.attractions[k]["c"] + " "
                                "r:" + self.attractions[k]["r"] + " "
                                "o:" + self.attractions[k]["o"] + " "
                                + self.unique_words[i], fontsize=8)
                    except:
                        print 'Error word:', self.unique_words[i]
                        self.PrintException()

                sys.stdout.write("\rStatus: %s / %s"%(i+1, uw_length))
                sys.stdout.flush()

        ax.set_title('2D Distribution on: ' + self.filename)
        print "\n" + "-"*80
        filename = self.filename + ".png"
        print "Writing", "\033[1m" + filename + "\033[0m", "to", self.dst_o
        plt.savefig(self.dst_o + filename)
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
    plot = Plot()
    plot.render()

