# _03_c_analyze_amenities.py
# James Braun


import numpy as np
import pandas as pd
from scipy import stats


def main():
	nbh_amen = pd.read_csv("datafiles/actual_amenity_counts.csv", index_col='neighbourhood')
	# print(nbh_amen)

	populations = pd.read_csv("datafiles/poulation_extrapolated.csv", index_col='neighbourhood', sep="\t")
	# print(populations['2021'])

	# Sum up the total amount of amenities of each category across all neighbourhoods.
	total_amen = nbh_amen.sum(axis=0)
	# print(total_amen)

	# Calculate Vancouver's (estimated) 2021 population.
	total_pop = populations['2021'].sum()
	# print(total_pop)

	# Calculate the estimated relative population of each neighbourhood in 2021.
	relative_pops = populations['2021'] / total_pop
	# print(relative_pops)

	# Use the total number of amenities and the relative population of each neighbourhood
	# 	to calculate the expected number of amenities per neighbourhood.
	# For example, if there are 2,000 eating establishments in Vancouver,
	# 	and Kerrisdale has 2% of Vancouver's total population,
	# 	then we expect that Kerrisdale would have 2,000 * 0.02 = 40 eating establishments within its borders.
	rel_pop_np = relative_pops.to_numpy().reshape(22,1)
	total_amen_np = total_amen.to_numpy().reshape(1,6)
	expected_amen = pd.DataFrame(data=(rel_pop_np @ total_amen_np), index=nbh_amen.index, columns=nbh_amen.columns)
	expected_amen.to_csv("datafiles/expected_amenity_counts.csv")
	# print(expected_amen)

	# For each amenity category, use a one-way chi-squared test to determine if
	# 	the neighbourhood you are in affects the number of amenities you'll find beyond differences due to differing populations.
	# This sets expected amenity counts relative to each neighbourhood's population.
	print("One-Way Chi-square Tests for each Amenity Category:")
	for amenity in nbh_amen.columns:
		print(amenity, "\ntwo-sided p-value:", stats.chisquare(nbh_amen[amenity], f_exp=expected_amen[amenity]).pvalue)
		print("")

	amen_p_table = nbh_amen.copy()

	# For every amenity category and every neighbourhood:
	# 	use a binomial test to determine the probability under the null hypothesis that
	# 	the amenity count is as extreme or is more extreme as it is.
	# We want to determine if each neighbourhood has statistically more or less amenities than we'd expect given its relative population.
	# For example, using Kerrisdale eating establishments again:
	# 	Null hypothesis: true proportion of eating establishments in Kerrisdale compared to all of Vancouver = 0.02
	# 	Alternative hypothesis: true proportion of eating establishments != 0.02
	# For the binomial test:
	# 	the number of successes is the amenity count for that category.
	# 	the number of trials is the total amenity count across all of Vancouver for that category.
	# 	the probability of success is the relative population of the given neighbourhood.
	for amenity in nbh_amen.columns:
		for nbh in nbh_amen.index:
			amen_p_table.loc[nbh, amenity] = stats.binomtest(k=nbh_amen.loc[nbh, amenity], n=total_amen[amenity], p=relative_pops[nbh], alternative='two-sided').pvalue

	print("Amenity Binomial Test Two-Sided p-values:")
	print(amen_p_table, "\n")

	# These two 'bool' DataFrames hold whether or not the p value 
	# 	for each amenity category/neighbourhood pair binomial test
	# 	is below a certain threshold, with or without a Bonferroni correction.
	regular_p_bool = amen_p_table<0.05  # without Bonferroni correction.
	bon_p_bool = amen_p_table<(0.05/22) # with Bonferroni correction b/c there are 22 neighbourhoods.
	amen_scores = nbh_amen.copy()

	# This calculates a score out of 5 based on the aforementioned p-values.
	# If the p-value is significant even after a Bonferroni correction, it gets a 1 or 5.
	# If the p-value is significant at p=0.05, but not after a Bonferroni correction, it gets a 2 or 4.
	# If the p-value is greater than 0.05, then it gets a 3 
	# 	b/c then there's not enough evidence to say the count is different from what's expected.
	# Here higher count = higher score.
	for amenity in nbh_amen.columns:
		for nbh in nbh_amen.index:
			if regular_p_bool.loc[nbh, amenity] == False:
				amen_scores.loc[nbh, amenity] = 3
			elif bon_p_bool.loc[nbh, amenity] == True:
				if nbh_amen.loc[nbh, amenity] < expected_amen.loc[nbh, amenity]:
					amen_scores.loc[nbh, amenity] = 1
				else:
					amen_scores.loc[nbh, amenity] = 5
			else:
				if nbh_amen.loc[nbh, amenity] < expected_amen.loc[nbh, amenity]:
					amen_scores.loc[nbh, amenity] = 2
				else:
					amen_scores.loc[nbh, amenity] = 4

	# print(amen_scores.duplicated(keep=False))
	print("Amenity Scores:")
	print(amen_scores)

	amen_scores.to_csv("datafiles/amenity_scores.csv")



if __name__ == '__main__':
	main()