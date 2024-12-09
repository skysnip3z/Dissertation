# -*- coding: utf-8 -*-
"""

@author: Ali
"""
import os # file ops
import codecs as cd # encode text
import numpy as np
os.chdir(os.path.dirname(os.path.realpath(__file__))) # Make this files dir, working dir
from tkinter.filedialog import asksaveasfile # Save File Dialog
from tkinter.filedialog import askopenfile # Load File Dialog
from Model.reviewCollectorHTTP import ReviewCollectorHTTP # Review Retrieval Class
from Model.networkModel import NetworkModel # Deep Learning Network Model
try:
    import view as v
except ModuleNotFoundError:
    print("Error: Module Import Bug")
from keras import models

# MVC Architecture - Controller
class Controller:
    def __init__(self, view_=True):
        self.collector_model = ReviewCollectorHTTP("Model/Data/UserAgents.txt", "Model/Data/Products.txt")
        self.network_model = NetworkModel("Model/Data/ReviewList25000.txt", 3, 1000, 10000)
        self.network_model.network = models.load_model("baseline")
        self.view = v.View(self)
        self.search_mode = 1
        self.reviews = None
        self.preds = None
        
    # Mode: 0 - Simple(Amazon-Based)
    #       1 - Predictive(fully predictive)
    #       2 - Adaptive(review length-based)    
    def get_review_data(self, asin):
        reviews_html = self.collector_model.get_reviews_html(asin)
        if reviews_html == 0:
            return 0
        elif isinstance(reviews_html, list):
            tmp_reviews = self.collector_model.html_to_list(reviews_html)
            tmp_reviews = self.remove_from_list(tmp_reviews, "rating=3")
            reviews = []
            ratings = [5, 4, 2, 1]
            
            for rat in range(len(ratings)):
                for rev in tmp_reviews:
                    if ("rating=" + str(ratings[rat])) in rev:
                        reviews.append(rev)
            try:
                pos_reviews, neg_reviews = self.network_model.create_data_splits(reviews, 3, 1000)
                x, y = self.network_model.create_dataset(pos_reviews, neg_reviews)
                x_vals, y_vals = self.network_model.create_single_set(x, y)
                self.preds = self.network_model.pred_network(x_vals, y_vals, False, True)
                
                data = []
                for i in range(len(reviews)):
                    try: 
                        reviews[i] = cd.encode(reviews[i], "utf-8", errors="replace") 
                        if self.search_mode == 1:
                            data.append([self.get_rating_simple(reviews[i]), reviews[i]])
                        elif self.search_mode == 2:
                            data.append([self.preds[i], reviews[i]])
                        elif self.search_mode == 3:
                            if len(reviews[i]) > 50:
                                data.append([self.preds[i], reviews[i]])
                            else:
                                data.append([self.get_rating_simple(reviews[i]), reviews[i]])       
                    except IndexError:
                        print("Tkinter Interface Index Bug")
                self.reviews = data
                return data    
            except UnboundLocalError:
                return 0
        else:
            return 0
    
    def get_rating_simple(self, review):
        if "rating=5" in str(review) or "rating=4" in str(review):
            print(str(type(review)))
            print(review)
            print("POS")
            return np.array([1])
        elif "rating=2" in str(review) or "rating=1" in str(review):
            print(str(type(review)))
            print(review)
            print("NEG")
            return np.array([0])
    
    def remove_from_list(self, list_, val):
        return [vals for vals in list_ if val not in vals]
    
    def set_search_mode(self, val):
        self.search_mode = val
        print("Search Mode:" + str(self.search_mode))
    
    def save_reviews(self):
        file = asksaveasfile(defaultextension=".txt", 
                             filetype=[("Text Document", "*.txt")], mode="w")
        if file is None:
            return 0
        for i in range(len(self.reviews)):
            r = cd.decode(self.reviews[i][1], "utf-8", errors="replace")
            file.write(str(self.reviews[i][0]) + "," + r + "\n")
        file.close()
    
    def load_reviews(self):
        file = askopenfile()
        if file is None:
            return []
        if ".txt" not in str(file):
            return []
        with open(file.name) as infile:
            tmp_data = infile.readlines()
        infile.close()
        data = []
        for x in tmp_data:
            try:
                r = x[4:-1] # review
                r_encoded = cd.encode(r, "utf-8", errors="replace") 
                data.append([np.array([int(x[1])]), r_encoded]) # sentiment + review
            except ValueError:
                return []
            
        self.reviews = data
        return data
    
    def start_application(self):
        self.view.start_view()
        
        
#%% Start App

c = Controller()
c.start_application()