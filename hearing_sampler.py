
# coding: utf-8

# In[1]:

get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')


# In[7]:

import os
import re
import pandas as pd
from random import shuffle
os.chdir("C:\Users\Jeff\Documents\hearings\docs")


# Go through all hearings. If the combo of congress, chamber, and committee is unique/new, add the file name to our list.

# In[15]:

all_files = os.listdir('.')
shuffle(all_files)

meta_tracker = []
strat_sample = []

for i in all_files:
    split = re.split("_",i)
    congress = split[0]
    chamber = split[1]
    committee = split[2]
    
    if chamber == 'Joint Hearings':
        continue
    
    meta = congress+"_"+chamber+"_"+committee
    if meta not in meta_tracker:
        meta_tracker.append(meta)
        strat_sample.append(i)


# Copy files to new subfolder

# In[20]:

import shutil
dest = "C:\Users\Jeff\Documents\hearings\sample"
for f in strat_sample:
    shutil.copy(f, dest)


#this is a sample change
    

