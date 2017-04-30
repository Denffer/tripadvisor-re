import xlsxwriter
import os, json, re, sys
from operator import itemgetter

class ToExcel:
    """ This program aims to
        (1) take data/results/location as input
        (2) render into data/excel/
    """

    def __init__(self):
        self.src = "data/result"
        self.dst_name = "Reranked_NDCG_Results.xlsx"
        #self.topN = int(sys.argv[2])
        self.dst_dir = "data/excel/"
        self.locations = []

        self.workbook = xlsxwriter.Workbook(self.dst_dir + self.dst_name)
        self.worksheets = []
        self.worksheet1 = self.workbook.add_worksheet('ndcg@5')
        self.worksheets.append(self.worksheet1)
        self.worksheet2 = self.workbook.add_worksheet('ndcg@10')
        self.worksheets.append(self.worksheet2)
        self.worksheet3 = self.workbook.add_worksheet('ndcg@20')
        self.worksheets.append(self.worksheet3)

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
      # print self.locations

    def process_json_data(self, json_data):
        """ proces input json data dict->list """

        ndcg5_list = [
                json_data["lineXopinion_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXopinion_top_all_avg_ndcg@5"],
                json_data["lineXstar5_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXstar5_top_all_avg_ndcg@5"],
                json_data["lineXstar4_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXstar4_top_all_avg_ndcg@5"],
                json_data["lineXstar3_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXstar3_top_all_avg_ndcg@5"],
                json_data["lineXstar2_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXstar2_top_all_avg_ndcg@5"],
                json_data["lineXstar1_top_all_sum_cXnf_ndcg@5"],
                json_data["lineXstar1_top_all_avg_ndcg@5"],
                json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@5"],
                json_data["word2vecXopinion_top_all_avg_ndcg@5"],
                json_data["word2vecXstar5_top_all_sum_cXnf_ndcg@5"],
                json_data["word2vecXstar5_top_all_avg_ndcg@5"],
                json_data["b1_ndcg@5"],
                json_data["b2_ndcg@5"],
                json_data["b3_ndcg@5"]]

        ndcg10_list = [
                json_data["lineXopinion_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXopinion_top_all_avg_ndcg@10"],
                json_data["lineXstar5_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXstar5_top_all_avg_ndcg@10"],
                json_data["lineXstar4_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXstar4_top_all_avg_ndcg@10"],
                json_data["lineXstar3_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXstar3_top_all_avg_ndcg@10"],
                json_data["lineXstar2_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXstar2_top_all_avg_ndcg@10"],
                json_data["lineXstar1_top_all_sum_cXnf_ndcg@10"],
                json_data["lineXstar1_top_all_avg_ndcg@10"],
                json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@10"],
                json_data["word2vecXopinion_top_all_avg_ndcg@10"],
                json_data["word2vecXstar5_top_all_sum_cXnf_ndcg@10"],
                json_data["word2vecXstar5_top_all_avg_ndcg@10"],
                json_data["b1_ndcg@10"],
                json_data["b2_ndcg@10"],
                json_data["b3_ndcg@10"]]

        ndcg20_list = [
                json_data["lineXopinion_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXopinion_top_all_avg_ndcg@20"],
                json_data["lineXstar5_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXstar5_top_all_avg_ndcg@20"],
                json_data["lineXstar4_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXstar4_top_all_avg_ndcg@20"],
                json_data["lineXstar3_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXstar3_top_all_avg_ndcg@20"],
                json_data["lineXstar2_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXstar2_top_all_avg_ndcg@20"],
                json_data["lineXstar1_top_all_sum_cXnf_ndcg@20"],
                json_data["lineXstar1_top_all_avg_ndcg@20"],
                json_data["word2vecXopinion_top_all_sum_cXnf_ndcg@20"],
                json_data["word2vecXopinion_top_all_avg_ndcg@20"],
                json_data["word2vecXstar5_top_all_sum_cXnf_ndcg@20"],
                json_data["word2vecXstar5_top_all_avg_ndcg@20"],
                json_data["b1_ndcg@20"],
                json_data["b2_ndcg@20"],
                json_data["b3_ndcg@20"]]

        kendalltau_list = [
                json_data["lineXopinion_top_all_sum_cXnf_kendalltau"],
                json_data["lineXopinion_top_all_avg_kendalltau"],
                json_data["lineXstar5_top_all_sum_cXnf_kendalltau"],
                json_data["lineXstar5_top_all_avg_kendalltau"],
                json_data["lineXstar4_top_all_sum_cXnf_kendalltau"],
                json_data["lineXstar4_top_all_avg_kendalltau"],
                json_data["lineXstar3_top_all_sum_cXnf_kendalltau"],
                json_data["lineXstar3_top_all_avg_kendalltau"],
                json_data["lineXstar2_top_all_sum_cXnf_kendalltau"],
                json_data["lineXstar2_top_all_avg_kendalltau"],
                json_data["lineXstar1_top_all_sum_cXnf_kendalltau"],
                json_data["lineXstar1_top_all_avg_kendalltau"],
                json_data["word2vecXopinion_top_all_sum_cXnf_kendalltau"],
                json_data["word2vecXopinion_top_all_avg_kendalltau"],
                json_data["word2vecXstar5_top_all_sum_cXnf_kendalltau"],
                json_data["word2vecXstar5_top_all_avg_kendalltau"],
                json_data["b1_kendalltau"],
                json_data["b2_kendalltau"],
                json_data["b3_kendalltau"]]

        # decide how many columns
        self.column_num = len(ndcg5_list)
        #print self.column_num
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
        for worksheet in self.worksheets:
            worksheet.set_column(0, 0, max(location_name_length_list))
            worksheet.set_column(1, self.column_num, 16)

    def write_excel(self):
        """ render output to data/excel/ """

        index = ["A1","B1","C1","D1","E1","F1","G1","H1","I1","J1","K1","L1","M1","N1","O1","P1","Q1","R1","S1","T1"]
        ndcg_N = ["5","10","20"]
        # loop through worksheet1~3
        for worksheet, n in zip(self.worksheets, ndcg_N):
            print "Writing " + "\033[1m" + worksheet.name + "\033[0m"

            # Write data headers.
            worksheet.write(index[0], 'NDCG@'+n, self.title_format)
            worksheet.write(index[1], 'lineXopinion_cXnf', self.title_format)
            worksheet.write(index[2], 'lineXopinion_Avg', self.title_format)
            worksheet.write(index[3], 'lineXstar5_cXnf', self.title_format)
            worksheet.write(index[4], 'lineXstar5_Avg', self.title_format)
            worksheet.write(index[5], 'lineXstar4_cXnf', self.title_format)
            worksheet.write(index[6], 'lineXstar4_Avg', self.title_format)
            worksheet.write(index[7], 'lineXstar3_cXnf', self.title_format)
            worksheet.write(index[8], 'lineXstar3_Avg', self.title_format)
            worksheet.write(index[9], 'lineXstar2_cXnf', self.title_format)
            worksheet.write(index[10], 'lineXstar2_Avg', self.title_format)
            worksheet.write(index[11], 'lineXstar1_cXnf', self.title_format)
            worksheet.write(index[12], 'lineXstar1_Avg', self.title_format)
            worksheet.write(index[13], 'word2vecXopinion_cXnf', self.title_format)
            worksheet.write(index[14], 'word2vecXopinion_Avg', self.title_format)
            worksheet.write(index[15], 'word2vecXstar5_cXnf', self.title_format)
            worksheet.write(index[16], 'word2vecXstar5_Avg', self.title_format)
            worksheet.write(index[17], 'Baseline1', self.title_format)
            worksheet.write(index[18], 'Baseline2', self.title_format)
            worksheet.write(index[19], 'Baseline3', self.title_format)

        # Put data into the worksheet.
        row = 0
        for location in self.locations:
            row += 1
            for worksheet in self.worksheets:
                worksheet.write(row, 0, location['location_name'], self.location_format)
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

        for worksheet in self.worksheets:
            worksheet.write(row+1, 0, "Average", self.title_format)
            worksheet.write(row+1, 1, '=AVERAGE(B2:B'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 2, '=AVERAGE(C2:C'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 3, '=AVERAGE(D2:D'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 4, '=AVERAGE(E2:E'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 5, '=AVERAGE(F2:F'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 6, '=AVERAGE(G2:G'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 7, '=AVERAGE(H2:H'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 8, '=AVERAGE(I2:I'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 9, '=AVERAGE(J2:J'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 10, '=AVERAGE(K2:K'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 11, '=AVERAGE(L2:L'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 12, '=AVERAGE(M2:M'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 13, '=AVERAGE(N2:N'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 14, '=AVERAGE(O2:O'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 15, '=AVERAGE(P2:P'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 16, '=AVERAGE(P2:P'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 17, '=AVERAGE(P2:P'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 18, '=AVERAGE(P2:P'+ str(len(self.locations)+1) +')', self.avg_num_format)
            worksheet.write(row+1, 19, '=AVERAGE(P2:P'+ str(len(self.locations)+1) +')', self.avg_num_format)

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
        self.write_excel()

        print "Done"

if __name__ == '__main__':
    website = ToExcel()
    website.run()

