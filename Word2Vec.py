import sys, re, os, uuid, json, gensim, itertools

class Word2Vec:
    """ A python implementation on Word2Vector """
    def __init__(self):
        """ initalize paths """

        self.src = sys.argv[1]
        if "starred_corpus" in self.src:
            self.filename = "starred_corpus"
            self.dst_v200 = "data/word2vec/starred/" + self.filename + ".txt"
        else:
            self.filename = re.search("([A-Za-z|.]+\-*[A-Za-z|.]+\-*[A-Za-z|.]+).txt", self.src).group(1)
            self.dst_v200 = "data/word2vec/" + self.filename + ".txt"

        self.verbose = 1
        self.window_size = 3
        self.dimension = 200

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
        model = gensim.models.Word2Vec(sentences, min_count=20, size = self.dimension, window = self.window_size, workers=4)
        unique_words = list(model.vocab.keys())

        vectors200 = []
        for word in unique_words:
            vectors200.append(model[word].tolist())

        #print unique_words, vectors200
        return unique_words, vectors200

    def create_dirs(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname(self.dst_v200)
        if not os.path.exists(dir1):   # if the directory does not exist
            print "Creating directory:", dir1
            os.makedirs(dir1)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors200 = self.run_word2vec()
        self.create_dirs()

        print "Writing data to " + "\033[1m" + self.dst_v200 + "\033[0m"
        with open(self.dst_v200, 'w+') as f_v200:
            f_v200.write(str(len(unique_words)) + " " + "200" + "\n")
            for word, vector in zip(unique_words, vectors200):
                f_v200.write( word + " ")
                for element in vector:
                    f_v200.write(str(element) + ' ')
                f_v200.write("\n")

        print "-"*80

if __name__ == '__main__':
    word2vec = Word2Vec()
    word2vec.render()

