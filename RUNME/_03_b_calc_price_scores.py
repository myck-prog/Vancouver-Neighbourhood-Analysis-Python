# _03_b_calc_price_scores.py
# James Braun


import numpy as np
import pandas as pd

# Average sale price per square foot data courtesy of Redfin:
# 	www.redfin.ca.
# Values are correct as of July 17, 2021.
# Data scraped manually.

# Returns a score out of 5 based on the average sale price per square foot for a given neighbourhood.
# The further that price is compared to the mean price for all neighbourhoods, the more extreme the score.
# Cheaper = Better.
def calc_score(nbh, da_mean, da_std):
	if nbh <= (da_mean - da_std):
		return 5
	elif nbh <= (da_mean - 0.5*da_std):
		return 4
	elif nbh <= (da_mean + 0.5*da_std):
		return 3
	elif nbh <= (da_mean + da_std):
		return 2
	else:
		return 1


def main():
	prices = pd.read_csv("datafiles/input_files/prices_per_sqft.csv", index_col = 'neighbourhood')
	# print(prices)
	# print(prices.mean()[0], prices.std()[0])

	vfunc = np.vectorize(calc_score, otypes=[np.int])
	scores = pd.DataFrame(vfunc(prices, da_mean = prices.mean(), da_std = prices.std()), index=prices.index, columns=['price'])
	print("Average Sale Price per sqft Scores:")
	print(scores)

	scores.to_csv("datafiles/price_scores.csv")



if __name__ == '__main__':
	main()
