# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import urllib, unicodedata
import time, sys, re, random, json, uuid, os
from collections import OrderedDict
from selenium import webdriver

class DataCrawler:
    """ This program aims to (1) crawl menus from tripadvisor official website (2) create json file """

    def __init__(self):
        self.location = ''
        self.url = "https://www.tripadvisor.com/Attraction_Review-g293916-d2209608-Reviews-Wat_Bowonniwet_Vihara-Bangkok.html"
        #self.url = "https://www.tripadvisor.com/Attraction_Review-g293916-d311043-Reviews-Temple_of_the_Reclining_Buddha_Wat_Pho-Bangkok.html"
        self.dst = 'data/attraction_list.json'

    def pause(self):
        """ pause for a few seconds """
        time.sleep(random.randint(1,2))

    def crawl(self, url):
        """ crawl data from tripadvisor official website """

        driver = webdriver.Chrome()
        driver.get(url)

        sys.stdout.write("\rReaching into: %s"%(url))
        try:
            connection = urllib.urlopen(url).getcode()
            if connection == 503:
                print "Error", connection, "(IP Banned)"
                menu.append("Error_503")
            elif connection == 404:
                print "Error:", connection
                menu.append("Error_404")
                #self.pause()
            else:
                print "\nConnection Successful:", connection
                html_data = urllib.urlopen(url).read()
                soup = BeautifulSoup(html_data, "html.parser")

                # get current page
                current_page = soup.find("div", {"class": "pageNumbers"}).find("span").getText()
                # get last page
                for a in soup.find("div", {"class": "pageNumbers"}).findAll("a"):
                    last_page = a.getText()

                sys.stdout.write("\rStatus: %s / %s"%(current_page, last_page))
                sys.stdout.flush()

                # get attraction_name
                attraction_name = soup.find("div", {"class": "heading_name_wrapper"}).find("h1").getText().strip("\n")
                # get avg_rating
                avg_rating = soup.find("div", {"class": "rs rating"}).find("img")['content']
                # get review_count
                review_count = soup.find("div", {"class": "rs rating"}).find("a")['content']
                # get ranking
                ranking = soup.find("div", {"class": "slim_ranking"}).find("b").getText().strip("#")
                # get rating statistics
                rating_stats = []
                for li in soup.find("div", {"class": "histogramCommon simpleHistogram wrap"}).find("ul").findAll("li"):
                    rating_stats.append(li.find("div", {"class": "valueCount fr part"}).getText())
                # get location
                location = soup.find("div", {"class": "slim_ranking"}).find("a").getText()[16:]

                

                driver.execute_script("var elements = document.querySelectorAll('.moreLink');for (var i = 0; i < elements.length; i++) {elements[i].click();}");
                for item in driver.find_elements_by_css_selector(".innerBubble"):
                    print item.text

                #print soup.findAll("div", {"class": "review dyn_full_review inlineReviewUpdate provider0 newFlag"})
                for div in soup.findAll("div", {"class": "review basic_review inlineReviewUpdate provider0 newFlag"}):
                    title = div.find("div", {"class": "quote isNew"}).find("a").find("span").getText()
                    rating = div.find("div", {"class": "rating reviewItemInline"}).find("img")['alt'][0]
                    review = div.find("div", {"class": "entry"}).find("p").getText().strip("\n")
                    #print review

                if int(current_page) <= int(last_page):
                    if "-Reviews-or" in url:
                        insert_position = url.find("-Reviews-or")
                        next_url = url[:insert_position+11] + str(current_page) + "0-" + url[insert_position+14:]
                        #self.pause()
                    else:
                        insert_position = url.find("-Reviews-")
                        next_url = url[:insert_position+9] + "or" + str(current_page) + "0-" + url[insert_position+9:]
                        #self.pause()
                    
                    self.crawl(next_url)

        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

    def render(self):
        """ put things in order and render json file """
        self.crawl(self.url)

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
