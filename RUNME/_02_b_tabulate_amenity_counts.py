# _02_b_tabulate_amenity_counts.py
# James Braun and Jonghyeok Kim


import json
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Vancouver amenities data provided by Professor Baker:
# 	https://coursys.sfu.ca/2021su-cmpt-353-d1/pages/ProjectTour

# Vancouver boundaries originated from the City of Vancouver's Open Data Portal:
# 	opendata.vancouver.ca/explore/dataset/local-area-boundary/information/


# Return the amenity category for the given amenity (if possible).
def get_category(amenity, amen_cats):
	for cat, amens in amen_cats:
		if amenity in amens:
			return cat

	return None


# Return the latitude and longitude of the given geometric object.
def get_coords(geom):
	return geom['coordinates'][0]


# For a given amenity point, search through the neighbourhood polygons
# 	and find which neighbourhood it belongs to (if possible).
def get_nbh(amenity, nbhs):
	for neighbourhood, boundary in nbhs.items():
		if amenity.within(boundary):
			return neighbourhood

	return None


def main():
	# Read in Vancouver's neighbourhood boundaries.
	local_boundary = pd.read_csv('datafiles/input_files/local-area-boundary.csv',sep=';')

	# Create polygons to represent each neighbourhood.
	polygons = local_boundary['Geom'].apply(json.loads).apply(get_coords).apply(Polygon) #.reset_index(drop=True)

	# Store the polygons in a Series.
	boundaries = pd.DataFrame(local_boundary['Name']).sort_values('Name')
	boundaries['Poly'] = polygons
	boundaries.set_index('Name', inplace=True)
	boundaries = boundaries.squeeze()
	# print(boundaries)
	# print(type(boundaries))

	amenities = pd.read_json('datafiles/input_files/amenities-vancouver.json.gz', lines=True)

	# Split specific amenities into different categories.
	amen_cats = {
		"arts/culture": 		["arts_centre", "boat_rental", "cinema", "community_centre", "events_centre", "library", "meditation_centre", "monastery", "park", "place_of_worship", "public_bookcase", "spa", "theatre"],
		"cars": 				["car_rental", "car_rep", "car_sharing", "car_wash", "charging_station", "fuel"],
		"education/childcare": 	["childcare", "college", "cram_school", "driving_school", "family_centre", "kindergarten", "music_school", "playground", "prep_school", "research_institute", "school", "university"],
		"food/drink": 			["bar", "bbq", "biergarten", "bistro", "cafe", "fast_food", "food_court", "ice_cream", "internet_cafe", "juice_bar", "pub", "restaurant", "vending_machine"],
		"healthcare": 			["chiropractor", "dentist", "doctors", "first_aid", "healthcare", "hospital", "pharmacy", "veterinary"],
		"money": 				["atm", "atm;bank", "bank", "bureau_de_change", "money_transfer"]
	}

	amenities_select_cols = amenities[['lat', 'lon', 'name', 'amenity']].copy()
	# print(amenities_select_cols)

	# Determine the amenity category of each amenity.
	amenities_select_cols['category'] = amenities_select_cols['amenity'].apply(get_category, amen_cats=amen_cats.items())
	# print(amenities_select_cols)

	# This keeps only the amenities that belong to one of the categories we're looking at.
	amenities_with_cat = amenities_select_cols[amenities_select_cols['category'].notna()].copy().reset_index(drop=True)
	# print(amenities_with_cat)

	# Turn the amenity locations into geometric points and identify which neighbourhood they belong to.
	coords = pd.Series(zip(amenities_with_cat.iloc[:,1], amenities_with_cat.iloc[:,0]))
	points = coords.apply(Point)
	# print(points)

	amenities_with_cat['neighbourhood'] = points.apply(get_nbh, nbhs=boundaries)
	# print(amenities_with_cat)

	# Drop all amenities that don't belong to one of Vancouver's neighbourhoods.
	amenities_with_nbh = amenities_with_cat[amenities_with_cat['neighbourhood'].notna()].copy().reset_index(drop=True)
	# print(amenities_with_nbh)

	amenities_with_nbh.to_csv("datafiles/amenities_labelled_by_nbh.csv", index=False)
	print("Amenities Labelled by Category and Neighbourhood:")
	print(amenities_with_nbh, "\n")

	# Count how many amenities of each category belong to each neighbourhood.
	amen_counts = pd.crosstab(amenities_with_nbh['neighbourhood'], amenities_with_nbh['category'])
	amen_counts.columns.name = ""
	amen_counts = amen_counts[list(amen_cats.keys())]

	amen_counts.to_csv("datafiles/actual_amenity_counts.csv")
	print("Amenity Counts by Category and Neighbourhood:")
	print(amen_counts)


if __name__ == '__main__':
	main()
