# _03_e_analyze_yelp.py
# Myckland Matthew


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


# Plot a histogram of the Yelp restaurant ratings for a given neighbourhood.
def plot_hist(row):
	plt.figure()
	plot_title = row['neighbourhood'] + ' Restaurant Yelp Ratings'
	plt.hist(row['ratings'])
	plt.xlabel('Yelp Rating')
	plt.ylabel('Count')
	plt.title(plot_title)
	outfile = 'figures/yelp_hists/' + row['neighbourhood'] + '.png'
	plt.savefig(outfile)
	plt.close()


# ANOVA analysis to see if restaurants differ in quality by neighbourhood.
def main():
	ratings = pd.read_pickle("datafiles/input_files/yelp_restaurant_ratings")
	ratings_list = ratings.to_list()

	# Produce histograms for each neighbourhood's Yelp restaurant ratings to see if there are any issues with normality.
	ratings.reset_index().apply(plot_hist, axis=1)
	# Result: the data is normal-enough looking to proceed with ANOVA.

	# Perform ANOVA and look at p-value.
	anova = stats.f_oneway(*ratings_list)
	print("Yelp ANOVA p-value:", anova.pvalue, "\n")
	# Result: p-value is small enough to perform post-hoc analysis.

	ratings_formatted = pd.DataFrame(ratings_list).transpose()
	ratings_formatted.columns = ratings.index

	ratings_melted = pd.melt(ratings_formatted)
	# print(ratings_melted)

	# Perform Tukey's Honest Significant Difference test and plot the results.
	posthoc = pairwise_tukeyhsd(ratings_melted['value'], ratings_melted['neighbourhood'], alpha=0.05)
	# print(posthoc)

	fig = posthoc.plot_simultaneous(xlabel='Mean Yelp Rating', ylabel='Neighbourhood', figsize=(20,12))
	plt.savefig('figures/Yelp_Tukey_HSD.png')

	# Calculate the average Yelp restaurant rating for each neighbourhood and use it as the score.
	mean_ratings = ratings.apply(lambda x: np.mean(x))
	mean_ratings.rename("yelp", inplace=True)
	print("\nYelp Scores: ")
	print(mean_ratings)

	mean_ratings.to_csv("datafiles/yelp_scores.csv")


if __name__ == '__main__':
	main()
