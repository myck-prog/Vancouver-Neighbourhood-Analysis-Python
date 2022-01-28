# _01_a_get_neighbourhood_locs.py
# James Braun


import googlemaps
import numpy as np
import pandas as pd

# Learned how to use Google's Geocoding API from:
# 	https://github.com/googlemaps/google-maps-services-python

# Return a latitude, longitude point for a given neighbourhood.
# Uses Google Maps' Geocoding API.
def get_neighbourhood_loc(name, gmaps):
	da_search = name + " Vancouver neighbourhood"
	geocode_result = gmaps.geocode(da_search)
	da_lat = geocode_result[0]['geometry']['location']['lat']
	da_lon = geocode_result[0]['geometry']['location']['lng']

	return (da_lat, da_lon)


def main():
	gmaps = googlemaps.Client(key='')

	# A list of Vancouver's 22 official neighbourhoods.
	nbh_names = ["Arbutus Ridge", "Downtown", "Dunbar-Southlands", "Fairview", "Grandview-Woodland", "Hastings-Sunrise", \
				 "Kensington-Cedar Cottage", "Kerrisdale", "Killarney", "Kitsilano", "Marpole", "Mount Pleasant", "Oakridge", \
				 "Renfrew-Collingwood", "Riley Park", "Shaughnessy", "South Cambie", "Strathcona", "Sunset", "Victoria-Fraserview", \
				 "West End", "West Point Grey"]

	v_nbh_loc_func = np.vectorize(get_neighbourhood_loc, otypes=[np.float64, np.float64])
	nbh_lat_lons = v_nbh_loc_func(nbh_names, gmaps)

	neighbourhoods = pd.DataFrame(data={'neighbourhood':nbh_names, 'lat':nbh_lat_lons[0], 'lon':nbh_lat_lons[1]})
	neighbourhoods.set_index('neighbourhood', inplace=True)

	print("Vancouver Neighbourhoods and their Locations:")
	print(neighbourhoods)

	neighbourhoods.to_csv("datafiles/input_files/neighbourhood_locations.csv")


if __name__ == '__main__':
	main()
