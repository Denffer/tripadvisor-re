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
        self.topN = int(sys.argv[2])
        self.locations = []

        self.workbook = xlsxwriter.Workbook('data/excel/all.xlsx')
        self.worksheet = self.workbook.add_worksheet()

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
                            ndcg_list , kendalltau_list = self.process_json_data(json_data)
                            self.locations.append({'location_name':location_name, 'ndcg_list': ndcg_list})

            else:
                print "No file is found"
                print "-"*80

    def filter(self):
      """ filter topN if necessary """
      self.locations = sorted(self.locations, key=itemgetter('ndcg_list'), reverse=True)[:self.topN]
      # print self.locations

    def process_json_data(self, json_data):
        """ proces input json data dict->list """

        ndcg_list = [
                json_data["m_ndcg@10"],
                json_data["b1_ndcg@10"],
                json_data["b2_ndcg@10"],
                json_data["b3_ndcg@10"],
                json_data["b4_ndcg@10"],
                json_data["b5_ndcg@10"]]

        kendalltau_list = [
                json_data["m_kendalltau"],
                json_data["b1_kendalltau"],
                json_data["b2_kendalltau"],
                json_data["b3_kendalltau"],
                json_data["b4_kendalltau"],
                json_data["b5_kendalltau"]]

        return ndcg_list, kendalltau_list

    def customize_column_width(self):
        """ adjust column width according to the longest word """
        location_names = []
        for location in self.locations:
            location_names.append(location['location_name'])

        location_name_length_list = []
        for location_name in location_names:
            location_name_length_list.append(len(location_name))

        self.worksheet.set_column(0, 0, max(location_name_length_list))
        self.worksheet.set_column(1, 6, 11)

    def write_all(self):

         # Write data headers.
        self.worksheet.write('A1', 'NDCG@10', self.title_format)
        self.worksheet.write('B1', 'Methodology', self.title_format)
        self.worksheet.write('C1', 'Baseline1', self.title_format)
        self.worksheet.write('D1', 'Baseline2', self.title_format)
        self.worksheet.write('E1', 'Baseline3', self.title_format)
        self.worksheet.write('F1', 'Baseline4', self.title_format)
        self.worksheet.write('G1', 'Baseline5', self.title_format)

        # Put data into the worksheet.
        row = 0
        for location in self.locations:
            row += 1
            self.worksheet.write(row, 0, location['location_name'], self.location_format)
            column = 0
            for ndcg in location['ndcg_list']:
                column += 1
                if ndcg == max(location['ndcg_list']):
                    self.worksheet.write(row, column, ndcg, self.red_num_format)
                else:
                    self.worksheet.write(row, column, ndcg, self.num_format)

        self.worksheet.write(row+1, 0, "Average", self.title_format)
        self.worksheet.write(row+1, 1, '=AVERAGE(B2:B'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet.write(row+1, 2, '=AVERAGE(C2:C'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet.write(row+1, 3, '=AVERAGE(D2:D'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet.write(row+1, 4, '=AVERAGE(E2:E'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet.write(row+1, 5, '=AVERAGE(F2:F'+ str(len(self.locations)+1) +')', self.avg_num_format)
        self.worksheet.write(row+1, 6, '=AVERAGE(G2:G'+ str(len(self.locations)+1) +')', self.avg_num_format)

        self.workbook.close()

    def run(self):
        self.get_source()
        self.customize_column_width()
        self.filter()
        self.write_all()
        print "-"*80 + "\nDone"


if __name__ == '__main__':
    website = ToExcel()
    website.run()

