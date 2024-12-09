# -*- coding: utf-8 -*-
"""

@author: Ali
"""
import requests as rq # web requests
from bs4 import BeautifulSoup as bs # html parsing
import time # sleep & experimentation
import random as rand # human elements
import re # regex
from socket import error as se # handling socket errors
try:
    from Model.reviewUtils import ReviewUtils # when called from controller
except ModuleNotFoundError:
    from reviewUtils import ReviewUtils # when called from this file (Testing)

# Scraping Class for web-Based Amazon Reviews
class ReviewCollectorHTTP(ReviewUtils):
    def __init__(self, agents_list, products_list):
        super().__init__()
        self.headers = self.get_headers(agents_list)
        self.products_list = self.get_products(products_list)
        self.amz_url = "https://www.amazon.co.uk/product-reviews/"
    
    # Retrieves HTML headers for HTTP use
    def get_headers(self, filename):
        heads = [] 
        agents = self.read_file_unrestricted(filename)
        for x in agents:
            heads.append(({'User-Agent': x,
                           'Accept-Language': 'en-US, en;q=0.5'}))
        return heads
    
    # Retrieves large product list of ASINs
    def get_products(self, filename):
        products = self.read_file_newline(filename)
        return products
    
    # Get html of webpage containing reviews with bs
    def get_reviews_html(self, asin):
        page_no = "/?pageNumber="
        reviews_html = []
        
        for i in range(5):
            time.sleep(rand.uniform(1.0, 1.5))
            url = self.amz_url + asin + page_no + str(i+1)
            print(asin + "... Start")
            try:
                page = rq.get(url, headers=self.headers[2])
            except ConnectionError:
                print("Error: Connection Issues... Sleeping 10 secs")
                time.sleep(10)
                page = rq.get(url, headers=self.headers[2]) 
                
            soup = bs(page.content, "html.parser")
            tmp_soup = soup.find_all(class_="review")
            for r in tmp_soup:
                reviews_html.append(r)
        if len(reviews_html) == 0:
            return 0
        else:
            return reviews_html
    
    # turn html into list of dict, each a review w/ rating
    def html_to_list(self, reviews_html):
        reviews = []
        if len(reviews_html) == 0:
            print("Error: Product not found")
            return 0
        else:
            try:
                for r in reviews_html:
                    # Return bs objects as string
                    review = r.find(class_="review-text").prettify()
                    stars = r.find(class_="review-rating").prettify()  
                    rating = re.search(r"\d+", stars).group()
                    review = self.strip_html(review)
                    review = review + " #rating=" + rating
                    if "class=" in review:
                        continue
                    reviews.append(review)    
                return reviews
            except AttributeError:
                print("Error: Product not found")
                return 0
                
    # regex out html from reviews
    def strip_html(self, review):
        x, y = review.find("<span>"), review.find("</span>")
        review = review[x+6:y].strip()
        review = review.replace('<br>', '')
        review = review.replace('<br/>', '')
        review = review.replace('</br>', '')
        review = review.replace('\'', '\'')
        review = re.sub("\s\s+" , " ", review)
        return review
        
    # HTTP Request Processing & Data Collection - Writes to file
    def scrape_write(self, no_of_products=None, product_file="Model/Data/Products.txt"):
        product_list = self.get_products(product_file)
        if(no_of_products == None):
            no_of_products = len(product_list)
        time_start = time.time()
        
        amz_main = self.amz_url
        count = 0 # Used for user agent rotation
        scraped = 0
        failed = 0
        review_count = 0
        
        # Main product filename
        product_file = product_file
        product_nonexist = "Model/DataBin/ProductsNonexistent.txt"
        if not product_list[0]=='':
            try:
                for x in range(no_of_products):
                    asin = product_list[x]
                    print("(" + str(x+1) + ")" + asin + "... Start")
                    
                    self.update_product_list(product_file) 
                    time.sleep(rand.uniform(3.0, 3.5)) # pause - simulate human behaviour
                    url = amz_main + asin # + "?filterByStar=critical&pageNumber=1"
                    try:
                        page = rq.get(url, headers=self.headers[count]) # rotate user agents
                    except se:
                            product_file = product_file
                            self.append_to_file(asin, product_nonexist)
                            print("Socket Error: Moving To Next")
                            failed+=1
                            continue 
                    except ConnectionError:
                        print("Connection Issues. Sleeping")
                        time.sleep(30)
                        page = rq.get(url, headers=self.headers[count]) # rotate user agents
                        
                    
                    soup = bs(page.content, "html.parser")
                    reviews_html = soup.find_all(class_="review")
                    
                    #reviews = []
                    
                    if len(reviews_html) == 0:
                        print(asin + "... no longer exists.")
                        self.append_to_file(asin, product_nonexist)
                        failed+=1
                    else:
                        try:
                            for r in reviews_html:
                                # Return bs objects as string
                                review = r.find(class_="review-text").prettify()
                                stars = r.find(class_="review-rating").prettify()
                                rating = re.search(r"\d+", stars).group()    
                                # Regex and formatting
                                x, y = review.find("<span>"), review.find("</span>")
                                review = review[x+6:y].strip()
                                review = review.replace('<br>', '')
                                review = review.replace('<br/>', '')
                                review = review.replace('</br>', '')
                                review = review.replace('\'', '\'')
                                review = re.sub("\s\s+" , " ", review)
                                review = review + " #rating=" + rating
                                if "class=" in review:
                                    print("Different Language Found. Skipping Review.")
                                    continue
                                self.append_to_file(review, "Model/Data/RawReviews.txt")         
                                review_count += 1
                            print(asin + "... Processed.")
                            self.append_to_file(asin, "Model/DataBin/ProductsScraped.txt")
                            scraped+=1
                        # user agent rotation sentinel
                        except AttributeError:
                            print(asin + "... no longer exists(U).")
                            failed+=1
                            self.append_to_file(asin, product_nonexist)
                    if(count < 9):
                        count += 1
                    else:
                        count = 0
                    
            except KeyboardInterrupt:
                product_file = product_file
                self.update_product_list(product_file)
                print("Exit: Keyboard Interrupt")
            
            print("--- %s reviews ---" % review_count)                        
            print("--- %s seconds ---" % (time.time() - time_start))
        else:
            print("Error: File is empty.")
        print("Success: " + str(scraped))
        print("Failed: " + str(failed))
