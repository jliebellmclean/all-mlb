# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 16:17:22 2025

@author: julia
"""

import pandas as pd
import statistics
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 300

# Make the code generic for all teams

import json

with open('2_setup.json') as fh:
    info = json.load(fh)

year = info["year"]
team = info["team"]
div = info["div"]

# Read information from the cleaned schedule file

file_path = f"./outputs/{team}_{year}_cleaned.pkl"
series = pd.read_pickle(file_path)
drop = ['Time', 'D/N', 'Orig. Scheduled','location']
series = series.drop(columns=drop)

# Create a new column indicating when games are away. Count the number of series.

series["last_opp"] = series["Opp"].shift(+1)

series["new_series"] = series["Opp"] != series["last_opp"]
series.iloc[0]["new_series"] = True

sers = series[series["new_series"]]["new_series"].cumsum()
series["series"] = sers
series["series"] = series["series"].ffill()

#%%

# Use groupby to group the games by their series. Calculate the number of days per series

series_group = series.groupby('series')

start = series_group["Date"].first()
end = series_group["Date"].last()
diff_series = (end-start).dt.days
diff_series = diff_series+1

# Compute some information about the length of series in 2022

print(f"Number of series in {team} {year} season:",len(series_group))

longest = diff_series.max()
print("Longest series:",longest,"days")
shortest = diff_series.min()
print('Shortest series:',shortest,"days")
mode = statistics.mode(diff_series)
print("Most common series length:",mode,"days")
avg = round(diff_series.mean(),2)
print("Average series length:",avg,"days")

#%%

# Plot the segments (by number) with their lengths

diff_series.index = diff_series.index.astype(int)

fig, ax1 = plt.subplots()
fig.suptitle(f"{team} {year} Length of Series")
diff_series.plot.bar(ax=ax1)
ax1.set_ylabel("Days")
ax1.set_xlabel("Series Number")

# Define the outputs folder and save to the folder

output_folder = './outputs/'
fig.savefig(output_folder + f"{team}_{year}_series.png")

#%%

# Save series information to a csv

series.to_csv(output_folder + f"{team}_{year}_series.csv")