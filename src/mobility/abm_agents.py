# ------------------------------------------------------------------
#
#	Module for generation of ABM population (agents)
#
# ------------------------------------------------------------------

import math, random, warnings
import numpy as np
import abm_utils as aut
from copy import deepcopy
from collections import defaultdict

class Agents(object):
	''' Class for generating the population - agents '''

	def __init__(self, fname_age, fname_hs_age, fname_hs_size, ntot, max_age, n_houses, 
					fr_vacancy, fr_fam, fr_couple, fr_sp, fr_60, n_infected, fname_census):
		''' Load basic data '''

		# Total number of people
		self.ntot = ntot
		# Maximum age to assume
		self.max_age = max_age
		# Number of households excluding vacant
		self.n_houses = math.floor(n_houses*(1-fr_vacancy))
		# Number of unpoulated houses
		self.rem_houses = self.n_houses
		# Fraction of families
		self.fr_families = fr_fam
		# Fraction of married couples without children
		self.fr_couple = fr_couple
		# Fraction of single parent families
		self.fr_single_parent = fr_sp
		# Fraction of households with a 60+ person
		self.fr_60 = fr_60
		# Total number of initially infected
		self.n_infected = n_infected

		# Age group : number of people in that group
		self.age_dist = self.load_age_dist(fname_age, self.ntot, 0, 4)
		# Household head age distribution
		self.hs_age_dist = self.load_age_dist(fname_hs_age, self.n_houses, 18, 34)
		# Household size distribution
		self.hs_size_dist = self.load_data(fname_hs_size)
		

		# Still left to distribute 
		self.age_remaining = deepcopy(self.age_dist) 

		# Current free agent ID
		self.ID = 1

		# Agents
		self.agents = []
		# List of agents in retirement homes
		self.rh_agents = []
		
		# Census statistics of occupation distribution
		# { occupation type : number of agents, percentage }
		self.census_stats = {} 
		self.load_census_stats(fname_census)

		# Default Agent paramters
		# Deepcopy and use to create specific parameters
		self.default_parameters = {'ID':0, 'student':False, 'works':False,
							  'yrs':-1, 'lon':0, 'lat':0, 'houseID':0,
							  'isPatient':False, 'schoolID':0, 
							  'workID':0, 'worksHospital':False, 
							  'hospitalID':0, 'infected':False, 
							  'RetirementHome': False, 'worksRH': False, 
							  'worksSchool': False, 'isFamily': False,
							  'works from home': False, 'work travel time': 0.0,
							  'work travel mode': None, 'specialWorkID': 0, 
							  'carpoolID': 0, 'publicID': 0, 'occupation': 'none',
							  'work_type': 'muzikant'}

	def load_age_dist(self, fname_age, ntot, min_age, max_min_age):
		''' Read and process an age distribution '''
		# Returns a map with age group : number of people
		# in that group

		with open(fname_age, 'r') as fin:

			# Total generated 
			cur_total = 0

			age_dist = {}    
			# First line is different
			line = next(fin)
			in_group = math.floor(float(line.strip().split()[-1])/100*ntot)
			key = str(min_age)+'-'+str(max_min_age)
			age_dist[key] = {'min': min_age, 'max': max_min_age, 'number': in_group}			
			cur_total += in_group

			for line in fin:
				line = line.strip().split()
				in_group = math.floor(float(line[-1])/100*ntot)
				if not (line[0] == '85'):
					key = line[0] + '-' + line[2]
					age_dist[key] = {'min': int(line[0]), 'max': int(line[2]), 'number': in_group}
				else:
					age_dist['85-'+str(self.max_age)] = {'min': 85, 'max': self.max_age, 'number': in_group}
				cur_total += in_group
				
			# Correct for rounding
			if cur_total != ntot:
				ind = 0
				keys = list(age_dist.keys())
				if cur_total < ntot:
					while (cur_total < ntot):
						age_dist[keys[ind]]['number'] += 1 
						cur_total += 1
						if ind < len(keys)-1:
							ind += 1
						else:
							ind = 0
				else:
					while (cur_total > ntot):
						age_dist[keys[ind]]['number'] -= 1 
						cur_total -= 1
						if ind < len(keys)-1:
							ind += 1
						else:
							ind = 0
			return age_dist

	def load_data(self, fname):
		''' Loads simple two column file into a dictionary
				with key the first and value (percents converted 
				to fractions) in the second column '''

		temp = {}
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				temp[line[0]] = float(line[1])/100
		return temp

	def load_census_stats(self, fname):
		with open(fname, 'r') as statsFile:
			for line in statsFile:
				infoList = line.strip().split()
				self.census_stats[infoList[3]] = (int(infoList[1]), float(infoList[2]))
	
	def distribute_retirement_homes(self, retirement_homes):
		''' Select agents 75+ for retirement homes '''
	
		for rh in retirement_homes:
			n_residents = rh['num residents']
			for ai in range(n_residents):
				temp = {}
				temp = deepcopy(self.default_parameters)
				# Agent ID
				temp['ID'] = self.ID
				self.ID += 1
				# Age + update
				temp['yrs'] = np.random.randint(75, self.max_age+1)
				self.update_ages(temp['yrs'])
				# Agents position
				temp['lon'] = rh['lon']
				temp['lat'] = rh['lat']
				# House ID
				temp['houseID'] = rh['ID']
				# Processing flag that it's retirement home
				temp['RetirementHome'] = True
				self.agents.append(temp)
				# List of agents in retirement homes
				self.rh_agents.append(temp)
			

	def distribute_hospital_patients(self, hospitals):
		''' Select patients with conditions other than 
				COVID, all ages '''
	
		for hosp in hospitals:
			n_patients = hosp['num patients']
			for ai in range(n_patients):
				temp = {}
				temp = deepcopy(self.default_parameters)
				# Agent ID
				temp['ID'] = self.ID
				self.ID += 1
				# Age + update
				temp['yrs'] = np.random.randint(0, self.max_age+1)
				self.update_ages(temp['yrs'])
				# Agents position
				temp['lon'] = hosp['lon']
				temp['lat'] = hosp['lat']
				# Other info
				temp['isPatient'] = True
				temp['hospitalID'] = hosp['ID']
				self.agents.append(temp)

	def distribute_households(self, households, fr_vacancy):
		''' Assign agents to households '''
		
		# fr_vacancy - fraction of vacant households
		
		# Exclude vacant
		houses_tot = len(households)
		nh_vacant = math.floor(fr_vacancy*houses_tot)
		ind_vacant = random.sample(range(1, houses_tot+1), nh_vacant)

		# Select head of each household			
		ind_available = list(set(range(1,houses_tot+1))-set(ind_vacant))
		household_heads = self.select_household_heads(households, ind_available)
	
		# Select household type for each head
		# Returns total number of households in each category
		hs_size_totals = self.assign_household_type(household_heads)
		# Assign remaining agents
		self.complete_households(hs_size_totals, household_heads, households)

	def update_ages(self, age):
		''' Reduce the number of agents in a given age group by 1 '''
		
		key = self.find_age_range(age)
		self.age_remaining[key]['number'] -= 1
		if self.age_remaining[key]['number'] < 0:
			self.age_remaining[key]['number'] = 0
			raise RuntimeError('Number of agents in the age group below zero')

	def find_age_range(self, age):
		''' Find the range in which the age is '''

		found_range = False
		for key, value in self.age_remaining.items():
			if (age >= value['min']) and (age <= value['max']):
				found_range = True
				break
		if not found_range:
			raise RuntimeError('Agents age not found in the age groups')
		return key

	def select_household_heads(self, households, house_ind):
		''' Defines the head of the household 
				and stores relevant information ''' 

		household_heads = []
		for key, value in self.hs_age_dist.items():
			for head in range(value['number']):
				temp = {}
				temp = deepcopy(self.default_parameters)

				# Randomly select index and remove it
				# These are actually IDs
				ind = house_ind[random.sample(range(0, len(house_ind)), 1)[0]]
				house_ind.remove(ind)
					
				# Select specific age
				spec_age = np.random.randint(value['min'], value['max']+1)
				# Maintain 60+ fraction
				while (spec_age >= 60) and (np.random.uniform(0,1) > self.fr_60): 
					spec_age = np.random.randint(value['min'], value['max']+1)
				age_dist_key = self.find_age_range(spec_age)
	
				# Remove that age from total poll and create agent entry
				self.update_ages(spec_age)
				# Agent ID
				temp['ID'] = self.ID
				self.ID += 1
				# Age + update
				temp['yrs'] = spec_age 
				# Agents position
				temp['lon'] = households[ind-1]['lon']
				temp['lat'] = households[ind-1]['lat']
				# House ID
				temp['houseID'] = households[ind-1]['ID']
				self.agents.append(temp)

				# Add an entry to head storage
				household_heads.append({'ID': temp['ID'], 'yrs' : spec_age, 'houseID': temp['houseID'], 'lon' : temp['lon'], 'lat': temp['lat']})

		return household_heads
			
	def assign_household_type(self, household_heads):
		''' Associate a household type with a 
				head - randomly '''
	
		# Turn percents into numbers
		h_tot = len(household_heads)
		hs_numbers = {}
		h_cur = 0
		for h_size, value in self.hs_size_dist.items():
			hs_numbers[h_size] = math.floor(value*h_tot)
			h_cur += hs_numbers[h_size]
		# Correction
		if h_cur != h_tot:
			size_range = list(self.hs_size_dist.keys())
			ind = 0
			len_keys = len(size_range)
			while (h_cur < h_tot):
				hs_numbers[size_range[ind]] += 1
				h_cur += 1
				if ind < len_keys - 1:
					ind += 1
				else:
					ind = 0

		# For later calculation - totals
		hs_total_numbers = deepcopy(hs_numbers)

		# Now randomly distribute the agents
		# using the dict with actual numbers of each houseld type
		for agent in household_heads:
			h_ind = np.random.randint(1,5)
			h_size = hs_numbers[str(h_ind)]
			if h_size > 0:
				hs_numbers[str(h_ind)] -= 1
				agent['household size'] = h_ind
			else:
				# Pick next available
				found_household = False
				for key, value in hs_numbers.items():
					if value > 0:
						agent['household size'] = int(key)
						hs_numbers[key] -= 1
						found_household = True
						break
				if found_household == False:
					raise RuntimeError('Not enough households for household heads')

		return hs_total_numbers

	def complete_households(self, hs_size_totals, household_heads, households):
		''' Assign remaining agents to households based on heads and 
				household sizes; assumes max parent age is 60 '''

		# IDs of houses that have 4+ members for correction
		houses_4p = []

		for head in household_heads:
			# Nothing to do for one person	
			if head['household size'] == '1':
				continue
			elif  head['household size'] == 2:
				# Probability a family
				if (np.random.uniform(0,1) <= self.fr_families):
					# Probability a married couple, no children
					if head['yrs'] > 60:
						# Married couple
						self.add_spouse(head)
					else:
						if (np.random.uniform(0,1) <= self.fr_couple):
							# Married couple
							self.add_spouse(head)
						else:
							# Single parent + one child
							self.add_children(head, 1, head['yrs'], head['yrs'])
				else:
					# Not a family
					# Add a random age roommate or child that is not own
					# Preference to former (not own children are a small
					# fraction)
					self.add_agent_iterate_age(head, 18, self.max_age)
			elif head['household size'] == 3:
				# Probability a family
				if ((np.random.uniform(0,1) <= self.fr_families) and (head['yrs'] <= 60)):
					# Probability single parent 
					if (np.random.uniform(0,1) <= self.fr_single_parent):
						# Add two children
						self.add_children(head, 2, head['yrs'], head['yrs'])
					else:
						# Add a spouse
						spouse = self.add_spouse(head)
						# Add a child
						self.add_children(head, 1, head['yrs'], spouse['yrs'])
				else:
					# Not a family
					# Add two random age roommates 18+
					# Less preferably a child that is not a family member
					for i in range(2):
						self.add_agent_iterate_age(head, 18, self.max_age)

			elif head['household size'] == 4:
				# Probability a family
				if ((np.random.uniform(0,1) <= self.fr_families) and (head['yrs'] <= 60)):					
					# Probability single parent 
					if (np.random.uniform(0,1) <= self.fr_single_parent):
						# Add three children
						self.add_children(head, 3, head['yrs'], head['yrs'])
						houses_4p.append({'houseID' : head['houseID'], 'size' : 4})
					else:
						# Add a spouse
						spouse = self.add_spouse(head)
						# Add two children
						self.add_children(head, 2, head['yrs'], spouse['yrs'])
						houses_4p.append({'houseID' : head['houseID'], 'size' : 4})
				else:
					# Not a family
					# Add three random age roommates 18+
					# Or not own children
					for i in range(3):
						self.add_agent_iterate_age(head, 18, self.max_age)
					houses_4p.append({'houseID' : head['houseID'], 'size' : 4})
			
		self.household_agents_correction(houses_4p, households)

	def add_children(self, head, n_children, age_1, age_2):
		''' Add n_children to agents of age_1 and age_2 '''

		parent_min = min(age_1, age_2)
		parent_max = max(age_1, age_2)

		# Children age range - hardcoded to 18-43 age difference
		# with parent but not strongly enforced
		min_age = max(0, min(17, parent_max-43)) 
		max_age = max(0, min(17, parent_min-18))

		# Find children in range, if not available in that range
		# add any age
		for ni in range(n_children):
			self.add_agent_iterate_age(head, min_age, max_age, True)
		self.agents[head['ID']-1]['isFamily'] = True

	def add_spouse(self, head):
		''' Add spouse with constraints of age difference max 
				15 years '''
		
		min_age = max(18, head['yrs']-15)
		max_age = min(self.max_age, head['yrs']+15)

		# Try adding in range, if not any age 
		# like roommate, family, etc.
		temp = self.add_agent_iterate_age(head, min_age, max_age, True)
		self.agents[head['ID']-1]['isFamily'] = True
		return temp

	def add_agent_iterate_age(self, head, min_age, max_age, family = False):	
		''' Find and register agent with age in min/max range.
				If range depleted - add random age. '''
	
		if min_age > (max_age+1):
			temp = max_age+1
			max_age = min_age
			min_age = temp
		if min_age == max_age + 1:
			max_age = min(100, max_age+2)

		agent_age = np.random.randint(min_age, max_age+1)
		key = self.find_age_range(agent_age)

		if self.age_remaining[key]['number'] == 0:
			flag_60 = False
			# Add any age that is not zero and less than 60
			while (self.age_remaining[key]['number'] == 0) or flag_60 == True:
				flag_60 = False
				agent_age = np.random.randint(0, self.max_age+1)
				if agent_age >= 60:
					if (np.random.uniform(0,1) > self.fr_60):
						flag_60 = True
						continue
				key = self.find_age_range(agent_age)

		self.update_ages(agent_age)
		
		# Once found, assign
		temp = {}
		temp = deepcopy(self.default_parameters)
		# Agent ID
		temp['ID'] = self.ID
		self.ID += 1
		# Age + update
		temp['yrs'] = agent_age 
		# Agents position
		temp['lon'] = head['lon']
		temp['lat'] = head['lat']
		# House ID
		temp['houseID'] = head['houseID']
		# Family status - just for tracking
		temp['isFamily'] = family

		self.agents.append(temp)
		return temp

	def household_agents_correction(self, houses_4p, households):
		''' Assign remanining agents to 4+ households and 
				retirement homes '''
		
		# Simple random assignment for now
		num_houses = len(houses_4p)
		num_rh = len(self.rh_agents)
		
		for key, value in self.age_remaining.items():
			while not (value['number'] == 0):
				agent_age = np.random.randint(value['min'], value['max']+1)
				self.update_ages(agent_age)
				
				temp = deepcopy(self.default_parameters)
				if agent_age >= 60:
					# Determine if placed in a household 
					if (np.random.uniform(0,1) <= self.fr_60):
						ind4p = np.random.randint(0, num_houses)
						houseID = houses_4p[ind4p]['houseID']
						houses_4p[ind4p]['size'] += 1
					else:
						# Place in a retirment home
						indRH = np.random.randint(0, num_rh)
						houseID = self.rh_agents[indRH]['houseID']
						temp['RetirementHome'] = True
				else:
					ind4p = np.random.randint(0, num_houses)
					houseID = houses_4p[ind4p]['houseID']
					houses_4p[ind4p]['size'] += 1

				# Agent ID
				temp['ID'] = self.ID
				self.ID += 1
				# Age + update
				temp['yrs'] = agent_age 
				# Agents position
				temp['lon'] = households[int(houseID)-1]['lon']
				temp['lat'] = households[int(houseID)-1]['lat']
				# House ID
				temp['houseID'] = houseID
				self.agents.append(temp)	

	def distribute_schools(self, schools):
		''' Assigns school IDs (daycare - college) to agents '''

		# Preprocess for easier usage
		all_schools = {'daycare':[], 'primary':[], 'middle':[], 
						'high':[], 'college':[]}
		
		for school in schools:
			all_schools[school['school type']].append({'ID':school['ID'], 'num students' : school['num students']})

		school_ages = {'daycare': [0,1,2,3,4], 'primary' : [5,6,7,8,9,10],
						'middle': [11,12,13], 'high' : [14,15,16,17],
						'college': [18,19,20,21,22,23,24]}

		# Loop through agents and assign school based on age
		for agent in self.agents:
			age = agent['yrs']
			# Exclude agents that are assumed to be out of school
			if (age > 21) or (agent['isPatient'] == True):
				continue
			# Select school type and available schools
			for key, value in school_ages.items():
				if age in value:
					spec_schools = all_schools[key]
					school_type = key
					
			# Assign first that's non zero
			found_school = False
			for scl in spec_schools:
				if scl['num students'] == 0:
					continue
				found_school = True
				agent['student'] = True
				agent['schoolID'] = scl['ID']
				scl['num students'] -= 1
				break

			# If all are zero and not daycare or college  - assign randomly
			if (found_school == False) and (school_type != 'daycare') and (school_type != 'college'):
				agent['student'] = True
				agent['schoolID'] = spec_schools[np.random.randint(0,len(spec_schools))]['ID']
			else:
				continue
	
	def distribute_transit_and_workplaces(self, households, workplaces, transit, max_working_age, n_employed, occ_map):
		''' Assigns workplace IDs to n_employed agents within working age '''

		#
		# workplaces - a list of Workplace objects
		# households - a list of Household objects
		# transit - Transit class object
		# max_working_age - max age to work 
		# n_employed - number of employed agents
		#

		# If the household-work distance is below this tolerance
		# that workplace is added to potential workplace group 
		dist_tol = 5.0

		transit_times_with_home, times = transit.sample_travel_times(n_employed)
		transit_modes_with_home = transit.sample_travel_modes(n_employed)

		# Number of working agents
		count_working = 0

		# Work from home
		transit_times, transit_modes, count_working = self.assign_work_from_home(transit_times_with_home, \
						transit_modes_with_home, transit, max_working_age)

		# From the remaining, assign all other workplaces
		for agent in self.agents:
		
			# Done assigning
			if not transit_times:
				break
			# All categories that should not be considered
			if agent['works from home']:
				continue
			if (agent['yrs'] < 16) or (agent['yrs'] > max_working_age):
				continue
			if (agent['RetirementHome'] == True) or (agent['isPatient'] == True):
				continue

			# Assign transit time and mode
			agent['work travel time'] = transit_times.pop() 
			agent['work travel mode'] = transit_modes.pop()
			other_types = ['car', 'carpool', 'public', 'other']
			# Overwrite if walking
			if agent['work travel time'] <= transit.walking_treshold:
				agent['work travel mode'] = 'walk'
			else:
				# Make sure mode is not 'walk' if the time isn't
				# Reassign randomly 
				if agent['work travel mode'] == 'walk':
					mode = random.sample(other_types, 1)[0]
			
			cur_work = self.select_workplace(transit, workplaces, households, agent, dist_tol)

			# Assign closest workplace
			agent['works'] = True
			agent['workID'] = cur_work['ID']
			
			# Correct for separately modeled workplaces
			if cur_work['type'] == 'F':
				agent['worksSchool'] = True
				agent['specialWorkID'] = cur_work['specialID']

			if cur_work['type'] == 'AA': 
				agent['worksRH'] = True
				agent['specialWorkID'] = cur_work['specialID']
			
			if cur_work['type'] == 'H':
				agent['works'] = False
				agent['worksHospital'] = True
				agent['specialWorkID'] = cur_work['specialID']
				agent['hospitalID'] = cur_work['specialID']
			
			# Assign workplace type to agent for future use (occupation assignment)
			agent['work_type'] = cur_work['occupation']
			
			count_working += 1

			if int(count_working % 5000) == 0:
				print('Assigned workplace to ' + str(count_working) + ' agents.')

		# Notify if assigned less than designated
		if count_working < n_employed:
			warnings.warn('Assigned employement to ' + str(count_warning) +
							' agents. Requested ' + str(n_employed))


		# The for all - will need to collect this data earlier, likely
		self.group_carpools(transit, workplaces)
		
		# Group public
		self.group_public_transit(transit, workplaces)	
		
		# Match agents' workplaces to occupations 
		self.match_workplace_to_occupation(occ_map)
		
	def match_workplace_to_occupation(self, occ_map):
		""" Match agents' workplace types to occupation types """
		
		#
		# occ_map - the map with workplace types (business types) to their corresponding occupation types
		#
		
		# Find the relative percentage for census data
		# Can change the number '10' to increase randomness / make it more evenly distributed
		census_list = [None] * 100
		 # Starting at index 0
		start_pos = 0 
		for occupation_type, value in self.census_stats.items():
			census_share = round(value[1])
			for ind in range(start_pos, start_pos + census_share):
				census_list[ind] = occupation_type
			start_pos += census_share
		census_list = [x for x in census_list if x != None]	
		# Shuffle the list for even distribution
		random.shuffle(census_list) 

		# First distribute all in-town workers
		# { occupation type : number of agents }
		intown_stats = {}
		for agent in self.agents:
			# Agent works in town -> assign occupation
			if (agent['works'] == True) and (agent['works from home'] == False): 
				if agent['work_type'] != 'outside': 
					agent['occupation'] = occ_map[agent['work_type']]
					if (agent['occupation'] == 'None'):
						agent['occupation'] = agent['work_type']
					if agent['occupation'] in intown_stats:
						intown_stats[agent['occupation']] += 1
					else:
						intown_stats[agent['occupation']] = 1

		# Check in-town stats against census stats
		# { occupation type : diff in number, diff in percentage }
		diff_map = {} 
		tot_agents_needed = 0
		for occupation_type, value in self.census_stats.items():
			# Consider only the type with less agents than census
			if occupation_type in intown_stats:
				if (value[0] - intown_stats[occupation_type]) > 0:
					diff_map[occupation_type] = value[0] - intown_stats[occupation_type]
					tot_agents_needed += diff_map[occupation_type]
			else:
				diff_map[occupation_type] = value[0]
				tot_agents_needed += diff_map[occupation_type]	
		
		# Find the relative percentage among all occupations needing more agents
		rotation_list = [None] * 100
		 # Starting at index 0
		starting_pos = 0 
		for occupation_type, value in diff_map.items():
			relative_share = int(value/tot_agents_needed*100)
			for ind in range(starting_pos, starting_pos + relative_share):
				rotation_list[ind] = occupation_type
			starting_pos += relative_share
		rotation_list = [x for x in rotation_list if x != None]	
		# Shuffle the list for even distribution
		random.shuffle(rotation_list) 
	
		# Distribute out-of-town (uncategorized) agents
		curr_occ_type = 0
		for agent in self.agents:
			if agent['work_type'] == 'outside': 
				if tot_agents_needed > 0: 
					agent['occupation'] = rotation_list[curr_occ_type]
					curr_occ_type += 1
					if curr_occ_type == len(rotation_list):
						curr_occ_type = 0 
				else: 
					# Occupation types estimately balanced
					# This shouldn't happen but in case it does
					# Distribute by the census percentage
					if census_list[curr_occ_type] != None:
						agent['occupation'] = census_list[curr_occ_type]
					curr_occ_type += 1
					if curr_occ_type == len(census_list):
						curr_occ_type = 0 
		
		# Count the types and compare to census
		print('Occupations - census values:')
		print(self.census_stats)
		n_given = 0
		final_given = {}
		for agent in self.agents:
			if agent['occupation'] == 'none':
				continue
			n_given += 1
			if agent['occupation'] in final_given:
				final_given[agent['occupation']] += 1
			else:
				final_given[agent['occupation']] = 1
		for key, value in final_given.items():
			final_given[key] *= 100/n_given
		print('Occupations - assigned values, category - percent')
		print(final_given)

	def assign_work_from_home(self, transit_times_with_home, transit_modes_with_home, transit, max_working_age):
		''' Selects agents that will work from home '''

		count_working = 0

		transit_times = []
		transit_modes = []

		other_types = ['car', 'carpool', 'public', 'walk', 'other']

		for time, mode in zip(transit_times_with_home, transit_modes_with_home):
			if time <= transit.wfh_treshold:
				found = False
				while not found:
					agent = self.agents[random.randint(0, len(self.agents)-1)]
					if (agent['yrs'] >= 16) and (agent['yrs'] <= max_working_age):
						if (agent['RetirementHome'] == False) and (agent['isPatient'] == False):
							found = True
							agent['works from home'] = True
							agent['work travel time'] = time			
							agent['work travel mode'] = 'wfh'
							agent['workID'] = agent['houseID']
							agent['works'] = True
							count_working += 1
			else:
				# Overwrite with another type, randomly
				if mode == 'wfh':
					mode = random.sample(other_types, 1)[0]
				transit_times.append(time)
				transit_modes.append(mode)

		return transit_times, transit_modes, count_working


	def select_workplace(self, transit, workplaces, households, agent, dist_tol):
		''' Find workplace of the agent based on work travel distance '''
		
		# Compute distance to work
		work_dist = transit.mode_speeds[agent['work travel mode']]*agent['work travel time']
		# Find the closest workplace to home
		min_diff = 10000000.0
		curID = 0
		agent_house = households[agent['houseID']-1]
		
		# Select potential workplaces within dist_tol
		tol_workplaces = []
		for work in workplaces:
			cur_dist = aut.compute_distance(agent_house, work)
			cur_diff = abs(work_dist - cur_dist)
			if cur_diff <= dist_tol:
				cur_work = deepcopy(work)
				cur_work['dist'] = cur_diff
				tol_workplaces.append(cur_work)
			# If more apart than based on the threshold
			if cur_diff < min_diff:
				min_diff = cur_diff
				closest_work = deepcopy(work)	

		# If nothing within the tolerance
		if not tol_workplaces:
			cur_work = closest_work
			if cur_work['type'] != 'outside':
				# Update the actual workplace count
				workplaces[cur_work['ID']-1]['N_emp'] += 1
		else:			
			# Sort by distance
			tol_workplaces.sort(key=lambda x: x['dist'])
			# If outside is closest, just assign
			if tol_workplaces[0]['type'] == 'outside':
				cur_work = tol_workplaces[0]
			else:
				# If in NR - first extract all NR that haven't yet reached capacity
				tol_workplaces_temp = [x for x in tol_workplaces if (x['type'] != 'outside') and (x['N_emp']<x['N_max'])]
				if len(tol_workplaces_temp) == 0:
					warnings.warn('No workplaces to consider after capacity cuts. Using all NR workplaces instead.')
					tol_workplaces = [x for x in tol_workplaces if (x['type'] != 'outside')]
				else:
					tol_workplaces = tol_workplaces_temp
				# Then sort by remaining capacity, from least filled
				tol_workplaces.sort(key = lambda x: max(0, float(x['N_emp'])/float(x['N_max'])))
				# Randomly select out of first 20 or max if less than 20
				cur_work = tol_workplaces[random.randint(0, min(20, len(tol_workplaces)-1))]
				# Update the actual workplace count
				workplaces[cur_work['ID']-1]['N_emp'] += 1

		return cur_work

	def group_carpools(self, transit, workplaces):
		''' Select agents into concrete carpool groups based on census and 
				workplace location - travel time '''

		# First count and group by destination/travel time
		# NR is grouped by travel time and outside locations 
		# are grouped by zipcode
		n_carpools = 0
		carpools_NR = {}
		carpools_outside = {}
		for agent in self.agents:
			if not (agent['work travel mode'] == 'carpool'):
				continue
			n_carpools += 1

			# Outside
			wID = agent['workID']-1
			if workplaces[wID]['type'] == 'outside':
				zipcode = str(workplaces[wID]['zip'])
				if zipcode in carpools_outside:
					carpools_outside[zipcode].append(agent['ID'])
				else:
					carpools_outside[zipcode] = [agent['ID']]
			else:
				# In New Rochelle - travel time
				time = str(agent['work travel time'])
				if time in carpools_NR:
					carpools_NR[time].append(agent['ID'])
				else:
					carpools_NR[time] = [agent['ID']]
	
		# Get distribution of groups (2, 3, 4+ people)
		samples = transit.sample_carpool_numbers(n_carpools)
	
		n_cp = self.distribute_concrete_carpools(carpools_NR, samples, transit, workplaces, 0)
		n_out_cp = self.distribute_concrete_carpools(carpools_outside, samples, transit, workplaces, n_cp)
		if n_out_cp == n_cp:
			warnings.warn("No outside workplaces have carpools")

	def group_public_transit(self, transit, workplaces):
		''' Group the agents into public transit '''

		public_transit_outside = {}
		public_transit_NR = {}

		# Create individual groups
		for agent in self.agents:
			if not (agent['work travel mode'] == 'public'):
				continue
			# Outside
			wID = agent['workID']-1
			if workplaces[wID]['type'] == 'outside':
				zipcode = str(workplaces[wID]['zip'])
				# Check if there is public transit
				if not transit.has_public(zipcode):
					# Change type and continue
					agent['work travel mode'] = 'car'
					continue
				if zipcode in public_transit_outside:
					public_transit_outside[zipcode].append(agent['ID'])
				else:
					public_transit_outside[zipcode] = [agent['ID']]
			else:
				# In New Rochelle - travel time
				time = str(int(agent['work travel time']))
				if time in public_transit_NR:
					public_transit_NR[time].append(agent['ID'])
				else:
					public_transit_NR[time] = [agent['ID']]		
		
		# Assign IDs and make objects 
		# One group = one object
		for pt_group_zip, agent_IDs in public_transit_outside.items():
			work_type = 'outside'
			# Use the first agents travel time
			aID = agent_IDs[0]
			travel_time = self.agents[aID-1]['work travel time']
			pt_ID = transit.create_public_transit(work_type, travel_time, pt_group_zip)
			assert pt_ID != 0, 'Invalid public transit ID - out of town'
			# Assign ID to all agents in this transit
			for aID in agent_IDs:
				self.agents[aID-1]['publicID'] = pt_ID
		
		for pt_group_time, agent_IDs in public_transit_NR.items():
			# Use the first agents travel time
			aID = agent_IDs[0]
			wID = self.agents[aID-1]['workID']
			work_type = workplaces[wID-1]['type']
			travel_time = float(pt_group_time) 
			pt_ID = transit.create_public_transit(work_type, travel_time, 'NR')
			assert pt_ID != 0, 'Invalid public transit ID - New Rochelle'
			# Assign ID to all agents in this transit
			for aID in agent_IDs:
				self.agents[aID-1]['publicID'] = pt_ID

	def distribute_concrete_carpools(self, cp_dict, samples, transit, workplaces, n_cp):
		''' Groups people into concrete carpools 
				starting from cp_dict that grouped the agents 
				by travel time and destination. samples have the data
				on number of passengers in each agents carpool. transit and n_cp
				are needed to create new Carpool objects and keep track of created IDs.
				ncp is the current number of carpools. '''
		
		# Pair the agents within each carpool subgroup	
		for key, value in cp_dict.items():
			passengers = {'2':[], '3':[], '4':[]}
			# This will store agent IDs that have 2, 3, or 4+
			# people in the carpool
			for aID in value:
				pnum = str(samples.pop())
				passengers[pnum].append(aID)
			
			# Now group based on the pnum - 2,3, or 4 value 
			for pnum, pIDs in passengers.items():
				while pIDs and (len(pIDs) > int(pnum)):
					# One carpool
					n_cp += 1
					for i in range(0,int(pnum)):
						aID = pIDs.pop() - 1 
						# Create this carpool if it doesn't exist yet
						wID = self.agents[aID]['workID']
						work_type = workplaces[wID-1]['type']
						work_destination = 0
						if work_type == 'outside':
							work_destination = workplaces[wID-1]['zip']
						travel_time = self.agents[aID]['work travel time']
						transit.create_carpools(n_cp, work_type, travel_time, work_destination)
						# pvs are agent IDs
						self.agents[aID]['carpoolID'] = n_cp
				# If remaining, just group together or add to existing 
				# if only one agent
				if pIDs:
					if len(pIDs) == 1:
						aID = pIDs.pop() - 1
						self.agents[aID]['carpoolID'] = n_cp
					else:
						n_cp += 1
						for i in range(0,len(pIDs)):
							aID = pIDs.pop() - 1 
							# Create this carpool if it doesn't exist yet
							wID = self.agents[aID]['workID']
							work_type = workplaces[wID-1]['type']
							work_destination = 0
							if work_type == 'outside':
								work_destination = workplaces[wID-1]['zip']
							travel_time = self.agents[aID]['work travel time']
							transit.create_carpools(n_cp, work_type, travel_time, work_destination)
							# pvs are agent IDs
							self.agents[aID]['carpoolID'] = n_cp
		return n_cp 


	def set_infected(self, n_infected_0):
		''' Randomly chooses n_infected_0 agents to be initially
				infected '''

		# Indices of agents that are infected
		infected_index = random.sample(range(0, len(self.agents)), n_infected_0)
		for idx in infected_index:
			self.agents[idx]['infected'] = True	

	def __repr__(self):
		''' String output for stdout or files '''

		self.set_infected(self.n_infected)
		temp = []
		for agent in self.agents:
			temp.append((' ').join([str(int(agent['student'])), str(int(agent['works'])), 
									str(agent['yrs']), str(agent['lon']), str(agent['lat']), 
									str(agent['houseID']), str(int(agent['isPatient'])), 
									str(agent['schoolID']), str(int(agent['RetirementHome'])),
									str(int(agent['worksRH'])), str(int(agent['worksSchool'])),
									str(agent['workID']), str(int(agent['worksHospital'])), 
									str(agent['hospitalID']), str(int(agent['infected'])), 
									str(int(agent['works from home'])), str(agent['work travel time']),
									str(agent['work travel mode']), str(agent['specialWorkID']),
									str(agent['carpoolID']), str(agent['publicID']), str(agent['occupation'])])) 
	
		return ('\n').join(temp)

