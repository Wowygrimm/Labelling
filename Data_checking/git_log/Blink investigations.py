
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


# In[ ]:


def clean_columns(data):
    data["CURRENT_FIX_Y"] = pd.to_numeric(data["CURRENT_FIX_Y"].str.replace(',','.'))
    data["CURRENT_FIX_X"] = pd.to_numeric(data["CURRENT_FIX_X"].str.replace(',','.'))
    data["NEXT_SAC_AMPLITUDE"] = pd.to_numeric(data["NEXT_SAC_AMPLITUDE"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_END_X"] = pd.to_numeric(data["NEXT_SAC_END_X"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_END_Y"] = pd.to_numeric(data["NEXT_SAC_END_Y"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_DURATION"] = pd.to_numeric(data["NEXT_SAC_DURATION"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_ANGLE"] = pd.to_numeric(data["NEXT_SAC_ANGLE"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_AVG_VELOCITY"] = pd.to_numeric(data["NEXT_SAC_AVG_VELOCITY"].str.replace(".", "").str.replace(",", "."))
    data["NEXT_SAC_BLINK_DURATION"] = pd.to_numeric(data["NEXT_SAC_BLINK_DURATION"].str.replace(".", "").str.replace(",", "."))


# # OVERALL

# In[ ]:


alld = pd.read_csv("../data/all_data.csv")
alld.shape


# In[ ]:


alld.shape


# In[ ]:


#graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), scanpath)


# We are going to strat with blinks `CURRENT_FIX_BLINK_AROUND == 'BOTH'`

# In[ ]:


alld.query("CURRENT_FIX_BLINK_AROUND == 'BOTH'").head()


# In[ ]:


alld.loc[533:537]


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [463, 263],
    [558, 274],
    [551, 302],
    [506, 293],
    [460, 306]
])


# Second we are going to investigate how to handle blinks when `NEXT_SAC_CONTAINS_BLINK == "true"`

# In[ ]:


alld.query("NEXT_SAC_CONTAINS_BLINK == 'true'").head()


# In[ ]:


alld["NEXT_SAC_SPEED"] = alld["NEXT_SAC_AMPLITUDE"] / alld["NEXT_SAC_DURATION"] / 1000


# In[ ]:


alld.loc[18:21].drop(["EYE_USED", "NEXT_SAC_DIRECTION", "NEXT_SAC_BLINK_END", "NEXT_SAC_BLINK_START", "NEXT_SAC_BLINK_DURATION"], axis=1)


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [1560, 607],
    [1534, 607],
    [959, 574],
    [779, 574]
])


# In[ ]:


alld.loc[38:41]


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [372, 18],
    [474, 17],
    [786, 698],
    [541, 786]
])


# In[ ]:


alld.loc[99:102]#30745 	30339


# In[ ]:


graphics.draw_scanpath(Image.new("RGB", (1920, 1080), "gray"), [
    [927, 703],
    [910, 711],
    [832, 227],
    [797, 314]
])


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 100")["CURRENT_FIX_BLINK_AROUND"].value_counts()


# In[ ]:


alld.query("CURRENT_FIX_DURATION < 120")["CURRENT_FIX_BLINK_AROUND"].value_counts()


# In[ ]:


alld.query("NEXT_SAC_CONTAINS_BLINK == 'true'")["EYE_USED"].count()


# In[ ]:


(428+381+128)*100/2497


# In[ ]:


(677+565+139)*100/2497


# In[ ]:


alld["NEXT_SAC_BLINK_END"] = pd.to_numeric(alld["NEXT_SAC_BLINK_END"].str.replace(".", "").str.replace(",", "."))


# In[ ]:


alld["diff_blink"] = alld.query("NEXT_SAC_BLINK_DURATION > 0")["CURRENT_FIX_START"].shift(-1)
alld.query("NEXT_SAC_BLINK_DURATION > 0")["diff_blink"] = alld.query("NEXT_SAC_BLINK_DURATION > 0")["diff_blink"] - alld.query("NEXT_SAC_BLINK_DURATION > 0")["NEXT_SAC_BLINK_END"]
alld.query("NEXT_SAC_BLINK_DURATION == 0")["diff_blink"] = 0


# In[ ]:


alld.query("diff_blink > 0 and diff_blink < 100")


# In[ ]:


round(7/49045*100,5)

