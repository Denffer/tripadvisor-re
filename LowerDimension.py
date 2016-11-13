import json, uuid
import numpy as np
from sklearn import decomposition
from sklearn.manifold import TSNE

class LowerDimension:
    """ This program aims to reduce vectors of 200 dimension to 2 dimension (shortcut)"""

    def __init__(self):
        self.src = "./data/coreProcess/vectors200.txt"
        self.dst = "./data/coreProcess/vectors2.txt"

    def get_vectors200(self):
        """ append every crawled business_list into source """

        print "Loading data from:", self.src

        vectors200 = []
        with open(self.src) as f:
            for line in f:
                #print line
                vectors200.append(json.loads(line))

        #print vectors200
        return vectors200

    def get_vectors50(self):
        """ (1) get vectors200 (2) perform reduction to 50 dimension by pca """
        vecotrs200 = self.get_vectors200()

        print "Reducing vectors200 to vectors50 by pca"
        pca = decomposition.PCA(n_components=50)
        pca.fit(vecotrs200)
        vectors50 = pca.transform(vecotrs200).tolist()

        return vectors50

    def get_vectors2(self):
        """ (1) get vectors50 (2) perform reduction to 2 dimension by tsne """
        vectors50 = self.get_vectors50()

        print "Reducing vectors50 to vectors2 by tSNE"
        X = np.array(vectors50)
        model = TSNE(n_components=2, random_state=0)
        np.set_printoptions(suppress=True)
        vectors2 = model.fit_transform(X).tolist()

        return vectors2

    def render(self):
        """ put keys in order and render json file """

        vectors2 = self.get_vectors2()
        print "Writing data to:", self.dst

        f = open(self.dst, 'w+')
        for vector in vectors2:
            f.write(str(vector) + '\n')

        print "Done"

if __name__ == '__main__':
    lowerDimension = LowerDimension()
    lowerDimension.render()

