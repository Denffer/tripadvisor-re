# -*- coding: utf-8 -*-
import sys, re, json, os, uuid, itertools
from operator import itemgetter
from collections import OrderedDict
import unicodedata, linecache
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

class ReviewProcess:
    """ This program aims to transform all data in json files in data/reviews/ into
        (1) backend_reviews.txt in 'data/backend_reviews/'
        (2) location_*.json in 'data/frontend_reviews/'
        (3) sentiment_statistics_location_*.json in the 'data/statistics/'
    """

    def __init__(self):
        self.verbose = 0

        self.src = sys.argv[1]  # E.g. data/reranked_reviews/bangkok_3.json
        self.filename = re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+\_.*).json", self.src).group(1)
        #print self.filename
        print "Processing " +"\033[1m" + self.filename + ".json"  + "\033[0m"
        self.src_opinion_lexicon = "data/lexicon/opinion_lexicon.json"
        self.src_pos_tagged_lexicon = "data/lexicon/pos_tagged_lexicon.json"
        self.dst_frontend = "data/frontend_reviews/"
        self.dst_backend = "data/backend_reviews/"
        self.dst_starred = "data/starred_backend_reviews/"
        self.dst_hybrid = "data/hybrid_reviews/"
        self.dst_sentiment_statistics = "data/sentiment_statistics/"

        self.entity = {}
        self.sentiment_words = []
        self.entity_name, self.entity_regexr, self.entity_al, self.entity_marked = "", "", "", ""
        self.total_words_count, self.total_entity_count = 0, 0
        self.avg_pos_tagged_sentiment_count, self.avg_opinion_positive_count, self.avg_opinion_negative_count = 0.0, 0.0, 0.0
        self.avg_nearest_opinion_sentiment_distance, self.avg_nearest_pos_tagged_sentiment_distance = 0.0, 0.0

        self.pos_tagged_sentiment_words, self.opinion_positive_words, self.opinion_negative_words, self.ratings = [], [], [], []
        self.clean_reviews, self.frontend_reviews, self.backend_reviews, self.starred_backend_reviews, self.hybrid_reviews = [], [], [], [], []
        self.opinion_sentiment_statistics, self. pos_tagged_sentiment_statistics = [], []

        self.stopwords = set(stopwords.words('english'))
        self.stemmer = SnowballStemmer("english")

    def get_entity(self):
        """ Load data from data/reviews/*.json """
        if self.verbose:
            print "Loading data from " + "\033[1m" + self.src + "\033[0m"

        """ entity could be an attraction or a tour, stored in the form of a python dictionary """
        with open(self.src) as f:
            self.entity = json.load(f)

        return self.entity

    def get_entity_name(self):
        """ get entity_name from entity_dict """

        self.entity_name = self.entity["entity_name"].replace("-"," ")

        if self.verbose:
            print "This is entity: " + "\033[1m" + self.entity_name + "\033[0m"

    def get_entity_regexr(self):
        """ entity_regexr is the regular expression for entity_name """
        if self.verbose:
            print "-"*80
            print "Generating entity_regexr"

        entity_regexr = self.entity_name.replace("&","and").replace(self.entity["location"], "").strip()
        entity_regexr = entity_regexr.split()
        if entity_regexr[-1] == "tours":
            entity_regexr[0] = "\\s(the\\s|this\\s|" + entity_regexr[0]

            for i in xrange(len(entity_regexr)-1):
                entity_regexr[i] += "\\s"
            for i in xrange(len(entity_regexr)-2):
                entity_regexr[i] += "|"

            entity_regexr[len(entity_regexr)-2] = entity_regexr[len(entity_regexr)-2] + ")*"
            entity_regexr[-1] = entity_regexr[-1][:-1] # tours -> tour
            entity_regexr = "".join(entity_regexr)
            self.entity_regexr = entity_regexr + "(s)?\\s"
        else:
            entity_regexr[0] = "\\s(the\\s|this\\s|" + entity_regexr[0]

            for i in xrange(len(entity_regexr)-1):
                if entity_regexr[i][-1] == "s":
                    entity_regexr[i] += "(s)?\\s"
                else:
                    entity_regexr[i] += "\\s"
            for i in xrange(len(entity_regexr)-2):
                entity_regexr[i] += "|"

            entity_regexr[len(entity_regexr)-2] = entity_regexr[len(entity_regexr)-2] + ")+"
            if entity_regexr[-1][-1] == "s":
                entity_regexr[-1] = entity_regexr[-1][:-1] + "(s)?"# temples -> temple(s)
            entity_regexr[-1] = "(" + entity_regexr[-1] + "|place)"
            self.entity_regexr = "".join(entity_regexr)

        if self.verbose:
            print self.entity_regexr

    def get_entity_al(self):
        """ entity_al is entity_name 'a'ppending 'l'ocation | E.g., temple_bangkok """

        if self.verbose:
            print "-"*80 + "\n" + "Generating entity_al"

        location = self.entity["location"]
        #entity_al = self.entity_name
        entity_al = self.entity_name.replace("&","and").replace(self.entity["location"], "").strip()
        self.entity_al = " " + entity_al.replace(" ", "-") + "_" + location.replace(" ", "-") + " "

        if self.verbose:
            print self.entity_al

    def get_entity_marked(self):
        """ mark entity_name for further frontend display """
        if self.verbose:
            print "-"*80 + "\n" + "Generating entity_marked"

        #entity_marked = self.entity_name
        entity_marked = self.entity_name.replace("&","and").replace(self.entity["location"], "").strip()
        entity_marked = entity_marked.replace(" ","-")
        self.entity_marked = " <mark>" + entity_marked + "</mark> "

        if self.verbose:
            print self.entity_marked

    def get_opinion_lexicon(self):
        """ load positive and negative sentiment_words from data/lexicon/opinion_lexicon.json """
        if self.verbose:
            print "\n" + "-"*80 + "\n" + "Loading sentiment words from " + "\033[1m" + self.src_opinion_lexicon + "\033[0m"

        with open(self.src_opinion_lexicon) as f:
            json_data = json.load(f)

        self.opinion_positive_words = json_data["positive"]
        self.opinion_negative_words = json_data["negative"]

    def get_pos_tagged_lexicon(self):
        """ load sentiment_words from data/lexicon/pos_tagged_lexicon.json """
        if self.verbose:
            print "-"*80 + "\n" + "Loading sentiment words from " + "\033[1m" + self.src_pos_tagged_lexicon + "\033[0m"

        with open(self.src_pos_tagged_lexicon) as f:
            self.pos_tagged_sentiment_words = json.load(f)

    def get_clean_reviews(self):
        """ Clean reviews """
        if self.verbose:
            print "-"*80 + "\nCleaning reviews"

        reviews = self.entity["reviews"]
        cnt = 0
        review_length = len(reviews)
        for review_dict in reviews:
            cnt += 1
            text = review_dict["review"]

            # Remove accents
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
            # Remove all website urls written in the review
            text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
            # Space out every sign & symbol & punctuation
            text = re.sub("([^\w\s]|\_)",r" \1 ", text)
            # Remove non english letters or words and numbers
            text = re.sub(r'[^a-zA-Z!@#$%^&*():;/\\<>\"+_\-.,?=\s\|]', '', text)
            # Remove extra nextline
            text = re.sub("(\\n)+", r" ", text)

            # I'm -> I am
            text = re.sub(r"'m", " am", text)
            text = re.sub(r"'re", " are", text)
            text = re.sub(r"'s", " is", text)
            text = re.sub(r"'ve", " have", text)
            text = re.sub(r"'d", " would", text)
            text = re.sub(r"n't", " not", text)
            text = re.sub(r"'ll", " will", text)

            text = text.replace("\'","")
            text = re.sub("(\s)+", r" ", text)

            self.clean_reviews.append(text)
            self.ratings.append(review_dict["rating"])

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, review_length))
                sys.stdout.flush()

    def get_frontend_reviews(self):
        """ Match entity by entity_regexr and replace them by entity_marked """
        if self.verbose:
            print "\n" + "-"*80 + "\n" + "Processing frontend reviews"

        review_cnt = 0
        reviews_length = len(self.clean_reviews)
        try:
            for review in self.clean_reviews:
                """ Replacing | E.g., I love happy tour . -> I love <mark>happy tour</mark>. """
                review_cnt += 1
                # remove extra space in front of \W
                review = re.sub(r"[^\w\s]|\_", r"", review)
                review = re.sub(self.entity_regexr, self.entity_marked, review, flags = re.IGNORECASE)
                # remove - from entity_location
                review = review.replace("-"," ")
                review = re.sub("(\s)+", r" ", review)

                #FIXME Temtatively filter out those review with the entity mentioned
                if "<mark>" in review:
                    self.frontend_reviews.append(review)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s"%(review_cnt, reviews_length))
                    sys.stdout.flush()
        except:
            self.PrintException()

    def get_backend_reviews(self):
        """ match the entity_name in the reviews with entity_regexr and replace them by entity_al  """

        if self.verbose:
            print "\n" + "-"*80 + "\n" + "Processing backend reviews"

        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review in self.clean_reviews:
            review_cnt += 1
            # lower review to ensure words like 'good' and 'Good' are counted as the same
            review = review.lower()
            # remove all punctuations
            review = re.sub("[^\w\s]|\_",r" ", review)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)

            """ Replacement | E.g., I love happy temple. -> I love "title" Happy-Temple_Bangkok "title" . """
            review = re.sub(self.entity_regexr, self.entity_al, review, flags = re.IGNORECASE)

            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            # split review into a list of words
            words = review.split(" ")
            # remove stopwords
            words_stopwords_removed = [w.lower() for w in words if w not in self.stopwords]
            words_stemmed = [self.stemmer.stem(w) if '_' not in w else w for w in words_stopwords_removed]

            review = ' '.join(words_stemmed).encode('utf-8').strip()
            self.backend_reviews.append(review)

            self.total_entity_count += review.count(self.entity_al.lower())
            self.total_words_count += len(review.split(" "))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_starred_backend_reviews(self):
        """ replace all entity_name by star_1 & star_2 & star_3 & star_4 & star_5 according to their rating """

        if self.verbose:
            print "\n" + "-"*80 + "\n" + "Processing starred_backend_reviews"

        stars = [" 1_star ", " 2_star ", " 3_star ", " 4_star ", " 5_star "]
        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review, rating in zip(self.clean_reviews, self.ratings):
            review_cnt += 1
            # lower review to ensure words like 'good' and 'Good' are counted as the same
            review = review.lower()
            # remove all punctuations
            review = re.sub("[^\w\s]|\_",r" ", review)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            """ Replacement | E.g. I love happy temple -> I love star_5 """
            review = re.sub(self.entity_regexr, stars[int(rating)-1], review, flags = re.IGNORECASE)
            # remove extra spaces
            review = re.sub("(\s)+", r" ", review)
            # split review into a list of words
            words = review.split(" ")
            # remove stopwords
            words_stopwords_removed = [w.lower() for w in words if w not in self.stopwords]
            words_stemmed = [self.stemmer.stem(w) if '_' not in w else w for w in words_stopwords_removed]

            review = ' '.join(words_stemmed)

            #print review
            self.starred_backend_reviews.append(review)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_hybrid_reviews(self):
        """ create parallel comparision for original reviews and processed reviews """
        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing hybrid_reviews"

        review_cnt = 0
        review_length = len(self.clean_reviews)
        for review_dict, review, clean_review in zip(self.entity["reviews"], self.backend_reviews, self.clean_reviews):
            review_cnt += 1
            self.hybrid_reviews.append({"title": review_dict["title"], "review": review, "clean_review": clean_review})

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

    def get_avg_nearest_opinion_sentiment_distance(self):
        """ walk into reviews and get distance with entity and sentiment_word in opinion_lexicon"""

        if self.verbose:
            print "-"*80 + "\nUsing opinion_lexicon to calculate average nearest sentiment distance"

        opinion_sentiment_words = []
        for p in self.opinion_positive_words:
            opinion_sentiment_words.append(p["stemmed_word"])
        for n in self.opinion_negative_words:
            opinion_sentiment_words.append(n["stemmed_word"])

        review_cnt = 0
        review_length = len(self.starred_backend_reviews)
        opinion_nearest_sentiment_distance_list = []
        for review in self.starred_backend_reviews:
            review_cnt += 1
            words = review.split(" ")[:-1]
            num_of_words = len(words)

            # the index for _star in the text
            indexes = [i for i,w in enumerate(words) if "_star" in w]
            #print "indexes:", indexes
            for index in indexes:
                cnt = 0
                nearest_sentiment_distance = 0

                while True:
                    cnt += 1
                    #forward search
                    try:
                        for s in opinion_sentiment_words:
                            #print "Matching for", s
                            if index+cnt < num_of_words:
                                #print "Forward +", cnt, ":", words[index+cnt]
                                if s == words[index+cnt]:
                                    #print "Forward Match:", s
                                    nearest_sentiment_distance = cnt
                                    raise
                            if index-cnt >= 0:
                                #print "Backward +", cnt, ":", words[index-cnt]
                                if s == words[index-cnt]:
                                    #print "Backward Match:", s
                                    nearest_sentiment_distance = cnt
                                    raise
                            if index+cnt >= num_of_words and index-cnt < 0:
                                raise
                        #print "-"*10
                    except:
                        break

                opinion_nearest_sentiment_distance_list.append(nearest_sentiment_distance)
                #print opinion_nearest_sentiment_distance_list

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

        #  nearest_sentiment_distance_list
        n = opinion_nearest_sentiment_distance_list
        self.avg_nearest_opinion_sentiment_distance = float(sum(n)/float(len(n)))

    def get_avg_nearest_pos_tagged_sentiment_distance(self):
        """ walk into reviews and get distance with entity and sentiment_word in pos_tagged_lexicon"""

        if self.verbose:
            print "\n" + "-"*80 + "\nUsing pos_tagged_sentiment_words to calculate average nearest sentiment distance"

        pos_tagged_sentiment_words = []
        for word_dict in self.pos_tagged_sentiment_words:
            pos_tagged_sentiment_words.append(word_dict["stemmed_word"])

        review_cnt = 0
        review_length = len(self.starred_backend_reviews)
        pos_tagged_nearest_sentiment_distance_list = []
        for review in self.starred_backend_reviews:
            review_cnt += 1
            words = review.split(" ")[:-1]
            num_of_words = len(words)
            #print words

            indexes = [i for i,w in enumerate(words) if "_star" in w]
            for index in indexes:
                cnt = 0
                nearest_sentiment_distance = 0

                while True:
                    cnt += 1
                    #forward search
                    try:
                        for s in pos_tagged_sentiment_words:
                            #print "Matching for", s
                            if index+cnt < num_of_words:
                                #print "Forward +", cnt, ":", words[index+cnt]
                                if s == words[index+cnt]:
                                    #print "Forward Match:", s
                                    nearest_sentiment_distance = cnt
                                    raise

                            if index-cnt >= 0:
                                #print "Backward +", cnt, ":", words[index-cnt]
                                if s == words[index-cnt]:
                                    #print "Backward Match:", s
                                    nearest_sentiment_distance = cnt
                                    raise
                            if index+cnt >= num_of_words and index-cnt < 0:
                                raise
                        #print "-"*10
                    except:
                        break

                #print "?:", nearest_sentiment_distance
                pos_tagged_nearest_sentiment_distance_list.append(nearest_sentiment_distance)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(review_cnt, review_length))
                sys.stdout.flush()

        #  nearest_sentiment_distance_list
        n = pos_tagged_nearest_sentiment_distance_list
        self.avg_nearest_pos_tagged_sentiment_distance = float(sum(n)/float(len(n)))

    def get_opinion_sentiment_statistics(self):
        """ count the opinion lexicon's positive and negative sentiment words in reviews """

        # (1) opinion lexicon (positive)
        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing opinion positive sentiment_statistics"
        positive_statistics = []
        total_positive_sentiment_count = 0

        index = 0
        length = len(self.opinion_positive_words)
        for word_dict in self.opinion_positive_words:
            index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + word_dict["stemmed_word"] + " ")

            total_positive_sentiment_count += sentiment_count

            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["count"] = sentiment_count
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            positive_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index, length))
                sys.stdout.flush()

        self.avg_opinion_positive_count = float("{0:.3f}".format(float(total_positive_sentiment_count) / float(len(self.backend_reviews))))

        # (2) opinion lexicon (negative)
        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing opinion negative sentiment_statistics"
        negative_statistics = []
        total_negative_sentiment_count = 0

        index = 0
        length = len(self.opinion_negative_words)
        for word_dict in self.opinion_negative_words:
            index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + word_dict["stemmed_word"] + " ")

            total_negative_sentiment_count += sentiment_count

            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["count"] = sentiment_count
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            negative_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index, length))
                sys.stdout.flush()

        self.avg_opinion_negative_count = float("{0:.3f}".format(float(total_negative_sentiment_count) / float(len(self.backend_reviews))))


        opinion_orderedDict = OrderedDict()
        opinion_orderedDict["positive_statistics"] = positive_statistics
        opinion_orderedDict["negative_statistics"] = negative_statistics
        self.opinion_sentiment_statistics = opinion_orderedDict

    def get_pos_tagged_sentiment_statistics(self):
        """ count pos_tagged lexicon's sentiment words in reviews """

        if self.verbose:
            print "\n" + "-"*80 + "\nProcessing pos_tagged sentiment_statistics"
        sentiment_statistics = []
        total_sentiment_count = 0

        index = 0
        length = len(self.pos_tagged_sentiment_words)
        for word_dict in self.pos_tagged_sentiment_words:
            index += 1
            sentiment_count = 0
            for review in self.backend_reviews:
                sentiment_count += review.count(" " + word_dict["stemmed_word"] + " ")

            total_sentiment_count += sentiment_count

            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["count"] = sentiment_count
            orderedDict["stemmed_word"] = word_dict["stemmed_word"]
            orderedDict["word"] = word_dict["word"]
            sentiment_statistics.append(NoIndent(orderedDict))

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(index, length))
                sys.stdout.flush()

        self.avg_pos_tagged_sentiment_count = float("{0:.3f}".format(float(total_sentiment_count) / float(len(self.backend_reviews))))
        self.pos_tagged_sentiment_statistics = sentiment_statistics

    def create_dirs(self, location):
        """ create directory under data/backend_revies/ """
        # print "Creating directories if not existed"
        dir1 = os.path.dirname(self.dst_frontend + location)
        if not os.path.exists(dir1):
            print "Creating Directory: " + dir1 + "/"
            os.makedirs(dir1)
        dir2 = os.path.dirname(self.dst_backend + location)
        if not os.path.exists(dir2):
            print "Creating Directory: " + dir2 + "/"
            os.makedirs(dir2)
        dir3 = os.path.dirname(self.dst_starred + location)
        if not os.path.exists(dir3):
            print "Creating Directory: " + dir3 + "/"
            os.makedirs(dir3)
        dir4 = os.path.dirname(self.dst_hybrid + location)
        if not os.path.exists(dir4):
            print "Creating Directory: " + dir4 + "/"
            os.makedirs(dir4)
        dir5 = os.path.dirname(self.dst_sentiment_statistics + location + "opinion/")
        if not os.path.exists(dir5):
            print "Creating Directory: " + dir5 + "/"
            os.makedirs(dir5)
        dir6 = os.path.dirname(self.dst_sentiment_statistics + location + "pos_tagged/")
        if not os.path.exists(dir6):
            print "Creating Directory: " + dir6 + "/"
            os.makedirs(dir6)

    def render(self):
        """ render frontend_review & backend_reviews & sentiment_statistics """
        reload(sys)
        sys.setdefaultencoding("utf-8")

        if self.verbose:
            print "\n" + "-"*80 + "\n" + "Saving json files"
        self.create_dirs(self.entity["location"] + "/")

        """ (1) save location_*.json in ./frontend_reviews """
        frontend_orderedDict = OrderedDict()
        frontend_orderedDict["location"] = self.entity["location"]
        frontend_orderedDict["entity_name"] = self.entity["entity_name"]
        frontend_orderedDict["avg_rating_stars"] = self.entity["avg_rating_stars"]
        frontend_orderedDict["reranked_ranking"] = self.entity["reranked_ranking"]
        frontend_orderedDict["original_ranking"] = self.entity["original_ranking"]

        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = self.entity["rating_stats"]["excellent"]
        rating_stats_dict["very_good"] = self.entity["rating_stats"]["very_good"]
        rating_stats_dict["average"] = self.entity["rating_stats"]["average"]
        rating_stats_dict["poor"] = self.entity["rating_stats"]["poor"]
        rating_stats_dict["terrible"] = self.entity["rating_stats"]["terrible"]
        frontend_orderedDict["rating_stats"] = NoIndent(rating_stats_dict)

        # be noted that the reviews count is the number of reviews with entity mentioned
        frontend_orderedDict["review_count"] = len(self.frontend_reviews)
        frontend_orderedDict["total_entity_count"] = self.total_entity_count
        frontend_orderedDict["avg_opinion_positive_count"] = self.avg_opinion_positive_count
        frontend_orderedDict["avg_opinion_negative_count"] = self.avg_opinion_negative_count
        frontend_orderedDict["avg_pos_tagged_sentiment_count"] = self.avg_pos_tagged_sentiment_count
        frontend_orderedDict["avg_word_count"] = float(self.total_words_count) / float(len(self.backend_reviews))
        frontend_orderedDict["avg_nearesti_opinion_sentiment_distance"] = self.avg_nearest_opinion_sentiment_distance
        frontend_orderedDict["avg_nearesti_pos_tagged_sentiment_distance"] = self.avg_nearest_pos_tagged_sentiment_distance

        review_ordered_dict_list = []
        review_cnt = 0
        for review in self.frontend_reviews:
            review_cnt += 1
            review_ordered_dict = OrderedDict()
            review_ordered_dict['index'] = review_cnt
            review_ordered_dict['review'] = review
            review_ordered_dict_list.append(review_ordered_dict)

        frontend_orderedDict["reviews"] = review_ordered_dict_list

        frontend_json = open(self.dst_frontend + self.entity["location"] + "/" + self.filename + ".json", "w+")
        frontend_json.write(json.dumps( frontend_orderedDict, indent = 4, cls=NoIndentEncoder))
        frontend_json.close()

        if self.verbose:
            print self.filename, "'s frontend is complete"

        """ (2) save location_*.txt in ./backend_reviews/location/ """
        backend_txt = open(self.dst_backend +"/"+ self.entity["location"] +"/"+ self.filename + ".txt", "w+")
        for review in self.backend_reviews:
            backend_txt.write(review.encode("utf-8") + '\n')
        backend_txt.close()

        if self.verbose:
            print self.filename, "'s backend is complete"

        """ (3) save location_*.txt in ./starred_backend_reviews/location/ """
        stars_txt_file = open(self.dst_starred +"/"+ self.entity["location"] +"/"+ self.filename + ".txt", "w+")
        for review in self.starred_backend_reviews:
            stars_txt_file.write(review.encode("utf-8") + '\n')
        stars_txt_file.close()

        if self.verbose:
            print self.filename, "'s starred_backend is complete"

        """ (4) save location_*.json in ./hybrid_reviews/location/ """
        hybrid_json_file = open(self.dst_hybrid +"/"+ self.entity["location"] +"/"+ self.filename + ".json", "w+")

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
        orderedDict = OrderedDict()
        orderedDict["location"] = self.entity["location"]
        orderedDict["entity_name"] = self.entity["entity_name"]
        orderedDict["entity_al"] = self.entity["entity_name"].lower() + "_" + self.entity["location"].lower()
        orderedDict["avg_opinion_positive_count"] = self.avg_opinion_positive_count
        orderedDict["avg_opinion_negative_count"] = self.avg_opinion_negative_count
        orderedDict["sentiment_statistics"] = self.opinion_sentiment_statistics

        opinion_sentiment_json = open(self.dst_sentiment_statistics + self.entity["location"] + "/opinion/" + self.filename + ".json", "w+")
        opinion_sentiment_json.write(json.dumps(orderedDict, indent = 4, cls=NoIndentEncoder))
        opinion_sentiment_json.close()

        if self.verbose:
            print self.filename, "'s opinion sentiment statistics is complete"

        """ (6) render location.json containing a list """
        orderedDict = OrderedDict()
        orderedDict["location"] = self.entity["location"]
        orderedDict["entity_name"] = self.entity["entity_name"]
        orderedDict["entity_al"] = self.entity["entity_name"].lower() + "_" + self.entity["location"].lower()
        orderedDict["avg_pos_tagged_sentiment_count"] = self.avg_pos_tagged_sentiment_count
        orderedDict["sentiment_statistics"] = self.pos_tagged_sentiment_statistics

        opinion_sentiment_json = open(self.dst_sentiment_statistics + self.entity["location"] + "/pos_tagged/" + self.filename + ".json", "w+")
        opinion_sentiment_json.write(json.dumps(orderedDict, indent = 4, cls=NoIndentEncoder))
        opinion_sentiment_json.close()

        if self.verbose:
            print self.filename, "'s pos_tagged sentiment statistics is complete"
            print "-"*80

        print self.filename, "is complete"
    def run(self):
        self.get_entity()
        self.get_entity_name()
        self.get_entity_regexr()
        self.get_entity_al()
        self.get_entity_marked()
        self.get_clean_reviews()
        self.get_frontend_reviews()
        self.get_backend_reviews()
        self.get_starred_backend_reviews()
        self.get_opinion_lexicon()
        self.get_pos_tagged_lexicon()
        self.get_avg_nearest_opinion_sentiment_distance()
        self.get_avg_nearest_pos_tagged_sentiment_distance()
        #self.get_hybrid_reviews()
        self.get_opinion_sentiment_statistics()
        self.get_pos_tagged_sentiment_statistics()
        self.render()

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
    process.run()

