import json, os, sys, uuid, re
from nltk import pos_tag
from nltk.corpus import stopwords
from collections import OrderedDict
from operator import itemgetter

class MakeLexicon3:
    """ This program aims to rerank attraction according to their ranking_score """

    def __init__(self):
        self.src = "data/reranked_reviews/"
        self.dst = "data/sentiment_statistics2/"

        self.attractions = []
        self.pos_tags = ["JJ","RB","VBG","VBN"]
        self.statistics = {}
        self.stopwords = set(stopwords.words('english'))

    def get_attractions(self):
        """ load all reviews in data/reranked_reviews/ and merge them """
        print "Starting to load: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                #print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"
                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                        break
                    else:
                        file_cnt += 1
                        # print "Merging " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            attraction = json.load(file)

                    print "Processing " + "\033[1m" + attraction["attraction_name"] + "\033[0m" + " in " + "\033[1m" + attraction["location"] + "\033[0m"
                    self.analyze_part_of_speech(attraction["reviews"])
                    #render(attraction, reviews)

            else:
                print "No file is found"
                print "-"*80

        print "Done"

    def analyze_part_of_speech(self, reviews):
        """ run nltk.pos_tag to analysis the part_of_speech of every word """

        for review_dict in reviews:
            text = review_dict["review"].lower()
            # remove punctuation
            text = re.sub(r'[^\w\s]|\_]', ' ', text)
            # remove digits
            text = re.sub(r'[0-9]',' ', text)
            # turn multiple spaces into one
            text = re.sub(r'(\s)+', ' ', text)
            # remove extra space at both ends of the text
            text = text.strip()
            # remove stop_words
            tokenized_text = text.split(" ")
            tokenized_text = [w for w in tokenized_text if w not in self.stopwords]
            # remove empty string
            tokenized_text = [w for w in tokenized_text if w]
            #print tokenized_text
            # a list of word tuples
            word_tuple_list = pos_tag(tokenized_text)

            for word_tuple in word_tuple_list:
                # putting them into dictionary # add 1 to value if exist # add key and value if not
                if word_tuple[1] in self.pos_tags:
                    if word_tuple[0] in self.statistics:
                        self.statistics[word_tuple[0]] += 1
                    else:
                        self.statistics[word_tuple[0]] = 1
                else:
                    pass

        print self.statistics

    def render(self):
        """ run nltk.pos_tag to analysis the part_of_speech of every word """

        # sort key by value # sort word by its frequency # return a list of tuples from largest to smallest
        sorted_statistics = sorted(self.statistics.items(), key=lambda x: x[1], reverse = True)
        #print sorted_statistics

        sentiment_list = []
        index = 0
        key_num = len(sorted_statistics)
        for word_tuple in sorted_statistics:

            index += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = index
            ordered_dict["sentiment_word"] = word_tuple[0]
            ordered_dict["frequency"] = word_tuple[1]
            sentiment_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(index, key_num))
            sys.stdout.flush()

            #  """ render out new ranking as json file in data/reranked_reviews/ """
            #  if int(index) < 10:
            #      file_name = attraction["location"].replace("-", "_") + "_0" + str(index) + ".json"
            #  else:
            #      file_name = attraction["location"].replace("-", "_") + "_" + str(index) + ".json"
            #
        print "\nSaving data to: " + self.dst + "\033[1m" + "statistics.json" + "\033[0m"
        f_out = open(self.dst + "statistics.json", 'w+')
        f_out.write( json.dumps( sentiment_list, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

        print "-"*80

    def run(self):
        """ run the entire code """
        self.get_attractions()
        self.create_dirs()
        self.render()

class NoIndent(object):
    def __init__(self, value):
        self.value = value

class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in self._replacement_map.iteritems():
            result = result.replace('"@@%s@@"' % (k,), v)
        return result

if __name__ == '__main__':
    p = MakeLexicon3()
    p.run()

