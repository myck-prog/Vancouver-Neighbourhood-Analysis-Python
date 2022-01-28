# _03_a_calc_skytrain_scores.py
# James Braun


import numpy as np
import pandas as pd


# Calculates the distance in metres to every Skytrain station for a given neighbourhood.
# Code modified from James Braun's "calc_distance.py" file from Exercise 3.
def distance(nbh, stations):
	# Mean radius of Earth in metres courtesy of NASA:
	# 	https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
	earth_radius = 6371000

	# Convert latitude/longitude from degrees to radians to use the haversine formula.
	nbh_lat = np.deg2rad(nbh['lat'])
	nbh_lon = np.deg2rad(nbh['lon'])
	station_lats = np.deg2rad(stations['lat'])
	station_lons = np.deg2rad(stations['lon'])

	h = (1-np.cos(station_lats-nbh_lat))/2 + np.cos(nbh_lat) * np.cos(station_lats) * (1-np.cos(station_lons-nbh_lon))/2
	return 2 * earth_radius * np.arcsin(np.sqrt(h))


# Returns the distance in metres to the closest Skytrain station for a given neighbourhood.
def closest_station(nbh, stations):
	return distance(nbh, stations).min()


# Returns a score out of 5 based on the distance to the closest Skytrain station for a given neighbourhood.
# The further that distance is compared to the mean distance for all neighbourhoods, the more extreme the score.
# Closer = Better.
def calc_score(dist, da_mean, da_std):
	if dist <= (da_mean - da_std):
		return 5
	elif dist <= (da_mean - 0.5*da_std):
		return 4
	elif dist <= (da_mean + 0.5*da_std):
		return 3
	elif dist <= (da_mean + da_std):
		return 2
	else:
		return 1


def main():
	nbhs = pd.read_csv("datafiles/input_files/neighbourhood_locations.csv", index_col = 'neighbourhood')
	# print(nbhs, "\n\n")
	stations = pd.read_csv("datafiles/input_files/skytrain_locations.csv", index_col = 'station')
	# print(stations, "\n\n")

	skytrain_dists = nbhs.apply(closest_station, stations=stations, axis=1)
	skytrain_dists.name = 'distance'
	# print(skytrain_dists, "\n\n")

	scores = skytrain_dists.apply(calc_score, da_mean=skytrain_dists.mean(), da_std=skytrain_dists.std())
	scores.name = "skytrain"
	scores.index.name = "neighbourhood"
	print("Skytrain Distance Scores:")
	print(scores)

	scores.to_csv("datafiles/skytrain_scores.csv")


if __name__ == '__main__':
	main()
