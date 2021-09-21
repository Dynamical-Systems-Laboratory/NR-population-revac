# ------------------------------------------------------------------
#
#	Tests for abm_public module	
#
# ------------------------------------------------------------------

import sys
py_path = '../../tools/'
sys.path.insert(0, py_path)

py_path = '../../src/mobility/'
sys.path.insert(0, py_path)

import os, math
import utils as ut
from colors import *

import abm_public as apb

#
# Supporting functions
#

def compare_workplace_dicts(exp, cur, outsideIDs):
	''' Checks if all the data in exp is the same as in cur - both 
			are lists of dicts, one dict per place. outsideIDs is a list of 
			IDs of workplaces that are outside NR - checks if loaded as such. '''

	tol = 1e-5

	if len(exp) != len(cur):
		print('Current workplace list different number of elements than expected')
		return False

	for de, dc in zip(exp, cur):
		for key, value in de.items():
			if (key == 'ID') or (key == 'zip'):
				if int(dc[key]) != int(value):
					print('ID or zip codes don\'t match: ')
					return False
			elif key == 'type':
				if dc[key] != value:
					print('Types don\'t match: ')
					print(dc['ID'], dc[key], value)
					return False
			elif key == 'occupation':
				if dc[key] != value:
					print('Occupation don\'t match: ')
					print(dc['ID'], dc[key], value)
					return False
			else:
				if not ut.float_equality(value, dc[key], tol):
					print('lat, lon or capacities don\'t match')
					print(dc['ID'], dc[key], value)
					return False

	for ind in outsideIDs:
		if cur[ind-1]['type'] != 'outside':
			print('Outside workplace not properly labelled')
			return False
		if int(cur[ind-1]['zip']) != int(exp[ind-1]['zip']):
			print('Outside workplace with an unexpected zip code')
			return False
	
	return True

def compare_special_workplace_dicts(exp, cur, specIDs):
	''' Checks if all the data in exp is the same as in cur - both 
			are lists of dicts, one dict per place. This tests only looks 
			for attributes of workplaces modeled separatly such as schools '''

	for ind in specIDs:
		if int(cur[ind-1]['specialID']) != int(exp[ind-1]['specialID']):
			print('Wrong special ID')
			return False
	
	return True

def check_types(workplaces, exp_type):
	''' Checks if types and capacities are correctly loaded for a select
			number of types in exp_type dictionary '''

	# Check how the map is loaded
	all_types = workplaces.workplace_map
	for key, value in exp_type.items():
		if not (key in all_types):
			print('Requested type not found')
			return False
		
		if value != all_types[key]:
			print('Type data does not match expected')
			return False

	return True

def compare_leisure_dicts(exp, cur):
	''' Checks if all the data in exp is the same as in cur - both 
			are lists of dicts, one dict per place '''

	tol = 1e-5

	if len(exp) != len(cur):
		print('Current leisure location list different number of elements than expected')
		return False

	for de, dc in zip(exp, cur):
		for key, value in de.items():
			if (key == 'ID'):
				if int(dc[key]) != int(value):
					print('ID or zip codes don\'t match: ')
					return False
			elif (key == 'type') or (key == 'name') or (key == 'in/out'):
				if dc[key] != value:
					print('Types or names don\'t match: ')
					print(dc['ID'], dc[key], value)
					return False
			else:
				if not ut.float_equality(value, dc[key], tol):
					print('lat or lon don\'t match')
					print(dc['ID'], dc[key], value)
					return False

	return True

def check_saving(exp, tags, fname):
	''' Check if the data for a given category was 
			properly saved

			exp - list of dictionaries with expected data
			tags - list of ordered keywords - strings that 
				should be saved as named in exp
			fname - file where the data was saved 
	'''

	n_count = 0
	with open(fname, 'r') as fin:
		for il, line in enumerate(fin):
			n_count += 1
			temp = line.strip().split()
			for jl, entry in enumerate(temp):
				try:
					if not math.isclose(float(entry), exp[il][tags[jl]]):
						return False
				except ValueError:
					if not (entry == exp[il][tags[jl]]):
						return False
	
	if n_count != len(exp):
		return False

	return True
				
#
# Tests 
#

#
# Test 1: Load workplaces and see if relevant information 
# is correct
#

exp_workplaces = [{'ID': 1, 'type': 'M', 'lat': 40.894162, 'lon': -73.789744, 'N_min': 1, 'N_max': 10, 'N_emp': 0},
				{'ID': 2, 'type': 'C', 'lat': 42.987825, 'lon': -73.781636, 'N_min': 1, 'N_max': 10, 'N_emp': 0},
				{'ID': 3, 'type': 'CC', 'lat': 41.909354, 'lon': -73.78192, 'N_min': 2, 'N_max': 5, 'N_emp': 0},
				{'ID': 4, 'occupation': 'A', 'lat': 40.894161, 'lon': -73.789744, 'N_min': 10, 'N_max': 1000, 'N_emp': 0},
				{'ID': 5, 'occupation': 'B', 'lat': 45.987822, 'lon': -78.781636, 'N_min': 5, 'N_max': 50, 'N_emp': 0},
				{'ID': 6, 'type': 'outside', 'lat': 41.2423, 'lon': -73.7772, 'zip': 10901},
				{'ID': 7, 'type': 'outside', 'lat': 40.908895, 'lon': -73.781193, 'zip': 10801}
]

inNR = 'test_data/public_places.txt'
outNR = 'test_data/public_places_outside.txt'
fmap = 'test_data/public_types_mobility.txt'
foccupation = 'test_data/match_occupation.txt'
fsafegraph = 'test_data/safegraph_places.txt'
focc_cap = 'test_data/occupation_capacity.txt'

outIDs = [6,7]

workplaces = apb.Workplaces(inNR, outNR, fmap, foccupation, fsafegraph, focc_cap)
ut.test_pass(compare_workplace_dicts(exp_workplaces, workplaces.workplaces, outIDs), 'NR and outside workplaces')

#
# Test 2: add special workplace categories - merge
#

# Schools
schools = apb.Schools(inNR, fmap)

exp_workplaces.append({'ID': 8, 'type': 'F', 'lat': 45.987825, 'lon': -78.781636, 'specialID': 1, 'N_min': 50, 'N_max': 300, 'N_emp': 0})
exp_workplaces.append({'ID': 9, 'type': 'F', 'lat': 45.987825, 'lon': -78.781636, 'specialID': 2, 'N_min': 50, 'N_max': 300, 'N_emp': 0})
exp_workplaces.append({'ID': 10, 'type': 'F', 'lat': 45.987825, 'lon': -78.781636, 'specialID': 3, 'N_min': 50, 'N_max': 300, 'N_emp': 0})
exp_workplaces.append({'ID': 11, 'type': 'F', 'lat': 40.905115, 'lon': -76.79072, 'specialID':  4, 'N_min': 2, 'N_max': 30, 'N_emp': 0})

# Retirement homes
retirement_homes = apb.RetirementHomes(inNR, fmap)

exp_workplaces.append({'ID': 12, 'type': 'AA', 'lat': 40.909571, 'lon': -73.792891, 'specialID': 1, 'N_min': 20, 'N_max': 50, 'N_emp': 0})
exp_workplaces.append({'ID': 13, 'type': 'AA', 'lat': 40.929115	, 'lon': -73.788614, 'specialID': 2, 'N_min': 20, 'N_max': 50, 'N_emp': 0})
exp_workplaces.append({'ID': 14, 'type': 'AA', 'lat': 43.917963, 'lon': -73.788635, 'specialID': 3, 'N_min': 20, 'N_max': 50, 'N_emp': 0})

# Hospitals
hospitals = apb.Hospitals(inNR, fmap)

exp_workplaces.append({'ID': 15, 'type': 'H', 'lat': 40.894725, 'lon': -73.781787, 'specialID': 1})

specIDs = list(range(8,16))
workplaces.merge_with_special_workplaces(schools.schools, retirement_homes.retirement_homes, hospitals.hospitals)

ut.test_pass(compare_workplace_dicts(exp_workplaces, workplaces.workplaces, outIDs), 'Merged workplaces - common features')
ut.test_pass(compare_special_workplace_dicts(exp_workplaces, workplaces.workplaces, specIDs), 'Merged workplaces - special features')

#
# Test 3: check if types are correctly loaded
#

types_to_check = {'F': ['school', 50, 300], 'Z': ['museum', 5, 10], 'HH': ['transit center', 5, 10]}
ut.test_pass(check_types(workplaces, types_to_check), 'Workplace types and capacities')

#
# Test 4: leisure locations - correct loading
#

fleisureOut = 'test_data/core_poi_NROut_LeisureTrimmed.csv'
fleisureIn = 'test_data/core_poi_NRIn_LeisureTrimmed.csv'

exp_leisure = [ {'ID': 1, 'name': 'Jo-Ann Fabric and Craft Stores', 'type': 'Sporting Goods, Hobby, and Musical Instrument Stores' , 'lat': 40.991466, 'lon': -73.823074},
				{'ID': 2, 'name': 'Korean BBQ Grill', 'type': 'Restaurants and Other Eating Places' , 'lat': 40.908895, 'lon': -73.781193}]
leisure = apb.LeisureLocations(fleisureIn)
ut.test_pass(compare_leisure_dicts(exp_leisure, leisure.leisure_locations), 'Loading leisure locations')

exp_leisure2 = [ {'ID': 1, 'name': 'Jo-Ann Fabric and Craft Stores', 'type': 'Sporting Goods, Hobby, and Musical Instrument Stores' , 'lat': 40.991466, 'lon': -73.823074},
				{'ID': 2, 'name': 'Korean BBQ Grill', 'type': 'Restaurants and Other Eating Places' , 'lat': 40.908895, 'lon': -73.781193},
				{'ID': 3, 'name': 'Afra Beauty Supply', 'type': 'Health and Personal Care Stores' , 'lat': 40.876484, 'lon': -73.849026},
				{'ID': 4, 'name': 'StilltheOne Distillery' , 'type': 'Beverage Manufacturing', 'lat': 40.997632, 'lon': -73.660723},
				{'ID': 5, 'name': 'BCBGeneration', 'type': 'Clothing Stores', 'lat': 40.928535, 'lon': -73.855649},
				{'ID': 6, 'name': 'Gus & Nicks Auto Body', 'type': 'Automotive Repair and Maintenance', 'lat': 40.935259, 'lon': -73.88327}]

leisure2 = apb.LeisureLocations(fleisureIn, fleisureOut, True)
ut.test_pass(compare_leisure_dicts(exp_leisure2, leisure2.leisure_locations), 'Loading mixed leisure locations')


#
# Test 5: check if all types are correctly saved
#

wfname = 'test_data/workplaces_out.txt'
sfname = 'test_data/school_out.txt'
hfname = 'test_data/hosptals_out.txt'
rtfname = 'test_data/rhomes_out.txt'
lfname = 'test_data/leisure_out.txt'
lfname2 = 'test_data/leisure_mix.txt'

for file_rm in [wfname, sfname, hfname, rtfname, lfname]:
	if os.path.exists(file_rm):
		os.remove(file_rm)

# Workplaces
wtags = ['ID', 'lat', 'lon', 'occupation', 'specialID']
with open(wfname, 'w') as fout:
	fout.write(repr(workplaces))
ut.test_pass(check_saving(workplaces.workplaces, wtags, wfname), 'Writing workplace data to file')

# Schools
stags = ['ID', 'lat', 'lon', 'school type']
with open(sfname, 'w') as fout:
	fout.write(repr(schools))
ut.test_pass(check_saving(schools.schools, stags, sfname), 'Writing school data to file')

# Hospitals 
htags = ['ID', 'lat', 'lon']
with open(hfname, 'w') as fout:
	fout.write(repr(hospitals))
ut.test_pass(check_saving(hospitals.hospitals, htags, hfname), 'Writing hospital data to file')

# Retirement homes 
with open(rtfname, 'w') as fout:
	fout.write(repr(retirement_homes))
ut.test_pass(check_saving(retirement_homes.retirement_homes, htags, rtfname), 'Writing retirement home data to file')

# Leisure locations
ltags = ['ID', 'lat', 'lon', 'in/out']
with open(lfname, 'w') as fout:
	fout.write(repr(leisure))
ut.test_pass(check_saving(leisure.leisure_locations, ltags, lfname), 'Writing leisure data to file')

# Leisure locations - two files
ltags = ['ID', 'lat', 'lon', 'in/out']
with open(lfname2, 'w') as fout:
	fout.write(repr(leisure2))
ut.test_pass(check_saving(leisure.leisure_locations, ltags, lfname), 'Writing leisure data to file')

