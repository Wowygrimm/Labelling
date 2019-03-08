
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import pandas as pd
import numpy as np

import json
import pickle
import os
import re
import glob

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

# # Functions

# In[ ]:


def clean_columns(data):
    data["CURRENT_FIX_Y"] = pd.to_numeric(data["CURRENT_FIX_Y"].str.replace(',','.')).fillna(0)
    data["CURRENT_FIX_X"] = pd.to_numeric(data["CURRENT_FIX_X"].str.replace(',','.')).fillna(0)
    data["NEXT_SAC_AMPLITUDE"] = pd.to_numeric(data["NEXT_SAC_AMPLITUDE"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_END_X"] = pd.to_numeric(data["NEXT_SAC_END_X"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_END_Y"] = pd.to_numeric(data["NEXT_SAC_END_Y"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_DURATION"] = pd.to_numeric(data["NEXT_SAC_DURATION"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_BLINK_START"] = pd.to_numeric(data["NEXT_SAC_BLINK_START"].str.replace(".", "")).fillna(0)
    data["NEXT_SAC_BLINK_END"] = pd.to_numeric(data["NEXT_SAC_BLINK_END"].str.replace(".", "")).fillna(0)
    data["NEXT_SAC_ANGLE"] = pd.to_numeric(data["NEXT_SAC_ANGLE"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_AVG_VELOCITY"] = pd.to_numeric(data["NEXT_SAC_AVG_VELOCITY"].str.replace(".", "").str.replace(",", ".")).fillna(0)
    data["NEXT_SAC_BLINK_DURATION"] = pd.to_numeric(data["NEXT_SAC_BLINK_DURATION"].str.replace(".", "").str.replace(",", ".")).fillna(0)


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


# Extract mouse data from json file
def extract_mouse(mrs_json, idx):
    # There is two key format: scroll|mouse-website_id-part_id or scroll|mouse-website_id
    # So we need to check that out
    r = re.compile("mouse-"+str(idx)+"(?!\d)")

    for item in mrs_json:
        match = list(filter(r.match, list(item.keys())))
        
        if(len(match) > 0):
            return pd.DataFrame(item[match[0]])
    
    return None


# In[ ]:


# Extract message datetime in a new column
def split_equal(row):
    string = row["CURRENT_MSG_TEXT"].split("=")
    row["EVENT_NAME"] = string[0].strip()
    row["EVENT_DATETIME"] = string[1].strip()
    
    del row["CURRENT_MSG_TEXT"]
    
    return row


# In[ ]:


# Time sync
def sync_time(cell, msg):
    # Difference between current CURRENT_FIX_START and first msg event
    timedelta = cell - msg["CURRENT_MSG_TIME"][0]
    # The delta is added to initial msg date to infer full datetime of CURRENT_FIX_START event
    to_return = msg.loc[0, "EVENT_DATETIME"] + pd.Timedelta(milliseconds=timedelta)
    return to_return


# In[ ]:


def sync_and_clean(group):
    trial_index = group['TRIAL_INDEX'].unique()[0]
    
    msg_start_trial = msg.query("TRIAL_INDEX == @trial_index and EVENT_NAME == 'TRIAL START'").reset_index(drop=True)
    msg_end_trial = msg.query("TRIAL_INDEX == @trial_index and EVENT_NAME == 'TRIAL END'").reset_index(drop=True)

    group["DATETIME"] = group["CURRENT_FIX_START"].apply(lambda x: sync_time(x, msg_start_trial))
    
    # Clean events before and after TRIAL_START and TRIAL_END
    group = group[group["DATETIME"] > msg_start_trial["EVENT_DATETIME"][0]]
    group = group[group["DATETIME"] < msg_end_trial["EVENT_DATETIME"][0]]
    
    return group


# In[ ]:


def get_website_id(trial_num):
    return config["rand_weblist"][trial_num - 1]["id"]


# In[ ]:


def get_last_offset(trial_scroll, date_eye):
    result = trial_scroll[trial_scroll["datetime"] < date_eye]
    if(result.empty):
        return 0
    else:
        return result.iloc[-1]["offset"]


# In[ ]:


def get_offset(group):
    website_id = get_website_id(group['TRIAL_INDEX'].unique()[0])
    group["OFFSET"] = group["DATETIME"].apply(lambda x: get_last_offset(df_scroll.query("website_id == "+str(website_id)), x))
    return group


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


# In[ ]:


def generate_order(group):
    size = group.shape[0]
    group["ORDER"] = np.arange(1, size+1)
    return group


# # Main CSV

# In[ ]:


root_dir = "../data/"
file_suffix = "_raw.csv"
export_suffix = "_built.csv"


# In[ ]:


overwrite = True


# In[ ]:


for path in glob.glob(root_dir+"**/*"+file_suffix):
    print("Processing {}".format(path))
    path_dir = os.path.dirname(path)
    
    ################ LOAD
    
    df = pd.read_csv(path, sep="\t")
    clean_columns(df)
    msg = pd.read_csv(path.replace(file_suffix, "_msg.csv"), sep="\t")
    
    part_id = int(path_dir.split("_")[1])
    
    mrs_json = json.load(open(path_dir+"/records-"+str(part_id)+".mrs"))
    config = pickle.load(open(path.replace(file_suffix, ".cfg"), 'rb'))
    
    df["PART_ID"] = part_id
    
    ################ SCROLL and MOUSE
    
    # Build scroll offset and mouse dataset
    df_scroll = pd.DataFrame()
    df_mouse = pd.DataFrame()
    for i in range(1,19):
        scroll = None
        mouse = None
        scroll = extract_scroll(mrs_json, i)
        mouse = extract_mouse(mrs_json, i)
        scroll["website_id"] = i
        mouse["website_id"] = i
        df_scroll = pd.concat([df_scroll, scroll])
        df_mouse = pd.concat([df_mouse, mouse])

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
    df_mouse["datetime"] = pd.to_datetime(df_mouse["timestamp"], unit="ms") + pd.Timedelta(hours=time_to_add)
    
    
    ################ MESSAGE
    
    # Delete useless msg
    msg = msg[~msg["CURRENT_MSG_TEXT"].str.contains("!MODE RECORD")].reset_index(drop=True)
    # Split columns
    msg = msg.apply(split_equal, axis=1)
    # Convert to Datetime
    try:
        msg["EVENT_DATETIME"] = pd.to_datetime(msg["EVENT_DATETIME"])
    except ValueError:
        msg["EVENT_DATETIME"] = pd.to_datetime(msg["EVENT_DATETIME"], format="%Y-%m-%d %H:%M:%S %f")

    
    ################ EXPORT
    
    if(not os.path.isfile(path.replace(file_suffix, export_suffix)) or overwrite):
        print("--- Exporting to {}".format(path.replace(file_suffix, export_suffix)))
        
        ################ TIME SYNC
    
        df = df.groupby("TRIAL_INDEX").apply(sync_and_clean).reset_index(drop = True)


        ################ OFFSET

        df = df.groupby("TRIAL_INDEX").apply(get_offset)
        df["Y_OFFSET"] = df["CURRENT_FIX_Y"] + df["OFFSET"]


        ################ WEBSITES AND CONDITIONS

        df["WEBSITE_ID"] = df["TRIAL_INDEX"].apply(get_website_id)
        df["CONDITION"] = df["TRIAL_INDEX"].apply(get_condition)
        
        
        ################ TASKS
        
        df["TASK"] = 'Target'
        df.loc[df.query("CONDITION in [1,3,5]").index, "TASK"] = "Free"

        
        ################ DISTRACTORS
        
        df["DISTRACTOR"] = 'NoAd'
        df.loc[df.query("CONDITION in [3,4]").index, "DISTRACTOR"] = "Skin"
        df.loc[df.query("CONDITION in [5,6]").index, "DISTRACTOR"] = "SkinMpu"
        
        
        ################ ORDER
        
        df = df.groupby("TRIAL_INDEX").apply(generate_order)
        
        df.to_csv(path.replace(file_suffix, export_suffix), index=False)
    
    else:
        print("--- Skipping export")
        
    if(not os.path.isfile(path.replace(file_suffix, "_scroll.csv")) or overwrite):
        df_scroll.to_csv(path.replace(file_suffix, "_scroll.csv"),index=False)
        print("--- Exporting to {}".format(path.replace(file_suffix, "_scroll.csv")))
    else:
        print("--- Skipping export")
        
    if(not os.path.isfile(path.replace(file_suffix, "_mouse_browser.csv")) or overwrite):
        df_mouse.to_csv(path.replace(file_suffix, "_mouse_browser.csv"),index=False)
        print("--- Exporting to {}".format(path.replace(file_suffix, "_mouse_browser.csv")))
    else:
        print("--- Skipping export")
    
    #df = None
    #msg = None
    #df_scroll = None
    #df_mouse = None
    #mrs_json = None
    #config = None
    break

print("Done")

