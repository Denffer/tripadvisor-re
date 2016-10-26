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
        self.url = "https://www.tripadvisor.com/Attraction_Review-g294217-d593230-Reviews-Deep_Water_Bay-Hong_Kong.html"

        self.super_attraction_ranking = ""
        self.super_attraction_name = ""
        self.location = "" # Customize location
        self.ranking = "" # Customize ranking

        self.file_path, self.next_url = "", ""
        self.current_page, self.last_page = 0, 0
        self.previous_review_ordered_dict_list = []

        self.attraction_name, self.attraction_type, self.avg_rating, self.rating_stats, self.review_count = "", "", "", "", ""
        self.review_info_list = []

        self.driver = webdriver.Chrome()  # Activate Chrome Driver

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

                """ Check if this is the first entry """
                if not self.attraction_name:

                    # get attraction_name
                    self.attraction_name = soup.find("div", {"class": "heading_name_wrapper"}).find("h1").getText().replace(" ", "_").strip("\n")
                    # get avg_rating
                    self.avg_rating = soup.find("div", {"class": "rs rating"}).find("img")['content']
                    # get review_count
                    self.review_count = soup.find("label", {"for": "taplc_prodp13n_hr_sur_review_filter_controls_0_filterLang_en"}).find("span").getText().replace("(","").replace(")","")
                    # get ranking
                    if not self.ranking:
                        self.ranking = soup.find("div", {"class": "slim_ranking"}).find("b").getText().strip("#")
                    # get rating statistics
                    self.rating_stats = []
                    for li in soup.find("div", {"class": "histogramCommon simpleHistogram wrap"}).find("ul").findAll("li"):
                        self.rating_stats.append(li.find("div", {"class": "valueCount fr part"}).getText())
                    # get attraction_type & location
                    tmp_text = soup.find("div", {"class": "slim_ranking"}).find("a").getText()
                    self.attraction_type = re.search('(\w+.*) in', tmp_text).group(1).replace(" ","_")
                    if not self.location:
                        self.location = re.search('in (\w+.*)', tmp_text).group(1).replace(" ","_")

                    # get current_page
                    self.current_page = soup.find("span", {"class": "pageNum current"}).getText()
                    self.current_page = int(self.current_page) - 1
                    # get last_page
                    for a in soup.find("div", {"class": "pageNumbers"}).findAll("a"):
                        self.last_page = a.getText()

                    # Check if file exists
                    self.check_file()
                else:
                    pass

                self.pause()
                self.remove_ads()
                self.pause()
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                print "This is " + self.attraction_type + " " + self.ranking + " in " + self.location
                print "Attraction Name: " + self.attraction_name + " | Super Attraction Name: " + self.super_attraction_name
                # add 1 current page
                self.current_page = int(self.current_page) + 1

                review_cnt = 0
                # Crawl the first review out of ten reviews
                try:
                    div = soup.find("div", {"class": "track_back"})
                    review_cnt += 1
                    try:
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
                    for div in soup.findAll("div", {"class": "reviewSelector  "}):
                        review_cnt += 1
                        try:
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
                        self.next_url = ""

                except:
                    self.PrintException()
                    pass
        except:
            self.PrintException()
            pass

    def check_file(self):
        """ check if the file is existed and continue to crawl """
        if self.super_attraction_name:
            self.file_path = "data/" + self.location.encode('utf-8').lower() + "/attraction_" + self.super_attraction_ranking + "/tour" + "_" + self.ranking + ".json"
        else:
            self.file_path = "data/" + self.location.encode('utf-8').lower() + "/attraction_" + self.ranking + ".json"
        print "Checking if the file exists: " + self.file_path
        try:
            if os.path.isfile(self.file_path):
                f = open(self.file_path, 'r')
                print "The file in the path: " + self.file_path + " is found"

                data = json.load(f)
                for review_dict in data["reviews"]:
                    self.review_info_list.append([review_dict["title"], review_dict["rating"], review_dict["review"]])

                print "Continue to crawl from: " + self.url
                print "-"*120
            else:
                print "NO file: " + self.file_path + " is found"
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
        """ create the directory if not exist """
        if self.super_attraction_name:
            directory = "data/" + self.location.encode('utf-8').lower() + "/attraction_" + self.super_attraction_ranking + "/"
        else:
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
        if self.next_url:
            attraction_ordered_dict["next_url"] = self.next_url
        attraction_ordered_dict["location"] = self.location
        if self.super_attraction_name:
            attraction_ordered_dict["super_attraction_name"] = self.super_attraction_name
        if self.super_attraction_ranking:
            attraction_ordered_dict["super_attraction_ranking"] = self.super_attraction_ranking
        attraction_ordered_dict["attraction_name"] = self.attraction_name
        attraction_ordered_dict["attraction_type"] = self.attraction_type
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


