import sys
py_path = '../../tools/'
sys.path.insert(0, py_path)

py_path = '../../src/mobility/'
sys.path.insert(0, py_path)

import abm_residential as res

# ------------------------------------------------------------------
#
# Tests for arcGIS functionality in Households class
#
# ------------------------------------------------------------------

# File with residential arcGIS data
res_file = 'test_data/residential.txt'
# File with unit distribution
units_file = 'test_data/unit_stats.txt'

# Output Files
# Output file with residential database
house_out = 'test_data/house_arcgis_output.txt'
# Output file with summary of added vs expected units
house_summary = 'test_data/house_arcgis_testsummary'

# Total number of buildings collected through arcGIS (Colonie)
n_tot = 29361

households = res.Households(n_tot, res_file, None, units_file)


# Print added units for each category
#	for comparison with unit_stats.txt file
print("Test map:")
print(households.test_map)

# Print units and coordinates for each 20+ unit building
print("\n20+ unit building Data:")
for building in households.res_buildings:
	print(building['lon'], building['lat'], building['n_units'])

# Clear
households.res_buildings.clear()

with open(house_summary, 'w') as fout:
	fout.write('Category\tAdded\tExpected\tOff_by\n')
	expected_excess=0
	for key , value in households.test_map.items():
		if key == '1_unit':
			category = key
			added = value
			expected = int(households.unit_map['1_detached']) + int(households.unit_map['1_attached']) + int(households.unit_map['other']) + int(
				households.unit_map['mobile'])
		elif key == 'remainder added to 20+ buildings':
			category = key
			added = value
			expected = expected_excess
		else:
			category = str(key)
			added = value
			expected = int(households.unit_map[str(key)])
			expected_excess += expected - added
		line = category + '\t'+ str(added) + '\t' + str(expected) + '\t' + str(expected - added) + '\n'
		print(line, file=fout)

with open(house_out, 'w') as fout:
	fout.write(repr(households))
