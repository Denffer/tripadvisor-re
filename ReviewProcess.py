# -*- coding: utf-8 -*-
import sys, re, json, os, uuid, itertools
from operator import itemgetter
from collections import OrderedDict
import unicodedata, linecache

class ReviewProcess:
    """ This program aims to transform all json files in data/reviews/ into
        (1) backend_reviews.txt in 'data/backend_reviews/'
        (2) location_*.json in 'data/frontend_reviews/'
        (3) sentiment_statistics_location_*.json in the 'data/statistics/'
    """

    def __init__(self):
        self.src = sys.argv[1]  # E.g. data/reviews/bangkok_3.json
        print "Processing " + "\033[1m" + self.src + "\033[0m"
        self.verbose = 1

        self.attraction = {}
        self.attraction_name = ""
        self.attraction_regexr = ""
        self.attraction_al = ""
        self.attraction_marked = ""

        self.clean_reviews = []
        self.backend_reviews = []
        self.frontend_reviews = []
        self.sentiment_statistics = []

        self.dst_backend = "data/backend_reviews/"
        self.dst_frontend = "data/frontend_reviews/"
        self.dst_sentiment_statistics = "data/sentiment_statistics/"
        self.dst_lexicon = "data/lexicon/lexicon.json"

    def get_attraction(self):
        """ Load data from data/reviews/*.json """
        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src + "\033[0m"

        """ attraction is a dictionary """
        with open(self.src) as f:
            self.attraction = json.load(f)

        return self.attraction

    def get_attraction_name(self):
        """ get attraction_name from attraction_dict """

        self.attraction_name = self.attraction["attraction_name"].replace("-"," ")

        if self.verbose:
            print "This is attraction: " + "\033[1m" + self.attraction_name + "\033[0m"

    def get_attraction_regexr(self):
        """ attraction_regexr is the regular expression for attraction_name """
        if self.verbose:
            print "-"*80
            print "Generating attraction_regexr"

        attraction_regexr = self.attraction_name
        attraction_regexr = attraction_regexr.split()
        if attraction_regexr[-1] == "tours":
            attraction_regexr[0] = "\\s(the\\s|this\\s|" + attraction_regexr[0]

            for i in xrange(len(attraction_regexr)-1):
                attraction_regexr[i] += "\\s"
            for i in xrange(len(attraction_regexr)-2):
                attraction_regexr[i] += "|"

            attraction_regexr[len(attraction_regexr)-2] = attraction_regexr[len(attraction_regexr)-2] + ")*"
            attraction_regexr[-1] = attraction_regexr[-1][:-1] # tours -> tour
            attraction_regexr = "".join(attraction_regexr)
            self.attraction_regexr = attraction_regexr + "(s)?\\s"
        else:
            attraction_regexr[0] = "\\s(the\\s|this\\s|" + attraction_regexr[0]

            for i in xrange(len(attraction_regexr)-1):
                attraction_regexr[i] += "\\s"
            for i in xrange(len(attraction_regexr)-2):
                attraction_regexr[i] += "|"

            attraction_regexr[len(attraction_regexr)-2] = attraction_regexr[len(attraction_regexr)-2] + ")*"
            if attraction_regexr[-1][-1] == "s":
                attraction_regexr[-1] = attraction_regexr[-1][:-1] + "(s)?\\s"# temples -> temple(s)
            attraction_regexr[-1] = "(" + attraction_regexr[-1] + "|place)\\s"
            self.attraction_regexr = "".join(attraction_regexr)

        if self.verbose:
            print self.attraction_regexr

    def get_attraction_al(self):
        """ attraction_al is attraction_name 'a'ppending 'l'ocation | E.g. temple_bangkok """
        if self.verbose:
            print "-"*80
            print "Generating attraction_al"

        location = self.attraction["location"]
        attraction_al = self.attraction_name
        self.attraction_al = " " + attraction_al.replace(" ", "-") + "_" + location.replace(" ", "-") + " "

        if self.verbose:
            print self.attraction_al

    def get_attraction_marked(self):
        """ mark attraction_name for further frontend display """
        if self.verbose:
            print "-"*80
            print "Generating attraction_marked"

        attraction_marked = self.attraction_name
        attraction_marked = attraction_marked.replace(" ","-")
        self.attraction_marked = " <mark>" + attraction_marked + "</mark> "

        if self.verbose:
            print self.attraction_marked

    def get_lexicon(self):
        """ return positive_list containing dictionaries of positive words """
        if self.verbose:
            print "Loading lexicon from " + "\033[1m" + self.dst_lexicon + "\033[0m"

        sentiment_list = []
        with open(self.dst_lexicon) as f:
            lexicon = json.load(f)
            for word_dict in lexicon:
                sentiment_list.append(word_dict["word"])

        #print sentiment_list
        return sentiment_list

    def get_clean_reviews(self):
        """ Clean reviews """
        if self.verbose:
            print "-"*80
            print "Cleaning reviews"

        reviews = self.attraction["reviews"]
        cnt = 0
        review_length = len(reviews)
        for review_dict in reviews:
            cnt += 1
            text = review_dict["review"]
            # Just to be sure, rid all website urls written in the review # might slow down the process
            text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
            # Remove non english letters or words
            text = re.sub(r'[^a-zA-Z0-9!@#$%^&*():;/\\<>\"\'+_\-.,?=]', ' ', text)

            # Ensure words and punctuation are separated
            text = text.replace("!"," ! ").replace("@"," @ ").replace("#"," # ").replace("$"," $ ").replace("%"," % ")
            text = text.replace("^"," ^ ").replace("&"," & ").replace("*"," * ").replace("("," ( ").replace(")"," ) ")
            text = text.replace(":"," : ").replace(";"," ; ").replace("."," . ").replace(","," , ").replace("=", " = ")
            text = text.replace("+"," + ").replace("-"," - ").replace("|"," | ").replace("\\"," \ ").replace("/"," / ")
            text = text.replace("~"," ~ ").replace("_", "").replace(">"," > ").replace("<", " < ").replace("?", " ? ")
            text = text.replace("\""," ").replace("[","").replace("]","").replace("{","").replace("}","")

            text = re.sub(r"'m", " am", text)
            text = re.sub(r"'re", " are", text)
            text = re.sub(r"'s", " is", text)
            text = re.sub(r"'ve", " have", text)
            text = re.sub(r"'d", " would", text)
            text = re.sub(r"n't", " not", text)
            text = re.sub(r"'ll", " will", text)

            text = text.replace("\'"," ")
            text = re.sub("(\\n)+", r" ", text)
            text = re.sub("(\s)+", r" ", text)

            #FIXME Remove accents
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
            #text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text)) # sooo happppppy -> so happy

            self.clean_reviews.append(text)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, review_length))
                sys.stdout.flush()

    def get_frontend_reviews(self):
        """ Match attraction by attraction_regexr and replace them by attraction_marked """
        if self.verbose:
            print "\n" + "-"*80
            print "Processing frontend reviews"

        review_cnt = 0
        reviews_length = len(self.clean_reviews)
        try:
            for review in self.clean_reviews:
                """ Replacing | E.g. I love happy tour . -> I love <mark>happy tour</mark>. """
                review_cnt += 1
                review = re.sub(self.attraction_regexr, self.attraction_marked, review, flags = re.IGNORECASE)
                review = review.replace(" ! ","! ").replace(" @ ","@ ").replace(" # ","# ").replace(" $ ","$ ").replace(" % ","% ")
                review = review.replace(" ^ ","^ ").replace(" & ","& ").replace(" * ","* ").replace(" ( ","( ").replace(" ) ",") ")
                review = review.replace(" : ",": ").replace(" ; ","; ").replace(" . ",". ").replace(" , ",", ").replace(" = ", "= ")
                review = review.replace(" + ","+ ").replace(" - ","- ").replace(" | ","| ")
                review = review.replace(" ~ ","~ ").replace(" > ","> ").replace(" < ", "< ").replace(" ? ", "? ")
                review = re.sub("(\s)+", r" ", review)
                review = review.replace("-"," ")

                #FIXME Temtatively filter out those review with the attraction mentioned
                if "<mark>" in review:
                    self.frontend_reviews.append(review)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(review_cnt, reviews_length))
                    sys.stdout.flush()
        except:
            self.PrintException()

    def get_backend_reviews(self):
        """ match the attraction_name in the reviews with attraction_regexr and replace them by attraction_al  """

        if self.verbose:
            print "\n" + "-"*80
            print "Processing backend_reviews"

        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review in self.clean_reviews:
            review_cnt += 1
            # lower review to ensure words like 'good' and 'Good' are counted as the same
            review = review.lower()
            """ Replacement | E.g. I love happy temple. -> I love Happy-Temple_Bangkok. """
            review = re.sub(self.attraction_regexr, self.attraction_al, review, flags = re.IGNORECASE)
            self.backend_reviews.append(re.sub("(\s)+", r" ", review))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_sentiment_statistics(self):
        """ count the sentiment words in reviews """
        if self.verbose:
            print "\n" + "-"*80
            print "Processing sentiment_statistics"

        sentiment_list = self.get_lexicon()
        sentiment_statistics = []
        sentiment_index = 0
        sentiment_length = len(sentiment_list)

        for sentiment_word in sentiment_list:
            sentiment_index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + sentiment_word + " ")
            orderedDict = OrderedDict()
            orderedDict["index"] = sentiment_index
            orderedDict["word"] = sentiment_word
            orderedDict["count"] = sentiment_count
            self.sentiment_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sentiment_index, sentiment_length))
                sys.stdout.flush()

    def create_dirs(self):
        """ create the directory if not existed """
        dir1 = os.path.dirname(self.dst_backend)
        dir2 = os.path.dirname(self.dst_frontend)
        dir3 = os.path.dirname(self.dst_sentiment_statistics)

        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            os.makedirs(dir3)

    def render(self):
        """ render frontend_review & backend_reviews & sentiment_statistics """
        self.create_dirs()
        if self.verbose:
            print "\n" + "-"*80
            print "Saving files"

        filename = sys.argv[1][13:-5] # E.g. data/reviews/ | amsterdam_18 | .json

        """ (1) save location_*.json in ./frontend_reviews """
        frontend_orderedDict = OrderedDict()
        frontend_orderedDict["location"] = self.attraction["location"]
        frontend_orderedDict["attraction_name"] = self.attraction["attraction_name"]
        frontend_orderedDict["ranking"] = self.attraction["ranking"]
        frontend_orderedDict["avg_rating"] = self.attraction["avg_rating"]

        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = self.attraction["rating_stats"]["excellent"]
        rating_stats_dict["very good"] = self.attraction["rating_stats"]["very good"]
        rating_stats_dict["average"] = self.attraction["rating_stats"]["average"]
        rating_stats_dict["poor"] = self.attraction["rating_stats"]["poor"]
        rating_stats_dict["terrible"] = self.attraction["rating_stats"]["terrible"]
        frontend_orderedDict["rating_stats"] = NoIndent(rating_stats_dict)

        frontend_orderedDict["mentioned_count"] = len(self.frontend_reviews)

        review_ordered_dict_list = []
        review_cnt = 0
        for review in self.frontend_reviews:
            review_cnt += 1
            review_ordered_dict = OrderedDict()
            review_ordered_dict['index'] = review_cnt
            review_ordered_dict['review'] = review
            review_ordered_dict_list.append(review_ordered_dict)

        frontend_orderedDict["reviews"] = review_ordered_dict_list

        frontend_json = open(self.dst_frontend + filename + ".json", "w+")
        frontend_json.write(json.dumps( frontend_orderedDict, indent = 4, cls=NoIndentEncoder))
        frontend_json.close()

        if self.verbose:
            print filename, "'s frontend is complete"

        """ (2) save location_*.txt in ./backend_reviews """
        backend_txt = open(self.dst_backend + filename + ".txt", "w+")
        for review in self.backend_reviews:
            backend_txt.write(review.encode("utf-8") + '\n')
        backend_txt.close()

        if self.verbose:
            print filename, "'s backend is complete"

        """ (1) save location_*.json in ./frontend_reviews """
        """ (3) render restaurant.json containing dictionaries of each positive sentiment word """

        sentiment_statistics_json = open(self.dst_sentiment_statistics + filename + ".json", "w+")
        sentiment_statistics_json.write(json.dumps(self.sentiment_statistics, indent = 4, cls=NoIndentEncoder))
        sentiment_statistics_json.close()

        if self.verbose:
            print filename, "'s sentiment analysis is complete"
            print "-"*80

        print filename, "is complete"

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

if  __name__ == '__main__':
    process = ReviewProcess()
    process.get_attraction()
    process.get_attraction_name()
    process.get_attraction_regexr()
    process.get_attraction_al()
    process.get_attraction_marked()
    process.get_clean_reviews()
    process.get_frontend_reviews()
    process.get_backend_reviews()
    process.get_sentiment_statistics()
    process.render()

