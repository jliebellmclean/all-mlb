# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 16:41:36 2025

@author: julia
"""

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 300

# Make the code generic for all teams

import json

with open('2_setup.json') as fh:
    info = json.load(fh)

year = info["year"]
team = info["team"]
div = info["div"]

# Read information about the team's schedule/season

file_path = f"./outputs/{team}_{year}_cleaned.pkl"

segments = pd.read_pickle(file_path)

drop = ['Time', 'D/N', 'Orig. Scheduled','location']
segments = segments.drop(columns=drop)

# Create a new column indicating when games are away

segments["away"] = segments["@"].fillna(0)
segments["away"] = segments["away"].replace("@",1,regex=True)

# Create a lagged column

segments["lag"] = segments["away"].shift(+1)

#  Use it to find the start of home/away segments

segments['seg_start'] = segments['away'] != segments['lag']
segments.iloc[0]['seg_start'] = True

#  Number the segments consecutively

seg_num = segments[ segments['seg_start'] ]['seg_start'].cumsum()

#  Add the segment numbers to the data

segments['seg'] = seg_num
segments['seg'] = segments['seg'].ffill()

#%%

# Count the number of home and away games

print(f"{team} {year} Game Data:")

home_games = segments[segments["away"]==0]
print("Number of home games:",len(home_games))

away_games = segments[segments["away"]==1]
print("Number of away games:",len(away_games))

total_games = len(segments["away"])
print("Total games:",total_games)

# Count the number of home and away segments

print("Number of home and away stands:",len(seg_num))


#%%

# Group by the home and away stands (segs)

segs = segments.groupby('seg')

start = segs["Date"].first()
end = segs["Date"].last()
diff = (end-start).dt.days
seg_length = diff+1

seg_length.index = seg_length.index.astype(int)

# Plot the segments (by number) with their lengths

fig, ax1 = plt.subplots()
fig.suptitle(f"{team} {year}: Length of Home and Away Stands")
seg_length.plot.bar(ax=ax1)
ax1.set_ylabel("Days")
ax1.set_xlabel("Stand Number")

# Save the figure to the outputs folder

output_folder = './outputs/'
fig.savefig(output_folder + f"{team}_{year}_segs.png")

#%%

# Save the segments data to a file

segments.to_csv(output_folder + f"{team}_{year}_segments.csv")