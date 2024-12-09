# -*- coding: utf-8 -*-
"""

@author: Ali
"""
import codecs as cd # encode text
import string as s # formatting strings
import os # file ops
from sys import exit # DEBUG exit
from nltk.corpus import stopwords # Natural Language Library - Stopwords
from nltk.tokenize import word_tokenize # Natural Language Library - Tokenizer
from nltk.stem.porter import PorterStemmer # Natural Language Library - Word Stemmer

# Utility Functions for Review Processing
class ReviewUtils:
    def __init__(self):
        pass
    
    # File reading by newline w/encoding restrictions
    def read_file_newline(self, path):
        try:
            file = cd.open(path, "r", "utf-8", errors="replace")
            content = file.read()
            file.close()
            return content.split("\n")
        except FileNotFoundError:
            print(path + ", does not exist.")
            exit(1)
    
    # File read by new line - no encoding restrictions
    def read_file_unrestricted(self, path):        
        try:
            file = open(path, "r")
            content = file.read()
            file.close()
            return content.split("\n")
        except FileNotFoundError:
            print(path + ", does not exist.")
            exit(1)    
            
    # Saving Review Data to a File (Multiple in a Dict)
    def save_file_reviews(self, fname, list_, review_key, rating_key):
        file = cd.open(fname, "w+", "utf-8")
        for i in range(len(list_)):
            record = list_[i][review_key] + " #rating=" + list_[i][rating_key] + "\n"
            file.write(record)
        file.close()
    
    # Saving single Dict key-based data to a File
    def save_file_key(self, fname, list_, key):
        file = cd.open(fname, "w+", "utf-8")
        for i in range(len(list_)):
            record = list_[i][key] + "\n"
            file.write(record)
        file.close()
    
    
    # Defs Remove Punctuation & Add Word Count Values
    def remove_punctuation(self, str_):
        str_ = str_.translate(str.maketrans("", "", s.punctuation))
        return str_
    
    # Count values will aid vectorization
    def add_count_values(self, str_):
        str_ = str_.split()
        review = ""
        for word in str_:
            review = review + word + ":1 "
        return review
    
    # Remove top line from product list file and return removed value
    def update_product_list(self, f_name):
        with open(f_name, 'r') as in_:
            data = in_.read().splitlines(True)
        with open(f_name, 'w') as out_:
            out_.writelines(data[1:])
    
    # Add data to end of file new line
    def append_to_file(self, data, f_name, newline=True):
        with cd.open(f_name, 'a+', "utf-8") as out_:
            if not data == "" and newline:
                out_.write(data + "\n")
            elif not data == "" and not newline:
                out_.write(data)
    
    # Extract all values by key
    def extract_vals_by_key(self, list_, key):
        values = []
        for i in range(len(list_)):
            values.append(list_[i][key])
        return values
    
    # Remove list duplicates
    def remove_duplicates_list(self, list_):
        list_ = list(dict.fromkeys(list_))
        return list_
    
    # Get all files from dir path
    def get_all_dir_files(self, path):
            files = []
            for file in os.listdir(path):
                if os.path.isfile(os.path.join(path, file)):
                    files.append(file)
            return files
        
    # Count lines in file    
    def file_count_lines(self, path):
        count = 0
        file = cd.open(path, 'r', "utf-8", errors="replace")
        contents = file.read().splitlines(True)
        file.close()
        count = len(contents)
        print(path + " (line count):" + str(count))

    def list_to_str(self, list_):
        r = " ".join([w for w in list_])
        return r
    
    def remove_stopwords(self, str_):
        stop_wrds = set(stopwords.words("english"))
        tokens = word_tokenize(str_)
        processed = [s for s in tokens if not s in stop_wrds]
        return processed
    
    def remove_digits(self, str_):
        processed = "".join([d for d in str_ if not d.isdigit()])
        return processed
    
    # Stem all str in list using Porter Stemmer
    def stem_words(self, list_):
        stemmer = PorterStemmer()
        stemmed = [stemmer.stem(w) for w in list_]
        return stemmed
    
    # Apply all preprocessing techniques to a raw review str
    def cleanse_review(self, r, isPos):
        if(isPos):
            r = r[:-1] + ":positive" + r[-1:]
        elif(not isPos):
            r = r[:-1] + ":negative" + r[-1:]
        rating = r[-19:-1]
        r = r[:-19]
        r = self.remove_punctuation(r)
        r = self.remove_digits(r)
        r = r.lower()
        r = self.remove_stopwords(r)
        r = self.stem_words(r)
        r = self.list_to_str(r)
        r = self.add_count_values(r)
        r = r + " " + rating   
        return r
    
    # Write reviews to file - w/ default heuristic of 3 as rating boundry
    def write_reviews(self, pos_count, neg_count, pos_name, neg_name):
        ratings = {"five": 0, "four": 0, "three": 0, "two": 0, "one": 0}
        file = cd.open("Data/RawReviews.txt", 'r', "utf-8", errors="replace")
        contents = file.read().splitlines(True)
        file.close()
        
        pos = 0
        neg = 0
        
        for r in contents:        
            rating = int(r[-2:-1])
            if rating == 5 and pos < pos_count:
                r = self.cleanse_review(r, True)
                self.append_to_file(r, pos_name)
                pos+=1
                ratings["five"]+=1
            elif rating == 4 and pos < pos_count:
                r = self.cleanse_review(r, True)
                self.append_to_file(r, pos_name)
                pos+=1
                ratings["four"]+=1
            elif rating == 3:
                ratings["three"]+=1
            elif rating == 2 and neg < neg_count:
                r = self.cleanse_review(r, False)
                self.append_to_file(r, neg_name)
                neg+=1
                ratings["two"]+=1
            elif rating == 1 and neg < neg_count:
                r = self.cleanse_review(r, False)
                self.append_to_file(r, neg_name)
                neg+=1
                ratings["one"]+=1 
    
    # count ratings' count in file
    def file_ratings_counts(self, path):
        ratings = {"five": 0, "four": 0, "three": 0, "two": 0, "one": 0}
        file = cd.open(path, 'r', "utf-8", errors="replace")
        contents = file.read().splitlines(True)
        file.close()
        
        not_number = 0
        
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
            else:
                not_number+=1
            
        print("5 Star: " + str(ratings["five"]))
        print("4 Star: " + str(ratings["four"]))
        print("3 Star: " + str(ratings["three"]))
        print("2 Star: " + str(ratings["two"]))
        print("1 Star: " + str(ratings["one"]))
        print("Not Number: " + str(not_number))
    
        
#%% Demonstration Purposes

ru = ReviewUtils()

# Apply all preprocessing techniques to a raw review str
def cleanse_review_demo(r, isPos):
    print("#### Before Processing ####" + "\n")
    print(r + "\n")
    if(isPos):
        r = r[:-1] + ":positive" + r[-1:]
    elif(not isPos):
        r = r[:-1] + ":negative" + r[-1:]
    rating = r[-19:-1]
    r = r[:-19]
    print("#### Remove Rating Indicator ####" + "\n")
    print(r + "\n")
    r = ru.remove_punctuation(r)
    print("#### Remove Punctuation ####" + "\n")
    print(r + "\n")
    r = ru.remove_digits(r)
    print("#### Remove Numbers ####" + "\n")
    print(r + "\n")
    r = r.lower()
    r = ru.remove_stopwords(r)
    print("#### Remove Stopwords & Lowercase ####" + "\n")
    print(str(r) + "\n")
    r = ru.stem_words(r)
    print("#### Stem Words ####" + "\n")
    print(str(r) + "\n")
    r = ru.list_to_str(r)
    r = ru.add_count_values(r)
    print("#### Add Count Values ####" + "\n")
    print(r + "\n")
    r = r + " " + rating
    print("#### Add Back Rating Indicator ####" + "\n")
    print(r + "\n")

demo_review = "It surprisingly works better than the broken one <3. #rating=5"
demo_review1 = "worst than the broken one <3. #rating=5"

#cleanse_review_demo(demo_review, True)
#cleanse_review_demo(demo_review1, False)

#ru.file_ratings_counts("Data/ReviewListNo25000.txt")