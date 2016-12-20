import matplotlib, json, os, sys, linecache
import matplotlib.pyplot as plt
import numpy as np

class Plot:
    """ This program take vectors2 as input and draw them by matplotlib """
    def __init__(self):
        self.input = "bangkok.json"
        self.dst_o = "data/graphic_output/"

        self.src_v2 = "data/vectors2/"
        self.src_ss = "data/line/enhanced_lexicon.json"
        self.src_fr = "data/frontend_reviews/"

        self.json_data = []
        self.unique_words = []
        self.vectors2 = []
        self.sentiment_statistics = []
        self.attraction_name_list = []

    def get_json_data(self):
        """ get json """
        print self.src_v2 + "\033[1m" + self.input + "\033[0m"
        with open(self.src_v2+self.input) as f:
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

    def get_sentiment_statistics(self):
        """ Get sentiment_statistics """
        with open(self.src_ss) as f:
            self.sentiment_statistics = json.load(f)

        self.sentiment_statistics = self.sentiment_statistics[:150]
        #print self.sentiment_statistics

    def get_attraction_names(self):
        """ load all reviews in data/frontend_reviews/ and store attraction_name to a list """
        attractions = []
        for dirpath, dir_list, file_list in os.walk(self.src_fr):

            file_cnt = 0
            length = len(file_list)
            for f in file_list:
                file_cnt += 1
                #print "Merging " + str(dirpath) + str(f) + " into attractions"
                with open(dirpath+f) as file:
                    attractions.append(file.read())

                sys.stdout.write("\rStatus: %s / %s"%(file_cnt, length))
                sys.stdout.flush()

        print "\nExtracting attraction_names"
        length = len(attractions)
        attraction_cnt = 0
        for attraction in attractions:
            attraction = eval(attraction)
            attraction_cnt += 1
            attraction_name = attraction["attraction_name"] + "_" + attraction["location"]
            attraction_name = attraction_name.lower()
            self.attraction_name_list.append(attraction_name)

            sys.stdout.write("\rStatus: %s / %s"%(attraction_cnt, length))
            sys.stdout.flush()

        print ""
        #print attraction_name

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
        self.get_sentiment_statistics()
        self.get_attraction_names()

        self.create_dirs()

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig, ax = plt.subplots()
        #ax.set_xlim( -2.0, 1.1)
        #ax.set_ylim( -1.5, 1.5)
        ss_cnt = 0
        ss_length = len(self.sentiment_statistics)

        print "Matching and drawing"

        uw_length = len(self.unique_words)
        for i in xrange(len(self.unique_words)):
            for j in xrange(len(self.sentiment_statistics)):

                if self.unique_words[i] == self.sentiment_statistics[j]["stemmed_word"]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'bo')
                        # instead of printing stemmed word, print unstemmed word
                        plt.text( (self.vectors2[i][0])+0.002, (self.vectors2[i][1])+0.002, self.sentiment_statistics[j]["word"][0], fontsize=8)
                    except:
                        print 'Error word:', word_dict["stemmed_word"]
                        self.PrintException()

            for k in xrange(len(self.attraction_name_list)):
                if self.unique_words[i] == self.attraction_name_list[k]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'go')
                        plt.text( self.vectors2[i][0]+0.002, self.vectors2[i][1]+0.002, self.unique_words[i], fontsize=8)
                    except:
                        print 'Error word:', self.unique_words[i]
                        self.PrintException()

                sys.stdout.write("\rStatus: %s / %s"%(i+1, uw_length))
                sys.stdout.flush()

        ax.set_title('2D Distribution on: ' + self.input[:-4])
        print "\n" + "-"*80
        filename = self.input[:-5] + ".png"
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

