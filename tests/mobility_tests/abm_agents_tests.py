# ------------------------------------------------------------------
#
#	Tests for abm_agents module	
#
# ------------------------------------------------------------------

import sys
py_path = '../../tools/'
sys.path.insert(0, py_path)

py_path = '../../src/mobility/'
sys.path.insert(0, py_path)

import collections, math
import utils as ut
from colors import *

import abm_residential as res
import abm_public as public
import abm_transit as travel 
import abm_agents as agents

# ------------------------------------------------------------------
#
# Supporting functions
#
# ------------------------------------------------------------------

def check_work_dist_agent_props(agents, workplaces, max_working_age, travel_modes, tmax, t_wfh, t_walk):
	''' Checks attributes of agents that work '''

	for agent in agents:
		if (agent['works'] == False) and (agent['worksHospital'] == False):
			continue

		# Basic characteristics
		if (agent['yrs'] < 16) or (agent['yrs'] > max_working_age):
			print('Working agent with age outside the working age range')
			return False
		if (agent['isPatient'] == True) or (agent['RetirementHome'] == True):
			print('Working agent is a hospital patient or a retirement home resident')
			return False

		# Special categories
		wID = agent['workID']
		if agent['worksSchool'] == True:
			if not (int(agent['specialWorkID']) == int(workplaces[wID-1]['specialID'])):
				return False
		if agent['worksRH'] == True:
			if not (int(agent['specialWorkID']) == int(workplaces[wID-1]['specialID'])):
				return False			
		if agent['worksHospital'] == True:
			if not (int(agent['hospitalID']) == int(workplaces[wID-1]['specialID'])):
				return False
			if (agent['works'] == True) or (agent['worksHospital'] == False):
				return False

		# Work from home
		if agent['work travel time'] <= t_wfh:
			if agent['works from home'] == False:
				return False
			if agent['work travel mode'] != 'wfh':
				return False
			if int(agent['workID']) != int(agent['houseID']):
				return False
			continue
		# All others should have this flag set to False
		if agent['works from home'] == True:
			return False

		# Walking
		if agent['work travel time'] <= t_walk:
			if agent['work travel mode'] != 'walk': 
				return False

		# Other transit properties
		if not (agent['work travel mode'] in travel_modes):
			print('Unrecognizable travel mode')
			return False
		if (agent['work travel time'] > tmax):
			print('Too long travel time')
			return False

	return True

def check_work_dist_validity(agents, workplaces, fname_out, fname_NR, n_hs):
	''' Verifies - computes various metrics related to correctness of 
			the workplace distribution. Saves workID | #employees for further
			inspection in fname. '''
	
	# Number of employees in each workplace
	emp_count = [0]*len(workplaces)
	# Stores how many employed in a household
	household_emp = [0]*n_hs
	# Household IDs of employees in each workplace 
	work_house_var = {}

	n_wfh = 0
	for agent in agents:
		if (agent['works'] == False) and (agent['worksHospital'] == False):
			continue

		house_ID = agent['houseID']
		household_emp[house_ID-1] += 1
		if (agent['works from home'] == True):
			n_wfh += 1
			continue

		# Count employees in each workplace
		emp_count[agent['workID']-1] +=1
		# Store household IDs of each employee
		wkey = str(agent['workID'])
		if wkey in work_house_var:
			work_house_var[wkey].append(house_ID)
		else:
			work_house_var[wkey] = [house_ID]

	# Save employee count to file and check if any are zeros
	# Applies only to NR
	flag_zero = False
	n_outside = 0
	with open(fname_out, 'w') as fout, open(fname_NR, 'w') as fout_NR:
		for ind, val in enumerate(emp_count):
			if (workplaces[ind]['type'] != 'outside') and (int(val) == 0):
				flag_zero = True
			if (workplaces[ind]['type'] == 'outside'):
				n_outside += val
				fout.write((' ').join([str(ind+1), str(val)]))
				fout.write('\n')
			else:
				fout_NR.write((' ').join([str(ind+1), str(val), str(workplaces[ind]['type'])]))
				fout_NR.write('\n')

	print('Agents working from home: ' + str(n_wfh))
	print('Agents working outside New Rochelle: ' + str(n_outside))

	if flag_zero:
		print('Some of the workplaces have zero employees')
		return False

	# Print household employment statistics
	# Should approximately match census
	# Counts households with 0, 1, and 2+ employed members
	hs_emp_count = [0, 0, 0]
	for hse in household_emp:
		if int(hse) == 0:
			hs_emp_count[0] += 1
		elif int(hse) == 1:
			hs_emp_count[1] += 1
		else:
			hs_emp_count[2] += 1

	print('*'*5+' Household employment ' + '*'*5)
	print('No employed agents: ' + str(hs_emp_count[0]/n_hs*100) + '%')
	print('One employed agent: ' + str(hs_emp_count[1]/n_hs*100) + '%')
	print('Two or more employed agents: ' + str(hs_emp_count[2]/n_hs*100) + '%')

	# Print percent of households where people share workplaces
	# This will also include the outside of NR
	n_same = 0
	for key, value in work_house_var.items():
		if len(value) != len(set(value)):
			n_same += 1
	print('Households with at least two people working in the same place: ' + str(n_same/n_hs*100))

	return True

def check_mode_dist(agents, tot_working):
	''' Count and print percentages of agents taking given transportation 
			mode to work '''

	mode_count = {}
	
	for agent in agents:
		if (agent['works'] == False) and (agent['worksHospital'] == False):
			continue

		mode = agent['work travel mode'] 
		if mode in mode_count:
			mode_count[mode] += 1
		else:
			mode_count[mode] = 1

	for key, value in mode_count.items():
		print(key + ': ' + str(value/tot_working*100) + '%')

def check_time_dist(agents, tot_working):
	''' Count and print percentages of agents by travel time to work '''

	time_count = {}
	
	for agent in agents:
		if (agent['works'] == False) and (agent['worksHospital'] == False):
			continue

		time = str(agent['work travel time']) 
		if time in time_count:
			time_count[time] += 1
		else:
			time_count[time] = 1

	for key, value in time_count.items():
		print(key + ': ' + str(value/tot_working*100) + '%')

def print_info(data, ind):
	''' Print all the information stored in a dictionary located
			at ind in data '''

	for key, value in data[ind].items():
		print(key, value)

def check_carpools(agents, transit, workplaces):
	''' Verification of carpool distribution '''

	carpools = transit.carpools
	all_carpools = {}
	for agent in agents:
		if not (agent['work travel mode'] == 'carpool'):
			continue

		# This may fail if too little agents used for 
		# testing and the only carpooling agent for a given 
		# destination is assigned the initial ID 0
		cID = str(agent['carpoolID'])
		if int(cID) == 0:
			print('Carpool ID is 0')
			return False

		if cID in all_carpools:
			all_carpools[cID] += 1
		else:
			all_carpools[cID] = 1

		if carpools[int(cID)-1].ID != int(cID):
			print('Wrong carpool ID')
			return False

		if workplaces[agent['workID']-1]['type'] == 'outside':
			if carpools[int(cID)-1].work_type != 'outside':
				print('Wrong carpool destination type for out of town locations')
				return False
			if carpools[int(cID)-1].work_destination != workplaces[agent['workID']-1]['zip']:
				# This can fail if not enough agents and some carpools have only one agent 
				# (which is then reassigned to a different carpool, with a potentially  
				#	different carpool destination)
				print('Wrong carpool destination label for out of town locations')
				#return False
		else:
			if not math.isclose(carpools[int(cID)-1].travel_time, agent['work travel time']):
				print('Wrong carpool travel time for NR locations')
				return False

	# All carpools
	cpool_pnumbers = {} 
	max_cpool = -100
	for key, value in all_carpools.items():
		if value < 2:
			print('Carpool with less than two people')
			return False
		num_people = str(value)
		if num_people in cpool_pnumbers:
			cpool_pnumbers[num_people] += 1
		else:
			cpool_pnumbers[num_people] = 1

	print('Number of passengers in carpools, %')
	for key, value in cpool_pnumbers.items():
		print(key, str(value/len(all_carpools)*100))

	return True

def check_public_transit(agents, transit, workplaces):
	''' Verification of public transit distribution '''

	public_transit = transit.GSP
	all_public_transit = {}
	for agent in agents:
		if not (agent['work travel mode'] == 'public'):
			continue

		pID = str(agent['publicID'])
		if int(pID) == 0:
			print('Public ID is 0')
			return False

		if pID in all_public_transit:
			all_public_transit[pID] += 1
		else:
			all_public_transit[pID] = 1

		if public_transit[int(pID)-1].ID != int(pID):
			print('Wrong public transit ID')
			return False

		if workplaces[agent['workID']-1]['type'] == 'outside':
			if public_transit[int(pID)-1].work_type != 'outside':
				print('Wrong public transit destination type for out of town locations')
				return False
			cur_zip = str(workplaces[agent['workID']-1]['zip'])
			route_name = public_transit[int(pID)-1].name
			if not (cur_zip in transit.transit_routes[route_name][0]):
				print('Wrong public transit destination zip for out of town locations')
				return False
		else:
			cur_zip = 'NR' 
			route_name = public_transit[int(pID)-1].name
			if not (cur_zip in transit.transit_routes[route_name][0]):
				print('Wrong public transit destination zip for NR locations')
				print(transit.transit_routes[route_name][0])
				return False

	# All public transit 
	pt_pnumbers = {} 
	max_pt = -100
	for key, value in all_public_transit.items():
		num_people = str(value)
		if num_people in pt_pnumbers:
			pt_pnumbers[num_people] += 1
		else:
			pt_pnumbers[num_people] = 1

	print('Number of passengers in public transit, %')
	for key, value in pt_pnumbers.items():
		print(key, str(value/len(all_public_transit)*100))

	print('Number of passengers by route')
	for pID, num in all_public_transit.items():
		print(public_transit[int(pID)-1].name, ': ', str(num))

	return True



# ------------------------------------------------------------------
#
# Generate New Rochelle population for the COVID model
#
# ------------------------------------------------------------------

#
# Input files
#

# GIS and type data files database
dpath = '../../town_data/NewRochelle/database/'
cpath = '../../town_data/NewRochelle/census_data/'

# File with residential GIS data
res_file = dpath + 'residential.txt' 
# File with residential building types
res_type_file = dpath + 'residential_types.txt'
# File with public places GIS data (used only for special workplaces)
pb_file = 'test_data/public.txt'
# File with regular workplaces inside New Rochelle
pb_file_in = 'test_data/2020_core_poi_NewRochelleIn_OccupationTrimmed.csv' 
# File with public places GIS data that are outside New Rochelle
pb_file_out = dpath + 'workplaces_outside.txt'
# File with building types
pb_type_file = dpath + 'public_types_mobility.txt'
# File with leisure - time off buildings
pb_leisure_file = dpath + 'core_poi_NR_LeisureTrimmed.csv'

# File with age distribution
file_age_dist = cpath + 'age_distribution.txt'
# File with age distribution of the household head
file_hs_age = cpath + 'age_household_head.txt'
# File with household size distribution
file_hs_size = cpath + 'household_size.txt'
# File with travel times to work
ftimes = cpath + 'travel_time_to_work.txt'
# File with means of transportation to work
fmodes = cpath + 'transit_mode.txt'
# Carpool count of passengers and fraction of carpools that have it
fcpools = cpath + 'carpool_stats.txt'
# Public transit routes in the area
fpt_routes = dpath + 'public_transit_routes.txt'
# Occupation statistics
foccupation = 'test_data/match_occupation.txt'
focc_cap = 'test_data/occupation_capacity.txt'
agent_occ = 'test_data/occupation_stats.txt'

#
# Other input
#

# Total number of units (households + vacancies)
n_tot = 29645
# Fraction of vacant households
fr_vacant = 0.053
# Total number of agents
n_agents = 79205
# Number of employed agents
n_employed = 39460
# Longest time to travel to work
tmax = 60*24 
# Acceptable transit modes
travel_modes = ['car', 'carpool', 'public', 'walk', 'other', 'wfh']
# Speed of each travel mode used to compute distance
mode_speed = {'car': 30, 'carpool': 30, 'public': 20, 
					'walk': 2, 'other': 3, 'wfh': 0}
t_wfh = 5.0
t_walk = 12.0
# Assumed maximum age
max_age = 100
# Fraction of families
fr_fam = 0.6727
# Fraction of couple no children
fr_couple = 0.49
# Fraction of single parents
fr_sp = 0.25
# Fraction of households with a 60+ person
fr_60 = 0.423
# Initially infected
n_infected = 1
# Max working age (same for hospitals and non-hospitals now)
max_working_age = 70

#
# Generate places
#

# Retirement homes
retirement_homes = public.RetirementHomes(pb_file, pb_type_file)
# Households 
households = res.Households(n_tot, res_file, res_type_file)
# Workplaces 
workplaces = public.Workplaces(pb_file, pb_file_out, pb_type_file, foccupation, pb_file_in, focc_cap)
# Hospitals
hospitals = public.Hospitals(pb_file, pb_type_file)
# Schools
schools = public.Schools(pb_file, pb_type_file)
# Leisure/time off locations 
leisure = public.LeisureLocations(pb_leisure_file)
# Transit
transit = travel.Transit(ftimes, fmodes, fcpools, fpt_routes, mode_speed, t_wfh, t_walk) 

# Merge workplaces for distribution
workplaces.merge_with_special_workplaces(schools.schools, retirement_homes.retirement_homes, hospitals.hospitals)

#
# Create the population
# 

agents = agents.Agents(file_age_dist, file_hs_age, file_hs_size, n_agents, max_age, n_tot, fr_vacant, fr_fam, fr_couple, fr_sp, fr_60, n_infected, agent_occ)
agents.distribute_retirement_homes(retirement_homes.retirement_homes)
agents.distribute_hospital_patients(hospitals.hospitals)
agents.distribute_households(households.households, fr_vacant)

agents.distribute_schools(schools.schools)
agents.distribute_transit_and_workplaces(households.households, workplaces.workplaces, transit, max_working_age, n_employed, workplaces.occ_map)

# ------------------------------------------------------------------
#
#	Tests 
#
# ------------------------------------------------------------------

#
# Test 1 - agent attributes
#

ut.test_pass(check_work_dist_agent_props(agents.agents, workplaces.workplaces, max_working_age, travel_modes, tmax, t_wfh, t_walk), 'Workplace and transit distribution - agent attributes')

#
# Test 2 - conceptual validity of workplace distribution 
#

# This will store workplace ID | number of employees
# Use it to inspect the distribution manually as a whole
# NR also has a third column with workplace type
fout_outside = 'work_dist_out_count.txt'
fout_NR = 'work_dist_NR_count.txt'

ut.test_pass(check_work_dist_validity(agents.agents, workplaces.workplaces, fout_outside, fout_NR, len(households.households)), 'Workplace distribution - validity')
#print_info(workplaces.workplaces, 1056)
check_mode_dist(agents.agents, n_employed)
check_time_dist(agents.agents, n_employed)
ut.test_pass(check_carpools(agents.agents, transit, workplaces.workplaces), 'Grouping agents into carpools')
ut.test_pass(check_public_transit(agents.agents, transit, workplaces.workplaces), 'Grouping agents into public transit')
