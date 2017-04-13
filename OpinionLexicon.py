import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import opinion_lexicon

class MakeLexicon:
    """ This program aims to
    (1) extract useful information out of the raw lexicon
    (2) render lexicon.json with positive words and negative words
    """

    def __init__(self):
        self.dst = "./data/lexicon/opinion_lexicon.json"
        self.lexicon = []
        self.stemmer = SnowballStemmer("english")

        self.verbose = 1

    def get_positive_words(self):
        """ return a list of positive_words """

        print "Getting positive_words"
        positive_words = opinion_lexicon.positive()
        return positive_words

    def get_negative_words(self):
        """ return a list of positive_words """

        print "Getting negative_words"
        negative_words = opinion_lexicon.negative()
        return negative_words

    def get_lexicon(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """

        print "Making lexicon from nltk opinion_lexicon"
        # a list of word_dicts
        positive_words = self.get_positive_words()
        positive_words = sorted(positive_words)
        print "Numbers of words in positve: " + "\033[1m" + str(len(positive_words)) +"\033[0m"

        negative_words = self.get_negative_words()
        negative_words = sorted(negative_words)
        print "Numbers of words in negative: " + "\033[1m" + str(len(negative_words)) +"\033[0m"

        print "-"*70

        return positive_words, negative_words

    def stem(self, input_lexicon):
        """ perform stemming on input_lexicon | input_lexicon is a list"""
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

    def render(self):
        """ put keys in order and render json file """

        positive, negative = self.get_lexicon()
        positive = self.stem(positive)
        negative = self.stem(negative)
        print "-"*70

        print "Merging positive"
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

        print "\nMerging negative"
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
        f = open(self.dst, 'w+')
        f.write(json.dumps(sentiment_ordered_dict, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*70
        print "Done"

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
    Makelexicon = MakeLexicon()
    Makelexicon.render()
