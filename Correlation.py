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
        self.src_vectors = sys.argv[1]
        self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)\.txt", self.src_vectors).group(1)
        self.src_norm_vectors = "data/line/norm_vectors200/" + self.filename + ".txt"
        self.src_cooccur = "data/line/cooccur/" + self.filename + ".txt"
        self.dst = "data/correlation/"
        self.verbose = 1
        self.norm_flag = 1

        self.unique_words = {}
        # hd stands for high dimension
        self.vectors = []
        self.norm_vectors = []
        self.dot_matrix = []
        self.cosine_matrix = []
        self.norm_dot_matrix = []
        self.norm_cosine_matrix = []
        self.cooccur_matrix = []

    def get_vectors(self):
        """ get high dimension vectors (vectors200) """

        print "Loading data from:", "\033[1m" + self.src_vectors + "\033[0m"
        with open(self.src_vectors) as f:
            next(f)
            index = 0
            for line in f:
                vector = line.strip("\n").strip().split(" ")
                self.unique_words.update({vector[0]:index})
                vector = vector[1:]
                vector = [float(v) for v in vector]
                self.vectors.append(vector)
                index += 1
        #print self.unique_words

    def get_norm_vectors(self):
        """ get normalized dimension vectors (vectors200) """

        print "Loading data from:", "\033[1m" + self.src_norm_vectors + "\033[0m"
        with open(self.src_norm_vectors) as f:
            next(f)
            index = 0
            for line in f:
                vector = line.strip("\n").strip().split(" ")
                #self.unique_words.update({vector[0]:index})
                vector = vector[1:]
                vector = [float(v) for v in vector]
                self.norm_vectors.append(vector)
                index += 1
        #print self.unique_words

    def get_dot_matrix(self):
        """  get dot matrix """

        print "Constructing dot product matrix"
        self.dot_matrix = np.dot(np.array(self.vectors), np.array(self.vectors).T)
        # print self.dot_matrix

    def get_norm_dot_matrix(self):
        """  get normalized dot matrix """

        print "Constructing normalized dot product matrix"
        self.norm_dot_matrix = np.dot(np.array(self.norm_vectors), np.array(self.norm_vectors).T)
        # print self.norm_dot_matrix

    def get_cosine_matrix(self):
        """  get cosine matrix """

        print "Constructing cosine similarity matrix"
	self.cosine_matrix = cosine_similarity(np.array(self.vectors))
	#print self.cosine_matrix

    def get_norm_cosine_matrix(self):
        """  get normalized cosine matrix """

        print "Constructing normalized cosine similarity matrix"
	self.norm_cosine_matrix = cosine_similarity(np.array(self.norm_vectors))
	#print self.cosine_matrix

    def get_cooccur_matrix(self):
        """ get cooccur_matrix """

        print "Constructing cooccurrence matrix"
        cooccur_lines = []
        with open(self.src_cooccur) as f:
            for line in f:
                cooccur_lines.append(line.strip("\n").strip().split(" "))

        length = len(self.unique_words)
        self.cooccur_matrix = np.zeros(shape=(length,length))
        for line in cooccur_lines:
            if line[0] and line[1] in self.unique_words:
                index1 = self.unique_words[line[0]]
                index2 = self.unique_words[line[1]]
                self.cooccur_matrix[index1][index2] = line[2]
                #self.cooccur_matrix[index2][index1] = line[2]
            else:
                pass
        #print len(self.cooccur_matrix)

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def render(self):
        """ customize output json file """

        self.get_vectors()
        if self.norm_flag:
            self.get_norm_vectors()
        print "-"*80

        self.get_dot_matrix()
        self.get_cosine_matrix()
        self.get_cooccur_matrix()
        if self.norm_flag:
            self.get_norm_dot_matrix()
            self.get_norm_cosine_matrix()
        print "-"*80

        self.create_dirs()

        cooccur_1D = self.cooccur_matrix.ravel()
        cosine_1D = self.cosine_matrix.ravel()
        dot_1D = self.dot_matrix.ravel()
        if self.norm_flag:
            norm_cosine_1D = self.norm_cosine_matrix.ravel()
            norm_dot_1D = self.norm_dot_matrix.ravel()

        # cos vs cooccur
        print "Calculating correlation between cosine_similarity_matrix and cooccurrence_matrix"
        cosine = np.corrcoef(cosine_1D, cooccur_1D)[0,1]
        #cosine = pearsonr(cosine_1D, cooccur_1D)

        # dot vs cooccur
        print "Calculating correlation between dot_product_matrix and cooccurrence_matrix"
        dot = np.corrcoef(dot_1D, cooccur_1D)[0,1]
        #dot = pearsonr(dot_1D, cooccur_1D)

        # norm_cos vs cooccur
        if self.norm_flag:
            print "Calculating correlation between normalized cosine_similarity_matrix and cooccurrence_matrix"
            cosine1 = np.corrcoef(norm_cosine_1D, cooccur_1D)[0,1]
            #cosine1 = pearsonr(norm_cosine_1D, cooccur_1D)

        # norm_dot vs cooccur
        if self.norm_flag:
            print "Calculating correlation between normalized dot_product_matrix and cooccurrence_matrix"
            dot1 = np.corrcoef(norm_dot_1D, cooccur_1D)[0,1]
            #dot1 = pearsonr(norm_dot_1D, cooccur_1D)

        indices = np.nonzero(cooccur_1D)[0]
        cooccur_noZeros_1D = [cooccur_1D[index] for index in indices]
        cosine_noZeros_1D = [cosine_1D[index] for index in indices]
        dot_noZeros_1D = [dot_1D[index] for index in indices]

        if self.norm_flag:
            norm_cosine_noZeros_1D = [norm_cosine_1D[index] for index in indices]
            norm_dot_noZeros_1D = [norm_dot_1D[index] for index in indices]

        # noZeros cos vs noZeros cooccur
        print "Calculating correlation between noZeros cosine_similarity_matrix and noZeros cooccurrence_matrix"
        cosine2 = np.corrcoef(cosine_noZeros_1D, cooccur_noZeros_1D)[0,1]
        #cosine2 = pearsonr(cosine_noZeros_1D, cooccur_noZeros_1D)

        # noZeros dot vs noZeros cooccur
        print "Calculating correlation between noZeros dot_product_matrix and noZeros cooccurrence_matrix"
        dot2 = np.corrcoef(dot_noZeros_1D, cooccur_noZeros_1D)[0,1]
        #dot2 = pearsonr(dot_noZeros_1D, cooccur_noZeros_1D)

        # noZeros norm_cos vs noZeros cooccur
        if self.norm_flag:
            print "Calculating correlation between noZeros cosine_similarity_matrix and noZeros cooccurrence_matrix"
            cosine3 = np.corrcoef(norm_cosine_noZeros_1D, cooccur_noZeros_1D)[0,1]
            #cosine3 = pearsonr(norm_cosine_noZeros_1D, cooccur_noZeros_1D)

        # noZeros norm_dot vs noZeros cooccur
        if self.norm_flag:
            print "Calculating correlation between noZeros dot_product_matrix and noZeros cooccurrence_matrix"
            dot3 = np.corrcoef(norm_dot_noZeros_1D, cooccur_noZeros_1D)[0,1]
            #dot3 = pearsonr(norm_dot_noZeros_1D, cooccur_noZeros_1D)

        if self.verbose:
            print "-"*50
            print "All values are included:"
            print "cosine:", cosine
            print "dot:", dot
            if self.norm_flag:
                print "norm_cosine:", cosine1
                print "norm_dot:", dot1

            print "-"*50
            print "Zeros and diagonal elements are excluded:"
            print "cosine:", cosine2
            print "dot:", dot2
            if self.norm_flag:
                print "norm_cosine:", cosine3
                print "norm_dot:", dot3
            print "-"*80

        print "Writing data to" + self.dst + "\033[1m" + self.filename + "\033[0m" + ".txt"
        f_out = open(self.dst + self.filename + ".txt", "w")
        if self.norm_flag:
            f_out.write(json.dumps(
                {"cosine": cosine, "norm_cosine": cosine1,
                "dot": dot, "norm_dot": dot1,
                "noZeros_cosine": cosine2, "noZeros_norm_cosine": cosine3,
                "noZeros_dot": dot2, "noZeros_norm_dot": dot3}
                , indent = 4))
        else:
            f_out.write(json.dumps(
                {"cosine": cosine, "dot": dot,
                "noZeros_cosine": cosine2, "noZeros_dot": dot2}
                , indent = 4))

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
