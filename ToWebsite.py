import json, os, sys, uuid, re
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class ToWebsite:
    """ This program aims to
        (1) take data/frontend_reivews/ & data/vectors2/ & data/lexicon/enhanced_lexicon.json as input
        (2) insert matched unique_word in vectors2 into data/frontend_reivews/ & data/lexicon/enhanced_lexicon.json
    """

    def __init__(self):
        self.src_fr = "data/frontend_reviews/"
        self.src_vectors2 = "data/vectors2/"
        self.src_lexicon = "data/lexicon/processed_opinion_positive.json"
        self.src_computed_rankings = "data/ranking/"

        self.dst_fr = "website/data/frontend_reviews/"
        self.dst_rfr = "website/data/refined_frontend_reviews/"
        self.dst_lexicon = "website/data/lexicon/"
        self.dst_location = "website/data/locations.json"
        #self.locations = []
        self.lexicon = []

    def get_lexicon(self):
        """ load data from data/lexicon/enhanced_lexicon.json  """

        print "Loading data from: " + "\033[1m" + self.src_lexicon + "\033[0m"
        lexicon = json.load(open(self.src_lexicon))

        self.lexicon = lexicon
        print "-"*80

    def get_frontend_reviews(self):
        """ load data in data/frontend_reviews/ -> match -> insert -> save """
        for dirpath, dir_list, file_list in os.walk(self.src_fr):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                location = re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+)", file_list[0]).group(1) # E.g. New_York_City
                unique_words, vectors2 = self.get_vectors2(location)
                computed_rankings = self.get_computed_rankings(location)

                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + f)
                        break
                    else:
                        file_cnt += 1
                        #print "Loading data from " + str(dirpath) + "/" + str(f)
                        with open(dirpath +"/"+ f) as file:
                            try:
                                attraction = json.load(file)
                                # store all location to self.locations
                                # self.locations.append(attraction["attraction_name"])
                                entity_name = attraction["entity_name"].lower() + "_" + location.lower()
                                # look for attraction_al
                                attraction_index = unique_words[entity_name]
                                attraction_vector2 = vectors2[attraction_index]
                                attraction_computed_ranking = computed_rankings[attraction["entity_name"]]
                                #print attraction_computed_ranking
                                self.render_frontend(attraction, attraction_vector2, attraction_computed_ranking)
                            except:
                                print "\nError occurs on attraction. No Render"
                                raise

                new_lexicon = []
                for word_dict in self.lexicon:
                    try:
                        senti_index = unique_words[word_dict["stemmed_word"]]
                        senti_vector2 = vectors2[senti_index]
                        word_dict.update({"vector2": senti_vector2})
                        if "vector2" in word_dict:
                            new_lexicon.append(word_dict)
                    except:
                        pass
                #print new_lexicon
                self.renderLexicon(new_lexicon , attraction["location"].replace("-","_"))

            else:
                pass
                # print "No file is found"

    def get_vectors2(self, location):
        """ first call readline() to read thefirst line of vectors2 file to get vocab_size and dimension_size """

        print "Loading data from " + "\033[1m" + self.src_vectors2 + location +"\033[0m"
        f_src = open(self.src_vectors2 + location + ".json", "r")
        source = json.load(f_src)

        unique_words = {}
        vectors2 = []
        print "Building Index"
        cnt = 0
        length = len(source)
        for word_dict in source:
            cnt += 1
            # {"good":1, "attraciton":2, "Tokyo": 3}
            unique_words[word_dict["word"]] = word_dict["index"]
            vectors2.append(eval(str(word_dict["vector2"])))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()
        f_src.close()

        # normalize
        xs, ys = [], []
        for vector in vectors2:
            xs.append(float(vector[0]))
            ys.append(float(vector[1]))

        xs = [ 2 * ( (float(x)-min(xs)) / (max(xs)-min(xs)) ) - 1 for x in xs]
        xs = [ float(x)*100 for x in xs]
        ys = [ 2 * ( (float(y)-min(ys)) / (max(ys)-min(ys)) ) - 1 for y in ys]
        ys = [ float(y)*100 for y in ys]

        normalized_vectors2 = []
        for x, y in zip(xs, ys):
            normalized_vectors2.append([x,y])

        #print normalized_vectors2
        print "\n" + "-"*80
        return unique_words, normalized_vectors2

    #def normalize(self):

    def get_computed_rankings(self, location):
        """ get computed rankings from data/ranking/location/lineXopinion.json """

        print "Loading data from: " + "\033[1m" + self.src_computed_rankings + location + "/" + "line_opinion.json" +"\033[0m"
        json_data = json.load(open(self.src_computed_rankings + location + "/" + "line_opinion.json"))

        computed_rankings = {}
        for attraction_dict in json_data["Entity_Rankings"]:
            #computed_rankings[attraction_dict["attraction_name"]] = attraction_dict["computed_ranking"]
            computed_rankings[attraction_dict["entity_name"]] = attraction_dict["computed_ranking"]
        #print computed_rankings
        return computed_rankings

    def render_frontend(self, attraction, vector2, computed_ranking):
        """ insert vector2 to attractionn """

        location = attraction["location"].replace("-", "_")
        self.create_frontend_dir(location)

        if computed_ranking < 10:
            sys.stdout.write("\rSaving files to " + self.dst_fr + location + "/" + location + "_0" + str(computed_ranking) + ".json")
            sys.stdout.flush()
        else:
            sys.stdout.write("\rSaving files to " + self.dst_fr + location + "/" + location + "_" + str(computed_ranking) + ".json")
            sys.stdout.flush()

        self.create_frontend_dir(attraction["location"].replace("-","_") + "/")

        """ (1) save location_*.json in ./website/frontend_reviews """
        frontend_orderedDict = OrderedDict()
        frontend_orderedDict["location"] = attraction["location"]
        frontend_orderedDict["entity_name"] = attraction["entity_name"]
        frontend_orderedDict["vector2"] = NoIndent(vector2)
        #frontend_orderedDict["ranking_score"] = attraction["ranking_score"]
        frontend_orderedDict["computed_ranking"] = computed_ranking
        frontend_orderedDict["original_ranking"] = int(attraction["original_ranking"])
        frontend_orderedDict["reranked_ranking"] = attraction["reranked_ranking"]
        frontend_orderedDict["avg_rating"] = float(attraction["avg_rating_stars"])

        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = attraction["rating_stats"]["excellent"]
        rating_stats_dict["very_good"] = attraction["rating_stats"]["very_good"]
        rating_stats_dict["average"] = attraction["rating_stats"]["average"]
        rating_stats_dict["poor"] = attraction["rating_stats"]["poor"]
        rating_stats_dict["terrible"] = attraction["rating_stats"]["terrible"]
        frontend_orderedDict["rating_stats"] = NoIndent(rating_stats_dict)

        frontend_orderedDict["review_count"] =  attraction["review_count"]
        frontend_orderedDict["total_entity_count"] = attraction["total_entity_count"]
        frontend_orderedDict["avg_sentiment_counts"] = attraction["avg_opinion_positive_count"]
        frontend_orderedDict["avg_word_count"] = attraction["avg_word_count"]
        frontend_orderedDict["avg_nearest_opinion_sentiment_distance"] = attraction["avg_nearesti_opinion_sentiment_distance"]

        review_ordered_dict_list = []
        for review_dict in attraction["reviews"]:
            review_ordered_dict = OrderedDict()
            review_ordered_dict['index'] = review_dict["index"]
            review_ordered_dict['review'] = review_dict["review"]
            review_ordered_dict_list.append(review_ordered_dict)

        frontend_orderedDict["reviews"] = review_ordered_dict_list

        if computed_ranking < 10:
            dst = self.dst_fr + location + "/" + location + "_0" + str(computed_ranking) + ".json"
        else:
            dst = self.dst_fr + location + "/" + location + "_" + str(computed_ranking) + ".json"

        frontend_json = open(dst, "w")
        frontend_json.write(json.dumps( frontend_orderedDict, indent = 4, cls=NoIndentEncoder))
        frontend_json.close()

        #print "-"*80

    def renderLexicon(self, positive, location):
        """ put keys in order and render json file """

        self.create_lexicon_dir()
        print "\nSaving data to:", "\033[1m" + self.dst_lexicon + location + ".json" + "\033[0m"

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
            ordered_dict["vector2"] = NoIndent(word_dict["vector2"])
            positive_ordered_dict_list.append(ordered_dict)

        f = open(self.dst_lexicon + location + ".json", 'w+')
        f.write( json.dumps( positive_ordered_dict_list, indent = 4, cls=NoIndentEncoder))
        print "-"*80

    def render_locations(self):
        """ generate a list containing all location names """

        # location rank by tripadvisor
        locations = [
                "London, United Kingdom",
                "Istanbul, Turkey",
                "Marrakech, Morocco",
                "Paris, France",
                "Siem Reap, Cambodia",
                "Prague, Czech Republic",
                "Rome, Italy",
                "Hanoi, Vietnam",
                "New York City, New York",
                "Ubud, Indonesia",
                "Barcelona, Spain",
                "Lisbon, Portugal",
                "Dubai, United Arab Emirate",
                "St. Petersburg, Russia",
                "Bangkok, Thailand",
                "Amsterdam, The Netherlands",
                "Buenos Aires, Argentina",
                "Hong Kong, China",
                "Playa del Carmen, Mexico",
                "Cape Town Central, South Africa",
                "Tokyo, Japan",
                "Cusco, Peru",
                "Kathmandu, Nepal",
                "Sydney, Australia",
                "Budapest, Hungary"
                ]

        f = open(self.dst_location, "w")
        f.write(json.dumps( locations, indent = 4))
        f.close()

    def split_frontend(self):
        """ load data in website/data/frontend_reviews/location/ -> sort -> save """
        print "Starting to load: " + self.dst_fr
        for dirpath, dir_list, file_list in os.walk(self.dst_fr):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                attractions = []
                file_cnt = 0
                length = len(file_list)
                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + "/"+ str(f)
                        os.remove(dirpath + "/" + f)
                    else:
                        file_cnt += 1
                        sys.stdout.write("\rLoading data from " + str(dirpath) + "/" + str(f))
                        sys.stdout.flush()
                        with open(dirpath + "/" + f) as file:
                            try:
                                attractions.append(json.load(file))
                            except:
                                pass
                                print "Error occurs on attraction. No Render"

                print "\n" + "-"*80
                #  attractions1 = attractions[:]
                #  attractions1 = sorted(attractions1, key=lambda k: k['computed_ranking'])[:5]
                #  self.split_attraction(attractions1, "computed")
                #  attractions2 = attractions[:]
                #  attractions2 = sorted(attractions2, key=lambda k: k['reranked_ranking'])[:5]
                #  self.split_attraction(attractions2, "reranked")
                #  attractions3 = attractions[:]
                #  attractions3 = sorted(attractions3, key=lambda k: k['original_ranking'])[:5]
                #  self.split_attraction(attractions3, "original")
                attractions4 = attractions[:]
                attractions4 = sorted(attractions4, key=lambda k: k['review_count'], reverse = True)[:5]
                self.split_attraction(attractions4, "frequency")


    def split_attraction(self, attractions, ranking_type):
        """ take input attractions | split reviews | pass on to render """

        print "Processing " + "\033[1m" + ranking_type + "\033[0m"
        rank = 0
        for attraction in attractions:
            rank += 1
            review_counts = len(attraction["reviews"])

            #print type(attraction["reviews"])
            # split reviews into 10
            reviews = attraction["reviews"]
            attraction["reviews"] = [reviews[i:i+len(reviews)/10] for i in range(0, len(reviews), len(reviews)/10)]
            attraction["reviews"][-2] = attraction["reviews"][-2] + attraction["reviews"][-1]

            if len(attraction["reviews"]) == 11:
                attraction["reviews"] = attraction["reviews"][:-1]
            elif len(attraction["reviews"]) == 10:
                attraction["reviews"] = attraction["reviews"][:]
            else:
                print "Error"

            for index in xrange(1,11):
                #print attraction
                self.render_split(rank, index, ranking_type, attraction)

        print "\n" + "-"*80



    def render_split(self, rank, index, ranking_type, attraction):

        location = attraction["location"].replace("-", "_")
        self.create_refined_frontend_dir(location, ranking_type)

        if index < 10:
            sys.stdout.write("\rSaving files to" + self.dst_rfr + location + "/" + ranking_type + "/" + location + "_0" + str(rank) + "_0" + str(index)+ ".json")
            sys.stdout.flush()
        else:
            sys.stdout.write("\rSaving files to " + self.dst_rfr + location + "/" + ranking_type + "/" + location + "_0" + str(rank) + "_" + str(index)+ ".json")
            sys.stdout.flush()

        """ (1) save location_(01~05)_(01~10).json in ./website/refined_frontend_reviews/ """
        split_orderedDict = OrderedDict()
        split_orderedDict["location"] = attraction["location"]
        split_orderedDict["attraction_name"] = attraction["entity_name"]
        split_orderedDict["vector2"] = NoIndent(attraction["vector2"])
        #split_orderedDict["ranking_score"] = attraction["ranking_score"]
        split_orderedDict["computed_ranking"] = attraction["computed_ranking"]
        split_orderedDict["original_ranking"] = int(attraction["original_ranking"])
        split_orderedDict["reranked_ranking"] = attraction["reranked_ranking"]
        split_orderedDict["frequency"] = attraction["total_entity_count"]
        split_orderedDict["avg_rating"] = float(attraction["avg_rating"])

        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = attraction["rating_stats"]["excellent"]
        rating_stats_dict["very_good"] = attraction["rating_stats"]["very_good"]
        rating_stats_dict["average"] = attraction["rating_stats"]["average"]
        rating_stats_dict["poor"] = attraction["rating_stats"]["poor"]
        rating_stats_dict["terrible"] = attraction["rating_stats"]["terrible"]
        split_orderedDict["rating_stats"] = NoIndent(rating_stats_dict)

        split_orderedDict["review_with_attraction_mentioned_count"] =  attraction["review_count"]
        split_orderedDict["avg_sentiment_counts"] = attraction["avg_sentiment_counts"]
        split_orderedDict["avg_word_counts"] = attraction["avg_word_count"]
        split_orderedDict["avg_nearest_sentiment_distance"] = attraction["avg_nearest_opinion_sentiment_distance"]

        review_ordered_dict_list = []
        #print "reviews_length", len(attraction["reviews"])
        for review_dict in attraction["reviews"][int(index)-1]:
            try:
                review_ordered_dict = OrderedDict()
                review_ordered_dict['index'] = review_dict["index"]
                review_ordered_dict['review'] = review_dict["review"]
                review_ordered_dict_list.append(review_ordered_dict)
                #print len(review_dict)
                #print "dict_type", type(review_dict)
            except:
                split_json = open("data/test.json", "w")
                split_json.write(json.dumps( attraction["reviews"][index-1], indent = 4, cls=NoIndentEncoder))
                split_json.close()
                #print len(review_dict)
                #print "dict_type", type(review_dict)
                raise

        split_orderedDict["reviews"] = review_ordered_dict_list

        if index < 10:
            dst = self.dst_rfr + location + "/" + ranking_type + "/" + location + "_0" + str(rank) + "_0" + str(index)+ ".json"
        else:
            dst = self.dst_rfr + location + "/" + ranking_type + "/" + location + "_0" + str(rank) + "_" + str(index)+ ".json"

        split_json = open(dst, "w")
        split_json.write(json.dumps( split_orderedDict, indent = 4, cls=NoIndentEncoder))
        split_json.close()

    def create_frontend_dir(self, location):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_fr + location + "/")

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def create_refined_frontend_dir(self, location, ranking_type):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_rfr + location + "/" + ranking_type + "/")

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def create_lexicon_dir(self):
        """ create the directory if not exist"""
        dir2 = os.path.dirname(self.dst_lexicon)

        if not os.path.exists(dir2):
            print "Creating directory: " + dir2
            os.makedirs(dir2)

    def run(self):
        """ run the entire process """
        #self.get_lexicon()
        #self.get_frontend_reviews()
        #self.render_locations()
        self.split_frontend()

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
    website = ToWebsite()
    website.run()

