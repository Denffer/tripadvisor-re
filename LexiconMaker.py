import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter
from itertools import groupby
from nltk.stem.snowball import SnowballStemmer

class LexiconMaker:
    """ This program aims to
    (1) extract useful information out of the raw lexicon
    (2) render lexicon.json with only positive words
    """

    def __init__(self):
        self.src1 = "./data/lexicon/mpqa/subjclueslen1-HLTEMNLP05.tff"
        self.src2 = "./data/lexicon/bingliu/positive-words.txt"
        self.src3 = "./data/lexicon/vader/vader_sentiment_lexicon.txt"
        self.dst = "./data/lexicon/lexicon.json"

        self.stemmer = SnowballStemmer("english")
        self.verbose = 1

    def get_source1(self):
        """ append every line into source """

        print "Loading data from:", self.src1

        source = []
        cnt = 0
        length = sum(1 for line in open(self.src1))

        with open(self.src1) as f:
            for line in f:
                cnt += 1
                source.append(line)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print source
        return source

    def get_source2(self):
        """ append every line into source """

        print "-"*70
        print "Loading data from:", self.src2

        source = []
        cnt = 0
        length = sum(1 for line in open(self.src2))

        with open(self.src2) as f:
            for line in f:
                cnt += 1
                source.append(line)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print source
        return source

    def get_source3(self):
        """ append every line into source """

        print "-"*70
        print "Loading data from:", self.src3

        source = []
        cnt = 0
        length = sum(1 for line in open(self.src3))

        with open(self.src3) as f:
            for line in f:
                cnt += 1
                source.append(line)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print source
        return source

    def get_lexicon1(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """
        source = self.get_source1()

        print "\n" + "-"*70
        print "Making lexicon1 from source:", self.src1
        lexicon1 = []
        cnt = 0
        length = len(source)

        for line in source:
            cnt += 1
            word = re.search('word1=(.+?) ', line).group(1)
            polarity = re.search('priorpolarity=(.+?)', line).group(1)

            if polarity == 'p':
                lexicon1.append(word)
                if lexicon1[-1] in lexicon1[:-1]:
                    lexicon1.pop()

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        lexicon1 = sorted(lexicon1)

        print "\n" + "Numbers of words in this lexcon is: " + "\033[1m" + str(len(lexicon1)) +"\033[0m"
        #print lexicon
        return lexicon1

    def get_lexicon2(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """
        source = self.get_source2()

        print "\n" + "-"*70
        print "Making lexicon2 from source:", self.src2
        lexicon2 = []
        cnt = 0
        length = len(source)

        for word in source:
            cnt += 1
            lexicon2.append(word.strip())

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        lexicon2 = sorted(lexicon2)

        print "\n" + "Numbers of words in this lexcon is: " + "\033[1m" + str(len(lexicon2)) +"\033[0m"
        #print lexicon2
        return lexicon2

    def get_lexicon3(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """
        source = self.get_source3()

        print "\n" + "-"*70
        print "Making lexicon3 from source:", self.src3
        lexicon3 = []
        cnt = 0
        length = len(source)

        for line in source:
            cnt += 1
            """ abandon -1.9 0.53852 [-1, -2, -2, -2, -2, -3, -2, -2, -1, -2] -> ["abandon", "-1.9", "0.53852", "[-1, -2, -2, -2, -2, -3, -2, -2, -1, -2]"] """
            if line.split()[1] >= 0:
                lexicon3.append(line.split()[0])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        print "\n" + "Numbers of words in this lexcon is: " + "\033[1m" + str(len(lexicon3)) +"\033[0m"
        lexicon3 = sorted(lexicon3)

        #print lexicon3
        return lexicon3

    def get_stemmed_lexicon(self, input_lexicon):
        """ stem lexicon and return a list of {"sentiment_word": sincere, "stemmed_sentiment_word": sincer} """
        # remove duplicates
        stemmed_lexicon = sorted([self.stemmer.stem(w) for w in input_lexicon])
        lexicon = []
        for word, stemmed_word in zip(stemmed_lexicon, input_lexicon):
            word_dict = {"word": word, "stemmed_word": stemmed_word}
            lexicon.append(word_dict)

        print "Stemming and Matching sentiment words"
        processed_lexicon = []
        length1 = len(stemmed_lexicon)
        length2 = len(input_lexicon)
        w1_cnt = 0
        for w1 in stemmed_lexicon:
            w1_cnt += 1
            w2_cnt = 0
            word_list = []
            for w2 in input_lexicon:
                w2_cnt += 1
                # Check for duplicates
                if stemmed_lexicon.count(w1) > 1:
                    if w1 == self.stemmer.stem(w2):
                        word_list.append(w2)

                elif stemmed_lexicon.count(w1) == 1:
                    if w1 == self.stemmer.stem(w2):
                        word_list.append(w2)

                else:
                    self.PrintException()

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(w1_cnt, length1, w2_cnt, length2))
                    sys.stdout.flush()

            if len(word_list) > 0:
                processed_lexicon.append({"word": word_list, "stemmed_word": w1})
            else:
                processed_lexicon.append({"word": word, "stemmed_word": w1})

        # Remove duplicates
        processed_lexicon = [i for n, i in enumerate(processed_lexicon) if i not in processed_lexicon[n + 1:]]

        #print processed_lexicon
        return processed_lexicon

    def render(self):
        """ put keys in order and render json file """

        lexicon1 = self.get_lexicon1()
        lexicon2 = self.get_lexicon2()
        lexicon3 = self.get_lexicon3()

        print "-"*70
        print "Merging lexicon1 & lexicon2 & lexicon3"

        #processed_lexicon = sorted(set(lexicon1).intersection(lexicon2).intersection(lexicon3))
        lexicon1 = sorted(set(lexicon1).intersection(lexicon2))
        lexicon2 = sorted(set(lexicon2).intersection(lexicon3))
        lexicon3 = sorted(set(lexicon3).intersection(lexicon1))

        lexicon = lexicon1 + lexicon2 + lexicon3
        merged_lexicon = sorted(set(lexicon))

        processed_lexicon = self.get_stemmed_lexicon(merged_lexicon)
        #print processed_lexicon

        cnt = 0
        length = len(processed_lexicon)
        ordered_dict_list = []
        for word_dict in processed_lexicon:

            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["stemmed_word"] = word_dict["stemmed_word"]
            ordered_dict["word"] = word_dict["word"]

            ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        f = open(self.dst, 'w+')
        f.write( json.dumps(ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*80
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
