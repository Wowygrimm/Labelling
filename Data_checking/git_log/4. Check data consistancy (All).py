
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

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


# # Table of contents

# * [Criterias](#Validation-criterias)
# * [Functions](#Functions)
# * [Process](#Process)
# * [Export](#Export)
# * [Drop trials](#Drop-trials)

# # Validation criterias
# 
# - We have 18 TRIAL_INDEX
# 
# - CURRENT_FIX_X and CURRENT_FIX_Y are positives and in the 1920x1080 screen
# 
# - CURRENT_FIX_START is positive
# 
# - EYE_USED is always equal to RIGHT
# 
# - CURRENT_FIX_DURATION is positive
# 
# - We have 18 WEBSITE_ID
# 
# - We have 6 x 3 CONDITION 

# # Functions

# In[ ]:


# TRIAL_INDEX
def check_trial_count(data):
    # Sort by TRIAL_INDEX
    data_sorted = data["TRIAL_INDEX"].unique()
    data_sorted.sort()
    
    good_trialsID = np.arange(1, 19)
    if(np.array_equal(data_sorted, good_trialsID)):
        return 2
    else:
        return 0


# In[ ]:


def check_x(data):
    df = data.query("CURRENT_FIX_X < 0 or CURRENT_FIX_X > 1920")
    fixX_prop_inscreen = 1 - round(df.shape[0]/data.shape[0], 2)

    if (fixX_prop_inscreen == 1):
        return 2, None
    elif (fixX_prop_inscreen > 0.95):
        return 1, df["TRIAL_INDEX"].unique()
    else:
        return 0, df["TRIAL_INDEX"].unique()


# In[ ]:


def check_y(data):
    df = data.query("CURRENT_FIX_Y < 0 or CURRENT_FIX_Y > 1080")
    fixY_prop_inscreen = 1 - round(df.shape[0]/data.shape[0], 2)

    if (fixY_prop_inscreen == 1):
        return 2, None
    elif (fixY_prop_inscreen > 0.95):
        return 1, df["TRIAL_INDEX"].unique()
    else:
        return 0, df["TRIAL_INDEX"].unique()


# In[ ]:


def check_fix_start(data):
    df = data.query("CURRENT_FIX_START < 0")
    fixStart_prop = 1 - round(df.shape[0]/data.shape[0], 2) 

    if (fixStart_prop == 1):
        return 2, None
    elif (fixStart_prop > 0.95):
        return 1, df["TRIAL_INDEX"].unique()
    else:
        return 0, df["TRIAL_INDEX"].unique()


# In[ ]:


def check_eye(data):
    eye_prop = round(len(data.query("EYE_USED == 'RIGHT'"))/len(data),3)

    if (eye_prop == 1):
        return 2
    else:
        return 0


# In[ ]:


def check_fix_duration(data):
    df = data.query("CURRENT_FIX_DURATION < 0")
    fixDuration_prop = 1 - round(df.shape[0]/data.shape[0], 3)

    if (fixDuration_prop == 1):
        return 2, None
    else:
        return 0, df["TRIAL_INDEX"].unique()


# In[ ]:


def check_website_id(data):
    def get_website_id(trial_num):
        return config["rand_weblist"][trial_num - 1]["id"]

    data["WEBSITE_ID"] = data["TRIAL_INDEX"].apply(get_website_id)

    web = data["WEBSITE_ID"].unique()
    web.sort()

    good_websites = np.arange(1, 19)
    if(np.array_equal(web, good_websites)):
        return 2
    else:
        return 0


# In[ ]:


def check_condition(data):
    def get_condition(trial_num):
        data = config["rand_weblist"][trial_num - 1]
        if(data["type"] == "free" and data["ad_id"] == 0 and data["mpu_id"] == 0):
            return 1
        elif(data["type"] == "target" and data["ad_id"] == 0 and data["mpu_id"] == 0):
            return 2
        elif(data["type"] == "free" and data["ad_id"] > 0 and data["mpu_id"] == 0):
            return 3
        elif(data["type"] == "target" and data["ad_id"] > 0 and data["mpu_id"] == 0):
            return 4
        elif(data["type"] == "free" and data["ad_id"] > 0 and data["mpu_id"] > 0):
            return 5
        elif(data["type"] == "target" and data["ad_id"] > 0 and data["mpu_id"] > 0):
            return 6

        return None

    data["CONDITION"] = data["TRIAL_INDEX"].apply(get_condition)
    data.head()
    cond = data["CONDITION"].unique()
    cond.sort()
    good_condition = np.arange(1, 7)
    if(np.array_equal(cond, good_condition)):
        return 2
    else:
        return 0


# # Process

# In[ ]:


rootPath = '../data/'
file_suffix = "_no_outsider.csv"


# In[ ]:


deep_pal = sns.color_palette('deep')
colors_heatmap = sns.blend_palette([deep_pal[2], deep_pal[4], deep_pal[1]], as_cmap=True)


# In[ ]:


df = pd.DataFrame([], columns=[
    "PART_ID", "TRIAL_NB", "FIX_X", "FIX_Y", "FIX_START", "RIGHT_EYE", "FIX_DURATION", "WEBSITE_ID", "CONDITION", "TRIALS"])

files = glob.glob("{0}part_*/part_*{1}".format(rootPath, file_suffix))
for filename in files:
    data = pd.read_csv(filename)
    config = pickle.load(open(filename.replace(file_suffix, ".cfg"), 'rb'))
    
    to_insert = {
        "PART_ID":np.nan,
        "TRIAL_NB":np.nan,
        "FIX_X":np.nan,
        "FIX_Y":np.nan,
        "FIX_START":np.nan,
        "RIGHT_EYE":np.nan,
        "FIX_DURATION":np.nan,
        "WEBSITE_ID":np.nan,
        "CONDITION":np.nan,
        "TRIALS": np.nan
    }
    
    to_insert["PART_ID"] = data["PART_ID"].unique()[0]
    #to_insert["PART_FILE"] = filename
    
    # *** 18 TRIALS ***
    to_insert["TRIAL_NB"] = check_trial_count(data)

    # *** CURRENT_FIX_X and CURRENT_FIX_Y are positives and in the 1920x1080 screen ***
    to_insert["FIX_X"], trials_check2 = check_x(data)
    to_insert["FIX_Y"], trials_check3 = check_y(data)
    
    # *** CURRENT_FIX_START is positive ***
    to_insert["FIX_START"], trials_check4 = check_fix_start(data)

    # *** EYE_USED is always equal to RIGHT ***
    to_insert["RIGHT_EYE"] = check_eye(data)

    # *** CURRENT_FIX_DURATION is positive ***
    to_insert["FIX_DURATION"], trials_check6 = check_fix_duration(data)

    # *** We have 18 WEBSITE_ID ***
    to_insert["WEBSITE_ID"] = check_website_id(data)

    # *** We have 6 x 3 CONDITION ***
    to_insert["CONDITION"] = check_condition(data)
    
    # *** Trials to drop ***
    to_insert["TRIALS"] = [trials_check2, trials_check3, trials_check4, trials_check6]
    
    df = df.append([to_insert])


# In[ ]:


# Arrange dataset to pretty print it
df = df.sort_values("PART_ID")
df.index = df["PART_ID"].astype(int)
df.drop("PART_ID", inplace=True, axis=1)


# In[ ]:


# Display
plt.figure(figsize = (20,11))
sns.heatmap(df.drop(["TRIALS"], axis=1), annot=True, linewidths=1, linecolor='white', cmap=colors_heatmap, center=1, )


# # Export

# In[ ]:


# Here in case you just want to check the status without exporting again
raise ValueError


# In[ ]:


# Export Matrix trials
df.reset_index().drop(["TRIALS"], axis=1).to_csv('{}matrix_trials.csv'.format(rootPath), index=False)


# In[ ]:


# Export trials to drop
df.reset_index()[["PART_ID","TRIALS"]].to_csv('{}trials_droplist.csv'.format(rootPath), index=False)

