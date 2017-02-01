import json, uuid, sys, re, os
import numpy as np
from sklearn import decomposition
from sklearn.manifold import TSNE
from collections import OrderedDict

class LowerDimension:
    """ This program aims to reduce vectors of 200 dimension to 2 dimension (shortcut)"""

    def __init__(self):
        self.src_f = sys.argv[1]
        self.dst = "data/vectors2/"
        self.pca_dimension = 100

        self.unique_words = []

    def get_vectors200(self):
        """ append every crawled business_list into source """

        print "Loading data from:", "\033[1m" + sys.argv[1] + "\033[0m"


        vectors200 = []
        with open(self.src_f) as f:
            next(f)
            for line in f:
                vector200 = line.strip("\n").strip().split(" ")
                self.unique_words.append(vector200[0])
                vector200 = vector200[1:]
                vector200 = [float(v) for v in vector200]
                #print vector200
                vectors200.append(vector200)

        #print vectors200
        return vectors200

    def get_vectorsN(self):
        """ (1) get vectors200 (2) perform reduction to N dimension by pca """
        vectors200 = self.get_vectors200()

        print "Reducing vectors200 to vectors" + self.pca_dimension + " by PCA"
        pca = decomposition.PCA(n_components = self.pca_dimension)
        pca.fit(vectors200)
        vectorsN = pca.transform(vectors200)

        return vectorsN

    def get_vectors2(self):
        """ (1) get vectorsN (2) perform reduction to 2 dimension by tsne """
        vectorsN = self.get_vectorsN()

        print "Reducing vectors" + self.pca_dimension +" to vectors2 by tSNE"
        X = np.array(vectorsN)
        model = TSNE(n_components=2, random_state=0)
        np.set_printoptions(suppress=True)
        vectors2 = model.fit_transform(X).tolist()

        return vectors2

    def render(self):
        """ put keys in order and render json file """

        vectors2 = self.get_vectors2()

        filename = re.findall("[a-z|.]+\_*[a-z|.]+\_*[a-z|.]+\.txt", str(self.src_f))
        filename = filename[0][:-4] + ".json"
        print "Writing data to: " + str(self.dst) + "\033[1m" + str(filename) + "\033[0m"

        # f = open(self.dst+"/"+filename, 'w+')
        # for vector in vectors2:
        #     f.write(json.dump(str(vector) + '\n')

        v2_ordered_dict_list = []
        cnt = 0
        for vector, unique_word in zip(vectors2, self.unique_words):
            v2_ordered_dict = OrderedDict()
            cnt += 1
            v2_ordered_dict["index"] = cnt
            v2_ordered_dict["word"] = unique_word
            v2_ordered_dict["vector2"] = str(vector)
            v2_ordered_dict_list.append(NoIndent(v2_ordered_dict))

        f = open(self.dst+"/"+filename, 'w+')
        f.write(json.dumps(v2_ordered_dict_list, indent = 4, cls=NoIndentEncoder))
        print "Done " + str(self.dst) + "\033[1m" + str(filename) + "\033[0m"

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
    lowerDimension = LowerDimension()
    lowerDimension.render()

