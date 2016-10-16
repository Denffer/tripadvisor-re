# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib, unicodedata
import time, sys, re, random, json, uuid, os
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import linecache

class DataCrawler:
    """ This program aims to (1) crawl menus from tripadvisor official website (2) create json file """

    def __init__(self):
        """ Initialize Values """
        self.url = "https://www.tripadvisor.com/Attraction_Review-g298570-d451274-Reviews-National_Mosque_Masjid_Negara-Kuala_Lumpur_Wilayah_Persekutuan.html"
        #self.attraction_number = "29"
        self.file_path = ""

        self.next_url = ''
        self.url_flag = 1
        self.file_exist_flag = 0

        self.current_page = 0
        self.last_page = 1
        self.first_entry = 1
        self.previous_review_ordered_dict_list = []

        self.location = "Default Value"
        self.attraction_name = ""
        self.ranking = "Default Value"
        self.avg_rating = ""
        self.rating_stats = ""
        self.review_count = ""
        self.review_info_list = []

        self.verbose = 0
        # Activate Chrome Driver
        self.driver = webdriver.Chrome()

    def pause(self):
        """ pause for a few seconds """
        time.sleep(random.randint(5,5))

    def remove_ads(self):
        try:
            self.driver.find_element_by_class_name("moreLink").click()
        except:
            pass
        try:
            self.driver.find_element_by_class_name("ui_close_x").click()
        except:
            pass
        try:
            self.driver.find_element_by_class_name("moreLink").click()
        except:
            pass

    def crawl(self, url):
        """ crawl data from tripadvisor official website """

        print "Reaching into: " + url
        try:
            connection = urllib.urlopen(url).getcode()
            if connection == 503:
                print "Error", connection, "(IP Banned)"
                menu.append("Error_503")
            elif connection == 404:
                print "Error:", connection
                menu.append("Error_404")
            else:
                print "Connection Successful:", connection
                # let drive load url
                self.driver.get(url)

                self.pause()
                self.remove_ads()
                self.pause()
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                if self.first_entry:
                    # get last page
                    for a in soup.find("div", {"class": "pageNumbers"}).findAll("a"):
                        self.last_page = a.getText()

                    # get attraction_name
                    self.attraction_name = soup.find("div", {"class": "heading_name_wrapper"}).find("h1").getText().strip("\n")
                    # get avg_rating
                    self.avg_rating = soup.find("div", {"class": "rs rating"}).find("img")['content']
                    # get review_count
                    self.review_count = soup.find("label", {"for": "taplc_prodp13n_hr_sur_review_filter_controls_0_filterLang_en"}).find("span").getText().replace("(","").replace(")","")
                    # get ranking
                    self.ranking = soup.find("div", {"class": "slim_ranking"}).find("b").getText().strip("#")
                    # get rating statistics
                    self.rating_stats = []
                    for li in soup.find("div", {"class": "histogramCommon simpleHistogram wrap"}).find("ul").findAll("li"):
                        self.rating_stats.append(li.find("div", {"class": "valueCount fr part"}).getText())
                    # get location
                    tmp_text = soup.find("div", {"class": "slim_ranking"}).find("a").getText()
                    self.location = re.search('in (\w+.*)', tmp_text).group(1)

                    self.first_entry = 0
                    self.current_page = soup.find("span", {"class": "pageNum current"}).getText()
                    self.current_page = int(self.current_page) - 1
                    #print self.current_page
                    self.check_file()
                else:
                    pass

                self.pause()
                self.remove_ads()
                self.pause()
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                print "This is attraction " + self.ranking + " in " + self.location
                # add 1 current page
                self.current_page = int(self.current_page) + 1

                review_cnt = 0
                # Crawl the first review out of ten reviews
                try:
                    #self.driver.execute_script("if (document.querySelector('.ui_close_x')) {document.querySelector('.ui_close_x').click()};")
                    #WebDriverWait(self.driver, timeout=3).until(lambda x: x.find_element_by_class_name('track_back'))
                    div = soup.find("div", {"class": "track_back"})
                    review_cnt += 1
                    try:
                        #WebDriverWait(self.driver, timeout=10).until(lambda x: x.find_element_by_class_name('dyn_full_review'))
                        review = div.find("div", {"class": "dyn_full_review"}).find("div", {"class": "entry"}).find("p").getText().strip("\n")
                        print str(review_cnt) + ". full review: " + review
                    except:
                        review = div.find("div", {"class": "entry"}).find("p").getText().strip("\n")
                        print str(review_cnt) + ". basic review: " + review

                    title = div.find("div", {"class": "quote"}).find("span").getText()
                    rating = div.find("div", {"class": "rating"}).find("img")['alt'][0]
                    self.review_info_list.append([title, rating, review])
                except:
                    print "No div of 'track_back' is found"

                # Crawl the remaining nine reviews out of ten reviews
                try:
                    #self.driver.execute_script("if (document.querySelector('.ui_close_x')) {document.querySelector('.ui_close_x').click()};")
                    #WebDriverWait(self.driver, timeout=3).until(lambda x: x.find_element_by_class_name('reviewSelector  '))
                    for div in soup.findAll("div", {"class": "reviewSelector  "}):
                        review_cnt += 1
                        try:
                            #WebDriverWait(self.driver, timeout=10).until(lambda x: x.find_element_by_class_name('dyn_full_review'))
                            review = div.find("div", {"class": "dyn_full_review"}).find("div", {"class": "entry"}).find("p").getText().strip("\n")
                            print str(review_cnt) + ". full review: " + review
                        except:
                            review = div.find("div", {"class": "entry"}).find("p").getText().strip("\n")
                            print str(review_cnt) + ". basic review: " + review

                        title = div.find("div", {"class": "quote"}).find("span").getText()
                        rating = div.find("div", {"class": "rating"}).find("img")['alt'][0]
                        self.review_info_list.append([title, rating, review])
                except:
                    self.PrintException()
                    print "No div of 'reviewSelector' is found"

                try:
                    if int(self.current_page) < int(self.last_page):

                        if "-Reviews-or" in url:
                            self.next_url = re.sub(r"-or\d+0-", "-or" + str(self.current_page*10) + "-", url)
                        else:
                            head_position = url.find("-Reviews-")
                            self.next_url = url[:head_position+9] + "or" + str(self.current_page*10) + "-" + url[head_position+9:]

                        sys.stdout.write("\rStatus: %s / %s\n"%(self.current_page, self.last_page))
                        sys.stdout.flush()
                        print "-"*120

                        self.crawl(self.next_url)
                    else:
                        sys.stdout.write("\rStatus: %s / %s\n"%(self.current_page, self.last_page))
                        sys.stdout.flush()
                        print "-"*120
                        print "No Next Page is Detected"
                        self.url_flag = 0
                        #pass
                except:
                    self.PrintException()
                    pass
        except:
            self.PrintException()
            pass

    def check_file(self):
        """ check if the file is existed and continue to crawl"""
        self.file_path = "data/" + self.location.encode('utf-8').lower() + "/attraction_" + self.ranking + ".json"
        print "Checking the existence of the file: " + self.file_path
        try:
            if os.path.isfile(self.file_path):
                f = open(self.file_path, 'r')
                print "The file in the path: " + self.file_path + " is found"
                data = json.load(f)

                for review_dict in data["reviews"]:
                    self.review_info_list.append([review_dict["title"], review_dict["rating"], review_dict["review"]])
                # file exist so review count would not start from 1
                self.file_exist_flag = 1
                print "Continue to crawl from: " + self.url
            else:
                print "No file in the path:" + self.file_path + " is found"
                print "Start Crawling from the beginning"
                print "-"*120
        except:
            self.PrintException()
            pass

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print '    Exception in ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

    def create_dir(self):
        """ create the directory if not exist"""
        directory = "data/" + self.location.encode('utf-8').lower() + "/"
        dir1 = os.path.dirname(directory)
        if not os.path.exists(dir1):
            print "Making directory: " + directory
            os.makedirs(dir1)

    def render(self):
        """ put things in order and render json file """
        self.crawl(self.url)
        self.create_dir()

        print "-"*120
        print "Putting data in ordered json format"

        attraction_ordered_dict = OrderedDict()
        if self.url_flag:
            attraction_ordered_dict["next_url"] = self.next_url
        attraction_ordered_dict["location"] = self.location
        attraction_ordered_dict["attraction_name"] = self.attraction_name
        attraction_ordered_dict["ranking"] = self.ranking
        attraction_ordered_dict["avg_rating"] = self.avg_rating
        attraction_ordered_dict["rating_stats"] = self.rating_stats
        attraction_ordered_dict["review_count"] = self.review_count
        rating_stats_dict = OrderedDict()
        rating_stats_dict["excellent"] = self.rating_stats[0]
        rating_stats_dict["very good"] = self.rating_stats[1]
        rating_stats_dict["average"] = self.rating_stats[2]
        rating_stats_dict["poor"] = self.rating_stats[3]
        rating_stats_dict["terrible"] = self.rating_stats[4]

        attraction_ordered_dict["rating_stats"] = NoIndent(rating_stats_dict)

        review_ordered_dict_list = []
        review_cnt = 0
        for review_info in self.review_info_list:
            review_ordered_dict = OrderedDict()
            review_cnt += 1
            review_ordered_dict["index"] = review_cnt
            review_ordered_dict["title"] = review_info[0]
            review_ordered_dict["rating"] = review_info[1]
            review_ordered_dict["review"] = review_info[2]
            review_ordered_dict_list.append(review_ordered_dict)

        attraction_ordered_dict["reviews"] = review_ordered_dict_list

        print "Writing data to:", self.file_path
        f = open(self.file_path, 'w+')
        f.write( json.dumps( attraction_ordered_dict, indent = 4, cls=NoIndentEncoder))
        self.driver.close()
        print "Done"

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
    crawler = DataCrawler()
    crawler.render()


