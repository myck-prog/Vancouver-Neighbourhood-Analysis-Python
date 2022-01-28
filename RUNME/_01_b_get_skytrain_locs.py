# _01_b_get_skytrain_locs.py
# James Braun


import googlemaps
import numpy as np
import pandas as pd


# Return a latitude, longitude point for a given Skytrain station.
# Uses Google Maps' Geocoding API.
def get_skytrain_loc(name, gmaps):
	da_search = name + " Skytrain station"
	geocode_result = gmaps.geocode(da_search)
	da_lat = geocode_result[0]['geometry']['location']['lat']
	da_lon = geocode_result[0]['geometry']['location']['lng']

	return (da_lat, da_lon)


def main():
	gmaps = googlemaps.Client(key='')

	# Scrape a Wikipedia article to get the list of Skytrain station names.
	skytrain_wiki_url = 'https://en.wikipedia.org/wiki/List_of_Vancouver_SkyTrain_stations#Stations'
	skytrain_html = pd.read_html(skytrain_wiki_url)
	stations = skytrain_html[1]['Station']
	station_names = stations.replace(r'\*|\[.\]','', regex=True)

	v_skytrain_loc_func = np.vectorize(get_skytrain_loc, otypes=[np.float64, np.float64])
	skytrain_lat_lons = v_skytrain_loc_func(station_names, gmaps)

	stations = pd.DataFrame(data={'station': station_names, 'lat': skytrain_lat_lons[0], 'lon': skytrain_lat_lons[1]})
	stations.set_index('station', inplace=True)

	print("Skytrain Stations and their Locations:")
	print(stations)

	stations.to_csv("datafiles/input_files/skytrain_locations.csv")


if __name__ == '__main__':
	main()
