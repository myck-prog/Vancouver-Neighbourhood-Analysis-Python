# _02_c_tabulate_monthly_crimes.py
# Jonghyeok Kim


import numpy as np
import pandas as pd

# Vancouver Crime Data courtesy of the VPD:
# 	https://geodash.vpd.ca/opendata/

def clean_crime_data(crime_file):
	# Select violent crimes from 2016 to 2020 that have a neighbourhood.
	crime_data = pd.read_csv(crime_file)
	violent_crimes = ['Homicide', 'Offence Against a Person', 'Break and Enter Residential/Other']
	crime_data_no_NA = crime_data[["TYPE", "YEAR", "MONTH", "NEIGHBOURHOOD"]].dropna(subset=['NEIGHBOURHOOD'])
	crime_data_with_nbh = crime_data_no_NA[(crime_data_no_NA['NEIGHBOURHOOD'] != "Stanley Park") & (crime_data_no_NA['NEIGHBOURHOOD'] != "Musqueam")]
	crime_data_last_5_years = crime_data_with_nbh[(crime_data_with_nbh['YEAR'] >= 2016) & (crime_data_with_nbh['YEAR'] != 2021)]
	violent_crime_data = crime_data_last_5_years[crime_data_last_5_years['TYPE'].apply(lambda x: x in violent_crimes)]
	# print(violent_crime_data)

	# Count the number of crimes by month for each neighbourhood.
	violent_crime_data_count = violent_crime_data.groupby(by=['NEIGHBOURHOOD', 'YEAR', 'MONTH']).count().iloc[:, 0:4].reset_index().rename(columns={'TYPE': 'crime_count'})
	violent_crime_data_count['NEIGHBOURHOOD'] = violent_crime_data_count['NEIGHBOURHOOD'].str.replace("Central Business District", "Downtown")
	violent_crime_data_count.columns = ["neighbourhood", "year", "month", "crime_count"]
	# print(violent_crime_data_count)

	return violent_crime_data_count


def clean_population_data(population_file):
	neighbourhood_pop_5yrs = pd.read_csv(population_file, sep='\t', index_col=0).iloc[:, 9:14].reset_index()
	# print(neighbourhood_pop_5yrs)

	# Melt the population DataFrame to make it's shape similar to the crime DataFrame.
	neighbourhood_pop_5yrs = pd.melt(neighbourhood_pop_5yrs, id_vars=['neighbourhood']).rename(columns={'variable': 'year', 'value': 'population'})
	neighbourhood_pop_5yrs['year'] = neighbourhood_pop_5yrs['year'].astype(int)
	# print(neighbourhood_pop_5yrs)

	return neighbourhood_pop_5yrs


def main():
	crime = clean_crime_data('datafiles/input_files/crimedata_csv_all_years.csv.gz')
	population = clean_population_data('datafiles/poulation_extrapolated.csv')

	pop_with_crime = population.merge(crime, on=['neighbourhood', 'year'])
	# print(pop_with_crime)

	# Calculate the violent crime rate per 10,000 residents for each neighbourhood.
	pop_with_crime['crime_rate'] = pop_with_crime['crime_count'] / pop_with_crime['population'] * 10000
	pop_with_crime.columns = ["neighbourhood", "year", "population", "month", "crime_count", "crime_rate"]
	pop_with_crime = pop_with_crime[["neighbourhood", "year", "month", "crime_count", "population", "crime_rate"]]
	pop_with_crime.to_csv('datafiles/monthly_crime.csv', index=False)

	print("Violent Crime Counts and Rates by Neighbourhood and Month: ")
	print(pop_with_crime)


if __name__ == "__main__":
	main();
