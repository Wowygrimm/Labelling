
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import pandas as pd
import numpy as np

import pickle
import os
import glob
import re

import matplotlib.pyplot as plt
import matplotlib as mpl

from ast import literal_eval


# # Calibration Problems and Drop trials

# In[ ]:


rootPath = '../data/'
file_suffix = "_no_outsider.csv"
export_suffix = "_drop.csv"


# In[ ]:


trials_to_drop = pd.read_csv("{}trials_droplist.csv".format(rootPath))
trials_to_drop["TYPE"] = "checking"


# In[ ]:


trials_to_drop


# In[ ]:


# Trials with problems
trials_to_drop = trials_to_drop.append([
    {"PART_ID": 2, "TRIALS": [8], "TYPE": "other"},
    {"PART_ID": 3, "TRIALS": [15], "TYPE": "other"},
    {"PART_ID": 710, "TRIALS": [15], "TYPE": "other"},
    {"PART_ID": 711, "TRIALS": [16], "TYPE": "other"},
    {"PART_ID": 712, "TRIALS": [10], "TYPE": "other"},
    {"PART_ID": 715, "TRIALS": [8], "TYPE": "other"},
    {"PART_ID": 716, "TRIALS": [12, 13], "TYPE": "other"}
])


# In[ ]:


# Trials with calibration problems
trials_to_drop = trials_to_drop.append([
    {"PART_ID": 4, "TRIALS": [1], "TYPE": "calibration"},
    {"PART_ID": 710, "TRIALS": [1, 5], "TYPE": "calibration"},
    {"PART_ID": 711, "TRIALS": [1], "TYPE": "calibration"},
    {"PART_ID": 713, "TRIALS": [1], "TYPE": "calibration"},
    {"PART_ID": 714, "TRIALS": [1], "TYPE": "calibration"},
    {"PART_ID": 716, "TRIALS": [1], "TYPE": "calibration"}
])


# In[ ]:



def delete_trials(data, trials):
    data["CALIBRATION_PROBLEM"] = 'No'
    
    checking = trials.query("TYPE == 'checking'")
    other = trials.query("TYPE == 'other'")
    calibration = trials.query("TYPE == 'calibration'")
    
    if(not checking.empty):
        checking = checking["TRIALS"].values[0]
        if(type(checking) == str):
            checking = literal_eval(checking.replace("array(", "").replace(")", ""))
        trials_del = np.hstack(checking)
        data = data[~data["TRIAL_INDEX"].isin(trials_del)]
    
    if(not other.empty):
        other = other["TRIALS"].values[0]
        if(type(other) == str):
            other = literal_eval(other.replace("array(", "").replace(")", ""))
        trials_del = np.hstack(other)
        data = data[~data["TRIAL_INDEX"].isin(trials_del)]
    """
    if(not calibration.empty):
        calibration = calibration["TRIALS"].values[0]
        if(type(calibration) == str):
            calibration = literal_eval(calibration.replace("array(", "").replace(")", ""))
        trials_edit = np.hstack(calibration)
        data.loc[data.loc[:,"TRIAL_INDEX"].isin(trials_edit), "CALIBRATION_PROBLEM"] = "Yes"
    """
    return data

files = glob.glob("{0}part_*/part_*{1}".format(rootPath, file_suffix))
for filename in files:
    df = pd.read_csv(filename)
    print("Cleaning {}".format(filename))
    df["CALIBRATION_PROBLEM"] = 'No'
    
    part_id = df["PART_ID"].unique()[0]
    to_delete = trials_to_drop.query("PART_ID == @part_id")
    
    if(not to_delete.empty):
        df = delete_trials(df, to_delete)
    
    print("-- Exporting to {}".format(filename.replace(file_suffix, export_suffix)))
    df.to_csv(filename.replace(file_suffix, export_suffix), index = False)
print("Done")

