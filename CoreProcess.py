import json, sys, uuid, math, glob, scipy, os, math
import numpy as np
from scipy.spatial import distance
from json import dumps, loads, JSONEncoder, JSONDecoder
from operator import itemgetter
from collections import OrderedDict
from scipy import spatial

class CoreProcess:
    """ This program aim to
    1) Take 'unique_words.txt' & 'vectors2.txt' & 'vectors200.txt' & 'sentiment_statistics.json' & '/frontend_reviews/*.json' as inputs
    2) Calculate the score by the euclidean distance and cosine distance between the sentiment word (in 'sentimentWords.json') and every attraction (in frontend/*.json)
    3) Put in the values (x & y & vector2 & vector 200) of the words into 'sentimentWords.json' and the dishes in 'restaurant_list_*.json'
    """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_uw = "data/coreProcess/unique_words.txt"
        self.src_v2 = "data/coreProcess/vectors2.txt"
        self.src_v200 = "data/coreProcess/vectors200.txt"

        self.src_fr = "data/frontend_reviews/"
        self.src_ss = "data/coreProcess/sentiment_statistics.json"

        self.dst_p = "data/postProcess/"
        self.dst_al = "data/postProcess/attraction_list.json"
        self.dst_pss = "data/postProcess/processed_sentiment_statistics.json"

        self.unique_words = []
        self.vectors2 = []
        self.vectors200 = []
        self.sentiment_words = []
        self.attractions = []
        self.verbose = 1

    def get_unique_words(self):
        """  get a list of words from 'unique_words.txt' """
        print "Loading data from", self.src_uw

        self.unique_words = [line.rstrip('\n') for line in open(self.src_uw)]

    def get_vectors2(self):
        """  get a list of vectors in 2 dimensionv """
        print "Loading data from", self.src_v2

        self.vectors2 = [line.rstrip('\n') for line in open(self.src_v2)]

    def get_vectors200(self):
        """  get a list of vectors in 200 dimensionv """
        print "Loading data from", self.src_v200

        self.vectors200 = [line.rstrip('\n') for line in open(self.src_v200)]

    def get_sentiment_words(self):
        """  get a list of dictionary of sentiment_words """
        print "Loading data from", self.src_ss

        with open(self.src_ss) as f:
            self.sentiment_words = json.load(f)

    def get_attractions(self):
        """" return every location_*.json frontend_reviews"""

        print "Loading dat from: " + self.src_fr
        for dirpath, dir_list, file_list in os.walk(self.src_fr):

            file_cnt = 0
            length = len(file_list)
            for f in file_list:
                file_cnt += 1
                print "Appending " + str(dirpath) + str(f) + " into attractions"
                self.attractions.append(json.load(open( dirpath + "/" + f )))

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(file_cnt, length))
                    sys.stdout.flush()
        print ""

    def put_vectors(self):
        """ put vectors200 and vectors2 into every matched word in unique_words """

        print "-"*80
        print "Putting vectors2 and vectors200 into sentiment_words matched with unique_words"

        sw_length = len(self.sentiment_words)
        uw_length = len(self.unique_words)
        attraction_length = len(self.attractions)

        for i in xrange(len(self.sentiment_words)):

            # initialize value
            self.sentiment_words[i]['x'] = 0
            self.sentiment_words[i]['y'] = 0
            self.sentiment_words[i]['v200'] = [0]*200

            for j in xrange(len(self.unique_words)):
                if self.sentiment_words[i]['word'] == self.unique_words[j]:
                    self.sentiment_words[i]['x'] = json.loads(self.vectors2[j])[0]
                    self.sentiment_words[i]['y'] = json.loads(self.vectors2[j])[1]
                    self.sentiment_words[i]['v200'] = json.loads(self.vectors200[j])

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(i+1, sw_length, j+1, uw_length))
                    sys.stdout.flush()

        print "\n" + "-"*80
        print "Putting vectors2 and vectors200 into attraction_name matched with unique_words"

        attractions = self.attractions
        for i in xrange(len(self.attractions)):

            attractions[i]['x'] = 0
            attractions[i]['y'] = 0
            attractions[i]['v200'] = [0]*200

            uw_length = len(self.unique_words)
            for j in xrange(len(self.unique_words)):
                attraction_al = attractions[i]["attraction_name"] + "_" + attractions[i]["location"]
                if  attraction_al.lower() == self.unique_words[j]:
                    attractions[i]['x'] = json.loads(self.vectors2[j])[0]
                    attractions[i]['y'] = json.loads(self.vectors2[j])[1]
                    attractions[i]['v200'] = json.loads(self.vectors200[j])

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(i+1, attraction_length, j+1, uw_length))
                    sys.stdout.flush()

        self.attractions = attractions

    def put_scores(self):
        """ Calculate Euclidean Distance & Cosine Distance """
        print "\n" + "-"*80
        print "Calculating Cosine Similarity and Euclidean Distance between every dish and sentiment word"

        attraction_cnt = 0
        attraction_length = len(self.attractions)
        for attraction in self.attractions:
            attraction_cnt += 1

            attraction['cosine_avg_score'] = -2
            attraction['cosine_max_score'] = -2
            attraction['cosine_nearest'] = [{"word": None, "cosine_similarity": None}]*5
            attraction['euclidean_avg_score'] = -2
            attraction['euclidean_min_score'] = -2
            attraction['euclidean_nearest'] = [{"word": None, "euclidean_distance": None}]*5

            if attraction["v200"] != [0]*200: # Check if empty

                """ cosine similarity """
                similarity_list = []
                similarity_dict_list = []

                """ euclidean distance """
                distance_list = []
                distance_dict_list = []

                sw_cnt = 0
                sw_length = len(self.sentiment_words)
                for sentiment_word_dict in self.sentiment_words:
                    sw_cnt += 1

                    """ cosine similarity """
                    cosine_distance = spatial.distance.cosine(sentiment_word_dict["v200"], attraction["v200"])
                    cosine_similarity = 1 - cosine_distance

                    if math.isnan(cosine_similarity):
                        cosine_similarity = 0

                    similarity_list.append(cosine_similarity)
                    similarity_dict_list.append({"word": sentiment_word_dict["word"], "cosine_similarity": cosine_similarity})

                    """ euclidean distance """
                    euclidean_distance = distance.euclidean(sentiment_word_dict["v200"], attraction['v200'])
                    distance_list.append(euclidean_distance)
                    distance_dict = {"word": sentiment_word_dict["word"], "euclidean_distance": euclidean_distance}
                    distance_dict_list.append(distance_dict)

                    if self.verbose:
                        sys.stdout.write("\rStatus: %s / %s | %s / %s"%(attraction_cnt, attraction_length, sw_cnt, sw_length))
                        sys.stdout.flush()

                """ cosine similarity """
                tmp = []
                for num in similarity_list:
                    if math.isnan(num):
                        tmp.append(0)
                    else:
                        tmp.append(num)
                similarity_list = tmp

                cosine_avg_score = sum(similarity_list)/len(similarity_list)
                cosine_max_score = max(similarity_list)
                attraction["cosine_avg_score"] = cosine_avg_score
                attraction["cosine_max_score"] = cosine_max_score
                attraction["cosine_nearest"] = sorted(similarity_dict_list, key=itemgetter('cosine_similarity'))[:10]

                """ euclidean distance """
                euclidean_avg_score = 1/(sum(distance_list)/len(distance_list))
                euclidean_min_score = 1/min(distance_list)
                attraction["euclidean_avg_score"] = euclidean_avg_score
                attraction["euclidean_min_score"] = euclidean_min_score
                attraction["euclidean_nearest"] = sorted(distance_dict_list, key=itemgetter('euclidean_distance'))[:10]

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/postProcess/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)

    def render(self):
        """ customize output json file """

        self.get_attractions()
        self.get_sentiment_words()
        self.get_unique_words()
        self.get_vectors200()
        self.get_vectors2()
        self.put_vectors()
        self.put_scores()

        self.create_dirs()
        print '\n' + '-'*80
        print "Customizing attraction_list's json format"

        processed_attraction_list = []
        attraction_cnt = 0
        attraction_length = len(self.attractions)
        for attraction in self.attractions:
            attraction_cnt += 1

            attraction_ordered_dict = OrderedDict()
            attraction_ordered_dict['index'] = attraction_cnt
            attraction_ordered_dict['location'] = attraction['location']
            attraction_ordered_dict['attraction_name'] = attraction['attraction_name']
            attraction_ordered_dict['ranking'] = attraction['ranking']
            attraction_ordered_dict['avg_rating'] = attraction['avg_rating']

            rating_stats_dict = OrderedDict()
            rating_stats_dict["excellent"] = attraction["rating_stats"]["excellent"]
            rating_stats_dict["very good"] = attraction["rating_stats"]["very good"]
            rating_stats_dict["average"] = attraction["rating_stats"]["average"]
            rating_stats_dict["poor"] = attraction["rating_stats"]["poor"]
            rating_stats_dict["terrible"] = attraction["rating_stats"]["terrible"]
            attraction_ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

            attraction_ordered_dict['mentioned_count'] = attraction['mentioned_count']

            # Cosine
            attraction_ordered_dict["cosine_avg_score"] = attraction['cosine_avg_score']
            attraction_ordered_dict["cosine_max_score"] = attraction['cosine_max_score']

            cosine_nearest = []
            for distance_dict in attraction["cosine_nearest"]:
                cosine_ordered_dict = OrderedDict()
                cosine_ordered_dict["word"] = cosine_ordered_dict.get('word')
                cosine_ordered_dict["cosine_similarity"] = cosine_ordered_dict.get('cosine_similarity')
                cosine_nearest.append(cosine_ordered_dict)

            attraction_ordered_dict["cosine_nearest"] = NoIndent(cosine_nearest)

            # Euclidean
            euclidean_nearest = []
            for distance_dict in attraction["euclidean_nearest"]:
                euclidean_ordered_dict = OrderedDict()
                euclidean_ordered_dict["word"] = euclidean_ordered_dict.get('word')
                euclidean_ordered_dict["euclidean_distance"] = euclidean_ordered_dict.get('euclidean_distance')
                euclidean_nearest.append(euclidean_ordered_dict)

            attraction_ordered_dict["euclidean_nearest"] = NoIndent(euclidean_nearest)

            attraction_ordered_dict["x"] = attraction['x']
            attraction_ordered_dict["y"] = attraction['y']
            attraction_ordered_dict["v200"] = NoIndent(attraction['v200'])

            processed_attraction_list.append(attraction_ordered_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(attraction_cnt, attraction_length))
                sys.stdout.flush()

        f_al = open(self.dst_al, "w+")
        f_al.write(json.dumps(processed_attraction_list, indent = 4, cls=NoIndentEncoder))
        f_al.close()

        print '\n' + '-'*80
        print "Customizing sentiment_statistics's json format"

        sw_cnt = 0
        sw_length = len(self.sentiment_words)

        sw_ordered_dict_list = []
        for word_dict in self.sentiment_words:
            sw_cnt += 1

            sw_ordered_dict = OrderedDict()
            sw_ordered_dict['index'] = word_dict['index']
            sw_ordered_dict['word'] = word_dict['word']
            sw_ordered_dict['count'] = word_dict['count']
            sw_ordered_dict['x'] = word_dict['x']
            sw_ordered_dict['y'] = word_dict['y']
            sw_ordered_dict['v200'] = NoIndent(word_dict['v200'])
            sw_ordered_dict_list.append(sw_ordered_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sw_cnt, sw_length))
                sys.stdout.flush()

        f_ss = open(self.dst_pss, "w+")
        f_ss.write(json.dumps(sw_ordered_dict_list, indent = 4, cls=NoIndentEncoder))
        f_ss.close()

        print '\n' + '-'*80
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
    coreProcess = CoreProcess()
    coreProcess.render()
