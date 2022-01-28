# 03-analyze_data.py


import _03_a_calc_skytrain_scores as _03_a
import _03_b_calc_price_scores as _03_b
import _03_c_analyze_amenities as _03_c
import _03_d_analyze_crime as _03_d
import _03_e_anlayze_yelp as _03_e


def main():
	_03_a.main()
	print("\n")

	_03_b.main()
	print("\n")

	_03_c.main()
	print("\n")

	_03_d.main()
	print("\n")

	_03_e.main()


if __name__ == '__main__':
	main()
