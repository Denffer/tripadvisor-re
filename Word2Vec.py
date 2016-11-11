import sys, os, uuid, json, gensim, itertools

class Word2Vec:
    """ A python implementation on Word2Vector"""
    def __init__(self):
        """ initalize paths """
        self.src = "data/word2vec_input/corpus.txt"
        self.dst_uw = "data/coreProcess/unique_words.txt"
        self.dst_v200 = "data/coreProcess/vectors200.txt"
        self.dst_ld_v200 = "data/lower_dimension/vectors200.txt"

        self.verbose = 1

    def get_corpus(self):
        """ get reviews in corpus """
        print "Loading data from:", self.src

        with open(self.src) as f:
            corpus = f.readlines()

        #print corpus
        return corpus

    def get_sentences(self):
        """ get a list of lists of words | E.g. sentences = [["sentence","one"], ["sentence","two"]] """
        corpus = self.get_corpus()

        sentences = []
        for sentence in corpus:
            #print sentence
            sentences.append(sentence.split())

        #print sentences
        return sentences

    def run_word2vec(self):
        """ run word to vector """
        sentences = self.get_sentences()

        print '-'*80
        print "Running Word2Vec"
        model = gensim.models.Word2Vec(sentences, min_count=5, size=200, window = 10, workers=4)
        unique_words = list(model.vocab.keys())

        vectors200 = []
        for word in unique_words:
            vectors200.append(model[word].tolist())

        #print unique_words, vectors200
        return unique_words, vectors200

    def create_folder(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname("data/coreProcess/")
        dir2 = os.path.dirname("data/lower_dimension/")
        if not os.path.exists(dir1):   # if the directory does not exist
            print "Creating directory:", dir1
            os.makedirs(dir1)          # create the directory
        if not os.path.exists(dir2):   # if the directory does not exist
            print "Creating directory:", dir2
            os.makedirs(dir2)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors200 = self.run_word2vec()
        self.create_folder()

        print "-"*80
        print "Writing data to " + "\033[1m" + self.dst_uw + "\033[0m"
        with open(self.dst_uw, 'w+') as f_uw:
            for word in unique_words:
                f_uw.write( word + "\n")

        print "Writing data to " + "\033[1m" + self.dst_v200 + "\033[0m"
        with open(self.dst_v200, 'w+') as f_v200:
            for vector in vectors200:
                f_v200.write(str(vector) + '\n')

        print "Writing data to " + "\033[1m" + self.dst_ld_v200 + "\033[0m"
        with open(self.dst_ld_v200, 'w+') as f_ld_v200:
            for vector in vectors200:
                for dimension in vector:
                    f_ld_v200.write(str(dimension) + ' ')
                f_ld_v200.write("\n")

if __name__ == '__main__':
    word2vec = Word2Vec()
    word2vec.render()

