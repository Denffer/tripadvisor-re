import json, os, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter

class PreProcess2:
    """ This program aims to rerank attraction according to their ranking_score """

    def __init__(self):
        self.src = "data/reviews/"
        self.dst = "data/reranked_reviews/"

    def get_attractions(self):
        """ load all reviews in data/reviews/ and merge them """
        print "Starting to load: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            attractions = []
            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

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
                            attractions.append(json.load(file))

                self.rerank(attractions)

            else:
                print "No file is found"
                print "-"*80

        print "Done"

    def rerank(self, attractions):
        """ rerank attraction according to its ranking_score """

        print "Processing: " + "\033[1m" + attractions[0]["location"] + "\033[0m"
        # rerank by score
        reranked_attractions = sorted(attractions, key=lambda k: k['ranking_score'])


        index = 0
        attraction_length = len(attractions)
        for attraction in reranked_attractions:

            index += 1
            ordered_dict = OrderedDict()
            ordered_dict["location"] = attraction["location"]
            ordered_dict["attraction_name"] = attraction["attraction_name"]
            ordered_dict["ranking_score"] = attraction["ranking_score"]
            ordered_dict["reranked_ranking"] = index
            ordered_dict["original_ranking"] = attraction["ranking"]
            ordered_dict["avg_rating"] = attraction["avg_rating"]

            rating_stats_dict = OrderedDict()
            rating_stats_dict["excellent"] = attraction["rating_stats"]["excellent"]
            rating_stats_dict["very good"] = attraction["rating_stats"]["very good"]
            rating_stats_dict["average"] = attraction["rating_stats"]["average"]
            rating_stats_dict["poor"] = attraction["rating_stats"]["poor"]
            rating_stats_dict["terrible"] = attraction["rating_stats"]["terrible"]
            ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

            review_ordered_dict_list = []
            review_cnt = 0
            for review in attraction["reviews"]:
                review_cnt += 1
                review_ordered_dict = OrderedDict()
                review_ordered_dict['index'] = review_cnt
                review_ordered_dict['review'] = review
                review_ordered_dict_list.append(review_ordered_dict)

            ordered_dict["review_count"] = attraction["review_count"]
            ordered_dict["reviews"] = review_ordered_dict_list

            #sys.stdout.write("\rStatus: %s / %s"%(index, attraction_length))
            #sys.stdout.flush()

            """ render out new ranking as json file in data/reranked_reviews/ """
            if int(index) < 10:
                file_name = attraction["location"] + "_0" + str(index) + ".json"
            else:
                file_name = attraction["location"] + "_" + str(index) + ".json"

            print "Saving data to: " + self.dst + "\033[1m" + file_name + ".json" + "\033[0m"
            f_out = open(self.dst+file_name, 'w+')
            f_out.write( json.dumps( ordered_dict, indent = 4, cls=NoIndentEncoder))

        print "-"*80

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

        print "-"*80

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
    p = PreProcess2()
    p.create_dirs()
    p.get_attractions()

