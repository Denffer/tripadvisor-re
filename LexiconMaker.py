import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter
from itertools import groupby

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

        self.switch = 1

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

                if self.switch:
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

                if self.switch:
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

                if self.switch:
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

                if self.switch:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        lexicon1 = sorted(lexicon1)

        print "\n" + "Numbers of words in lexcon is:", len(lexicon1)
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

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        lexicon2 = sorted(lexicon2)

        print "\n"+ "Numbers of words in lexcon is:", len(lexicon2)
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

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        print "\n" + "Numbers of words in lexcon is:", len(lexicon3)
        lexicon3 = sorted(lexicon3)

        #print lexicon3
        return lexicon3

    def render(self):
        """ put keys in order and render json file """

        lexicon1 = self.get_lexicon1()
        lexicon2 = self.get_lexicon2()
        lexicon3 = self.get_lexicon3()

        print "-"*70
        print "Merging lexicon1 & lexicon2 & lexicon3"

        #processed_lexicon = sorted(set(lexicon1).intersection(lexicon2).intersection(lexicon3))
        tmp_lexicon1 = sorted(set(lexicon1).intersection(lexicon2))
        tmp_lexicon2 = sorted(set(lexicon2).intersection(lexicon3))
        tmp_lexicon3 = sorted(set(lexicon3).intersection(lexicon1))

        #tmp_lexicon1.extend(tmp_lexicon2)
        tmp_lexicon = tmp_lexicon1 + tmp_lexicon2 + tmp_lexicon3
        processed_lexicon = sorted(set(tmp_lexicon))

        cnt = 0
        length = len(processed_lexicon)
        ordered_dict_list = []

        print processed_lexicon
        for word in processed_lexicon:

            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["word"] = word

            ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        f = open(self.dst, 'w+')
        f.write( json.dumps(ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*70
        print "Done"

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
