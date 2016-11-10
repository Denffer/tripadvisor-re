import os, json, sys, glob, re, uuid
from operator import itemgetter
from collections import OrderedDict
from os import walk
# import pprint

class PreProcess:
    """ This program takes all json files in ./raw_data and filter out top 2000 restaurants with the most reviews. """

    def __init__(self):
        """ initialze the paths """
        self.src = "data/raw_data/"
        self.dst = "data/reviews/"

        self.review_count = 0
        self.dst_log = "data/reviews/_log.txt"

    def walk(self):
        """ recursively load data from ./data | search every file under any directory, if any """

        # the function os.walk will get the name of dirpath, dirs and files
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory:", dirpath
            print "Directory found: " + str(dir_list)
            if file_list > 0:
                print "Files found: " + str(file_list)
                tours = []
                for f in file_list:
                    if f.find("tour") == 0:
                        print "Appending " + str(dirpath) + "/" + str(f) + " into tours"
                        tours.append(json.load(open( dirpath + "/" + f )))
                    elif f.find("attraction") == 0:
                        print "processing " + str(dirpath) + "/" + str(f)
                        attraction = json.load(open( dirpath + "/" + f ))
                        self.render(attraction)
                    else:
                        pass
                if len(tours) > 0:
                    self.render(tours)
                else:
                    pass
            else:
                pass
            print '-'*100

    def create_dir(self):
        """ create the directory if not exist """
        dir1 = os.path.dirname(self.dst)
        if not os.path.exists(dir1):
            print "Making directory: " + dir1
            os.makedirs(dir1)

    def render(self, data):
        """ Check data | if it is tour_dict_list, then merge | if it is attraction, then render """
        self.create_dir()

        if isinstance(data, dict):
            attraction = data

            # ensure 01 ~ 20
            if int(attraction["ranking"]) < 10:
                file_name = attraction["location"].lower() + "_0" + attraction["ranking"] + ".json"
            else:
                file_name = attraction["location"].lower() + "_" + attraction["ranking"] + ".json"

            print "Saving json file: " + '\033[1m' + file_name + '\033[0m' +" into data/reviews/"

            attraction_ordered_dict = OrderedDict()

            """ Refine location | E.g. Hong_Kong, (Nickname). ->  Hong-Kong """ #FIXME on whether to lower()
            location = attraction["location"].replace("_","-").replace("&","and").replace("\'","").replace(".","")
            location = re.sub(r'\(.*?\)', r'', location)
            attraction_ordered_dict["location"] = location

            """ Refine attraction_name | E.g. Happy'_Temple, (Nickname). -> Happy-Temple """
            attraction_name = attraction["attraction_name"].replace("_","-").replace("&","and").replace("\'", "").replace(".","")
            attraction_name = re.sub(r'\(.*?\)', r'', attraction_name)
            attraction_ordered_dict["attraction_name"] = attraction_name

            attraction_ordered_dict["ranking"] = attraction["ranking"]
            attraction_ordered_dict["avg_rating"] = attraction["avg_rating"]
            attraction_ordered_dict["review_count"] = attraction["review_count"]

            rating_stats_dict = OrderedDict()
            rating_stats_dict["excellent"] = attraction["rating_stats"]["excellent"]
            rating_stats_dict["very good"] = attraction["rating_stats"]["very good"]
            rating_stats_dict["average"] = attraction["rating_stats"]["average"]
            rating_stats_dict["poor"] = attraction["rating_stats"]["poor"]
            rating_stats_dict["terrible"] = attraction["rating_stats"]["terrible"]

            attraction_ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

            review_ordered_dict_list = []
            review_cnt = 0
            for review_dict in attraction["reviews"]:
                review_ordered_dict = OrderedDict()
                self.review_count += 1
                review_cnt += 1
                review_ordered_dict["index"] = review_cnt
                review_ordered_dict["rating"] = review_dict["rating"]
                """ This is the part where 'title' and 'review' are merged """
                review_ordered_dict["review"] = review_dict["title"] + ". " + review_dict["review"]
                review_ordered_dict_list.append(review_ordered_dict)

            attraction_ordered_dict["reviews"] = review_ordered_dict_list

            f = open(self.dst+'/'+file_name, 'w+')
            f.write(json.dumps(attraction_ordered_dict, indent = 4, cls=NoIndentEncoder))

        elif isinstance(data, list):
            tour_list = data
            if int(tour_list[0]["super_attraction_ranking"]) < 10:
                file_name = tour_list[0]["location"].lower() + "_0" + tour_list[0]["super_attraction_ranking"] + ".json"
            else:
                file_name = tour_list[0]["location"].lower() + "_" + tour_list[0]["super_attraction_ranking"] + ".json"

            print "Mering all the tours .."

            attraction_ordered_dict = OrderedDict()

            """ Refine location | E.g. Hong_Kong, (Nickname). ->  Hong-Kong """ #FIXME on whether to lower()
            location = tour_list[0]["location"].replace("_","-").replace("&","and").replace("\'","").replace(".","")
            location = re.sub(r'\(.*?\)', r'', location)
            attraction_ordered_dict["location"] = location

            """ Refine attraction_name | E.g. Happy'_Temple, (Nickname). -> Happy-Temple """
            attraction_name = tour_list[0]["super_attraction_name"].replace("_","-").replace("&","and").replace("\'", "").replace(".","")
            attraction_name = re.sub(r'\(.*?\)', r'', attraction_name)
            attraction_ordered_dict["attraction_name"] = attraction_name

            attraction_ordered_dict["ranking"] = tour_list[0]["super_attraction_ranking"]

            avg_rating_list, sub_attraction_list, review_count_list = [], [], []
            excellent_list, very_good_list, average_list, poor_list, terrible_list = [], [], [], [], []
            review_dict_list = []
            for tour in tour_list:
                avg_rating_list.append(tour["avg_rating"])
                review_count_list.append(tour["review_count"])

                excellent_list.append(tour["rating_stats"]["excellent"])
                very_good_list.append(tour["rating_stats"]["very good"])
                average_list.append(tour["rating_stats"]["average"])
                poor_list.append(tour["rating_stats"]["poor"])
                terrible_list.append(tour["rating_stats"]["terrible"])

                """ Refine attraction_name | E.g. Happy'_Temple, (Nickname). -> Happy-Temple """
                sub_attraction_name = tour["attraction_name"].replace("_","-").replace("&","and").replace("\'", "").replace(".","")
                sub_attraction_name = re.sub(r'\(.*?\)', r'', sub_attraction_name)
                sub_attraction_list.append(sub_attraction_name)
                review_dict_list.extend(tour["reviews"])

            avg_rating = round(sum([float(i) for i in avg_rating_list])/len(avg_rating_list))
            attraction_ordered_dict["avg_rating"] = avg_rating

            review_count = sum([int(str(i).replace(",","")) for i in review_count_list])
            attraction_ordered_dict["review_count"] = review_count

            rating_stats_dict = OrderedDict()
            rating_stats_dict["excellent"] = sum([int(str(i).replace(",","")) for i in excellent_list])
            rating_stats_dict["very good"] = sum([int(str(i).replace(",","")) for i in very_good_list])
            rating_stats_dict["average"] = sum([int(str(i).replace(",","")) for i in average_list])
            rating_stats_dict["poor"] = sum([int(str(i).replace(",","")) for i in poor_list])
            rating_stats_dict["terrible"] = sum([int(str(i).replace(",","")) for i in terrible_list])
            attraction_ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

            attraction_ordered_dict["sub_attraction_list"] = NoIndent(sub_attraction_list)

            review_ordered_dict_list = []
            review_cnt = 0
            for review_dict in review_dict_list:
                review_ordered_dict = OrderedDict()
                self.review_count += 1
                review_cnt += 1
                review_ordered_dict["index"] = review_cnt
                review_ordered_dict["rating"] = review_dict["rating"]
                """ This is the part where 'title' and 'review' are merged """
                review_ordered_dict["review"] = review_dict["title"] + ". " + review_dict["review"]
                review_ordered_dict_list.append(review_ordered_dict)

            attraction_ordered_dict["reviews"] = review_ordered_dict_list

            print "Saving json file: " + '\033[1m' + file_name + '\033[0m' +" into data/reviews/"
            f = open(self.dst+'/'+file_name, 'w+')
            f.write(json.dumps(attraction_ordered_dict, indent = 4, cls=NoIndentEncoder))

        else:
            self.PrintException()

    def render_log(self):
        """ Save log in ./data/raw_data/ for future reference (to be added) """
        print "Saving log file to", '\033[1m' + self.dst_log + '\033[0m'
        f = open(self.dst_log, 'w+')
        f.write("Total Review Count: " + str(self.review_count))

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
    preprocess.walk()
    preprocess.render_log()

