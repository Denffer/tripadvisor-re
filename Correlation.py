import json, sys, uuid, math, glob, scipy, os, math, pprint
import numpy as np
from scipy.spatial import distance
from json import dumps, loads, JSONEncoder, JSONDecoder
from operator import itemgetter
from collections import OrderedDict
from scipy import spatial
from scipy.stats.stats import pearsonr
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity

class Correlation:
    """ This program aim to calculate correlation """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_hd_vectors = "data/line/vectors200/Amsterdam_1.txt"
        self.src_cooccur = "data/line/cooccur/Amsterdam_1.txt"

        self.unique_words = []
        # hd stands for high dimension
        self.hd_vectors = []
        self.dot_matrix = []
        self.cosine_matrix = []
        self.cooccur_matrix = []

    def get_hd_vectors(self):
        """ get high dimension vectors (vectors100 or vectors200) """

        print "Loading data from:", "\033[1m" + self.src_hd_vectors + "\033[0m"

        with open(self.src_hd_vectors) as f:
            next(f)
            for line in f:
                hd_vector = line.strip("\n").strip().split(" ")
                self.unique_words.append(hd_vector[0])
                hd_vector = hd_vector[1:]
                hd_vector = [float(v) for v in hd_vector]
                #print hd_vector
                self.hd_vectors.append(hd_vector)
        # print self.hd_vectors

    def get_dot_matrix(self):
        """  get dot matrix """

        print "Constructing dot product matrix"
        self.dot_matrix = np.dot(np.array(self.hd_vectors), np.array(self.hd_vectors).T)
        # print self.dot_matrix

    def get_cosine_matrix(self):
        """  get cosine matrix """
        print "Constructing cosine product matrix"

	self.cosine_matrix = cosine_similarity(np.array(self.hd_vectors), np.array(self.hd_vectors))
	#print self.cosine_matrix

    def get_cooccur_matrix(self):
        """ get cooccur_matrix """

        cooccur_lines = []
        with open(self.src_cooccur) as f:
            for line in f:
                cooccur_lines.append(line.strip("\n").strip().split(" "))
        #print self.unique_words

        unique_word_dict = {}
        length = len(self.unique_words)
        print "Building unique_dict_words"
        word_cnt = 0
        for word in self.unique_words:
            word_cnt += 1
            unique_word_dict.update({word_cnt:word})
        # print unique_word_dict

        self.cooccur_matrix = np.zeros((length,length))
        for line in cooccur_lines:
            index1 = unique_word_dict.keys()[unique_word_dict.values().index(line[0])]
            index2 = unique_word_dict.keys()[unique_word_dict.values().index(line[1])]
            cooccur =  line[2]
            self.cooccur_matrix[index1-1][index2-1] = cooccur
            self.cooccur_matrix[index2-1][index1-1] = cooccur
        # print self.cooccur_matrix

    def get_correlation(self):
        """ get correlation matrix? """
        dot_correlation_matrix = np.corrcoef(self.dot_matrix.ravel(), self.cooccur_matrix.ravel())[0][1]
        # print dot_correlation_matrix
        cos_correlation_matrix = np.corrcoef(self.cosine_matrix.ravel(), self.cooccur_matrix.ravel())[0][1]
        # print cos_correlation_matrix
        return dot_correlation_matrix, cos_correlation_matrix

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/correlation/")

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def render(self):
        """ customize output json file """

        self.get_hd_vectors()
        self.get_dot_matrix()
        self.get_cosine_matrix()
        self.get_cooccur_matrix()
        self.create_dirs()

        dot_correlation_matrix, cosine_correlation_matrix = self.get_correlation()

        f_dot = open("data/correlation/dot_correlation.txt", "w")
        f_dot.write(json.dumps(dot_correlation_matrix.tolist()))
        f_cosine = open("data/correlation/cosine_correlation.txt", "w")
        f_cosine.write(json.dumps(cosine_correlation_matrix.tolist()))

        print '-'*80
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
    correlation = Correlation()
    correlation.render()
