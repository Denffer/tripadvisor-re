# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import urllib, unicodedata
import time, sys, re, random, json, uuid, os
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

class DataCrawler:
    """ This program aims to (1) crawl menus from tripadvisor official website (2) create json file """

    def __init__(self):
        """ Initialize Values """
        self.url = "https://www.tripadvisor.com/Attraction_Review-g293916-d311046-Reviews-Temple_of_the_Golden_Buddha_Wat_Traimit-Bangkok.html"
        self.dst = 'data/attraction_11.json'
        self.current_page = 0
        self.last_page = 1
        self.first_entry = 1
        self.soup = ""

        self.location = ""
        self.attraction_name = ""
        self.ranking = ""
        self.avg_rating = ""
        self.rating_stats = ""
        self.review_count = ""

        self.review_info_list = []

        # Activate Chrome Driver
        self.driver = webdriver.Chrome()

    def pause(self):
        """ pause for a few seconds """
        time.sleep(random.randint(4,7))

    def crawl(self, url):
        """ crawl data from tripadvisor official website """

        print "Reaching into: " + url
        #sys.stdout.write("\rReaching into: %s"%(url))
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

                if self.first_entry == 1:
                     # execute javascript to click on all 'more'
                    self.driver.execute_script("if (document.querySelector('.ui_close_x')) {document.querySelector('.ui_close_x').click()};")
                    self.driver.execute_script("document.querySelector('.ulBlueLinks').click();")

                    #self.pause()
                else:
                    pass

                self.driver.execute_script("document.querySelector('.ulBlueLinks').click();")

                # Put page_source in beautiful soup

                #WebDriverWait(self.driver, timeout=10).until(lambda x: x.find_element_by_class_name('entry'))

                self.pause()
                soup = BeautifulSoup(self.driver.page_source, "html.parser")



                if self.first_entry == 1:
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
                    self.location = soup.find("div", {"class": "slim_ranking"}).find("a").getText()[16:]
                    self.first_entry = 0
                else:
                    pass

                # add 1 current page
                self.current_page += 1

                # get full review
                for div in soup.findAll("div", {"class": "dyn_full_review"}):
                    title = div.find("span", {"class": "noQuotes"}).getText()
                    rating = div.find("div", {"class": "rating"}).find("img")['alt'][0]
                    review = div.find("div", {"class": "entry"}).find("p").getText().strip("\n")
                    print "review:" + review
                    self.review_info_list.append([title, rating, review])

                if int(self.current_page) < int(self.last_page):

                    if "-Reviews-or" in url:
                        insert_position = url.find("-Reviews-or")
                        next_url = url[:insert_position+11] + str(self.current_page*10) + "-" + url[insert_position+12+len(str(self.current_page*10)):]
                    else:
                        insert_position = url.find("-Reviews-")
                        next_url = url[:insert_position+9] + "or" + str(self.current_page*10) + "-" + url[insert_position+9:]

                    sys.stdout.write("\rStatus: %s / %s\n"%(self.current_page, self.last_page))
                    sys.stdout.flush()

                    #self.pause()
                    self.crawl(next_url)
                else:
                    print "Page error:", sys.exc_info()[0]
                    pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def render(self):
        """ put things in order and render json file """
        self.crawl(self.url)

        print "-"*100
        print "Putting data in ordered json format"

        attraction_ordered_dict = OrderedDict()
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

        print "Writing data to:", self.dst
        f = open(self.dst, 'w+')
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


