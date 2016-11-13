import matplotlib, json, os, sys, linecache
import matplotlib.pyplot as plt

class Plot:
    """ This program take vectors2 as input and draw them by matplotlib """
    def __init__(self):
        self.verbose = 1
        self.dst_filename = "word distribution"
        self.dst_o = "data/output/"

        self.src_uw = "data/coreProcess/unique_words.txt"
        self.src_v2 = "data/coreProcess/vectors2.txt"
        self.src_ss = "data/coreProcess/sentiment_statistics.json"
        self.src_fr = "data/frontend_reviews/"

        self.unique_words = []
        self.vectors2 = []
        self.sentiment_statistics = []
        self.attraction_name_list = []

    def get_unique_words(self):
        """ Get unique_words"""
        with open(self.src_uw) as f:
            for line in f:
                self.unique_words.append(line.strip("\n"))
        #print self.unique_words

    def get_vectors2(self):
        """ Get vectors2 """
        with open(self.src_v2) as f:
            for line in f:
                self.vectors2.append(eval(line))
        #print self.vectors2

    def get_sentiment_statistics(self):
        """ Get sentiment_statistics """
        with open(self.src_ss) as f:
            self.sentiment_statistics = json.load(f)
        #print self.sentiment_statistics

    def get_attraction_names(self):
        """ load all reviews in data/frontend_reviews/ and store attraction_name to a list """
        attractions = []
        for dirpath, dir_list, file_list in os.walk(self.src_fr):

            file_cnt = 0
            length = len(file_list)
            for f in file_list:
                file_cnt += 1
                print "Merging " + str(dirpath) + str(f) + " into attractions"
                with open(dirpath+f) as file:
                    attractions.append(file.read())

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s\n"%(file_cnt, length))
                    sys.stdout.flush()

        print "Extracting attraction_names"
        length = len(attractions)
        attraction_cnt = 0
        for attraction in attractions:
            attraction = eval(attraction)
            attraction_cnt += 1
            attraction_name = attraction["attraction_name"] + "_" + attraction["location"]
            self.attraction_name_list.append(attraction_name)

            #print attraction_name

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_o)

        if not os.path.exists(dir1):
            print "Creating directory:", self.dst_o
            os.makedirs(dir1)

    def render(self):
        """ Draw matched vectors2 with unique_words and sentiment_words """

        self.get_unique_words()
        self.get_vectors2()
        self.get_sentiment_statistics()
        self.get_attraction_names()

        self.create_dirs()

        matplotlib.rcParams['axes.unicode_minus'] = False
        fig, ax = plt.subplots()
        #ax.set_xlim( -2.0, 1.1)
        #ax.set_ylim( -1.5, 1.5)

        print "Matching and drawing sentiment_words in unique_words"
        uw_length = len(self.unique_words)
        ss_cnt = 0
        ss_length = len(self.sentiment_statistics)
        for word_dict in self.sentiment_statistics:
            ss_cnt += 1

            for i in xrange(len(self.unique_words)):
                #print word_dict["word"]
                #print self.unique_words[i]
                if word_dict["word"] == self.unique_words[i]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'go')
                        plt.text( (self.vectors2[i][0])+0.05, (self.vectors2[i][1])+0.05, self.unique_words[i], fontsize=8)
                    except:
                        print 'Error word:', self.unique_words[i]
                        self.PrintException()

                sys.stdout.write("\rStatus: %s / %s | %s / %s"%(ss_cnt, ss_length, i+1, uw_length))
                sys.stdout.flush()

        print "\nDrawing attraction_names"
        an_cnt = 0
        an_length = len(self.attraction_name_list)
        for attraction_name in self.attraction_name_list:
            an_cnt += 1
            for i in xrange(len(self.unique_words)):
                if attraction_name == self.unique_words[i]:
                    try:
                        ax.plot( self.vectors2[i][0], self.vectors2[i][1], 'go')
                        plt.text( self.vectors2[i][0]+0.05, self.vectors2[i][1]+0.05, self.unique_words[i], fontsize=8)
                    except:
                        print 'Error word:', self.unique_words[i]
                        self.PrintException()

                sys.stdout.write("\rStatus: %s / %s | %s / %s"%(an_cnt, an_length, i+1, uw_length))
                sys.stdout.flush()

        ax.set_title('word distribution')
        print "\n" + "-"*80
        print "Writing", "\033[1m" + self.dst_filename + ".png" + "\033[0m", "to", self.dst_o
        plt.savefig('data/output/word distribution.png')

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

