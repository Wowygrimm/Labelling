
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


# In[ ]:


sys.path.append('../../../Libraries/')


# In[ ]:


from Utils.Toolbox import graphics


# In[ ]:


rootPath = '../data/'


# # OVERALL

# In[ ]:


alld = pd.read_csv("../data/all_data.csv")
alld.shape


# In[ ]:


alld.shape


# In[ ]:


#graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), scanpath)


# # X&Y

# ### Overall look

# First of all, let's look for stats of those outliers

# In[ ]:


alld.columns


# In[ ]:


def count_errors(group):
    count = group.query("CURRENT_FIX_X < 0 or CURRENT_FIX_X > 1920 or CURRENT_FIX_Y < 0 or CURRENT_FIX_Y > 1080")["EYE_USED"].count()
    group["error_ratio"] = count / group.shape[0]
    return group

# Compute the overall ratio of fixations outside the screen on the full dataset
alld = alld.groupby(["PART_ID","TRIAL_INDEX"]).apply(count_errors)


# In[ ]:


# Mean error rate by trial
calcul_by = "TRIAL_INDEX"
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).transpose()


# In[ ]:


# Mean error rate by Participant
calcul_by = "PART_ID"
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).query("PART_ID < 700").plot()
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).query("PART_ID > 700").plot()
print(pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).transpose()


# In[ ]:


# Mean error rate by Condition
calcul_by = "CONDITION"
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).transpose()


# In[ ]:


alld["TASK"] = 'Target'
alld.loc[alld.query("CONDITION in [1,3,5]").index, "TASK"] = "Free"


# In[ ]:


# Mean error rate by trial
calcul_by = "TASK"
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld.groupby(calcul_by)["error_ratio"].mean()).transpose()


# We can see that participants have a higher rate of error even if it is not very big. Let's look how it turns when we remove participants 710, 711 and then 7th. 

# ### 710 and 711

# In[ ]:


# Mean error rate by trial
calcul_by = "TRIAL_INDEX"
parts_to_drop = [710, 711]
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).transpose()


# In[ ]:


# Mean error rate by trial
calcul_by = "CONDITION"
parts_to_drop = [710, 711]
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).transpose()


# ### 710, 711 and 7

# In[ ]:


# Mean error rate by trial
calcul_by = "TRIAL_INDEX"
parts_to_drop = [710, 711, 7]
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).transpose()


# In[ ]:


# Mean error rate by trial
calcul_by = "CONDITION"
parts_to_drop = [710, 711, 7]
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).plot()
print(pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).mean())
pd.DataFrame(alld[~alld["PART_ID"].isin(parts_to_drop)].groupby(calcul_by)["error_ratio"].mean()).transpose()


# ## Single participant: PART_1

# Participant n°1 is the one with the minimum error ration (0.002), so let's investigate the easy case before looking for more complicated cases

# In[ ]:


df1 = alld.query("PART_ID == 1").copy()
df1.shape


# In[ ]:


# Number of looks on the LEFT of the screen
df1.query("CURRENT_FIX_X < 0")["EYE_USED"].count()


# No look on the left of the screen

# In[ ]:


# Number of looks on the RIGHT of the screen
df1.query("CURRENT_FIX_X > 1920")["EYE_USED"].count()


# In[ ]:


# Number of looks on the LEFT of the screen
df1.query("CURRENT_FIX_Y < 0")["EYE_USED"].count()


# In[ ]:


# Number of looks on the LEFT of the screen
df1.query("CURRENT_FIX_Y > 1080")["EYE_USED"].count()


# Are these related to a blink ?

# **RIGHT**

# In[ ]:


# Count of blinks during the saccade
df1.query("CURRENT_FIX_X > 1920").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["EYE_USED"].count()


# In[ ]:


df1.query("CURRENT_FIX_X > 1920")


# In[ ]:


# Is there a blink around ?
df1.ix[37580:37595]


# No blink around, so let's check how far the participant looked

# In[ ]:


d = (df1.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"] - 1920).mean()
s = df1.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_START"].mean()
print("-- RIGHT -- ")
print("Mean distance outside the screen is {}px ({}°)".format(round(d, 2), round(d/35, 2)))
print("Mean start time is {}s".format(round(s/1000, 2)))
df1.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].hist()


# In[ ]:


# Degree error of each error
(df1.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"] - 1920)/35


# **Since the fovea is 2-3° we can consider this type of outlier (<1°) can be edited to max value of X (1920).**

# **DOWN**

# In[ ]:


# Count of blinks during the saccade
df1.query("CURRENT_FIX_Y > 1080").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["EYE_USED"].count()


# In[ ]:


df1.query("CURRENT_FIX_Y > 1080")


# The second fixation contains blinks in both rows after and before so let's investigate on this one first

# In[ ]:


df1.ix[40110:40115]


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [1245, 266],
    [1246, 147],
    [202, 2003],
    [584, 470],
    [536, 427],
])


# This problem looks more like a blink issue than fixation outside the screen

# In[ ]:


df1.ix[39366:39370]


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [712, 555],
    [615, 299],
    [520, 1349],
    [898, 556]
])


# Here we have a blink AND the end of the trial, which means the participant tends to look down to press the space bar to end the trial. So this outsider is a blink matter too.

# ## Single participant: PART_710

# In[ ]:


df710 = alld.query("PART_ID == 710").copy()
df710.shape


# In[ ]:


# Number of looks on the LEFT of the screen
df1.query("CURRENT_FIX_X < 0")["EYE_USED"].count()


# In[ ]:


# Number of looks on the RIGHT of the screen
df1.query("CURRENT_FIX_X > 1920")["EYE_USED"].count()


# In[ ]:


# Number of looks on the TOP of the screen
df1.query("CURRENT_FIX_Y < 0")["EYE_USED"].count()


# In[ ]:


# Number of looks on the BOTTOM of the screen
df1.query("CURRENT_FIX_Y > 1080")["EYE_USED"].count()


# **DOWN**

# This situation looks similar to previous participant. Let's see the condition to know if this is related to space bar

# In[ ]:


df1.query("CURRENT_FIX_Y > 1080")["CONDITION"].unique()


# These are TF tasks. Let's see if it is at the end of the trial

# In[ ]:


df1.query("CURRENT_FIX_Y > 1080")


# In[ ]:


df1.ix[27989:27995]


# Conclusion: End of a TF trial AND blinks in both directions !

# **UP**

# In[ ]:


# Number of looks on the TOP of the screen
df710.query("CURRENT_FIX_Y < 0")["EYE_USED"].count()


# In[ ]:


# Number of looks on the TOP of the screen
df710.query("CURRENT_FIX_Y < 0")["CONDITION"].value_counts()


# In[ ]:


# Percentage of TF tasks
(44+14+6)*100/87


# In[ ]:


# Number of looks on the TOP of the screen
df1.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_DURATION <= 120")["EYE_USED"].count()


# In[ ]:


t = df710.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].count()
c = df710.query("CURRENT_FIX_Y < 0").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_Y"].count()
d = df710.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].mean()
s = df710.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_START"].mean()
print("-- UP -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].hist()


# # Other

# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120 and CURRENT_FIX_BLINK_AROUND == 'NONE'")["TRIAL_INDEX"].count()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120 and CURRENT_FIX_BLINK_AROUND != 'NONE'")["TRIAL_INDEX"].count()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120 and CURRENT_FIX_BLINK_AROUND == 'AFTER'")["TRIAL_INDEX"].count()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120 and CURRENT_FIX_BLINK_AROUND == 'BEFORE'")["TRIAL_INDEX"].count()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120 and CURRENT_FIX_BLINK_AROUND == 'BOTH'")["TRIAL_INDEX"].count()


# In[ ]:


t = alld.query("CURRENT_FIX_X < 0")["EYE_USED"].count()
c = alld.query("CURRENT_FIX_X < 0").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["EYE_USED"].count()
d = alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_X"].mean()
s = alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_START"].mean()
print("-- LEFT -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_X"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].count()
c = alld.query("CURRENT_FIX_X > 1920").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_X"].count()
d = (alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"] - 1920).mean()
s = alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_START"].mean()
print("-- RIGHT -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].count()
c = alld.query("CURRENT_FIX_Y < 0").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_Y"].count()
d = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].mean()
s = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_START"].mean()
print("-- UP -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"].count()
c = alld.query("CURRENT_FIX_Y > 1080").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_Y"].count()
d = (alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"] - 1080).mean()
s = alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_START"].mean()
print("-- DOWN -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"].hist()


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080").groupby("CONDITION")["CURRENT_FIX_Y"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0").groupby("CONDITION")["CURRENT_FIX_Y"].count()


# In[ ]:


alld.query("CURRENT_FIX_X < 0").groupby("CONDITION")["CURRENT_FIX_X"].count()


# In[ ]:


alld.query("CURRENT_FIX_X > 1920").groupby("CONDITION")["CURRENT_FIX_X"].count()


# In[ ]:


alld.groupby("CONDITION")["CURRENT_FIX_START"].mean()


# In[ ]:


(2000-1920)/35


# In[ ]:


alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].hist()


# In[ ]:


print("Out of the zone:")
alld.query("CURRENT_FIX_X < 0 and CURRENT_FIX_X < -180")["EYE_USED"].count()


# In[ ]:


print("In the zone:")
alld.query("CURRENT_FIX_X < 0 and CURRENT_FIX_X > -180")["EYE_USED"].count()


# In[ ]:


print("In the zone:")
alld.query("CURRENT_FIX_X > 1920 and CURRENT_FIX_X < 2095")["EYE_USED"].count()


# In[ ]:


print("Out of the zone:")
alld.query("CURRENT_FIX_X > 1920 and CURRENT_FIX_X > 2095")["EYE_USED"].count()


# In[ ]:


print("In the zone:")
alld.query("CURRENT_FIX_Y > 1080 and CURRENT_FIX_Y < 1255")["EYE_USED"].count()


# In[ ]:


print("Out of the zone:")
alld.query("CURRENT_FIX_Y > 1080 and CURRENT_FIX_Y > 1255")["EYE_USED"].count()


# In[ ]:


print("Out of the zone:")
alld.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_Y < -180")["EYE_USED"].count()


# In[ ]:


print("In the zone:")
alld.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_Y > -180")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].hist()


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"].hist()


# In[ ]:


5*35


# In[ ]:


alld.query("CURRENT_FIX_X < 0 and CURRENT_FIX_X > -180").groupby("TRIAL_INDEX")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_Y > -180").groupby("TRIAL_INDEX")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_X > 1920")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_X < 0")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080").groupby(["PART_ID"])["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0").groupby(["PART_ID"])["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_X > 1920").groupby(["PART_ID"])["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_X < 0").groupby(["PART_ID"])["EYE_USED"].count()


# In[ ]:


t = alld.query("CURRENT_FIX_X < 0")["EYE_USED"].count()
l = alld.query("CURRENT_FIX_X < 0 and CURRENT_FIX_X > -100")["CURRENT_FIX_X"].count()
c = alld.query("CURRENT_FIX_X < 0").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["EYE_USED"].count()
d = alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_X"].mean()
s = alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_START"].mean()
print("-- LEFT -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Number of fix within the 3°: {} ({}%)".format(l, round(l*100/t, 2)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_X < 0")["CURRENT_FIX_X"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].count()
l = alld.query("CURRENT_FIX_X > 1920 and CURRENT_FIX_X < 2020")["CURRENT_FIX_X"].count()
c = alld.query("CURRENT_FIX_X > 1920").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_X"].count()
d = (alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"] - 1920).mean()
s = alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_START"].mean()
print("-- RIGHT -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Number of fix within the 3°: {} ({}%)".format(l, round(l*100/t, 2)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_X > 1920")["CURRENT_FIX_X"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].count()
l = alld.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_Y > -100")["CURRENT_FIX_Y"].count()
c = alld.query("CURRENT_FIX_Y < 0").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_Y"].count()
d = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].mean()
s = alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_START"].mean()
print("-- UP -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Number of fix within the 3°: {} ({}%)".format(l, round(l*100/t, 2)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_Y < 0")["CURRENT_FIX_Y"].hist()


# In[ ]:


t = alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"].count()
l = alld.query("CURRENT_FIX_Y > 1080 and CURRENT_FIX_Y < 1180")["CURRENT_FIX_Y"].count()
c = alld.query("CURRENT_FIX_Y > 1080").query("NEXT_SAC_CONTAINS_BLINK == 'true'")["CURRENT_FIX_Y"].count()
d = (alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"] - 1080).mean()
s = alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_START"].mean()
print("-- DOWN -- ")
print("On {}, {}({}%) where blinks".format(t, c, round(c/t*100, 0)))
print("Mean distance is {} ({}°)".format(round(d, 0), round(d/35, 0)))
print("Number of fix within the 3°: {} ({}%)".format(l, round(l*100/t, 2)))
print("Mean start time is {}s".format(round(s/1000, 0)))
alld.query("CURRENT_FIX_Y > 1080")["CURRENT_FIX_Y"].hist()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120")["EYE_USED"].count()


# In[ ]:


alld.query("CURRENT_FIX_Y < 0 and CURRENT_FIX_DURATION < 120")


# In[ ]:


alld.query("CURRENT_FIX_X < 0 and CURRENT_FIX_DURATION < 120")


# In[ ]:


alld.query("CURRENT_FIX_X > 1920 and CURRENT_FIX_DURATION < 120")


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080")[["TRIAL_INDEX", "WEBSITE_ID", "PART_ID", "CONDITION", "CURRENT_FIX_Y", "CURRENT_FIX_START"]]


# In[ ]:


alld.iloc[1495:1533][["TRIAL_INDEX", "WEBSITE_ID", "PART_ID", "CONDITION", "CURRENT_FIX_Y", "CURRENT_FIX_START"]]


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080 or CURRENT_FIX_Y < 0 or CURRENT_FIX_X > 1920 or CURRENT_FIX_X < 0")["EYE_USED"].count()


# In[ ]:


def compute_advances_Y_1080(group):
    last_row = group.tail(1).fillna(0)
    end_time = last_row["CURRENT_FIX_START"].values[0] + last_row["CURRENT_FIX_DURATION"].values[0] + last_row["NEXT_SAC_DURATION"].values[0]
    
    group["TIME_POS"] = group["CURRENT_FIX_START"] * 100 / end_time
    group["REMAINING_TIME"] = end_time - group["CURRENT_FIX_START"]
    group["DISTANCE_Y"] = group["CURRENT_FIX_Y"] - 1080
    group["DEG"] = group["DISTANCE"]/35
    
    return group

def compute_advances_Y_0(group):
    last_row = group.tail(1).fillna(0)
    end_time = last_row["CURRENT_FIX_START"].values[0] + last_row["CURRENT_FIX_DURATION"].values[0] + last_row["NEXT_SAC_DURATION"].values[0]
    
    group["TIME_POS"] = group["CURRENT_FIX_START"] * 100 / end_time
    group["REMAINING_TIME"] = end_time - group["CURRENT_FIX_START"]
    group["DISTANCE_Y"] = np.abs(group["CURRENT_FIX_Y"])
    group["DEG"] = group["DISTANCE"]/35
    
    return group

alld = alld.groupby(["PART_ID", "TRIAL_INDEX"]).apply(compute_advances)


# In[ ]:


alld.query("CURRENT_FIX_Y > 1080 or CURRENT_FIX_Y < 0 or CURRENT_FIX_X > 1920 or CURRENT_FIX_X < 0")["DEG"]

