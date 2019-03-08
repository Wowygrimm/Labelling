
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


def clean_last_saccade(group):
    cols = list(group.columns)
    group.iloc[-1, cols.index("NEXT_SAC_END_X")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_END_X")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_END_Y")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_AMPLITUDE")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_DIRECTION")] = "."
    group.iloc[-1, cols.index("NEXT_SAC_DURATION")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_ANGLE")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_CONTAINS_BLINK")] = "false"
    group.iloc[-1, cols.index("NEXT_SAC_BLINK_START")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_BLINK_END")] = 0
    group.iloc[-1, cols.index("NEXT_SAC_BLINK_DURATION")] = 0
    return group

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
        if(data.loc[trials[idx][0], "NEXT_SAC_CONTAINS_BLINK"] == "false"):
            data.loc[trials[idx][0], "CURRENT_FIX_BLINK_AROUND"] = "NONE"
        elif(data.loc[trials[idx][0], "NEXT_SAC_CONTAINS_BLINK"] == "true"):
            data.loc[trials[idx][0], "CURRENT_FIX_BLINK_AROUND"] = "AFTER"
        else:
            raise ValueError("Unrecognized 'CURRENT_FIX_BLINK_AROUND' value ({})".format(trial[0]))
        
        # Last element is ignored because it does not contain saccade information
        # since it's the last fixation before the eye-tracker stop the recording
        indexes = trials[idx][1:-1]
        for index in indexes:
            if(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] == "false" and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] == "false"):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "NONE"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] == "false" and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] == "true"):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "AFTER"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] == "true" and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] == "false"):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "BEFORE"
            elif(data.loc[index-1, "NEXT_SAC_CONTAINS_BLINK"] == "true" and data.loc[index, "NEXT_SAC_CONTAINS_BLINK"] == "true"):
                data.loc[index, "CURRENT_FIX_BLINK_AROUND"] = "BOTH"
            else:
                raise ValueError("Unrecognized 'CURRENT_FIX_BLINK_AROUND' value ({})".format(index))

def correct_blink_saccade(data):
    data["NEXT_SAC_BLINK_DURATION"].fillna(0, inplace=True)
    data.loc[:,"CUMSUM_BLINK_DURATION"] = data.groupby("TRIAL_INDEX")["NEXT_SAC_BLINK_DURATION"].cumsum()
    
    # cumsum() result in adding the value of the current row.
    # Since we don't want to temporaly shift the current fix_start and fix_end with the current blink duration,
    # we remove it from rows containing blink to avoid this effect.
    contains_blink = data["NEXT_SAC_CONTAINS_BLINK"] == 'true'
    data.loc[contains_blink,"CUMSUM_BLINK_DURATION"] = data.loc[contains_blink,"CUMSUM_BLINK_DURATION"] - data.loc[contains_blink,"NEXT_SAC_BLINK_DURATION"]
    
    data["CURRENT_FIX_START"] = data["CURRENT_FIX_START"] - data["CUMSUM_BLINK_DURATION"]
    if("CURRENT_FIX_END" in data.columns):
        data["CURRENT_FIX_END"] = data["CURRENT_FIX_END"] - data["CUMSUM_BLINK_DURATION"]
    
    # A saccade duration contains the blink duration so we need to remove it
    data["NEXT_SAC_DURATION"] = data["NEXT_SAC_DURATION"] - data["NEXT_SAC_BLINK_DURATION"]
    
    data.drop("CUMSUM_BLINK_DURATION", inplace=True, axis=1)
    


# # Process and Export

# In[ ]:


rootPath = '../data/'
file_suffix = "_no_tail.csv"
export_suffix = "_no_blink.csv"


# In[ ]:


files = glob.glob("{0}part_*/part_*{1}".format(rootPath, file_suffix))
for filename in files:
    print("Processing {}".format(os.path.basename(filename)))
    df = pd.read_csv(filename)
    
    print("--- Deleting short fixs AFTER")
    # Clean all fixations < 120ms before blinks
    indexes = df.query("CURRENT_FIX_BLINK_AROUND == 'AFTER' and CURRENT_FIX_DURATION < 120").groupby("TRIAL_INDEX").groups
    for elt in indexes:
        delete_rows(df, indexes[elt])
    
    print("--- Deleting short fixs BEFORE")
    # Clean all fixations < 120ms before blinks
    indexes = df.query("CURRENT_FIX_BLINK_AROUND == 'BEFORE' and CURRENT_FIX_DURATION < 120").groupby("TRIAL_INDEX").groups
    for elt in indexes:
        delete_rows(df, indexes[elt])
    
    print("--- Deleting short fixs BOTH")
    # Clean all fixations < 120ms before blinks
    indexes = df.query("CURRENT_FIX_BLINK_AROUND == 'BOTH' and CURRENT_FIX_DURATION < 120").groupby("TRIAL_INDEX").groups
    for elt in indexes:
        delete_rows(df, indexes[elt])
    
    print("--- Updating blinks localisation")
    df.reset_index(drop=True, inplace=True)
    update_blinks_localisation(df)
    
    print("--- Time deletion of blinks in saccades")
    correct_blink_saccade(df)
    
    print("--- Recomputing saccades")
    df = df.groupby("TRIAL_INDEX").apply(clean_last_saccade)
    df = df.groupby("TRIAL_INDEX").apply(recompute_saccade)
    
    print("--- Exporting to {}".format(filename.replace(file_suffix, export_suffix)))
    df.to_csv(filename.replace(file_suffix, export_suffix), index = False)
print("Done")

