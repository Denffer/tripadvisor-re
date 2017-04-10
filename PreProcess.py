import os, json, sys, glob, re, uuid
from operator import itemgetter
from collections import OrderedDict
from os import walk

class PreProcess:
    """ This program walk into all directories under ./raw_data and
        (1) Render attractions
        (2) Merge and render sub-tours into one single tour
        (3) Re-arrange all attractions or tours in a city by the order of their average rating stars
        """

    def __init__(self):
        """ initialze the paths """
        self.src = "data/raw_data/"
        self.dst = "data/reviews/"

        self.total_review_count = 0
        self.dst_log = "data/log.txt"

    def walk(self):
        """ (1) Recursively seach and load every json file under the directory ./data/raw_data/
            (2) Append every attraction to entities
            (3) Merge every sub_tours into one single tour and append it to entities  """

        # the function os.walk will get the name of dirpath, dirs and files
        location = ""
        entities = []
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory:", dirpath
            try:
                location = re.search("data\/raw_data\/([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)", dirpath).group(1)
                print location
            except:
                pass
            print "Directory found: " + str(dir_list)
            if file_list > 0:
                print "Files found: " + str(file_list)
                sub_tours = []
                for f in file_list:
                    if f.find("tour") == 0:
                        print "Appending " + str(dirpath) + "/" + str(f) + " into tours"
                        sub_tours.append(json.load(open( dirpath + "/" + f )))
                    elif f.find("attraction") == 0:
                        print "Appending " + str(dirpath) + "/" + str(f) + "into entities"
                        attraction = json.load(open( dirpath + "/" + f ))
                        attraction = self.process_attraction(attraction)
                        entities.append(attraction)
                    else:
                        pass

                if len(sub_tours) > 0:
                    tour = self.process_sub_tours(sub_tours)
                    print '-'*80
                    entities.append(tour)
                else:
                    pass
            else:
                print "No files in this directory"
                pass

            if len(entities) == 20:
                self.render(entities)
                entities = []
            else:
                pass
            print '-'*100

    def process_attraction(self, attraction):
        """ (1) Denoise location_name and attraction_name (2) compute the average rating_stars for the attraction """

        processed_attraction = {}

        # Remove noisy text in location_name | E.g. Hong_Kong, (Nickname). ->  Hong-Kong
        location_name = attraction["location"].replace("_","-").replace("&","and").replace("\'","").replace(".","")
        location_name = re.sub(r'\(.*?\)', r'', location_name)
        processed_attraction["location"] = location_name

        # Remove noisy text in attraction_name | E.g. Happy'_Temple_(Nickname). -> Happy-Temple
        attraction_name = attraction["attraction_name"].replace("_","-").replace("-"," ").replace("\'", "").replace(".","").replace(",","")
        attraction_name = re.sub(r'\s+', r' ', attraction_name)
        attraction_name = re.sub(r'\(.*?\)', r'', attraction_name)
        attraction_name = attraction_name.strip().replace(" ", "-")
        processed_attraction["entity_name"] = attraction_name

        # Switch 'ranking' to 'original_ranking'
        processed_attraction["original_ranking"] = attraction["ranking"]

        # compute the average rating_stars for the attraction
        x = attraction["rating_stats"]
        score = (float(int(x["excellent"])*5 + int(x["very good"])*4 + int(x["average"])*3 + int(x["poor"])*2 + int(x["terrible"]))
                    / float(int(x["excellent"]) + int(x["very good"]) + int(x["average"]) + int(x["poor"]) + int(x["terrible"])))
        processed_attraction["avg_rating_stars"]= score

        # Remove punctuation "," from review_count E.g., "1,235" -> 1235
        processed_attraction["review_count"] = int(attraction["review_count"].replace(',', ''))

        # Rating Stats
        excellent_count, very_good_count, average_count, poor_count, terrible_count = 0, 0, 0, 0, 0
        excellent_count += int(attraction["rating_stats"]["excellent"])
        very_good_count += int(attraction["rating_stats"]["very good"])
        average_count += int(attraction["rating_stats"]["average"])
        poor_count += int(attraction["rating_stats"]["poor"])
        terrible_count += int(attraction["rating_stats"]["terrible"])
        processed_attraction["rating_stats"] = {"excellent": excellent_count, "very_good": very_good_count, "average":average_count, "poor": poor_count, "terrible": terrible_count}

        # Reviews
        processed_attraction["reviews"] = attraction["reviews"]

        #print processed_attraction
        return processed_attraction

    def process_sub_tours(self, sub_tours):
        """ (1) merge all sub_tours into one single tour (2) compute the average rating_stars for the tour"""
        tour = {}

        # Remove noisy text in location_name | E.g. Hong_Kong, (Nickname). ->  Hong-Kong
        location_name = sub_tours[0]["location"].replace("_","-").replace("&","and").replace("\'","").replace(".","")
        location_name = re.sub(r'\(.*?\)', r'', location_name)
        tour["location"] = location_name

        # Remove noisy text in tour_name | E.g. Happy'_Tour_By_Alexander(Alex Tour). -> Happy-Tour-By-Alexander
        tour_name = sub_tours[0]["super_attraction_name"].replace("_","-").replace("-"," ").replace("\'", "").replace(".","").replace(",","")
        tour_name = re.sub(r'\s+', r' ', tour_name)
        tour_name = re.sub(r'\(.*?\)', r'', tour_name)
        tour_name = tour_name.strip().replace(" ", "-")
        tour["entity_name"] = tour_name
        tour["original_ranking"] = sub_tours[0]["super_attraction_ranking"]

        # merge five different rating counts
        excellent_count, very_good_count, average_count, poor_count, terrible_count = 0, 0, 0, 0, 0
        for sub_tour in sub_tours:
            excellent_count += int(sub_tour["rating_stats"]["excellent"])
            very_good_count += int(sub_tour["rating_stats"]["very good"])
            average_count += int(sub_tour["rating_stats"]["average"])
            poor_count += int(sub_tour["rating_stats"]["poor"])
            terrible_count += int(sub_tour["rating_stats"]["terrible"])
        tour["rating_stats"] = {"excellent": excellent_count, "very_good": very_good_count, "average":average_count, "poor": poor_count, "terrible": terrible_count}

        # compute average rating_score
        score = (float(int(excellent_count)*5 + int(very_good_count)*4 + int(average_count)*3 + int(poor_count)*2 + int(terrible_count))
                    / float(int(excellent_count) + int(very_good_count) + int(average_count) + int(poor_count) + int(terrible_count)))
        tour["avg_rating_stars"] = score

        # reviews
        total_review_cnt = 0
        reviews = []
        for sub_tour in sub_tours:
            total_review_cnt += int(sub_tour["review_count"].replace(",",""))
            reviews.extend(sub_tour["reviews"])

        tour["review_count"] = total_review_cnt
        tour["reviews"] = reviews

        #print tour
        return tour

    def render(self, entities):
        """ (1) Rerank entities according to their average rating_stars (2) Put them in ordered_dict (3) Render them in data/reviews/"""

        # rerank entities according to their average rating_stars E.g., 4.89 > 4.86 > 4.51 > 4.39 > 4.12 -> 1 > 2 > 3 > 4 > 5
        reranked_entities = sorted(entities, key=lambda k: k['avg_rating_stars'], reverse = True)

        # an entity could be an attraction or a tour
        entity_ranking = 0 # reranked_ranking
        for entity in reranked_entities:
            entity_ranking += 1
            # naming json file from 01 to 20 for better listing effect
            if entity_ranking < 10:
                file_name = entity["location"] + "_0" + str(entity_ranking) + ".json"
            else:
                file_name = entity["location"] + "_" + str(entity_ranking) + ".json"

            # Put every entity in ordered_dict
            entity_ordered_dict = OrderedDict()
            entity_ordered_dict["location"] = entity["location"]
            entity_ordered_dict["entity_name"] = entity["entity_name"]
            entity_ordered_dict["avg_rating_stars"] = entity["avg_rating_stars"]
            entity_ordered_dict["reranked_ranking"] = entity_ranking
            entity_ordered_dict["original_ranking"] = entity["original_ranking"]
            entity_ordered_dict["review_count"] = entity["review_count"]

            # Rating statistics
            rating_stats_dict = OrderedDict()
            rating_stats_dict["excellent"] = entity["rating_stats"]["excellent"]
            rating_stats_dict["very_good"] = entity["rating_stats"]["very_good"]
            rating_stats_dict["average"] = entity["rating_stats"]["average"]
            rating_stats_dict["poor"] = entity["rating_stats"]["poor"]
            rating_stats_dict["terrible"] = entity["rating_stats"]["terrible"]
            entity_ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

            # Reviews
            review_ordered_dict_list = []
            review_cnt = 0
            for review_dict in entity["reviews"]:
                self.total_review_count += 1

                review_ordered_dict = OrderedDict()
                review_cnt += 1
                review_ordered_dict["index"] = review_cnt
                review_ordered_dict["rating"] = review_dict["rating"]
                # Merge 'title' and 'review'
                review_ordered_dict["review"] = review_dict["title"] + ". " + review_dict["review"]
                review_ordered_dict_list.append(review_ordered_dict)

            entity_ordered_dict["reviews"] = review_ordered_dict_list

            # Save to json file in data/reviews/
            print "Saving json file: " + '\033[1m' + file_name + '\033[0m' +" into data/reviews/"
            f = open(self.dst + '/' + file_name, 'w+')
            f.write(json.dumps( entity_ordered_dict, indent = 4, cls=NoIndentEncoder))

    def create_dir(self):
        """ create the directory if not exist """
        dir1 = os.path.dirname(self.dst + "/")
        if not os.path.exists(dir1):
            print "Making directory: " + dir1
            os.makedirs(dir1)

    def render_log(self):
        """ Save log in ./data/ for future reference (to be added) """
        print "Saving log file to", '\033[1m' + self.dst_log + '\033[0m'
        f = open(self.dst_log, 'w+')
        f.write("Total Review Count: " + str(self.total_review_count))

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
    preprocess = PreProcess()
    preprocess.create_dir()
    preprocess.walk()
    preprocess.render_log()

