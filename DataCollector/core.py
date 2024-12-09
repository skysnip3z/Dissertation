# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 20:36:09 2020

@author: Skysnip3z
"""

import dataCollection as dc

dc1 = dc.DataCollector("UserAgents.txt", "Products.txt")
review_data = dc1.scrape(3)
dc1.save_file_newline("reviews.txt", review_data)