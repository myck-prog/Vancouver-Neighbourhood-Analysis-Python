# 04-recommend_neighbourhood.py
# James Braun


import numpy as np
import pandas as pd


# Validate the user's inputs.
# Created by Jonghyeok Kim.
def askInput(da_input):
	while True:
		try:
			da_number = float(input(da_input))
			if da_number < 1 or da_number > 5:
				raise ValueError  # this will send it to the print message and back to the input option.
			else:
				return int(da_number)
		except ValueError:
			print("Invalid input. Must be a number in the range of 1-5.")


# Translate a user's input to a weight.
def input_to_weight(inpt):
	if inpt == 1:
		weight = 0.0
	elif inpt == 2:
		weight = 0.5
	elif inpt == 4:
		weight = 2.0
	elif inpt == 5:
		weight = 10.0
	else:
		weight = 1.0

	return weight


def main():
	skytrain = pd.read_csv("datafiles/skytrain_scores.csv",  index_col="neighbourhood")
	prices = pd.read_csv("datafiles/price_scores.csv", index_col="neighbourhood")
	amenities = pd.read_csv("datafiles/amenity_scores.csv", index_col="neighbourhood")
	crime = pd.read_csv("datafiles/safety_scores.csv", index_col="neighbourhood")
	yelp = pd.read_csv("datafiles/yelp_scores.csv", index_col="neighbourhood")

	# print(skytrain)
	# print(prices)
	# print(amenities)
	# print(crime)
	# print(yelp)

	together = skytrain.join(prices).join(amenities).join(crime).join(yelp)
	print("All the Neighourhood Scores Together: ")
	print(together)
	print("\n")

	together.to_csv("datafiles/all_scores.csv")

	print("Please enter a desirability score from 1-5 for the following amenities where:")
	print("1 = don't care at all")
	print("2 = care a bit")
	print("3 = care a moderate amount")
	print("4 = care a lot")
	print("5 = critically important\n")

	print("If you enter a number between 1 and 5 that has a decimal (e.g. 3.7), it will be rounded down.\n")

	print("Please see the README for more information and examples of the amenities.\n")

	user_skytrain = askInput("Distance to Skytrain: ")
	user_price = askInput("Housing Prices: ")
	user_arts = askInput("Artistic / Cultural Landmarks: ")
	user_cars = askInput("Automobile Services: ")
	user_educ = askInput("Education / Childcare Facilities: ")
	user_food = askInput("Wide Variety of Places to Eat and Drink: ")
	user_healthcare = askInput("Healthcare Clinics: ")
	user_money = askInput("Financial Institutions: ")
	user_crime = askInput("Safety: ")
	user_yelp = askInput("Restaurant Quality: ")

	print("\n")

	user_inputs = np.array([user_skytrain, user_price, user_arts, user_cars, user_educ, user_food, user_healthcare, user_money, user_crime, user_yelp], dtype='float16')
	# print(user_inputs)
	vfunc = np.vectorize(input_to_weight)
	user_inputs_weighted = vfunc(user_inputs)
	# print(user_inputs_weighted)
	
	calculated_scores = together @ user_inputs_weighted
	# print(calculated_scores)

	print("Here are the resulting scores for each of Vancouver's 22 neighbourhoods based on your given preferences:")
	final_scores = pd.DataFrame(data=calculated_scores, index=together.index, columns=['Final Neighourhood Score'])
	print(final_scores.round(2))
	print("\n")

	print("Finally, here are your top 5 recommended neighbourhoods starting with the top suggestion:")
	print(final_scores.nlargest(5, 'Final Neighourhood Score').round(2))


if __name__ == '__main__':
	main()
