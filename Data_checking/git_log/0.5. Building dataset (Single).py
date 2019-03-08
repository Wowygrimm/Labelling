
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import pandas as pd
import numpy as np

import json
import pickle
import re

import matplotlib.pyplot as plt


# # Variables
# 
# Here is the selected variables:
# 
# - `TRIAL_INDEX`
# - `EYE_USED`
# - `CURRENT_FIX_X`
# - `CURRENT_FIX_Y`
# - `CURRENT_FIX_START`
# - `CURRENT_FIX_DURATION`
# - `NEXT_SAC_END_X`
# - `NEXT_SAC_END_Y`
# - `NEXT_SAC_AMPLITUDE`
# - `NEXT_SAC_DIRECTION`
# - `NEXT_SAC_DURATION`
# - `NEXT_SAC_ANGLE`
# - `NEXT_SAC_AVG_VELOCITY`
# 
# Since the Timestamp of the events is not at the right time, we need to synchronize Mouse data and eyes data. To do such, we sent a MSG containing `TRIAL_START=XXX-XX-XX XX:XX:XX` at the begining of the trial and `TRIAL_END=XXX-XX-XX XX:XX:XX` at the end.

# # Load Data

# In[ ]:


part_id = 714


# In[ ]:


df = pd.read_csv("../data/part_{0}/part_{0}.csv".format(part_id), sep="\t")
df.head()


# In[ ]:


msg = pd.read_csv("../data/part_{0}/part_{0}_msg.csv".format(part_id), sep="\t")
msg.head()


# In[ ]:


mrs_json = json.load(open("../data/part_{0}/records-{0}.mrs".format(part_id)))


# In[ ]:


config = pickle.load(open("../data/part_{0}/part_{0}.cfg".format(part_id), 'rb'))


# # Extract data

# In[ ]:


# Extract scroll data from json file
def extract_scroll(mrs_json, idx):
    # There is two key format: scroll|mouse-website_id-part_id or scroll|mouse-website_id
    # So we need to check that out
    r = re.compile("scroll-"+str(idx)+"(?!\d)")

    for item in mrs_json:
        match = list(filter(r.match, list(item.keys())))
        
        if(len(match) > 0):
            return pd.DataFrame(item[match[0]])
    
    return None


# In[ ]:


# Build scroll offset dataset
df_scroll = pd.DataFrame()
for i in range(1,19):
    scroll = None
    scroll = extract_scroll(mrs_json, i)
    scroll["website_id"] = i
    df_scroll = pd.concat([df_scroll, scroll])


# In[ ]:


# Extract right Datetime
# Timestamp is gave by `new Date().getTime()` in Javascript which is in ms
# And since this same function give UTC time, we need to add 1H


time_to_add = 0
# There was a time change on 25 March 2018, so the time shift between the datasets is not 1h anymore but 2h
if(part_id > 700 and part_id < 712):
    time_to_add = 1
else:
    time_to_add = 2

df_scroll["datetime"] = pd.to_datetime(df_scroll["timestamp"], unit="ms") + pd.Timedelta(hours=time_to_add)


# In[ ]:


df_scroll.head()


# # Messages cleaning

# In[ ]:


# Delete useless msg
msg = msg[~msg["CURRENT_MSG_TEXT"].str.contains("!MODE RECORD")].reset_index(drop=True)
msg.head()


# In[ ]:


# Extract message datetime in a new column
def split_equal(row):
    string = row["CURRENT_MSG_TEXT"].split("=")
    row["EVENT_NAME"] = string[0].strip()
    row["EVENT_DATETIME"] = string[1].strip()
    
    del row["CURRENT_MSG_TEXT"]
    
    return row

msg = msg.apply(split_equal, axis=1)
msg.head()


# In[ ]:


msg["EVENT_DATETIME"] = pd.to_datetime(msg["EVENT_DATETIME"])


# # Other cleaning

# In[ ]:


# Left, Right, Up or Down
df["NEXT_SAC_DIRECTION"] = df["NEXT_SAC_DIRECTION"].astype("category")
df["NEXT_SAC_DIRECTION"].cat.categories


# In[ ]:


df["CURRENT_FIX_Y"] = pd.to_numeric(df["CURRENT_FIX_Y"].str.replace(',','.'))
df["CURRENT_FIX_X"] = pd.to_numeric(df["CURRENT_FIX_X"].str.replace(',','.'))


# Last fixations does not have NEXT_SAC information
df["NEXT_SAC_AMPLITUDE"] = pd.to_numeric(df["NEXT_SAC_AMPLITUDE"].str.replace(".", "").str.replace(",", "."))
df["NEXT_SAC_END_X"] = pd.to_numeric(df["NEXT_SAC_END_X"].str.replace(".", "").str.replace(",", "."))
df["NEXT_SAC_END_Y"] = pd.to_numeric(df["NEXT_SAC_END_Y"].str.replace(".", "").str.replace(",", "."))
df["NEXT_SAC_DURATION"] = pd.to_numeric(df["NEXT_SAC_DURATION"].str.replace(".", "").str.replace(",", "."))
df["NEXT_SAC_ANGLE"] = pd.to_numeric(df["NEXT_SAC_ANGLE"].str.replace(".", "").str.replace(",", "."))
df["NEXT_SAC_AVG_VELOCITY"] = pd.to_numeric(df["NEXT_SAC_AVG_VELOCITY"].str.replace(".", "").str.replace(",", "."))


# # Time Sync

# In[ ]:


# Time sync
def sync_time(cell, msg):
    timedelta = cell - msg["CURRENT_MSG_TIME"][0]
    to_return = msg.loc[0, "EVENT_DATETIME"] + pd.Timedelta(milliseconds=timedelta)
    return to_return


# In[ ]:


def sync_and_clean(group):
    trial_index = group['TRIAL_INDEX'].unique()[0]
    
    msg_start_trial = msg.query("TRIAL_INDEX == @trial_index and EVENT_NAME == 'TRIAL START'").reset_index(drop=True)
    msg_end_trial = msg.query("TRIAL_INDEX == @trial_index and EVENT_NAME == 'TRIAL END'").reset_index(drop=True)

    group["DATETIME"] = group["CURRENT_FIX_START"].apply(lambda x: sync_time(x, msg_start_trial))
    
    group = group[group["DATETIME"] > msg_start_trial["EVENT_DATETIME"][0]]
    group = group[group["DATETIME"] < msg_end_trial["EVENT_DATETIME"][0]]
    
    return group


# In[ ]:


df = df.groupby("TRIAL_INDEX").apply(sync_and_clean).reset_index(drop = True)


# # Websites and Conditions

# In[ ]:


# Condition 1:  Free    + NoPub
# Condition 2:  Target  + NoPub
# Condition 3:  Free    + Skin
# Condition 4:  Target  + Skin
# Condition 5:  Free    + Skin/MPU
# Condition 6:  Target  + Skin/MPU
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

def condition_string(num):
    if(num == 1):
        return "Free + NoPub"
    elif(num == 2):
        return "Target + NoPub"
    elif(num == 3):
        return "Free + Skin"
    elif(num == 4):
        return "Target + Skin"
    elif(num == 5):
        return "Free + Skin/MPU"
    elif(num == 6):
        return "Target + Skin/MPU"
    else:
        return None


# In[ ]:


def get_website_id(trial_num):
    return config["rand_weblist"][trial_num - 1]["id"]


# In[ ]:


df["WEBSITE_ID"] = df["TRIAL_INDEX"].apply(get_website_id)


# In[ ]:


df["CONDITION"] = df["TRIAL_INDEX"].apply(get_condition)


# # Offset Sync

# In[ ]:


def get_last_offset(trial_scroll, date_eye):
    result = trial_scroll[trial_scroll["datetime"] < date_eye]
    if(result.empty):
        return 0
    else:
        return result.iloc[-1]["offset"]


# In[ ]:


def get_offset(group):
    website_id = group['WEBSITE_ID'].unique()[0]
    group["OFFSET"] = group["DATETIME"].apply(lambda x: get_last_offset(df_scroll.query("website_id == "+str(website_id)), x))
    return group


# In[ ]:


df = df.groupby("TRIAL_INDEX").apply(get_offset)


# In[ ]:


df.groupby("TRIAL_INDEX")["OFFSET"].unique()


# In[ ]:


df["Y_OFFSET"] = df["CURRENT_FIX_Y"] + df["OFFSET"]


# # Export

# In[ ]:


df.to_csv("../data/part_{0}/part_{0}_clean.csv".format(part_id), index=False)


# In[ ]:


df.head()

