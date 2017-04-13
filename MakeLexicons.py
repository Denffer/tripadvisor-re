import json, sys, uuid, re, os
from collections import OrderedDict
from operator import itemgetter
from nltk import pos_tag
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords, opinion_lexicon

class MakeLexicons:
    """ This program aims to make 2 lexicons: 1) opinion_lexicon.json 2) pos_lexicon.json
    (1) opinion_lexicon contains positive and negative sentiment words
    (2) pos_lexicon merely contains non-polarity sentiment words as it is a content-driven lexicon by Part_of_Speech in nltk
    """

    def __init__(self):

        self.dst = "data/lexicon/"

        # pos_lexicon initialization # pos stands for Part of Speech
        self.pos_tagged_statistics = {}
        self.pos_tags = ["JJ","JJR", "JJS", "RB","VBG","VBN"]
        self.src = "data/reranked_reviews/"

        self.stemmer = SnowballStemmer("english")
        self.stopwords = set(stopwords.words('english'))

        self.verbose = 1

    def get_nltk_opinion_lexicon(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """

        print "Making opinion_lexicon from nltk opinion_lexicon"
        # a list of word_dicts
        positive_words = opinion_lexicon.positive()
        positive_words = sorted(positive_words)
        print "Numbers of positive sentiment word: " + "\033[1m" + str(len(positive_words)) +"\033[0m"

        negative_words = opinion_lexicon.negative()
        negative_words = sorted(negative_words)
        print "Numbers of negative sentiment word: " + "\033[1m" + str(len(negative_words)) +"\033[0m"

        print "-"*50
        return positive_words, negative_words

    def get_attractions(self):
        """ load all reviews in data/reranked_reviews/ and merge them """
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
            else:
                print "No file is found"

        print "Part of Speech Analysis on Reviews are Done"
        print "-"*80

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
            # a list of word tuples # [("great", "JJ"), ("tour", "NN") ...]
            word_tuple_list = pos_tag(tokenized_text)

            for word_tuple in word_tuple_list:
                # putting them into dictionary # add 1 to value if exist # add key and value if not
                if word_tuple[1] in self.pos_tags:
                    if word_tuple[0] in self.pos_tagged_statistics:
                        self.pos_tagged_statistics[word_tuple[0]] += 1
                    else:
                        self.pos_tagged_statistics[word_tuple[0]] = 1
                else:
                    pass
        #print self.pos_tagged_statistics

    def stem(self, input_lexicon):
        """ perform stemming on input_lexicon | input_lexicon should be a list """
        stemmed_lexicon = []
        for word in input_lexicon:
            stemmed_word = self.stemmer.stem(word)
            stemmed_lexicon.append({"word": word, "stemmed_word": stemmed_word})

        #print stemmed_lexicon
        stemmed_lexicon = sorted(stemmed_lexicon, key=lambda k: k['word'])

        print "Merging stemmed duplicates"
        processed_lexicon = []

        length = len(stemmed_lexicon)
        w1_cnt = 0
        for word_dict in stemmed_lexicon:
            w1_cnt += 1
            w2_cnt = 0
            word_list, negation_word_list = [], []
            for word_dict2 in stemmed_lexicon:
                w2_cnt += 1
                if word_dict["stemmed_word"] == word_dict2["stemmed_word"]:
                    word_list.append(word_dict2["word"])
                    #negation_word_list.append("not-"+word_dict2["word"])

                sys.stdout.write("\rStatus: %s / %s | %s / %s"%(w1_cnt, length, w2_cnt, length))
                sys.stdout.flush()

            processed_lexicon.append({"word": word_list, "stemmed_word": word_dict["stemmed_word"]})

        # Uniquifying dictionaries
        processed_lexicon = {word_dict['stemmed_word']:word_dict for word_dict in processed_lexicon}.values()
        # Sorting dictionaries by word
        processed_lexicon = sorted(processed_lexicon, key=lambda k: k['stemmed_word'])
	print ""
        #print processed_lexicon
        return processed_lexicon

    def render_opinion_lexicon(self):
        """ put keys in order and render json file """

        positive, negative = self.get_nltk_opinion_lexicon()
        print "Stemming positive sentiment words in opinion_lexicon"
        positive = self.stem(positive)
        print "-"*50
        print "Stemming negative sentiment words in opinion_lexicon"
        negative = self.stem(negative)
        print "-"*50

        print "Organizing positive words"
        cnt = 0
        length = len(positive)
        positive_ordered_dict_list = []
        for word_dict in positive:
            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]

            positive_ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        print "\nOrganizing negative words"
        cnt = 0
        length = len(negative)
        negative_ordered_dict_list = []
        for word_dict in negative:
            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]

            negative_ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        sentiment_ordered_dict = OrderedDict()
        sentiment_ordered_dict["positive"] = positive_ordered_dict_list
        sentiment_ordered_dict["negative"] = negative_ordered_dict_list


        print "\n" + "-"*50
        print "Saving data to: " + self.dst + "\033[1m" + "opinion_lexicon.json" + "\033[0m"
        f_out = open(self.dst + "opinion_lexicon.json", 'w+')
        f_out.write(json.dumps(sentiment_ordered_dict, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def render_pos_lexicon(self):
        """ run nltk.pos_tag to analysis the part_of_speech of every word """

        # Remove frequency less than 30
        print "Filtering out frequency lower than 30" + "\n" + "-"*50
        pos_tagged_words = [key for key in self.pos_tagged_statistics if self.pos_tagged_statistics[key] > 2 ]
        print "Stemming pos_tagged_words"
        pos_tagged_words = self.stem(pos_tagged_words)
        print "Numbers of pos_tagged sentiment word after filtering and stemming: " + "\033[1m" + str(len(pos_tagged_words)) +"\033[0m"
        print "-"*50
        #print pos_tagged_words

        #FIXME I decide to count the frequency in ReviewProcess
        #  # This will return a dictionary
        #  for key in self.pos_tagged_statistics.keys():
        #      if self.pos_tagged_statistics[key] < 10:
        #          del self.pos_tagged_statistics[key]
        #  print self.pos_tagged_statistics
        #
        #  # sort key by value # sort word by its frequency # return a list of tuples from largest to smallest
        #  sorted_statistics = sorted(self.pos_tagged_statistics.items(), key=lambda x: x[1], reverse = True)

        print "Organizing pos_tagged_words"
        cnt = 0
        length = len(pos_tagged_words)
        ordered_dict_list = []
        for word_dict in pos_tagged_words:
            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]

            ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        print "\n" + "-"*50
        print "Saving data to: " + self.dst + "\033[1m" + "pos_tagged_lexicon.json" + "\033[0m"
        f_out = open(self.dst + "pos_tagged_lexicon.json", 'w+')
        f_out.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def create_dir(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)
        print "-"*80

    def run(self):
        self.create_dir()
        print "(1) Making Opinion_Lexicon" + "\n" + "-"*80
        self.render_opinion_lexicon()
        print "(2) Making Pos_Tagged_Lexicon" + "\n" + "-"*80
        self.get_attractions()
        self.render_pos_lexicon()

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print '    Exception in ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

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
    Makelexicons = MakeLexicons()
    Makelexicons.run()
