# -*- coding: utf-8 -*-
"""

@author: Ali
"""

import numpy as np
from random import shuffle
import time # DEBUG - For loop optimizing
import os # file ops
#os.chdir(os.path.dirname(os.path.realpath(__file__))) # Uncomment when running exp
from sys import exit
import matplotlib.pyplot as plt # Math plotting library
import tensorflow as tf # Deep Learning Interface
from keras import models, layers # Deep Learning Interface
try:
    from Model.reviewUtils import ReviewUtils # when called from controller
except ModuleNotFoundError:
    from reviewUtils import ReviewUtils # when called from this file (Testing)

# Deep Learning network & experiment use  
class NetworkModel(ReviewUtils):
    def __init__(self, data, split_point, total, index_size, exp=False, start=1):
        super().__init__()
        if(exp == True):
            os.chdir(os.path.dirname(os.path.realpath(__file__))) # Make this files dir, working dir     
        self.data_pos, self.data_neg = self.create_data_splits(data, split_point, total)
        self.index_size = index_size
        self.start = start
        self.index = dict({})
        self.indexize_list(self.data_pos)
        self.indexize_list(self.data_neg)
        self.dict_words = self.create_word_dict()
        self.x_train = None
        self.y_train = None
        self.x_val = None
        self.y_val = None
        self.x_test = None
        self.y_test = None
        self.x_values, self.y_values = self.create_dataset(self.data_pos, self.data_neg)
        self.x_train, self.y_train, self.x_val, self.y_val, self.x_test, self.y_test = self.create_subsets(self.x_values, self.y_values)
        self.network = None
        self.h_dict = None
    
    # Splits unordered raw data into ordered data based on pos/neg - file or list
    # Split point 0 = Inclusive pos 3, -1 = Inclusive neg 3
    def create_data_splits(self, raw_data, split_point, total=10000):
        data_pos = []
        data_neg = []
        ratings_limits = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        print(str(ratings_limits))
        if isinstance(raw_data, str):
            raw_reviews = self.read_file_newline(raw_data)
        elif isinstance(raw_data, list):
            raw_reviews = raw_data             
        
        pos_ratings, neg_ratings = self.get_split_config(split_point)
        pos_weight, neg_weight = self.get_split_weight(split_point)
        
        # Set weight ratios for equal data distribution
        if split_point == 4:
            ratings_limits["5"] = total*pos_weight #p
            ratings_limits["3"] = total*neg_weight #n
            ratings_limits["2"] = total*neg_weight #n
            ratings_limits["1"] = total*neg_weight #n
        elif split_point == 3:
            ratings_limits["5"] = total*pos_weight #p 
            ratings_limits["4"] = total*pos_weight #p
            ratings_limits["2"] = total*neg_weight #n
            ratings_limits["1"] = total*neg_weight #n
        elif split_point == 2:
            ratings_limits["5"] = total*pos_weight #p
            ratings_limits["4"] = total*pos_weight #p
            ratings_limits["3"] = total*pos_weight #p
            ratings_limits["1"] = total*neg_weight #n
        elif split_point < 2:
            if split_point == 0:
                ratings_limits["5"] = total*pos_weight #p
                ratings_limits["4"] = total*pos_weight #p
                ratings_limits["3"] = total*pos_weight #p
                ratings_limits["2"] = total*neg_weight #n
                ratings_limits["1"] = total*neg_weight #n
            elif split_point == -1:
                ratings_limits["5"] = total*pos_weight #p
                ratings_limits["4"] = total*pos_weight #p
                ratings_limits["3"] = total*neg_weight #n
                ratings_limits["2"] = total*neg_weight #n
                ratings_limits["1"] = total*neg_weight #n
        else:
            print("Error: Incorrect split weights")
            exit(1)

        data_pos, pos_count = self.get_split_data(pos_ratings, raw_reviews,
                                                  ratings_limits, split_point)
        data_neg, neg_count = self.get_split_data(neg_ratings, raw_reviews,
                                                  ratings_limits, split_point)
        
        print("Positives: ", str(pos_count))
        print("Negatives: ", str(neg_count))
        print(str(ratings_limits))
        return data_pos, data_neg        

    # Extract positive/negative reviews from raw reviews
    def get_split_data(self, ratings_list, raw_reviews, ratings_limits, split_point=3):
        data = []
        count = 0
        for n in ratings_list:
            i = 0
            for l in raw_reviews:
                try:
                    rating = int(l[-1])
                except ValueError:
                    continue
                except IndexError:
                    continue
                if rating == int(n) and i <= ratings_limits[str(rating)]:
                    if split_point > 0:
                        if rating > split_point:
                            l = self.cleanse_review(l, True)
                        else: 
                            l = self.cleanse_review(l, False)
                    if split_point == 0:
                        if rating > 2:
                            l = self.cleanse_review(l, True)
                        else:
                            l = self.cleanse_review(l, False)
                    if split_point < 0:
                        if rating > 3:
                            l = self.cleanse_review(l, True)
                        else:
                            l = self.cleanse_review(l, False)
                    data.append(l)
                    i+=1
                    count+=1
        return data, count
                    
    # Return weight based on split point for data distribution
    def get_split_weight(self, split_point):
        if split_point == 4:
            return 0.5, 0.1666666667
        if split_point == 3:
            return 0.25, 0.25
        if split_point == 2:
            return 0.1666666667, 0.5
        if split_point == 0: # Default to an inclusive 3 as pos
            return 0.1333333337, 0.25
        if split_point == -1:
            return 0.25, 0.1333333337
        else:
            print("Error: Wrong split point given")
            exit(1) 
    
    # Get values which equate to pos/neg based on split point
    def get_split_config(self, split_point):
        if split_point == 4:
            return [5], [3, 2, 1]
        if split_point == 3:
            return [5, 4], [2, 1]
        if split_point == 2:
            return [5, 4, 3], [1]
        if split_point == 0:
            return [5, 4, 3], [2, 1]
        if split_point == -1:
            return [5, 4], [3, 2, 1]
        else:
            print("Error: Wrong split point given")
            exit(1)      
    
    # For use in indexize_list & indexize_file
    def indexize_loop(self, item):
        l = item.split()
        for i,s in enumerate(l):
            wordi, n = s.split(':')
            if not("#" in wordi):
                freq = self.index.get(wordi, 0)
                self.index[wordi]=freq+1
                
    # Take data from list and indexize words
    def indexize_list(self, list_):
        m=0
        if isinstance(list_, list):
            for item in list_:
                m = m+1
                self.indexize_loop(item)
    
    # Take data from file and indexize words
    def indexize_file(self, file):
        m=0
        with open(file, encoding="utf-8", errors="replace") as infile:
            for line in infile:
                m = m+1
                self.indexize_loop(line)
     
    # Create dictionary of words (in inverse order)
    def create_word_dict(self):
        ordered_index = sorted(self.index.items(), key=lambda x: x[1], reverse=True)
        words = [w for (w,v) in ordered_index if v >1 ]
        words = words[self.start:self.index_size+self.start] # pulls out highest freq words starting with pos start
        dict_words = dict([(k,i) for (i,k) in enumerate(words)]) # creates the index
        return dict_words
        
    # Read Sentances into their respective codes based on dictionary (File)
    def read_sentances_file(self, file):
        all_sents = []
        all_coded = []
        
        # m = 0 sentance count, not used
        with open(file, encoding="utf-8", errors="replace") as infile:
            for line in infile:
                l = line.split()
                one_sent = []
                one_code = []
                
                # m = m+m
                for i, s in enumerate(l):
                    wordi, n = s.split(":")
                    if not("#" in wordi):
                        one_sent.append(wordi)
                        code = self.dict_words.get(wordi, None)
                        if code == None:
                            one_code.append(0)
                        else:
                            one_code.append(code)
                            
                all_sents.append(one_sent)
                all_coded.append(one_code)
        return all_sents, all_coded
    
    # Read Sentances into their respective codes based on dictionary (List)
    def read_sentances_list(self, list_):
       all_sents = []
       all_coded = []
       
       # m = 0 sentance count, not used
       for line in list_:
           l = line.split()
           one_sent = []
           one_code = []
            
           # m = m+m
           for i, s in enumerate(l):
               wordi, n = s.split(":")
               if not("#" in wordi):
                   one_sent.append(wordi)
                   code = self.dict_words.get(wordi, None)
                   if code == None:
                       one_code.append(0)
                   else:
                       one_code.append(code)
                        
           all_sents.append(one_sent)
           all_coded.append(one_code)
       return all_sents, all_coded
    
    # Vectorise sentences for processing
    def vectorize(self, sequences, dimension=10000):
        results = np.zeros((len(sequences), dimension)) # array of zeors
        for i, seq in enumerate(sequences):
            results[i, seq] = 1
        return results
    
    # Read the sentences, produce the coded versions and create the data set including labels
    def create_dataset(self, data_pos, data_neg):
        positive_sents, positive_coded = self.read_sentances_list(data_pos)
        negative_sents, negative_coded = self.read_sentances_list(data_neg)
        
        postive_vectorized= self.vectorize(positive_coded,self.index_size)
        negative_vectorized = self.vectorize(negative_coded,self.index_size)
            
        y_positives = np.ones(len(postive_vectorized), dtype='float32')
        y_negatives = np.zeros(len(negative_vectorized),dtype='float32')
        
        y_values = np.hstack([y_positives,y_negatives])
        x_values = np.vstack([postive_vectorized, negative_vectorized ])
        print('shape of x_values',x_values.shape)
        print('shape of y_values',y_values.shape)   
        
        return x_values, y_values
        
    # Shuffle the data set and create the training, validation, testing set    
    def create_subsets(self, x_values, y_values):
        inds = np.arange(len(y_values))
        np.random.shuffle(inds)
        x_values = x_values[inds, :]
        y_values = y_values[inds]
        
        len_sample = len(y_values)
        len_train = np.trunc(len_sample*0.4).astype(int)
        len_test = np.trunc(len_sample*0.8).astype(int)
        
        x_train = x_values[0:len_train,:] # train set
        y_train = y_values[0:len_train]        
        x_val = x_values[len_train:len_test] # validation set
        y_val = y_values[len_train:len_test]
        x_test = x_values[len_test:] # test set
        y_test = y_values[len_test:]
        
        return x_train, y_train, x_val, y_val, x_test, y_test
    
    # Create a single dataset based on values provided (no splits for test/validation etc.) 
    def create_single_set(self, x_values, y_values):
        inds = np.arange(len(y_values))
        x_values = x_values[inds, :]
        y_values = y_values[inds]
        return x_values, y_values
       
    def shuffle_sets(self):
        self.x_train, self.y_train, self.x_val, self.y_val, self.x_test, self.y_test = [],[],[],[],[],[]
        self.x_train, self.y_train, self.x_val, self.y_val, self.x_test, self.y_test = self.create_subsets(self.x_values, self.y_values)
        
        
    # Define the network
    def create_network(self):
        network = models.Sequential()
        network.add(layers.Dense(64, activation='relu', input_shape=(self.index_size,)))
        network.add(layers.Dropout(0.5))
        network.add(layers.Dense(64, activation='relu'))
        network.add(layers.Dropout(0.5))
        network.add(layers.Dense(1, activation='sigmoid'))
        network.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
        print("Network Created")
        return network
    
    # Train Network
    def fit_network(self):
        hist = self.network.fit(self.x_train,self.y_train, epochs=20,
                                batch_size=64, validation_data=(self.x_val,self.y_val))
        return hist.history
    
    # Plot Training & Accuracy results
    def plot_results(self, hist, y1=None, y2=None, t1=None):
        acc = hist['accuracy']
        val_acc= hist['val_accuracy']
        
        eps = range(1,len(acc)+1)
        
        plt.plot(eps,acc,'b',label='Training Acc. (training)')
        plt.plot(eps,val_acc,label='Val Acc.(training)')
        if y1 != None:
            plt.scatter(x=20, y=(float(t1)/100), marker="o", color="darkred", zorder=4, label="Test Acc. (post-training)")
            plt.vlines(x=20, ymin=(y1/100), ymax=(y2/100), colors='red', ls='-', lw=2, label="Confidence Interval")      
        plt.legend()
        plt.show()
        
    # Automated predicted accuracy - does not allow for confidence intervals
    def eval_network(self, x_vals, y_vals):
        results = self.network.evaluate(x_vals, y_vals)
        #tf.compat.v1.reset_default_graph()
        print("Test Acc. (Automated): ", results[1])
    
    # Manually predicted accuracy - allows for confidence intervals
    def pred_network(self, x_test, y_test, return_i, return_p=False):
        predictions = self.network.predict_classes(x_test)
        N = len(predictions)
        S = (predictions.flatten()==y_test.flatten()).sum()
        p = (S/N)
        
        # Deriving confidence
        var_f = np.sqrt((p*(1-p)/N))
        z_value, z_interval = self.get_conf_limit(99.9)
        var_p = z_value * var_f
        tf.compat.v1.reset_default_graph() # reset tensorflow graph
        if return_p:
            return predictions
        else:
            p1 = round(((p-var_p)*100), 2)
            p2 = round(((p+var_p)*100), 2)
            t1 = str(round((p*100), 2))
            print("##############################################################", "\n")
            print("Test Acc. (Manual): ", str(round((p*100), 2)), "%", "\n")
            print("With", str(z_interval), "% confidence, p lies between"
              , str(p1), "% and", str(p2), "%", "\n")
            print("##############################################################", "\n")
            return p1, p2, t1
        
    # Get confidence limit - Experiments use 99.8% Confidence interval    
    def get_conf_limit(self, p):
        if p > 99.4:
            return 3.09, 99.8
        elif p <= 99.4 and p >= 98.5:
            return 2.58, 99.0
        elif p <= 98.4 and p >= 94.0:
            return 2.33, 98.0
        elif p <= 93.9 and p >= 85.0:
            return 1.65, 90.0
        elif p <= 84.9 and p >= 70.0:
            return 1.28, 80.0
        elif p <= 69.9 and p >= 40.0:
            return 0.84, 60.0
        elif p <= 39.9:
            return 0.25, 20.0
 
"""

# Retreive review data for use in experiments
ru = ReviewUtils()
review_list = ru.read_file_newline("Data/ReviewList25000.txt")  
review_list_unseen = ru.read_file_newline("Data/ReviewListNo25000.txt")  
shuffle(review_list)
shuffle(review_list_unseen)
  
"""  
  
#"""

# Model Required for repeating experiments

#nm = NetworkModel(review_list, 3, 25000, 10000, True) # Normal Split - Excludes 3 stars in train
#nm = NetworkModel(review_list, 0, 25000, 10000, True) # 3 stars in training as positive
#nm = NetworkModel(review_list, -1, 25000, 10000, True) # 3 stars in training as negative

#"""


#%% Experiment - Baseline of whichever NetworkModel is used

"""
exp_baseline_results = []

def exp_baseline():
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_pos, count = nm.get_split_data([5,4], review_list_unseen, {"5": 1000.0, "4": 1000.0})
    data_neg, count = nm.get_split_data([2,1], review_list_unseen, {"1": 1000.0, "2": 1000.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]  
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)
    
for x in range(10):
    exp_baseline()

"""
#%% Experiment - Baseline w/3-star reviews as positive in test set

"""
exp_baseline_threestar_pos_results = []

def exp_baseline_threestar_pos():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_pos, count = nm.get_split_data([3], review_list_unseen, {"3": 4000.0}, 0)
    data_neg, count = nm.get_split_data([1], review_list_unseen, {"1": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_threestar_pos_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_threestar_pos()
"""

#%% Experiment - Baseline w/3-star reviews as negative in test set

"""
exp_baseline_threestar_neg_results = []

def exp_baseline_threestar_neg():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_neg, count = nm.get_split_data([3], review_list_unseen, {"3": 4000.0}, -1)
    data_pos, count = nm.get_split_data([5], review_list_unseen, {"5": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_threestar_neg_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_threestar_neg()
"""

#%% Experiment - Baseline w/5-star reviews as positive in test set

"""
exp_baseline_fivestar_pos_results = []

def exp_baseline_fivestar_pos():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_pos, count = nm.get_split_data([5], review_list_unseen, {"5": 4000.0})
    data_neg, count = nm.get_split_data([1], review_list_unseen, {"1": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_fivestar_pos_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_fivestar_pos()

"""

#%% Experiment - Baseline w/4-star reviews as positive in test set

"""
exp_baseline_fourstar_pos_results = []

def exp_baseline_fourstar_pos():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_pos, count = nm.get_split_data([4], review_list_unseen, {"4": 4000.0})
    data_neg, count = nm.get_split_data([1], review_list_unseen, {"1": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_fourstar_pos_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_fourstar_pos()
"""

#%% Experiment - Baseline w/2-star reviews as negative in test set

"""
exp_baseline_twostar_neg_results = []

def exp_baseline_twostar_neg():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_neg, count = nm.get_split_data([2], review_list_unseen, {"2": 4000.0})
    data_pos, count = nm.get_split_data([5], review_list_unseen, {"5": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_twostar_neg_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_twostar_neg()
"""

#%% Experiment - Baseline w/1-star reviews as negative in test set

"""
exp_baseline_onestar_neg_results = []

def exp_baseline_onestar_neg():
    shuffle(review_list_unseen)
    nm.network = nm.create_network()
    tf.compat.v1.reset_default_graph()
    nm.shuffle_sets()
    nm.h_dict = nm.fit_network()
    data_neg, count = nm.get_split_data([1], review_list_unseen, {"1": 4000.0})
    data_pos, count = nm.get_split_data([5], review_list_unseen, {"5": 1.0})
    x, y = nm.create_dataset(data_pos, data_neg)
    x_vals, y_vals = nm.create_single_set(x, y)
    inds = np.arange(len(y_vals))
    x_values = x_vals[inds, :]
    y_values = y_vals[inds]                
    p1, p2, t1 = nm.pred_network(x_values, y_values, True)
    exp_baseline_onestar_neg_results.append([t1, p1, p2])
    nm.plot_results(nm.h_dict, p1, p2, t1)

for x in range(10):     
    exp_baseline_onestar_neg()
"""




