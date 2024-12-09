# -*- coding: utf-8 -*-
"""

@author: Ali
"""

import requests as rq # web requests
from bs4 import BeautifulSoup as bs # html parsing
import time # sleep & experimentation
import random as rand # human elements
import re # regex
import codecs as cd # encode text
import string as s # formatting strings
import json # to read in external json files
import os # file ops
os.chdir(os.path.dirname(os.path.realpath(__file__))) # Make this files dir, working dir

# File Reading by New line
def read_file_newline(path):
    try:
        file = open(path, "r")
        content = file.read()
        file.close()
        return content.split("\n")
    except FileNotFoundError:
        print(path + ", does not exist.")
        exit(1)
        
# Saving Review Data to a File (Multiple in a Dict)
def save_file_reviews(fname, list_, review_key, rating_key):
    file = cd.open(fname, "w+", "utf-8")
    for i in range(len(list_)):
        record = list_[i][review_key] + " #rating=" + list_[i][rating_key] + "\n"
        file.write(record)
    file.close()

# Saving single Dict key-based data to a File
def save_file_key(fname, list_, key):
    file = cd.open(fname, "w+", "utf-8")
    for i in range(len(list_)):
        record = list_[i][key] + "\n"
        file.write(record)
    file.close()


# Defs Remove Punctuation & Add Word Count Values
def remove_punctuation(str_):
    str_ = str_.translate(str.maketrans("", "", s.punctuation))
    return str_

# Count values will aid vectorization
def add_count_values(str_):
    str_ = str_.split()
    review = ""
    for word in str_:
        review = review + word + ":1 "
    return review

# Remove top line from product list file and return removed value
def update_product_list(f_name):
    with open(f_name, 'r') as in_:
        data = in_.read().splitlines(True)
    with open(f_name, 'w') as out_:
        out_.writelines(data[1:])

# Add data to end of file new line
def append_to_file(data, f_name):
    with cd.open(f_name, 'a+', "utf-8") as out_:
        if not data == "":
            out_.write(data + "\n")    

# Extract all values by key
def extract_vals_by_key(list_, key):
    values = []
    for i in range(len(list_)):
        values.append(list_[i][key])
    return values

# Remove list duplicates
def remove_duplicates_list(list_):
    list_ = list(dict.fromkeys(list_))
    return list_

# Get all files from dir path
def get_all_dir_files(path):
        files = []
        for file in os.listdir(path):
            if os.path.isfile(os.path.join(path, file)):
                files.append(file)
        return files
    
# Count lines in file    
def file_count_lines(path):
    count = 0
    file = cd.open(path, 'r', "utf-8", errors="replace")
    contents = file.read().splitlines(True)
    file.close()
    count = len(contents)
    print(path + " (line count):" + str(count))

class DataCollectorHTTP:
    def __init__(self, agents_list, products_list):
        self.headers = self.get_headers(agents_list) 
        self.products_list = self.get_products(products_list)
    
    def get_headers(self, filename):
        heads = [] 
        agents = read_file_newline(filename)
        for x in agents:
            heads.append(({'User-Agent': x,
                           'Accept-Language': 'en-US, en;q=0.5'}))
        return heads
    
    def get_products(self, filename):
        products = read_file_newline(filename)
        return products
    
    # HTTP Request Processing & Data Collection
    def scrape(self, no_of_products=None, product_file="Products.txt"):
        product_list = self.get_products(product_file)
        if(no_of_products == None):
            no_of_products = len(product_list)
        time_start = time.time()
        
        amz_main = "https://www.amazon.com/product-reviews/"
        count = 0 # Used for user agent rotation
        scraped = 0
        failed = 0
        
        # Main product filename
        product_file = product_file
        if not product_list[0]=='':
            try:
                for x in range(no_of_products):
                    asin = product_list[x]
                    print("(" + str(x+1) + ")" + asin + "... Start")
                    
                    update_product_list(product_file) 
                    time.sleep(rand.uniform(2.5, 3.0)) # pause - simulate human behaviour
                    url = amz_main + asin
                    try:    
                        page = rq.get(url, headers=self.headers[count]) # rotate user agents
                    except ConnectionError:
                        print("Connection Issues. Sleeping")
                        time.sleep(30)
                        page = rq.get(url, headers=self.headers[count]) # rotate user agents
                    
                    soup = bs(page.content, "html.parser")
                    reviews_html = soup.find_all(class_="review")
                    
                    #reviews = []
                    
                    if len(reviews_html) == 0:
                        print(str(soup))
                        print(asin + "... no longer exists.")
                        append_to_file(asin, "ProductsNonexistent.txt")
                        failed+=1
                    else:
                        try:
                            for r in reviews_html:
                                # Return bs objects as string
                                review = r.find(class_="review-text").prettify()
                                stars = r.find(class_="review-rating").prettify()
                                # Regex and formatting
                                rating = re.search(r"\d+", stars).group()            
                                x, y = review.find("<span>"), review.find("</span>")
                                review = review[x+6:y].strip()
                                review = review.replace('<br>', '')
                                review = review.replace('<br/>', '')
                                review = review.replace('</br>', '')
                                review = review.replace('\'', '\'')
                                review = re.sub("\s\s+" , " ", review)
                                #review = remove_punctuation(review)
                                #review = add_count_values(review)
                                #reviews.append({'review': review, 'rating': rating})
                                review = review + " #rating=" + rating
                                append_to_file(review, "RawReviews.txt")                   
                            print(asin + "... Processed.")
                            append_to_file(asin, "ProductsScraped.txt")
                            scraped+=1
                        #save_file_reviews("reviews.txt", reviews, "review", "rating")
                        # user agent rotation sentinel
                        except AttributeError:
                            print(asin + "... no longer exists(U).")
                            failed+=1
                            append_to_file(asin, "ProductsNonexistent.txt")
                    if(count < 9):
                        count += 1
                    else:
                        count = 0
                    
            except KeyboardInterrupt:
                product_file = "Products.txt"
                update_product_list(product_file)
                print("Exit: Keyboard Interrupt")
                        
            print("--- %s seconds ---" % (time.time() - time_start))
        else:
            print("Error: File is empty.")
        print("Success: " + str(scraped))
        print("Failed: " + str(failed))
        
class DataCollectorJSON:
    def __init__(self, file_dir):
        self.file_dir = file_dir
        
    # Unfiltered read all of JSON file
    def read_file_json(self, filename):
        all_data = []
        try:
            file = open(self.file_dir + filename, 'r')
            for line in file:
                all_data.append(json.loads(line))
            file.close()
            return all_data
        except FileNotFoundError:
            print("File: " + filename + ", does not exist.")
            
    def get_all_jsons(self):
        json_files = []
        for file in os.listdir(self.file_dir):
            if os.path.isfile(os.path.join(self.file_dir, file)) and file[-5:] == ".json":
                json_files.append(file)
        return json_files
    
    def vals_by_key_unique(self, filename, key):
        values = []
        try:
            file = open(self.file_dir + filename, 'r')
            for line in file:
                record = json.loads(line)
                values.append(record[key])
            file.close()
            values = list(dict.fromkeys(values))
            return values
        except FileNotFoundError:
            print("File: " + filename + ", does not exist.")
                
                
#%% Main

dcw = DataCollectorHTTP("UserAgents.txt", "Products.txt")

#%% Scrape

dcw.scrape(2)

#%% Review Count Check
    
file_count_lines("Products.txt")
file_count_lines("ProductsScraped.txt")
file_count_lines("ProductsNonexistent.txt")
file_count_lines("RawReviews.txt")

# count ratings   
def file_ratings_counts(path):
    ratings = {"five": 0, "four": 0, "three": 0, "two": 0, "one": 0}
    file = cd.open(path, 'r', "utf-8", errors="replace")
    contents = file.read().splitlines(True)
    file.close()
    for r in contents:
        rating = int(r[-2:-1])
        if rating == 5:
            ratings["five"]+=1
        elif rating == 4:
            ratings["four"]+=1
        elif rating == 3:
            ratings["three"]+=1
        elif rating == 2:
            ratings["two"]+=1
        elif rating == 1:
            ratings["one"]+=1
        
    print("5 Star: " + str(ratings["five"]))
    print("4 Star: " + str(ratings["four"]))
    print("3 Star: " + str(ratings["three"]))
    print("2 Star: " + str(ratings["two"]))
    print("1 Star: " + str(ratings["one"]))
        
file_ratings_counts("RawReviews.txt")
    

    

   