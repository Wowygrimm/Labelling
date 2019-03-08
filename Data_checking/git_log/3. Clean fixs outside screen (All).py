
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import os
import glob
import matplotlib as mpl
from math import *


# # Functions

# In[ ]:


def recompute_saccade(group):
    group["NEXT_SAC_END_X"].fillna(0, inplace=True)
    group["NEXT_SAC_END_Y"].fillna(0, inplace=True)

    group["NEXT_SAC_END_X"] = group["CURRENT_FIX_X"].shift(-1)
    group["NEXT_SAC_END_Y"] = group["CURRENT_FIX_Y"].shift(-1)

    dx = group["NEXT_SAC_END_X"] - group["CURRENT_FIX_X"]
    dy = group["NEXT_SAC_END_Y"] - group["CURRENT_FIX_Y"]
    dl = np.sqrt(dx**2 + dy**2)/35

    group.loc[:,"NEXT_SAC_AMPLITUDE"] = dl
    
    group.loc[dx > np.abs(dy), "NEXT_SAC_DIRECTION"] = "RIGHT"
    group.loc[dy > np.abs(dx), "NEXT_SAC_DIRECTION"] = "UP"
    group.loc[-dx > np.abs(dy), "NEXT_SAC_DIRECTION"] = "LEFT"
    group.loc[-dy > np.abs(dx), "NEXT_SAC_DIRECTION"] = "DOWN"
    
    group["NEXT_SAC_DURATION"] = group["CURRENT_FIX_START"].shift(-1) - (group["CURRENT_FIX_START"] + group["CURRENT_FIX_DURATION"])
    
    return group


# In[ ]:


# Delete a row for a given participant's dataset
# This function is not suited for dataset with all participants
def delete_rows(data, indexes):
    # Verifications
    for index in indexes:
        assert index in data.index, "The index ({}) does not exist !".format(index)

    trial = data.loc[indexes, "TRIAL_INDEX"]
    assert len(np.unique(trial)) == 1, "All indexes must be in the same TRIAL !"
    trial = trial.unique()[0]

    data.loc[:,"CUMSUM_TIME_TO_DEL"] = 0

    if("TIME_TO_DEL" not in data):
        data.loc[:,"TIME_TO_DEL"] = 0  # Variable to handle rows to delete

    trial_idxs = data.query("TRIAL_INDEX == @trial").index

    # Fixation duration and saccade duration wrap every events in one line of the dataset
    data.loc[indexes, "TIME_TO_DEL"] = data.loc[indexes, "CURRENT_FIX_DURATION"] + data.loc[indexes, "NEXT_SAC_DURATION"]

    data.loc[trial_idxs, "CUMSUM_TIME_TO_DEL"] = data.loc[trial_idxs, "TIME_TO_DEL"].cumsum()

    # Compute new start/end times values
    data.loc[trial_idxs, "CURRENT_FIX_START"] = data.loc[trial_idxs, "CURRENT_FIX_START"] - data.loc[trial_idxs, "CUMSUM_TIME_TO_DEL"]
    if("CURRENT_FIX_END" in data.columns):
        data.loc[trial_idxs, "CURRENT_FIX_END"] = data.loc[trial_idxs, "CURRENT_FIX_END"] - data.loc[trial_idxs, "CUMSUM_TIME_TO_DEL"]
    data.loc[trial_idxs, "NEXT_SAC_BLINK_START"] = data.loc[trial_idxs, "NEXT_SAC_BLINK_START"] - data.loc[trial_idxs, "CUMSUM_TIME_TO_DEL"]
    data.loc[trial_idxs, "NEXT_SAC_BLINK_END"] = data.loc[trial_idxs, "NEXT_SAC_BLINK_END"] - data.loc[trial_idxs, "CUMSUM_TIME_TO_DEL"]
    
    # Delete given rows
    data.drop(indexes, inplace=True)

    # Clean created columns
    data.drop(["TIME_TO_DEL", "CUMSUM_TIME_TO_DEL"], axis=1, inplace=True)


def update_blinks_localisation(data):
    trials = data.groupby("TRIAL_INDEX").indices
    
    for idx in trials:
        # First row
        if(data.loc[trials[idx][0], "NEXT_SAC_CONTAINS_BLINK"] in ["false", "False", False]):
            data.loc[trials[idx][0], "CURRENT_FIX_BLINK_AROUND"] = "NONE"
        elif(data.loc[trials[idx][0], "NEXT_SAC_CONTAINS_BLINK"] in ["true", "True", True]):
            data.loc[trials[idx][0], "CURRENT_FIX_BLINK_AROUND"] = "AFTER"
        else:
            raise ValueError("Unrecognized 'NEXT_SAC_CONTAINS_BLINK' value ({})".format(data.loc[trials[idx][0], "NEXT_SAC_CONTAINS_BLINK"]))
        
        # Last element is ignored because it does not contain saccade information
        # since it's the last fixation before the eye-tracker stop the recording
        indexes = trials[idx][1:-1]
        for index in indexes:
            if(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] in ["false", "False", False] and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] in ["false", "False", False]):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "NONE"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] in ["false", "False", False] and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] in ["true", "True", True]):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "AFTER"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] in ["true", "True", True] and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] in ["false", "False", False]):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "BEFORE"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] in ["true", "True", True] and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] in ["true", "True", True]):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "BOTH"
            else:
                raise ValueError("Unrecognized 'CURRENT_FIX_BLINK_AROUND' value ({})".format(index))


# In[ ]:


def generate_order(group):
    size = group.shape[0]
    group["ORDER"] = np.arange(1, size+1)
    return group


# # Process and Export

# In[ ]:


rootPath = '../data/'
file_suffix = "_no_blink.csv"
export_suffix = "_no_outsider.csv"
THREE_DEGREES = 35*3


# In[ ]:


files = glob.glob("{0}part_*/part_*{1}".format(rootPath, file_suffix))
for filename in files:
    print("Processing {}".format(os.path.basename(filename)))
    df = pd.read_csv(filename)
    indexes = []
    
    print("--- Deleting outsiders > 3deg")
    # Right outsiders
    fix_right = df.query("CURRENT_FIX_X > {}".format(1920+THREE_DEGREES)).index
    if(len(fix_right) > 0):
        indexes.append(fix_right)

    # Left outsiders
    fix_left = df.query("CURRENT_FIX_X < {}".format(-THREE_DEGREES)).index
    if(len(fix_left) > 0):
        indexes.append(fix_left)

    # Top outsiders
    fix_top = df.query("CURRENT_FIX_Y < {}".format(-THREE_DEGREES)).index
    if(len(fix_top) > 0):
        indexes.append(fix_top)

    # Bottom outsiders
    fix_bottom = df.query("CURRENT_FIX_Y > {}".format(1080+THREE_DEGREES)).index
    if(len(fix_bottom) > 0):
        indexes.append(fix_bottom)

    # Flatten indexes and get unique indexes
    if(len(indexes) > 0):
        indexes = np.unique(np.hstack(indexes))

    # Delete outsiders
    for idx in indexes:
        delete_rows(df, [idx])
    
    print("--- Adjusting outsiders < 3deg")
    # Right adjustments
    x_lt_3deg = df["CURRENT_FIX_X"] < 1920+THREE_DEGREES
    x_gt_1920 = df["CURRENT_FIX_X"] > 1920
    df.loc[x_lt_3deg & x_gt_1920, "CURRENT_FIX_X"] = 1920

    # Left adjustments
    x_gt_3deg = df["CURRENT_FIX_X"] > -THREE_DEGREES
    x_lt_0 = df["CURRENT_FIX_X"] < 0
    df.loc[x_gt_3deg & x_lt_0, "CURRENT_FIX_X"] = 0

    # Top adjustments
    y_gt_3deg = df["CURRENT_FIX_Y"] > -THREE_DEGREES
    y_lt_0 = df["CURRENT_FIX_Y"] < 0
    df.loc[y_gt_3deg & y_lt_0, "CURRENT_FIX_Y"] = 0

    # Bottom adjustments
    y_lt_3deg = df["CURRENT_FIX_Y"] < 1080+THREE_DEGREES
    y_gt_1080 = df["CURRENT_FIX_Y"] > 1080
    df.loc[y_lt_3deg & y_gt_1080, "CURRENT_FIX_Y"] = 1080
    
    print("--- Updating blinks localisation")
    df.reset_index(drop=True, inplace=True)
    update_blinks_localisation(df)
    
    print("--- Recomputing saccades")
    df = df.groupby("TRIAL_INDEX").apply(recompute_saccade)
    
    print("--- Compute fixation order")
    df = df.groupby("TRIAL_INDEX").apply(generate_order)
    
    print("--- Exporting to {}".format(filename.replace(file_suffix, export_suffix)))
    df.to_csv(filename.replace(file_suffix, export_suffix), index = False)
    index = None
    df = None
print("Done")

