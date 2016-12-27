# -*- coding: utf-8 -*-
import sys, re, json, os, uuid, itertools
from operator import itemgetter
from collections import OrderedDict
import unicodedata, linecache
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

class ReviewProcess:
    """ This program aims to transform all json files in data/reranked_reviews/ into
        (1) backend_reviews.txt in 'data/backend_reviews/'
        (2) location_*.json in 'data/frontend_reviews/'
        (3) sentiment_statistics_location_*.json in the 'data/statistics/'
    """

    def __init__(self):
        self.src = sys.argv[1]  # E.g. data/reranked_reviews/bangkok_3.json
        self.filename = re.findall("([A-Z]\w+)", self.src)[0]
        print "Processing " +"\033[1m" + self.filename + ".json" + "\033[0m"
        self.verbose = 0

        self.attraction = {}
        self.attraction_name, self.attraction_regexr, self.attraction_al, self.attraction_marked = "", "", "", ""
        self.avg_positive_sentiment_count, self.avg_negative_sentiment_count = 0.0, 0.0

        self.lexicon, self.positive, self.negative, self.ratings = [], [], [], []
        self.clean_reviews, self.frontend_reviews, self.backend_reviews, self.backend_stars_reviews, self.hybrid_reviews, self.sentiment_statistics = [], [], [], [], [], []

        self.dst_frontend = "data/frontend_reviews/"
        self.dst_backend = "data/backend_reviews/"
        self.dst_stars = "data/backend_stars_reviews/"
        self.dst_hybrid = "data/hybrid_reviews/"
        self.dst_sentiment_statistics = "data/sentiment_statistics/"
        self.dst_lexicon = "data/lexicon/lexicon.json"

        self.stopwords = set(stopwords.words('english'))
        self.stemmer = SnowballStemmer("english")

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
        """ return lexicon, a dictionary of positive_lexicon(list) and negative_lexicon(list) """
        if self.verbose:
            print "-"*80
            print "Loading lexicon from " + "\033[1m" + self.dst_lexicon + "\033[0m"

        with open(self.dst_lexicon) as f:
            self.lexicon = json.load(f)

        for word_dict in self.lexicon["positive"]:
            self.positive.append(word_dict["stemmed_word"])
        for word_dict in self.lexicon["negative"]:
            self.negative.append(word_dict["stemmed_word"])
        #print lexicon

    def get_clean_reviews(self):
        """ Clean reviews """
        if self.verbose:
            print "-"*80 + "\nCleaning reviews"

        reviews = self.attraction["reviews"]
        cnt = 0
        review_length = len(reviews)
        for review_dict in reviews:
            cnt += 1
            text = review_dict["review"]
            #print text
            #FIXME Remove accents
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
            # Just to be sure, rid all website urls written in the review # might slow down the process
            text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
            # Remove non english letters or words
            text = re.sub(r'[^a-zA-Z0-9!@#$%^&*():;/\\<>\"+_\-.,?=]', ' ', text)
            # Remove numbers
            text = re.sub(r'[0-9]', ' ', text)
            # Remove extra nextline
            text = re.sub("(\\n)+", r" ", text)
            # space out every sign & symbol & punctuation
            text = re.sub("(\W|\_)",r" \1 ", text)

            text = re.sub(r"'m", " am", text)
            text = re.sub(r"'re", " are", text)
            text = re.sub(r"'s", " is", text)
            text = re.sub(r"'ve", " have", text)
            text = re.sub(r"'d", " would", text)
            text = re.sub(r"n't", " not", text)
            text = re.sub(r"'ll", " will", text)

            text = text.replace("\'"," ")
            # Search for negation and merge them | E.g. not bad -> not-bad
            text = re.sub("(\s)+", r" ", text)

            #  print text
            self.clean_reviews.append(text)
            self.ratings.append(review_dict["rating"])

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
                # remove extra space in front of \W
                review = re.sub(r"\s(\W|\_)", r"\1", review)
                review = re.sub(self.attraction_regexr, self.attraction_marked, review, flags = re.IGNORECASE)
                # remove - from attraction_location
                review = review.replace("-"," ")
                review = re.sub("(\s)+", r" ", review)

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
        for review, review_dict in zip(self.clean_reviews, self.attraction["reviews"]):
            review_cnt += 1
            # lower review to ensure words like 'good' and 'Good' are counted as the same
            review = review.lower()
            # remove all punctuations
            review = re.sub("(\W|\_)",r" ", review)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)

            """ Replacement | E.g. I love happy temple. -> I love "title" Happy-Temple_Bangkok "title" . """
            title = review_dict["title"]
            review = re.sub(self.attraction_regexr, self.attraction_al, review, flags = re.IGNORECASE)
            # remove accent again for title

            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            # split review into a list of words
            words = review.split(" ")
            # remove stopwords
            words_stopwords_removed = [w.lower() for w in words if w not in self.stopwords]
            words_stemmed = [self.stemmer.stem(w) if '_' not in w else w for w in words_stopwords_removed]

            review = ' '.join(words_stemmed).encode('utf-8').strip()
            self.backend_reviews.append(review)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_backend_stars_reviews(self):
        """ replace all attraction_name by star_1 & star_2 & star_3 & star_4 & star_5 according to their rating """

        if self.verbose:
            print "\n" + "-"*80
            print "Processing backend_stars_reviews"

        stars = [" star_1 ", " star_2 ", " star_3 ", " star_4 ", " star_5 "]
        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review, rating in zip(self.clean_reviews, self.ratings):
            review_cnt += 1
            # lower review to ensure words like 'good' and 'Good' are counted as the same
            review = review.lower()
            # remove all punctuations
            review = re.sub("(\W|\_)",r" ", review)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            """ Replacement | E.g. I love happy temple -> I love star_5 """
            review = re.sub(self.attraction_regexr, stars[int(rating)-1], review, flags = re.IGNORECASE)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            # split review into a list of words
            words = review.split(" ")
            # remove stopwords
            words_stopwords_removed = [w.lower() for w in words if w not in self.stopwords]
            words_stemmed = [self.stemmer.stem(w) if '_' not in w else w for w in words_stopwords_removed]

            review = ' '.join(words_stemmed)

            #print review
            self.backend_stars_reviews.append(review)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_hybrid_reviews(self):
        """ create parallel comparision for origin reviews and processed reviews """
        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing hybrid_reviews"

        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review_dict, review, clean_review in zip(self.attraction["reviews"], self.backend_reviews, self.clean_reviews):
            review_cnt += 1
            self.hybrid_reviews.append({"title": review_dict["title"], "review": review, "clean_review": clean_review})

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_sentiment_statistics(self):
        """ count the sentiment words in reviews """
        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing positive sentiment_statistics"

        # (1) positive
        positive = self.lexicon["positive"]
        total_positive_sentiment_count = 0

        positive_statistics = []
        sentiment_index = 0
        sentiment_length = len(positive)
        for word_dict in positive:
            sentiment_index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + word_dict["stemmed_word"].encode("utf-8") + " ")

            total_positive_sentiment_count += sentiment_count

            orderedDict = OrderedDict()
            orderedDict["index"] = sentiment_index
            orderedDict["count"] = sentiment_count
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            positive_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sentiment_index, sentiment_length))
                sys.stdout.flush()

        self.avg_positive_sentiment_count = float("{0:.3f}".format(float(total_positive_sentiment_count) / float(len(self.backend_reviews))))

        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing negative sentiment_statistics"

        # (2) negative
        negative = self.lexicon["negative"]
        total_negative_sentiment_count = 0

        negative_statistics = []
        sentiment_index = 0
        sentiment_length = len(negative)
        for word_dict in negative:
            sentiment_index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + word_dict["stemmed_word"].encode("utf-8") + " ")

            total_negative_sentiment_count += sentiment_count

            orderedDict = OrderedDict()
            orderedDict["index"] = sentiment_index
            orderedDict["count"] = sentiment_count
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            negative_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sentiment_index, sentiment_length))
                sys.stdout.flush()

        self.avg_negative_sentiment_count = float("{0:.3f}".format(float(total_negative_sentiment_count) / float(len(self.backend_reviews))))

        self.sentiment_statistics = {"positive_statistics": positive_statistics, "negative_statistics": negative_statistics}

    def create_dirs(self, location):
        """ create directory under data/backend_revies/ """
        dir1 = os.path.dirname(self.dst_frontend + location)
        if not os.path.exists(dir1):
            print "Creating Directory: " + dir1 + "/"
            os.makedirs(dir1)
        dir2 = os.path.dirname(self.dst_backend + location)
        if not os.path.exists(dir2):
            print "Creating Directory: " + dir2 + "/"
            os.makedirs(dir2)
        dir3 = os.path.dirname(self.dst_stars + location)
        if not os.path.exists(dir3):
            print "Creating Directory: " + dir3 + "/"
            os.makedirs(dir3)
        dir4 = os.path.dirname(self.dst_hybrid + location)
        if not os.path.exists(dir4):
            print "Creating Directory: " + dir4 + "/"
            os.makedirs(dir4)
        dir5 = os.path.dirname(self.dst_sentiment_statistics + location)
        if not os.path.exists(dir5):
            print "Creating Directory: " + dir5 + "/"
            os.makedirs(dir5)

    def render(self):
        """ render frontend_review & backend_reviews & sentiment_statistics """
        reload(sys)
        sys.setdefaultencoding("utf-8")

        if self.verbose:
            print "\n" + "-"*80
            print "Saving files"
        self.create_dirs(self.attraction["location"].replace("-","_") + "/")

        """ (1) save location_*.json in ./frontend_reviews """
        frontend_orderedDict = OrderedDict()
        frontend_orderedDict["location"] = self.attraction["location"]
        frontend_orderedDict["attraction_name"] = self.attraction["attraction_name"]
        frontend_orderedDict["ranking_score"] = self.attraction["ranking_score"]
        frontend_orderedDict["reranked_ranking"] = self.attraction["reranked_ranking"]
        frontend_orderedDict["original_ranking"] = self.attraction["original_ranking"]
        frontend_orderedDict["avg_rating"] = self.attraction["avg_rating"]

        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = self.attraction["rating_stats"]["excellent"]
        rating_stats_dict["very good"] = self.attraction["rating_stats"]["very good"]
        rating_stats_dict["average"] = self.attraction["rating_stats"]["average"]
        rating_stats_dict["poor"] = self.attraction["rating_stats"]["poor"]
        rating_stats_dict["terrible"] = self.attraction["rating_stats"]["terrible"]
        frontend_orderedDict["rating_stats"] = NoIndent(rating_stats_dict)

        frontend_orderedDict["review_with_attraction_mentioned_count"] = len(self.frontend_reviews)
        frontend_orderedDict["avg_sentiment_counts"] = self.avg_positive_sentiment_count + self.avg_negative_sentiment_count

        review_ordered_dict_list = []
        review_cnt = 0
        for review in self.frontend_reviews:
            review_cnt += 1
            review_ordered_dict = OrderedDict()
            review_ordered_dict['index'] = review_cnt
            review_ordered_dict['review'] = review
            review_ordered_dict_list.append(review_ordered_dict)

        frontend_orderedDict["reviews"] = review_ordered_dict_list

        frontend_json = open(self.dst_frontend + self.attraction["location"].replace("-","_") + "/" + self.filename + ".json", "w+")
        frontend_json.write(json.dumps( frontend_orderedDict, indent = 4, cls=NoIndentEncoder))
        frontend_json.close()

        if self.verbose:
            print self.filename, "'s frontend is complete"

        """ (2) save location_*.txt in ./backend_reviews/location/ """
        backend_txt = open(self.dst_backend +"/"+ self.attraction["location"].replace("-","_") +"/"+ self.filename + ".txt", "w+")
        for review in self.backend_reviews:
            backend_txt.write(review.encode("utf-8") + '\n')
        backend_txt.close()

        if self.verbose:
            print self.filename, "'s backend is complete"

        """ (3) save location_*.txt in ./backend_reviews/location/ """
        stars_txt_file = open(self.dst_stars +"/"+ self.attraction["location"].replace("-","_") +"/"+ self.filename + ".txt", "w+")
        for review in self.backend_stars_reviews:
            stars_txt_file.write(review.encode("utf-8") + '\n')
        stars_txt_file.close()

        if self.verbose:
            print self.filename, "'s backend_stars is complete"

        """ (4) save location_*.json in ./hybrid_reviews/location/ """
        hybrid_json_file = open(self.dst_hybrid +"/"+ self.attraction["location"].replace("-","_") +"/"+ self.filename + ".json", "w+")

        cnt = 0
        hybrid_ordered_dict_list = []
        for review_dict in self.hybrid_reviews:
            cnt += 1
            hybrid_orderedDict = OrderedDict()
            hybrid_orderedDict["index"] = cnt
            hybrid_orderedDict["title"] = review_dict["title"].encode("utf-8")
            hybrid_orderedDict["processed_review"] = review_dict["review"].encode("utf-8")
            hybrid_orderedDict["clean_review"] = review_dict["clean_review"].encode("utf-8")
            hybrid_ordered_dict_list.append(hybrid_orderedDict)

        hybrid_json_file.write(json.dumps(hybrid_ordered_dict_list, indent = 4))
        hybrid_json_file.close()

        if self.verbose:
            print self.filename, "'s hybrid is complete"

        """ (5) render location.json containing a dictionaries of two key:list """
        statistics_orderedDict = OrderedDict()
        statistics_orderedDict["avg_positive_sentiment_counts"] = self.avg_positive_sentiment_count
        statistics_orderedDict["avg_negative_sentiment_counts"] = self.avg_negative_sentiment_count
        statistics_orderedDict["positive_statistics"] = self.sentiment_statistics["positive_statistics"]
        statistics_orderedDict["negative_statistics"] = self.sentiment_statistics["negative_statistics"]

        sentiment_statistics_json = open(self.dst_sentiment_statistics + "/" + self.attraction["location"].replace("-","_") + "/" + self.filename + ".json", "w+")
        sentiment_statistics_json.write(json.dumps(statistics_orderedDict, indent = 4, cls=NoIndentEncoder))
        sentiment_statistics_json.close()

        if self.verbose:
            print self.filename, "'s sentiment analysis is complete"
            print "-"*80

        print self.filename, "is complete"

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
    process.get_lexicon()
    process.get_clean_reviews()
    process.get_frontend_reviews()
    process.get_backend_reviews()
    process.get_backend_stars_reviews()
    process.get_hybrid_reviews()
    process.get_sentiment_statistics()
    process.render()

