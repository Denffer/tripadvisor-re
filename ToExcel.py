import xlsxwriter
import os, json, re, sys
from operator import itemgetter

class ToExcel:
    """ This program aims to
        (1) take data/results/location as input
        (2) render into data/excel/
    """

    def __init__(self):
        self.src = sys.argv[1]
        self.dst_name = "Reranked_NDCG_Results.xlsx"
        #self.topN = int(sys.argv[2])
        self.dst_dir = "data/excel/"
        self.locations = []

        self.workbook = xlsxwriter.Workbook(self.dst_dir + self.dst_name)
        self.worksheet1 = self.workbook.add_worksheet('ndcg@5')
        self.worksheet2 = self.workbook.add_worksheet('ndcg@10')
        self.worksheet3 = self.workbook.add_worksheet('ndcg@20')

        self.title_format = self.workbook.add_format({'bold': True, 'align': 'center'})
        self.location_format = self.workbook.add_format({'align': 'center'})
        self.num_format = self.workbook.add_format({'num_format': '0.0000', 'align': 'center'})
        self.red_num_format = self.workbook.add_format({'num_format': '0.0000', 'align': 'center', 'color': 'red'})
        self.avg_num_format = self.workbook.add_format({'num_format': '0.0000', 'align': 'center', 'bg_color': 'C0C0C0'})

    def get_source(self):
        """ load data from data/results/ """
        for dirpath, dir_list, file_list in os.walk("data/results/"):
            print "Walking into directory: " + str(dirpath)

            # in case there is a goddamn .DS_Store file
            if len(file_list) > 0:
                print "Files found: " + "\033[1m" + str(file_list) + "\033[0m"

                for f in file_list:
                    if str(f) == ".DS_Store":
                        print "Removing " + dirpath + str(f)
                        os.remove(dirpath + "/" +f)
                    else:
                        print "Appending " + "\033[1m" + str(f) + "\033[0m" + " into source"
                        location_name = re.search("([A-Za-z|.]+\_*[A-Za-z|.]+\_*[A-Za-z|.]+).json", f).group(1)
                        with open(dirpath +"/"+ f) as file:
                            json_data = json.load(file)
                            ndcg5_list, ndcg10_list, ndcg20_list , kendalltau_list = self.process_json_data(json_data)
                            self.locations.append({'location_name':location_name, 'ndcg5_list': ndcg5_list, 'ndcg10_list': ndcg10_list, 'ndcg20_list': ndcg20_list})

            else:
                print "No file is found"
        print "-"*80

    def filter(self):
      """ filter topN if necessary """
      self.locations = sorted(self.locations, key=itemgetter('ndcg5_list'), reverse=True)[:self.topN]
      self.locations = sorted(self.locations, key=itemgetter('ndcg10_list'), reverse=True)[:self.topN]
      # print self.locations

    def process_json_data(self, json_data):
        """ proces input json data dict->list """

        ndcg5_list = [
                #json_data["sum_cXf_ndcg@5"],
                json_data["top_all_sum_cXnf_ndcg@5"],
                json_data["top_all_sum_zXnf_ndcg@5"],
                #json_data["top5_ndcg@5"],
                #json_data["top50_ndcg@5"],
                #json_data["top100_ndcg@5"],
                #json_data["sum_ndcg@5"],
                #json_data["max_ndcg@5"],
                json_data["top_all_avg_ndcg@5"],
                json_data["b1_ndcg@5"],
                json_data["b2_ndcg@5"]]

        ndcg10_list = [
                #json_data["top_all_sum_cXf_ndcg@10"],
                json_data["top_all_sum_cXnf_ndcg@10"],
                json_data["top_all_sum_zXnf_ndcg@10"],
                #  json_data["top5_ndcg@10"],
                #  json_data["top50_ndcg@10"],
                #  json_data["top100_ndcg@10"],
                #  json_data["sum_ndcg@10"],
                #  json_data["max_ndcg@10"],
                json_data["top_all_avg_ndcg@10"],
                json_data["b1_ndcg@10"],
                json_data["b2_ndcg@10"]]

        ndcg20_list = [
                #json_data["sum_cXf_ndcg@20"],
                json_data["top_all_sum_cXnf_ndcg@20"],
                json_data["top_all_sum_zXnf_ndcg@20"],
                #  json_data["top5_ndcg@20"],
                #  json_data["top50_ndcg@20"],
                #  json_data["top100_ndcg@20"],
                #  json_data["sum_ndcg@20"],
                #  json_data["max_ndcg@20"],
                json_data["top_all_avg_ndcg@20"],
                json_data["b1_ndcg@20"],
                json_data["b2_ndcg@20"]]

        kendalltau_list = [
                #json_data["sum_cXf_kendalltau"],
                json_data["top_all_sum_cXnf_kendalltau"],
                json_data["top_all_sum_zXnf_kendalltau"],
                #  json_data["top5_kendalltau"],
                #  json_data["top50_kendalltau"],
                #  json_data["top100_kendalltau"],
                #  json_data["sum_kendalltau"],
                #  json_data["max_kendalltau"],
                json_data["top_all_avg_kendalltau"],
                json_data["b1_kendalltau"],
                json_data["b2_kendalltau"]]

        # decide how many columns
        self.methodology_length = len(ndcg5_list)
        return ndcg5_list, ndcg10_list, ndcg20_list, kendalltau_list

    def customize_column_width(self):
        """ adjust column width according to the longest word """

        print "Customizing width of columns ..."
        location_names = []
        for location in self.locations:
            location_names.append(location['location_name'])

        location_name_length_list = []
        for location_name in location_names:
            location_name_length_list.append(len(location_name))

        # first column list out all the location
        self.worksheet1.set_column(0, 0, max(location_name_length_list))
        self.worksheet2.set_column(0, 0, max(location_name_length_list))
        self.worksheet3.set_column(0, 0, max(location_name_length_list))
        # second parameter depends on how many methodology to compare
        self.worksheet1.set_column(1, self.methodology_length, 14)
        self.worksheet2.set_column(1, self.methodology_length, 14)
        self.worksheet3.set_column(1, self.methodology_length, 14)

    def write_ndcg(self):

        print "Writing " + "\033[1m" + self.worksheet1.name + "\033[0m" + " & " + "\033[1m" + self.worksheet2.name + "\033[0m" + " & " + "\033[1m" + self.worksheet3.name + "\033[0m"
         # Write data headers.
        self.worksheet1.write('A1', 'NDCG@5', self.title_format)
        #  self.worksheet1.write('B1', 'Sum_cXf_Cosine', self.title_format)
        self.worksheet1.write('B1', 'Sum_cXnf_Cosine', self.title_format)
        self.worksheet1.write('C1', 'Sum_zXnf_Cosine', self.title_format)
        #  self.worksheet1.write('E1', 'Top5_zScore', self.title_format)
        #  self.worksheet1.write('F1', 'Top50_zScore', self.title_format)
        #  self.worksheet1.write('G1', 'Top100_zScore', self.title_format)
        #  self.worksheet1.write('H1', 'Sum_Cosine', self.title_format)
        #  self.worksheet1.write('I1', 'Max_Cosine', self.title_format)
        self.worksheet1.write('D1', 'Avg_Cosine', self.title_format)
        self.worksheet1.write('E1', 'Baseline1', self.title_format)
        self.worksheet1.write('F1', 'Baseline2', self.title_format)

         # Write data headers.
        self.worksheet2.write('A1', 'NDCG@10', self.title_format)
        #self.worksheet2.write('B1', 'Sum_cXf_Cosine', self.title_format)
        self.worksheet2.write('B1', 'Sum_cXnf_Cosine', self.title_format)
        self.worksheet2.write('C1', 'Sum_zXnf_Cosine', self.title_format)
        #self.worksheet2.write('E1', 'Top5_zScore', self.title_format)
        #  self.worksheet2.write('F1', 'Top50_zScore', self.title_format)
        #  self.worksheet2.write('G1', 'Top100_zScore', self.title_format)
        #  self.worksheet2.write('H1', 'Sum_Cosine', self.title_format)
        #  self.worksheet2.write('I1', 'Max_Cosine', self.title_format)
        self.worksheet2.write('D1', 'Avg_Cosine', self.title_format)
        self.worksheet2.write('E1', 'Baseline1', self.title_format)
        self.worksheet2.write('F1', 'Baseline2', self.title_format)

         # Write data headers.
        self.worksheet3.write('A1', 'NDCG@20', self.title_format)
        #self.worksheet3.write('B1', 'Sum_cXf_Cosine', self.title_format)
        self.worksheet3.write('B1', 'Sum_cXnf_Cosine', self.title_format)
        self.worksheet3.write('C1', 'Sum_zXnf_Cosine', self.title_format)
        #self.worksheet3.write('E1', 'Top5_zScore', self.title_format)
        #self.worksheet3.write('F1', 'Top50_zScore', self.title_format)
        #self.worksheet3.write('G1', 'Top100_zScore', self.title_format)
        #self.worksheet3.write('H1', 'Sum_Cosine', self.title_format)
        #self.worksheet3.write('I1', 'Max_Cosine', self.title_format)
        self.worksheet3.write('D1', 'Avg_Cosine', self.title_format)
        self.worksheet3.write('E1', 'Baseline1', self.title_format)
        self.worksheet3.write('F1', 'Baseline2', self.title_format)

        # Put data into the worksheet.
        row = 0
        for location in self.locations:
            row += 1
            self.worksheet1.write(row, 0, location['location_name'], self.location_format)
            self.worksheet2.write(row, 0, location['location_name'], self.location_format)
            self.worksheet3.write(row, 0, location['location_name'], self.location_format)
            column = 0
            for ndcg5, ndcg10, ndcg20 in zip(location['ndcg5_list'], location['ndcg10_list'], location['ndcg20_list']):
                column += 1
                if ndcg5 == max(location['ndcg5_list']):
                    self.worksheet1.write(row, column, ndcg5, self.red_num_format)
                else:
                    self.worksheet1.write(row, column, ndcg5, self.num_format)

                if ndcg10 == max(location['ndcg10_list']):
                    self.worksheet2.write(row, column, ndcg10, self.red_num_format)
                else:
                    self.worksheet2.write(row, column, ndcg10, self.num_format)

                if ndcg20 == max(location['ndcg20_list']):
                    self.worksheet3.write(row, column, ndcg20, self.red_num_format)
                else:
                    self.worksheet3.write(row, column, ndcg20, self.num_format)

        self.worksheet1.write(row+1, 0, "Average", self.title_format)
        self.worksheet1.write(row+1, 1, '=AVERAGE(B2:B'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet1.write(row+1, 2, '=AVERAGE(C2:C'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet1.write(row+1, 3, '=AVERAGE(D2:D'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet1.write(row+1, 4, '=AVERAGE(E2:E'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet1.write(row+1, 5, '=AVERAGE(F2:F'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 6, '=AVERAGE(G2:G'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 7, '=AVERAGE(H2:H'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 8, '=AVERAGE(I2:I'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 9, '=AVERAGE(J2:J'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 10, '=AVERAGE(K2:K'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet1.write(row+1, 11, '=AVERAGE(L2:L'+ str(len(self.locations)+1) +')', self.avg_num_format)

        self.worksheet2.write(row+1, 0, "Average", self.title_format)
        self.worksheet2.write(row+1, 1, '=AVERAGE(B2:B'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet2.write(row+1, 2, '=AVERAGE(C2:C'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet2.write(row+1, 3, '=AVERAGE(D2:D'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet2.write(row+1, 4, '=AVERAGE(E2:E'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet2.write(row+1, 5, '=AVERAGE(F2:F'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 6, '=AVERAGE(G2:G'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 7, '=AVERAGE(H2:H'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 8, '=AVERAGE(I2:I'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 9, '=AVERAGE(J2:J'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 10, '=AVERAGE(K2:K'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet2.write(row+1, 11, '=AVERAGE(L2:L'+ str(len(self.locations)+1) +')', self.avg_num_format)

        self.worksheet3.write(row+1, 0, "Average", self.title_format)
        self.worksheet3.write(row+1, 1, '=AVERAGE(B2:B'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet3.write(row+1, 2, '=AVERAGE(C2:C'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet3.write(row+1, 3, '=AVERAGE(D2:D'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet3.write(row+1, 4, '=AVERAGE(E2:E'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet3.write(row+1, 5, '=AVERAGE(F2:F'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 6, '=AVERAGE(G2:G'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 7, '=AVERAGE(H2:H'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 8, '=AVERAGE(I2:I'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 9, '=AVERAGE(J2:J'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 10, '=AVERAGE(K2:K'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #  self.worksheet3.write(row+1, 11, '=AVERAGE(L2:L'+ str(len(self.locations)+1) +')', self.avg_num_format)
        #
        print "-"*80 + "\nSaving " + "\033[1m" + str(self.dst_name) + "\033[0m" + " in " + str(self.dst_dir)
        self.workbook.close()

    def create_dir(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname(self.dst_dir)

        if not os.path.exists(dir1):
            print "Creating directory: " + dir1
            os.makedirs(dir1)

    def run(self):
        self.get_source()
        self.customize_column_width()
        #self.filter()
        self.write_ndcg()

        print "Done"

if __name__ == '__main__':
    website = ToExcel()
    website.run()

