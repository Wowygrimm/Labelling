
# coding: utf-8

# ## Library

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import os
import matplotlib as mpl


# *** Validation criterias: ***
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

# *** Import Data ***

# In[ ]:


rootPath = '../data/'
partID = 710


# In[ ]:


# CSV Eye-tracker
data = pd.read_csv("{0}/part_{1}/part_{1}_clean.csv".format(rootPath, partID), sep=",")
# CFG Mouse-tracker
config = pickle.load(open("{0}/part_{1}/part_{1}.cfg".format(rootPath, partID), 'rb'))


# *** Modification type of features ***

# In[ ]:


#data["CURRENT_FIX_Y"] = pd.to_numeric(data["CURRENT_FIX_Y"].str.replace(',','.'))
#data["CURRENT_FIX_X"] = pd.to_numeric(data["CURRENT_FIX_X"].str.replace(',','.'))
#data["NEXT_SAC_AMPLITUDE"] = pd.to_numeric(data["NEXT_SAC_AMPLITUDE"].str.replace(".", "").str.replace(",", "."))
#data["NEXT_SAC_END_X"] = pd.to_numeric(data["NEXT_SAC_END_X"].str.replace(".", "").str.replace(",", "."))
#data["NEXT_SAC_END_Y"] = pd.to_numeric(data["NEXT_SAC_END_Y"].str.replace(".", "").str.replace(",", "."))
#data["NEXT_SAC_DURATION"] = pd.to_numeric(data["NEXT_SAC_DURATION"].str.replace(".", "").str.replace(",", "."))
#data["NEXT_SAC_ANGLE"] = pd.to_numeric(data["NEXT_SAC_ANGLE"].str.replace(".", "").str.replace(",", "."))
#data["NEXT_SAC_AVG_VELOCITY"] = pd.to_numeric(data["NEXT_SAC_AVG_VELOCITY"].str.replace(".", "").str.replace(",", "."))


# In[ ]:


data.dtypes


# In[ ]:


data.head()


# ## Criterias

# In[ ]:


a_matrix = np.array([0, 0, 0, 0, 0, 0, 0, 0])
a_matrix


# In[ ]:


custom_colors = mpl.colors.LinearSegmentedColormap.from_list("", ["red","orange","green"])

plt.matshow([a_matrix], cmap=custom_colors, vmin = 0, vmax = 2)
plt.show()


# *** 18 TRIAL_INDEX ***

# In[ ]:


# Sort by TRIAL_INDEX
data_sorted = data.TRIAL_INDEX.unique()
data_sorted.sort()


# In[ ]:


good_trialsID = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
if ((data_sorted == good_trialsID).all()) :
    a_matrix[0] = 2


# *** CURRENT_FIX_X and CURRENT_FIX_Y are positives and in the 1920x1080 screen ***

# In[ ]:


fixX_prop_inscreen = round(len(data.query("CURRENT_FIX_X >= 0 and CURRENT_FIX_X <= 1920"))/len(data),2)
fixY_prop_inscreen = round(len(data.query("CURRENT_FIX_Y >= 0 and CURRENT_FIX_Y <= 1080"))/len(data),2)

print(str(fixX_prop_inscreen*100) + "% of CURRENT_FIX_X are positives and < 1920 px")

if (fixX_prop_inscreen == 1):
    a_matrix[1] = 2
elif (fixX_prop_inscreen > 0.95):
    a_matrix[1] = 1
    
print(str(fixY_prop_inscreen*100) + "% of CURRENT_FIX_Y are positives and < 1080 px")

if (fixY_prop_inscreen == 1):
    a_matrix[2] = 2
elif (fixY_prop_inscreen > 0.95):
    a_matrix[2] = 1


# In[ ]:


fig, axs = plt.subplots(1,2)

data["CURRENT_FIX_X"].hist(ax=axs[0])
data["CURRENT_FIX_Y"].hist(ax=axs[1])


# *** CURRENT_FIX_START is positive ***

# In[ ]:


fixStart_prop = round(len(data.query("CURRENT_FIX_START >= 0"))/len(data),3) 

print(str(fixStart_prop *100) + "% of CURRENT_FIX_START are positive")
if (fixStart_prop == 1):
    a_matrix[3] = 2
elif (fixStart_prop > 0.95):
    a_matrix[3] = 1


# *** EYE_USED is always equal to RIGHT ***

# In[ ]:


eye_prop = round(len(data.query("EYE_USED == 'RIGHT'"))/len(data),3)

print(str(eye_prop*100) + "% of EYE_USED are right")
if (eye_prop == 1):
    a_matrix[4] = 2


# *** CURRENT_FIX_DURATION is positive ***

# In[ ]:


fixDuration_prop = round(len(data.query("CURRENT_FIX_DURATION > 0"))/len(data),3)

print(str(fixDuration_prop * 100) + "% of CURRENT_FIX_DURATION are positive")
if (fixDuration_prop == 1):
    a_matrix[5] = 2


# *** We have 18 WEBSITE_ID ***

# In[ ]:


def get_website_id(trial_num):
    return config["rand_weblist"][trial_num - 1]["id"]

data["WEBSITE_ID"] = data["TRIAL_INDEX"].apply(get_website_id)

web = data["WEBSITE_ID"].unique()
web.sort()


# In[ ]:


good_websites = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18])
if ((web == good_websites).all()) :
    a_matrix[6] = 2


# *** We have 6 x 3 CONDITION ***

# In[ ]:


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


# In[ ]:


cond = data["CONDITION"].unique()
cond.sort()


# In[ ]:


good_condition = np.array([1,2,3,4,5,6])
if ((cond == good_condition).all()) :
    a_matrix[7] = 2


# ## CHECK

# In[ ]:


plt.matshow([a_matrix], cmap=custom_colors, vmin = 0, vmax = 2)
plt.show()

