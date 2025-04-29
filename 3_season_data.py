# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:49:29 2025

@author: julia
"""

import pandas as pd
import json

with open('2_setup.json') as fh:
    info = json.load(fh)

year = info["year"]
team = info["team"]
div = info["div"]

# Read the season schedule data from the csv file within the season_data folder. Set the index to the game number
# csv data for the 2022 season is from baseball-reference: https://www.baseball-reference.com/teams/NYM/2024-schedule-scores.shtml#all_team_schedule

file_path = f"./season_data/{team}_{year}.csv"

season = pd.read_csv(file_path)
season = season.set_index("Gm#")

season = season.rename(columns={'Unnamed: 2':'boxscore','Unnamed: 4':'@'})

# List the column names from the csv file. Drop unnecessary columns

drop_cols = ['boxscore','W/L', 'R', 'RA', 'Inn', 'W-L','Rank', 'GB', 'Win', 'Loss', 'Save','Attendance', 'cLI','Streak']
season = season.drop(columns=drop_cols)

#%% 

# Determine which are away games. Create a column for location.

season["location"] = season["Tm"]
season["location"] = season["Opp"].where(season["@"]=='@')
season["location"] = season["location"].fillna(season["Tm"])

#%%

# Convert the date information into the proper form. Add 2022 to make it readable

season["Date"] = season["Date"].astype(str) + f" {year}"

# Eliminate the parentheses for double headers

season["Date"] = season["Date"].str.replace(r" \(\d\)","",regex=True)

season["Date"] = pd.to_datetime(season["Date"])

# Indicate the outputs folder. Save to a csv file and pickle file in the outputs folder.

output_folder = './outputs/'

season.to_csv(output_folder + f"{team}_{year}_cleaned.csv")
season.to_pickle(output_folder + f"{team}_{year}_cleaned.pkl")
