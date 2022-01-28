# _03_d_analyze_crime.py
# Jonghyeok Kim


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def min_max_score(x, max_x, min_x):
	return (1 - (x - min_x) / (max_x - min_x)) * 5


# Plot a histogram of the unchanged or square-rooted monthly violent crime rates for a given neighbourhood.
# trans_bool = whether or not this is the square-rooted data.
def plot_hist(row, trans_bool):
	if trans_bool:
		plot_title = 'Square Root of ' + row.name + ' Monthly Violent Crime Rates'
		x_label = 'sqrt(Monthly Instances of Violent Crime per 10,000 Residents)'
		outfile = 'figures/crime_hists_post_trans/' + row.name + '.png'
	else:
		plot_title = row.name + ' Monthly Violent Crime Rates'
		x_label = 'Monthly Instances of Violent Crime per 10,000 Residents'
		outfile = 'figures/crime_hists_pre_trans/' + row.name + '.png'

	plt.figure()
	plt.hist(row.to_list())
	plt.xlabel(x_label)
	plt.ylabel('Months')
	plt.title(plot_title)
	plt.savefig(outfile)
	plt.close()

# ANOVA analysis to see if neighbourhoods differ in amount of violent crime.
def main():
	crime_data = pd.read_csv("datafiles/monthly_crime.csv")
	# print(crime_data)

	# Reformat the crime data for an ANOVA test.
	crime_data_formatted = crime_data.pivot(index=['year', 'month'], columns='neighbourhood', values='crime_rate')
	# Produce histograms for each neighbourhood's monthly crime rates to see if there are any issues with normality.
	crime_data_formatted.apply(plot_hist, trans_bool=False)
	# Result: the data seems right-skewed, so let's use a square root transformation and re-plot.

	crime_data_sqrt = np.sqrt(crime_data_formatted)
	crime_data_sqrt.apply(plot_hist, trans_bool=True)
	# Result: good enough to perform ANOVA.

	# Perform ANOVA and look at p-value.
	anova = stats.f_oneway(*crime_data_sqrt.transpose().to_numpy())
	print("Crime ANOVA p-value:", anova.pvalue, "\n")
	# Result: p-value is small enough to perform post-hoc analysis.

	# Perform Tukey's Honest Significant Difference test and plot the results.
	posthoc = pairwise_tukeyhsd(np.sqrt(crime_data['crime_rate']), crime_data['neighbourhood'], alpha=0.05)
	# print(posthoc)

	fig = posthoc.plot_simultaneous(xlabel='Mean Square Root of Monthly Crime Rate', ylabel='Neighbourhood', figsize=(20,12))
	plt.savefig('figures/Crime_Tukey_HSD.png')

	# Calculate the average monthly crime rate and calculate the scores using min-max.
	mean_monthly = crime_data[['neighbourhood', 'crime_rate']].groupby(by=['neighbourhood']).mean()
	# print(mean_monthly)

	mean_monthly['safety'] = mean_monthly['crime_rate'].apply(min_max_score, max_x=mean_monthly['crime_rate'].max(), min_x=mean_monthly['crime_rate'].min())
	mean_monthly['safety'].round(2).to_csv('datafiles/safety_scores.csv')

	print("\nSafety Scores:")
	print(mean_monthly['safety'].round(2))


if __name__ == "__main__":
	main()
