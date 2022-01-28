# 01-get_data.py


import _01_a_get_neighbourhood_locs as _01_a
import _01_b_get_skytrain_locs as _01_b
import _01_c_get_yelp_ratings as _01_c


def main():
	_01_a.main()
	print("\n")

	_01_b.main()
	print("\n")

	_01_c.main()


if __name__ == '__main__':
	main()
