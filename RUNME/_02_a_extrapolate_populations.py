# _02_a_extrapolate_nbh_populations.py
# James Braun


import numpy as np
import pandas as pd

# Population figures from:
# 	https://www.abundanthousingvancouver.com/research
# which is based on Vancouver census data


# Extrapolates the 2017-2021 populations of Vancouver's neighbourhoods
# 	using their 2011 and 2016 populations.
# For example, if from 2011 to 2016 Marpole's population grew by 2% annually,
# 	then from 2017 to 2021 we would estimate that it would again grow by 2% annually.
def main():
	pops = pd.read_csv("datafiles/input_files/population.csv", sep="\t", index_col=[0], thousands=',')
	pops.index.name = 'neighbourhood'

	# Code to convert a numpy array of ints to strings adapted from Stardust's answer from:
	# 	https://stackoverflow.com/questions/9958846/converting-int-arrays-to-string-arrays-in-numpy-without-truncation
	years = list(map(str, np.arange(2016, 2022)))
	# print(years)

	# Calculate the annual population change.
	yrly_ch = np.power((pops['2016']/pops['2011']), 0.2)
	# print(yrly_ch)

	# Extrapolate the populations.
	for x in range(5):
		pops[years[x+1]] = pops[years[x]] * yrly_ch

	pops = pops.astype('int32')
	print("Extrapolated Neighbourhood Population by Year:")
	print(pops.iloc[:,8:])

	pops.to_csv("datafiles/poulation_extrapolated.csv", sep="\t")


if __name__ == '__main__':
	main()
