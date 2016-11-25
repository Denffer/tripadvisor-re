import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter
from itertools import groupby
from nltk.stem.snowball import SnowballStemmer

class LexiconMaker:
    """ This program aims to
    (1) extract useful information out of the raw lexicon
    (2) render lexicon.json with positive words and negative words
    """

    def __init__(self):
        self.src = "./data/lexicon/mpqa/subjclueslen1-HLTEMNLP05.tff"
        self.dst = "./data/lexicon/lexicon.json"
        self.lexicon = []

        self.stemmer = SnowballStemmer("english")
        self.verbose = 1

    def get_source(self):
        """ append every line into source """

        print "Loading data from:", self.src

        source = []
        cnt = 0
        length = sum(1 for line in open(self.src))

        with open(self.src) as f:
            for line in f:
                cnt += 1
                source.append(line)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print source
        return source

    def get_lexicon(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """
        source = self.get_source()

        print "\n" + "-"*70
        print "Making lexicon from source:", self.src
        positive = []
        negative = []

        cnt = 0
        length = len(source)
        for line in source:
            cnt += 1
            word = re.search('word1=(.+) po', line).group(1)
            strength = re.search('type=(.+)subj', line).group(1)
            polarity = re.search('priorpolarity=(.+)', line).group(1)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

            if polarity == 'positive':
                positive.append({"word": word, "strength": strength, "polarity": polarity})
                # remove repeated word
                if positive[-1] in positive[:-1]:
                    positive.pop()
                else:
                    pass
            elif polarity == 'negative':
                negative.append({"word": word, "strength": strength, "polarity": polarity})
                # remove repeated word
                if negative[-1] in negative[:-1]:
                    negative.pop()
                else:
                    pass
            else:
                pass
        # a list of word_dicts
        positive = sorted(positive)
        negative = sorted(negative)

        print "\nNumbers of words in positve: " + "\033[1m" + str(len(positive)) +"\033[0m"
        print "Numbers of words in negative: " + "\033[1m" + str(len(negative)) +"\033[0m"
        print "-"*70

        return positive, negative

    def stem(self, input_lexicon):
        """ stem lexicon and return a list of {"word": sincere, "stemmed_word": sincer, "stength": strength, "polarity": polarity} """
        stemmed_lexicon = []
        for word_dict in input_lexicon:
            stemmed_word = self.stemmer.stem(word_dict["word"])
            stemmed_lexicon.append({"word": word_dict["word"], "stemmed_word": stemmed_word, "strength": word_dict["strength"], "polarity": word_dict["polarity"]})

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

            processed_lexicon.append({"word": word_list, "stemmed_word": word_dict["stemmed_word"], "strength": word_dict["strength"], "polarity": word_dict["polarity"]})

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
            ordered_dict["strength"] = word_dict["strength"]
            ordered_dict["polarity"] = word_dict["polarity"]

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
            ordered_dict["strength"] = word_dict["strength"]
            ordered_dict["polarity"] = word_dict["polarity"]

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
    lexiconMaker = LexiconMaker()
    lexiconMaker.render()
