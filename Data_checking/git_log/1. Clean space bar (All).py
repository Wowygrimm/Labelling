
# coding: utf-8

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import os
import sys
import glob
import matplotlib as mpl
import math

from PIL import Image, ImageDraw, ImageFont, ImageChops


# # Functions

# In[ ]:


def clean_2s_tail_trial(group):
    if(group["CONDITION"].unique()[0] in [2,4,6]):
        last_row = group.tail(1).fillna(0)
        end_time = last_row["CURRENT_FIX_START"].values[0] + last_row["CURRENT_FIX_DURATION"].values[0] + last_row["NEXT_SAC_DURATION"].values[0]
        group["timediff_last_row"] = end_time - group["CURRENT_FIX_START"]

        # Return all rows after 2s from the end
        return group.query("timediff_last_row > 2000").drop("timediff_last_row", axis=1)
    else:
        return group


# In[ ]:


def clean_tail_trial(group):
    if(group["CONDITION"].unique()[0] in [2,4,6]):
        # If current fix is > 1080 or if previous one is or previous previous one is, the row is deleted
        group["to_delete"] = (group["CURRENT_FIX_Y"] > 1080) | (group["CURRENT_FIX_Y"].shift() > 1080) | (group["CURRENT_FIX_Y"].shift(2) > 1080)
        
        # We reverse `to_delete` column to apply cumsum and delete rows where value is 0 (True)
        group["to_delete"] = ~group["to_delete"]
        group["to_delete"] = group.loc[::-1, "to_delete"].cumsum()[::-1]

        return group.query("to_delete > 0").drop("to_delete", axis=1)
    else:
        return group


# # Process

# In[ ]:


rootPath = '../data/'
file_suffix = "_built.csv"
export_suffix = "_no_tail.csv"


# In[ ]:


files = glob.glob("{0}part_*/part_*{1}".format(rootPath, file_suffix))
for filename in files:
    print("Processing {}".format(os.path.basename(filename)))
    df = pd.read_csv(filename)
    
    print("--- Removing 2 last seconds of Target Finding tasks columns")
    df = df.groupby(["TRIAL_INDEX", "CONDITION"], as_index=False, group_keys=False).apply(clean_2s_tail_trial).sort_index()
    
    print("--- Removing outside screen fixation from tail in Target Finding tasks columns")
    df = df.groupby(["TRIAL_INDEX", "CONDITION"], as_index=False, group_keys=False).apply(clean_tail_trial).sort_index()

    
    print("--- Exporting to {}".format(filename.replace(file_suffix, export_suffix)))
    df.to_csv(filename.replace(file_suffix, export_suffix), index = False)
    
print("Done")

