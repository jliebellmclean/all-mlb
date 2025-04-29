# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 11:24:43 2025

@author: julia
"""

import pandas as pd
import geopandas as gpd
import json

with open('2_setup.json') as fh:
    info = json.load(fh)

year = info["year"]
team = info["team"]
div = info["div"]

# Merge the location data and division information onto the schedule

file_path = f"./outputs/{team}_{year}_cleaned.pkl"
schedule = pd.read_pickle(file_path)
locations = pd.read_pickle("./outputs/team_locations.pkl")

# Drop the divisions from locations. This is necessary so that divisions correspond to the opponent, not the location

locations = locations.drop(columns="DIVISION")

# Preserve the original index from the schedule data. Use it to reassign the inex post-merge

original_index = schedule.index
schedule = schedule.merge(locations,how="left",on="location")
schedule.index = original_index

# Drop unnecessary columns from the data frame

cols = schedule.columns
drop = ['Time','D/N','Orig. Scheduled','ABBREVIATION']
schedule = schedule.drop(columns=drop)

#%%

# Add back in information about divisions
# Strip the team info dataframe down to just division information

divisions = pd.read_pickle("./outputs/team_locations.pkl")
divisions = divisions.drop(columns=["LATITUDE","LONGITUDE","geometry","location"])
divisions = divisions.rename(columns={"ABBREVIATION":"Opp"})

# Merge the division information onto the schedule, matching it to the opponent for each game

schedule = schedule.merge(divisions, how="left",on="Opp")
schedule.index = original_index

#%%

# Add the data about segments

segments = pd.read_csv(f"./outputs/{team}_{year}_segments.csv")

# Make sure the Date information is compatible in both dataframes

schedule["Date"] = pd.to_datetime(schedule["Date"], errors="coerce")
segments["Date"] = pd.to_datetime(segments["Date"], errors="coerce")

# Complete the merge

schedule = schedule.merge(segments,how="left",on=["Gm#","Date","Tm","@","Opp"])

#%%

# Add the data about series

series = pd.read_csv(f"./outputs/{team}_{year}_series.csv")

# Make sure the Date information is compatible in both dataframes

schedule["Date"] = pd.to_datetime(schedule["Date"], errors="coerce")
series["Date"] = pd.to_datetime(series["Date"], errors="coerce")

# Complete the merge

schedule = schedule.merge(series, how="left",on=["Gm#","Date","Tm","@","Opp"])
schedule = schedule.set_index("Gm#")

#%%

# Calculate how many games were played in division

in_div = schedule[schedule["DIVISION"]== div]
out_div = schedule[schedule["DIVISION"] != div]

print("Number of in-division games:",len(in_div))
print("Out-of-division games:",len(out_div))

#%%

# Create new data frames for calculating distance. Remove unnecessary info

travel_end = schedule.copy()
drop = ['Date', 'Tm', '@', 'Opp','DIVISION', 'away', 'lag', 'seg_start', 'seg','last_opp', 'new_series', 'series']
travel_end = travel_end.drop(columns = drop)
travel_start = travel_end.copy()

# Determine the home location for a given team

home_geom = locations[locations["ABBREVIATION"] == team].iloc[0]

# Create a row for the home location

home_row = gpd.GeoDataFrame([{
    'location': home_geom['location'],
    'geometry': home_geom['geometry'],
    'LATITUDE': home_geom['LATITUDE'],
    'LONGITUDE': home_geom['LONGITUDE']
}], geometry='geometry', crs=locations.crs)

# Add home as the first row in travel_start and last in travel_end.
# This will ensure that the distance calculation captures travel to and from games at the start and end of the season.

travel_end = pd.concat([travel_end, home_row], ignore_index=True)
travel_start = pd.concat([home_row, travel_start], ignore_index=True)

# Convert into GeoDataFrames

geo_end = gpd.GeoDataFrame(data=travel_end, geometry="geometry",crs=3857)
geo_start = gpd.GeoDataFrame(data=travel_start, geometry="geometry",crs=3857)

#%%

# Calculate distances traveled

distance = geo_start.distance(geo_end,align=None)

# Convert into miles

distance = distance/1609.34

# Calculate the total distance traveled

tot_dis = distance.sum().round()
print(f"\nTotal distance traveled, {team} {year}:",tot_dis,"miles")

#%%

# Count the number of days traveled

days_trav = distance.reset_index()
days_trav = days_trav[days_trav[0]!=0]
days_trav = days_trav.dropna(subset=0)
days_trav_num = days_trav[0].count()

print("Days traveled:",days_trav_num,"days")  

#%%

# Differentiate the trips by air and land travel

air_dist = distance[distance>300]
land_dist = distance[(distance<=300) & (distance>0)]

# Count the number of air and land travel days

print("\nDays of air travel:",len(air_dist),"days")
print("Days of land travel:",len(land_dist),"days")

#%%

# Calculate the carbon emitted for air travel 

# Define the number of passengers

pass_num = 200

# Define the CO2 emitted for plane versus bus travel. Note this is input in grams per passenger per km

ratio_air_CO2 = 158
ratio_land_CO2 = 97

# Calculate the CO2 for air travel. Convert miles to kilometers and divide total calculation to get metric tons

air_miles = air_dist.sum()
air_km = air_miles*1.60934
air_CO2 = ratio_air_CO2*air_km*pass_num/1e+6

print("\nTotal carbon from air travel:",air_CO2.round(3),"metric tons")                                                                                                                                                                                                                                                                                 

# Repeat for land travel

land_miles = land_dist.sum()
land_km = land_miles*1.60934
land_CO2 = ratio_land_CO2*land_km*pass_num/1e+6

print("Total carbon from land travel:",land_CO2.round(3),"metric tons")  

print(f"\nTotal carbon from travel for {team} in {year}:",(land_CO2+air_CO2).round(3),"metric tons")
