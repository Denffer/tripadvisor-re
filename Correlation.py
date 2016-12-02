import json, sys, uuid, scipy, os, math, re
import numpy as np
from scipy.spatial import distance
from collections import OrderedDict
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats.stats import pearsonr

class Correlation:
    """ This program aim to calculate correlation """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_hd_vectors = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+\.txt)", self.src_hd_vectors).group(1)
        self.src_cooccur = "data/line/cooccur/" + self.filename
        self.dst = "data/correlation/"
        self.verbose = 1

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
                hd_vector = line.strip("\n").strip().split(" ")
                self.unique_words.update({hd_vector[0]:index})
                hd_vector = hd_vector[1:]
                hd_vector = [float(v) for v in hd_vector]
                self.hd_vectors.append(hd_vector)
                index += 1
        # print self.hd_vectors

    def get_dot_matrix(self):
        """  get dot matrix """

        print "Constructing dot product matrix"
        self.dot_matrix = np.dot(np.array(self.hd_vectors), np.array(self.hd_vectors).T)
        # print self.dot_matrix

    def get_cosine_matrix(self):
        """  get cosine matrix """

        print "Constructing cosine similarity matrix"
	self.cosine_matrix = cosine_similarity(np.array(self.hd_vectors))
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
                self.cooccur_matrix[index1][index2] = cooccur
                #self.cooccur_matrix[index2-1][index1-1] = cooccur
            else:
                pass

        # print self.cooccur_matrix
        print "-"*80

    def get_correlation(self, matrix1, matrix2):
        """ get correlation value """

        correlation = pearsonr(matrix1, matrix2)
        return correlation

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

        cooccur_1D = self.cooccur_matrix.ravel()
        cosine_1D = self.cosine_matrix.ravel()
        dot_1D = self.dot_matrix.ravel()
        print "Calculating correlation between cosine_similarity_matrix and cooccurrence_matrix"
        cosine = self.get_correlation(cosine_1D, cooccur_1D)
        print "Calculating correlation between dot_product_matrix and cooccurrence_matrix"
        dot = self.get_correlation(dot_1D, cooccur_1D)

        cooccur2 = np.fill_diagonal(self.cooccur_matrix, 0)
        cooccur2_1D = cooccur2.ravel()
        indices = np.nonzero(cooccur2_1D)[0]

        cooccur2_1D = [cooccur_1D[index] for index in indices]
        cosine2_1D = [cosine_1D[index] for index in indices]
        dot2_1D = [dot_1D[index] for index in indices]

        print "Calculating correlation between cosine_similarity_matrix and cooccurrence_matrix2"
        cosine2 = self.get_correlation(cosine2_1D, cooccur2_1D)
        print "Calculating correlation between dot_product_matrix and cooccurrence_matrix2"
        dot2 = self.get_correlation(dot2_1D, cooccur2_1D)

        if verbose:
            print "-"*10 + "All values are included" + "-"*10
            print "cosine:", cosine
            print "dot:", dot

            print "-"*10 + "Zeros and diagonal elements are excluded" + "-"*10
            print "cosine:", cosine2
            print "dot:", dot2

        print "Writing data to" + self.dst + "\033[1m" + self.filename + "\033[0m"
        f_out = open(self.dst + self.filename, "w")
        f_out.write(json.dumps({"cosine_correlation": cosine, "cosine_correlation2": cosine2, "dot_correlation": dot, "dot_correlation2": dot2}, indent = 4))

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
