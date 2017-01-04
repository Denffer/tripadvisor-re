from operator import div
from math import log
import sys, json, os, re, uuid

class NDCG:
    """ This program take ranking.json as input and yield NDCG results """
    def __init__(self):
        self.src = "data/ranking/"
        self.dst = "data/output/NDCG/"

        self.filename = ""
        self.cosine_source = []
        self.dot_source = []

    def get_cosine_source(self):
        """ load all json file in data/ranking/location/cosine/"""
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if "cosine" in dirpath:
                if len(file_list) > 0:
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                    file_cnt = 0
                    length = len(file_list)
                    ranking_dicts_list = []
                    spearmanr_list, kendalltau_list = [], []

                    for f in file_list:
                        # in case there is a goddamn .DS_Store file
                        if str(f) == ".DS_Store":
                            print "Removing " + dirpath + "/" + str(f)
                            os.remove(dirpath+ "/"+ f)
                            break
                        else:
                            file_cnt += 1
                            print "Merging " + str(dirpath) + "/" + str(f)

                            with open(dirpath +"/"+ f) as file:
                                self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                                self.cosine_source.append(json.loads(file.read()))

                else:
                    print "No file is found"
                    print "-"*80
        print "-"*80

    def get_dot_source(self):
        """ load all json file in data/location/ranking/dot/ """
        print "Loading data from: " + self.src
        for dirpath, dir_list, file_list in os.walk(self.src):
            print "Walking into directory: " + str(dirpath)

            if "dot" in dirpath:
                if len(file_list) > 0:
                    print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                    file_cnt = 0
                    length = len(file_list)
                    ranking_dicts_list = []
                    spearmanr_list, kendalltau_list = [], []
                    for f in file_list:
                        # in case there is a goddamn .DS_Store file
                        if str(f) == ".DS_Store":
                            print "Removing " + dirpath + "/" +str(f)
                            os.remove(dirpath+ "/"+ f)
                            break
                        else:
                            file_cnt += 1
                            print "Merging " + str(dirpath) + "/" + str(f)

                            with open(dirpath +"/"+ f) as file:
                                self.filename = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+)-", f).group(1) # E.g. Bangkok
                                self.dot_source.append(json.loads(file.read()))

                else:
                    print "No file is found"
                    print "-"*80
        print "-"*80

    def get_g(self, ranking_dict):
        """ get g """

        computed_rankings = []
        reranked_rankings = []

        if "cosine_ranking" in ranking_dict:
            for x in ranking_dict["cosine_ranking"]:
                computed_rankings.append(x["computed_ranking"])
                reranked_rankings.append(x["reranked_ranking"])
        #  print rankings
        #  print original_rankings
        if "dot_ranking" in ranking_dict:
            for x in ranking_dict["dot_ranking"]:
                computed_rankings.append(x["computed_ranking"])
                reranked_rankings.append(x["reranked_ranking"])

        g = []
        for i, j in zip(computed_rankings, reranked_rankings):
            if int(j)-1 <= int(i) <= int(j)+1:
                g.append(3)
            elif int(j)-2 <= int(i) <= int(j)+2:
                g.append(2)
            elif int(j)-3 <= int(i) <= int(j)+3:
                g.append(1)
            else:
                g.append(0)

        #  print g
        return g

    def get_dcg(self, r):
        return reduce(lambda dcgs, dg: dcgs + [dg+dcgs[-1]], map(lambda(rank, g): (2**g-1)/log(rank+2,2),enumerate(r)), [0])[1:]

    def get_ndcg(self, r):
        return map(div, self.get_dcg(r), self.get_dcg(sorted(r, reverse=True)))

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst)

        if not os.path.exists(dir1):
            print "Creating directory:", self.dst
            os.makedirs(dir1)

    def render(self):

        self.create_dirs()
        self.get_cosine_source()

        ndcg_dict_list = []
        for ranking_dict in self.cosine_source:
            g = self.get_g(ranking_dict)
            ndcg = self.get_ndcg(g)
            ndcg_dict = {"lambda": ranking_dict["lambda"], "g": NoIndent(g), "ndcg": NoIndent(ndcg)}
            ndcg_dict_list.append(ndcg_dict)

        f = open(self.dst + self.filename + "_Cosine.json", "w")
        f.write(json.dumps(ndcg_dict_list, indent=4, cls=NoIndentEncoder))

        self.get_dot_source()
        ndcg_dict_list = []
        for ranking_dict in self.dot_source:
            g = self.get_g(ranking_dict)
            ndcg = self.get_ndcg(g)
            ndcg_dict = {"lambda": ranking_dict["lambda"], "g": NoIndent(g), "ndcg": NoIndent(ndcg)}
            ndcg_dict_list.append(ndcg_dict)

        f = open(self.dst + self.filename + "_Dot.json", "w")
        f.write(json.dumps(ndcg_dict_list, indent=4, cls=NoIndentEncoder))


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
    n = NDCG()
    n.render()

