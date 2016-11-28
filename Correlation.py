import json, sys, uuid, scipy, os, math, re
import numpy as np
from scipy.spatial import distance
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity

class Correlation:
    """ This program aim to calculate correlation """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_hd_vectors = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+\.txt)", self.src_hd_vectors).group(1)
        self.src_cooccur = "data/line/cooccur/" + self.filename
        self.dst = "data/correlation/"

        self.unique_words = {}
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
            index = 0
            for line in f:
                index += 1
                hd_vector = line.strip("\n").strip().split(" ")
                self.unique_words.update({hd_vector[0]:index})
                hd_vector = hd_vector[1:]
                hd_vector = [float(v) for v in hd_vector]
                self.hd_vectors.append(hd_vector)
        # print self.hd_vectors

    def get_dot_matrix(self):
        """  get dot matrix """

        print "Constructing dot product matrix"
        self.dot_matrix = np.dot(np.array(self.hd_vectors), np.array(self.hd_vectors).T)
        # print self.dot_matrix

    def get_cosine_matrix(self):
        """  get cosine matrix """

        print "Constructing cosine similarity matrix"
	self.cosine_matrix = cosine_similarity(np.array(self.hd_vectors), np.array(self.hd_vectors))
	#print self.cosine_matrix

    def get_cooccur_matrix(self):
        """ get cooccur_matrix """

        print "Constructing cooccurrence matrix"
        cooccur_lines = []
        with open(self.src_cooccur) as f:
            for line in f:
                cooccur_lines.append(line.strip("\n").strip().split(" "))

        length = len(self.unique_words)
        self.cooccur_matrix = np.zeros((length,length))
        for line in cooccur_lines:
            if line[0] and line[1] in self.unique_words:
                index1 = self.unique_words[line[0]]
                index2 = self.unique_words[line[1]]
                cooccur =  line[2]
                self.cooccur_matrix[index1-1][index2-1] = cooccur
                self.cooccur_matrix[index2-1][index1-1] = cooccur
            else:
                pass

        # print self.cooccur_matrix
        print "-"*80

    def get_correlation(self):
        """ get correlation matrix? """

        print "Calculating correlation between dot_product_matrix and cooccurrence_matrix"
        dot_correlation = np.corrcoef(self.dot_matrix.ravel(), self.cooccur_matrix.ravel())[0][1]
        # print dot_correlation_matrix
        print "Calculating correlation between cosine_similarity_matrix and cooccurrence_matrix"
        cos_correlation = np.corrcoef(self.cosine_matrix.ravel(), self.cooccur_matrix.ravel())[0][1]
        # print cos_correlation_matrix
        return dot_correlation, cos_correlation

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

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
        dot_correlation, cosine_correlation = self.get_correlation()

        print "Writing data to" + self.dst + "\033[1m" + self.filename + "\033[0m"
        f_out = open(self.dst + self.filename, "w")
        f_out.write(json.dumps({"cosine_cooccur_correlation": cosine_correlation, "cosine_cooccur_correlation": dot_correlation}))

        print '-'*80 + "\nDone"

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
