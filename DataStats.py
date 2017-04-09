import glob, re, sys, os, json

class DataStats:
    """ This little program helps to edit the content of the entire dataset, if needed """
    def __init__(self):
        self.src = sys.argv[1]
        self.attraction_cnt = 0
        self.location_cnt = 0
        self.total_text_length = 0
        self.total_sentiment_counts = 0
        self.total_nearest_sentiment_distance = 0
        self.total_vocab_size = 0.0

    def walk(self):
        """ load all reviews in data/frontend_reviews/ and merge them """
        corpus = []
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            corpus = []
            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + str(file_list)

                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + "/" + str(f)
                        os.remove(dirpath + "/" + f)
                    else:
                        print "Editting " + str(dirpath) + "/" + str(f)
                        with open(dirpath + "/" + f) as file:
                            first_line = file.readline()
                            #print first_line
                            vocab_size = first_line.strip("\n").strip("200").strip()
                            print vocab_size
                            #json_data = json.load(file)
                            #self.accummulate(json_data)
                            self.accummulate(vocab_size)

                print "-"*60

            else:
                print "No file is found"
                print "-"*60

    # def accummulate(self, json_data):
    def accummulate(self, vocab_size):
        """ accummulate data """

        # self.attraction_cnt += 1
        self.location_cnt += 1
        # self.total_sentiment_counts += json_data["avg_sentiment_counts"]
        # self.total_text_length += json_data["avg_word_counts"]
        # self.total_nearest_sentiment_distance += json_data["avg_nearest_sentiment_distance"]
        self.total_vocab_size += float(vocab_size)
        #location = re.search('"location": "(.*)"', text).group(1).title()
        #text = re.sub(r'"location": "(.*)"', r'"location": "' + location + '"', text)

        #return text

    def print_results(self):
        """ save and replace the original file"""
        # print "self.avg_text_length:", self.total_text_length/self.attraction_cnt
        # print "self.avg_sentiment_counts:", self.total_sentiment_counts/self.attraction_cnt
        # print "self.avg_nearest_sentiment_distance", self.total_nearest_sentiment_distance/self.attraction_cnt

        print "avg_vocab_size:", self.total_vocab_size/self.location_cnt

        #f_out = open(f, "w")
        #f_out.write(text)
        #f_out.close()

if __name__ == '__main__':
    dataStats = DataStats()
    dataStats.walk()
    dataStats.print_results()

