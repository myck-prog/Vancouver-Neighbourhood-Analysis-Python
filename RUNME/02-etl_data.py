# 02-etl_data.py


import _02_a_extrapolate_populations as _02_a
import _02_b_tabulate_amenity_counts as _02_b
import _02_c_tabulate_monthly_crimes as _02_c


def main():
	_02_a.main()
	print("\n")

	_02_b.main()
	print("\n")

	_02_c.main()


if __name__ == '__main__':
	main()
