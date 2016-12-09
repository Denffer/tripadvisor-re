import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter

class MakeLexicon:
    """ This program aims to
    (1) extract overlapped sentiment_words
    (2) render enhanced_lexicon.json with positive words and negative words
    """

    def __init__(self):
        self.src = "data/distance/All_Stars/"
        self.dst = "data/lexicon/enhanced_lexicon.json"
        self.source = {}
        self.lexicon = []

        self.verbose = 1

    def get_source(self):
        """ return star_1 to star_5 json data """

        for i in range(1, 6):
            file_path = self.src + "star_" + str(i) + ".json"
            print "Loading data from", file_path
            json_data = json.load(open(file_path))
            self.source.update({str(i):json_data})

    def get_positive(self):
        """ return a list of positive {2: word_dict} """

        print "Getting positive_words"
        positive = []
        for key in self.source:
            for word_dict in self.source[key]["positive_topN_cosine_similarity"]:
                #  print {key:word_dict}
                positive.append({str(key):word_dict})

        #print positive
        return positive

    def get_negative(self):
        """ return a list of negative {1: word_dict} """

        negative = []
        for key in self.source:
            for word_dict in self.source[key]["negative_topN_cosine_similarity"]:
                negative.append({key:word_dict})

        #print negative
        return negative

    def get_lexicon(self):
        """ (1) find positve overlap for star_3 & star_4 & star_5 (2) find negative overlap for star_1 & star_2 & star_3 (3) append to lexicon """

        print "Collecting positive words from star_3 & star_4 & star_5"
        # a list of word_dicts
        positive = self.get_positive()
        #print positive
        filtered_positive = []
        for i in range(3,6):
            for word_dict in positive:
                if word_dict.get(str(i)):
                    try:
                        word_dict = word_dict.get(str(i))
                        del word_dict['index']
                        #  print word_dict
                    except KeyError:
                        pass
                    filtered_positive.append(word_dict)
        #  print filtered_positive

        print "Numbers of words in filtered_positive: " + "\033[1m" + str(len(filtered_positive)) +"\033[0m"
        print "Removing overlaps in filtered_positive"
        processed_positive = []
        for i in xrange(len(filtered_positive)):
            if filtered_positive[i] not in filtered_positive[i+1:]:
                processed_positive.append(filtered_positive[i])
        #  print processed_positive

        print "-"*40
        print "Collecting negative words from star_1 & star_2 & star_3"
        # a list of word_dicts
        negative = self.get_negative()
        #  print negative
        filtered_negative = []
        for i in range(1,4):
            for word_dict in negative:
                if word_dict.get(str(i)):
                    try:
                        word_dict = word_dict.get(str(i))
                        del word_dict['index']
                        #  print word_dict
                    except KeyError:
                        pass
                    filtered_negative.append(word_dict)

        print "Numbers of words in filtered_negative: " + "\033[1m" + str(len(filtered_negative)) +"\033[0m"
        print "Removing overlaps in filtered_negative"
        processed_negative = []
        for i in xrange(len(filtered_negative)):
            if filtered_negative[i] not in filtered_negative[i+1:]:
                processed_negative.append(filtered_negative[i])
        #  print processed_negative

        return processed_positive, processed_negative

    def render(self):
        """ put keys in order and render json file """

        self.get_source()
        print "-"*70
        positive, negative = self.get_lexicon()
        print "-"*70

        print "Merging positive"
        cnt = 0
        length = len(positive)
        positive_ordered_dict_list = []
        for word_dict in positive:
            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["count"] = word_dict["count"]
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
            ordered_dict["count"] = word_dict["count"]
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
