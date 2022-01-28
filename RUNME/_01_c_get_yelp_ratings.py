# _01_c_get_yelp_ratings.py
# Myckland Matthew


import json
import pandas as pd
import requests

# Yelp's Fusion API documentation can be found at:
# 	https://www.yelp.ca/developers/documentation/v3

# Return the ratings of the 50 most reviewed restaurants in a given neighbourhood
# 	(i.e. within a 2km radius of the single-point representation of the neighbourhood).
# Uses Yelp's Fusion API:
# 	https://www.yelp.ca/fusion
def get_ratings(nbh, ep, hdrs):
	PARAMETERS = {'latitude':nbh['lat'],
				  'longitude':nbh['lon'],
				  'limit':'50',
				  'radius':'2000',
				  'sort_by':'review_count',
				  'term':'restaurant'
	}

	response = requests.get(url=ep, params=PARAMETERS, headers=hdrs)
	parsed = json.loads(response.text)
	df = pd.json_normalize(parsed['businesses'])

	return df['rating'].to_numpy(copy=True)


def main():
	api_key=''
	headers = {'Authorization': 'Bearer %s' % api_key}
	ENDPOINT = "https://api.yelp.com/v3/businesses/search"

	nbh_locs = pd.read_csv("datafiles/input_files/neighbourhood_locations.csv")

	ratings = nbh_locs.apply(get_ratings, axis=1, ep=ENDPOINT, hdrs=headers)
	ratings.set_axis(nbh_locs['neighbourhood'], inplace=True)
	ratings.rename('ratings', inplace=True)

	ratings.to_pickle("datafiles/input_files/yelp_restaurant_ratings")

	print("Yelp Restaurant Ratings by Neighbourhood: ")
	print(ratings)

if __name__ == '__main__':
	main()
