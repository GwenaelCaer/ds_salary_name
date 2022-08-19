# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 18:09:57 2022

@author: gwena
"""

import glassdoor_scraper as gs
import pandas as pd

path = "C:/Users/gwena/Documents/ds_salary_proj/chromedriver.exe"
df = gs.get_jobs("data scientist", 15, False, path, 5)