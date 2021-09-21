# ------------------------------------------------------------------
#
#	Module for generation of travel times and transit modes 
#
# ------------------------------------------------------------------

import math
from random import choices, choice

class Transit(object):
	''' Class for generation of transit times and travel modes '''

	def __init__(self, ftimes, fmodes, fcpool, pt_routes, mode_speed, t_wfh, t_walk, fnp = None):
		''' Load and store travel time and mode information '''

			# ftimes - file with travel times data
		# fmodes - file with travel modes data 
		# fcpool - file with carpool statistics 
				# pt_routes - file with public transit routes 

		# Files have a structure time/mode | fraction/percent population 
				# pt_routes has a structure: ID | Name | zip1, zip2, ... (ID is 
				#	irrelevant)
		# Look into examples for exact format
	
		# Data points | fraction of population associated with them
		self.travel_times = {}
		self.travel_modes = {}
		self.carpool_stats = {}
		self.transit_routes = {}

		# Carpool and public transit (GSP) object collections
		self.carpools = []
		self.GSP = []

		# Speed associated with each mode, km/min
		self.conv_speed = 1.6/60.0
		self.mode_speeds = mode_speed
		self.wfh_treshold = t_wfh
		self.walking_treshold = t_walk
		for key, value in self.mode_speeds.items():
			self.mode_speeds[key] *= self.conv_speed

		self.load_travel_times(ftimes)
		self.load_travel_modes(fmodes)
		self.load_carpool_stats(fcpool)
		self.load_transit_routes(pt_routes)

		# Load zipcodes that have no public transit access
		self.no_public_transit = []
		if fnp:
			self.load_not_accessible(fnp)

	def load_not_accessible(self, fnp):
		''' Read and store zipcodes that are not 
				accessible through public transit '''
		with open(fnp, 'r') as fin:
			for line in fin:
				for zp in line.strip().split(','):
					self.no_public_transit.append(zp)
		print(self.no_public_transit)

	def has_public(self, zipcode):
		''' True if the zipcode has public transit access '''
		return not (zipcode in self.no_public_transit)

	def load_travel_times(self, ftimes):
		''' Read the file with times of travel of the population
				and fraction of the population that it is relevant to '''

		with open(ftimes, 'r') as fin:
			for line in fin:
				temp = line.strip().split()
				self.travel_times[temp[0]] = float(temp[1])

	def load_travel_modes(self, fmodes):
		''' Read the file with modes of travel of the population
				and percent of the population that it is relevant to. 
				Converts percent to fractions. '''

		with open(fmodes, 'r') as fin:
			for line in fin:
				temp = line.strip().split()
				self.travel_modes[temp[0]] = float(temp[1])/100.0
	
	def load_carpool_stats(self, fcpool):
		''' Read the file with number of people in a carpool
				and fraction of carpooled population that has this many '''

		with open(fcpool, 'r') as fin:
			for line in fin:
				temp = line.strip().split()
				self.carpool_stats[temp[0]] = float(temp[1])
	
	def load_transit_routes(self, pt_routes):
		''' Read the file with public transit routes; store in a dictionary 
				with Name : [[zipcodes for that route], 0]; 0 will be 
				replaced by a final ID if that route is created '''
	
		with open(pt_routes, 'r') as fin:
			for line in fin:
				temp = line.strip().split()
				zips = temp[2].split(',')
				
				# Names have to be unique
				if temp[1] in self.transit_routes:
					raise RuntimeError('Public transit route names need to be unique')
				self.transit_routes[temp[1]] = [[],0]
				
				# First element of the list is a list of 
				# zipcodes that are this transit destination
				for z in zips:
					self.transit_routes[temp[1]][0].append(z)
   

	def sample_travel_times(self, nsamples):
		''' Return nsamples of times of travel according to probability distribution 
				and the corresponding times (mid value of the input interval) '''
				
		times = []
		probs = []
		for key, value in self.travel_times.items():
			if '+' in key:
				temp = key.split('+')
				times.append(float(temp[0]))
			else:
				temp = key.split('-')
				times.append(float(temp[0])+(float(temp[1])-float(temp[0]))*0.5)
			probs.append(value)

		sampled = choices(times, probs, k=int(nsamples))

		return sampled, times

	def sample_travel_modes(self, nsamples):
		''' Return nsamples of modes of travel according to probability distribution '''
				
		modes = []
		probs = []
		for key, value in self.travel_modes.items():
			modes.append(key)		
			probs.append(value)

		sampled = choices(modes, probs, k=int(nsamples))

		return sampled

	def sample_carpool_numbers(self, nsamples):
		''' Return nsamples of number of people in a carpool 
				according to probability distribution '''
				
		numbers = []
		probs = []
		for key, value in self.carpool_stats.items():
			numbers.append(key)		
			probs.append(value)

		sampled = choices(numbers, probs, k=int(nsamples))

		return sampled

	def match_time(self, ti):
		''' Finds the time interval where ti occurs, returns it as a string '''

		for key, value in self.travel_times.items():
			if '+' in key:
				temp = key.split('+')
				if ti >= float(temp[0]):
					return key
			else:
				temp = key.split('-')
				if (ti >= float(temp[0])) and (ti <= float(temp[1])):
					return key
		
		return None

	def create_carpools(self, n_cp, work_type, travel_time, wdest):
		''' Create n_cp objects of type Carpool if they don't already exist '''

		if n_cp > len(self.carpools):
			self.carpools.append(Carpool(n_cp, work_type, travel_time, wdest))

	def create_public_transit(self, work_type, travel_time, wdest):
		''' Create objects of type public transit if they don't already exist; 
				Return ID of new or existing. Routes restricted by input.'''

		NR_choices = []
		for key, value in self.transit_routes.items():
			if wdest in value[0]:
				# Out of town - select by zipcode
				if work_type == 'outside':
					# Check if already created
					if value[1] > 0:
						# Return the ID (starts with 1)
						return value[1]		
					else:
						# Create new route and update the global dict
						ptID = len(self.GSP) + 1
						self.GSP.append(PublicTransit(ptID, work_type, travel_time, wdest,key))			
						self.transit_routes[key][1] = ptID
						return ptID
			else:
				# In New Rochelle - pick one randomly
				NR_choices.append(key)
		
		# Select a possible NR route
		key = choice(NR_choices)
		# Check if already a registered route
		if self.transit_routes[key][1] > 0:
			return self.transit_routes[key][1]
		else:
			# Create a new route
			ptID = len(self.GSP) + 1
			self.GSP.append(PublicTransit(ptID, work_type, travel_time, wdest,key))			
			self.transit_routes[key][1] = ptID
			return ptID

		# This would indicate something is wrong
		return 0

	def print_carpools(self, fname):
		''' Save carpool data to file fname '''
		
		with open(fname, 'w') as fout:
			for cpool in self.carpools:
				temp = (' ').join([str(cpool.ID), cpool.work_type, str(cpool.travel_time), str(cpool.work_destination)])
				temp += '\n'
				fout.write(temp)
	
	def print_public_transit(self, fname):
		''' Save public transit data to file fname '''
		
		with open(fname, 'w') as fout:
			for pt in self.GSP:
				temp = (' ').join([str(pt.ID), pt.work_type, str(pt.travel_time), str(pt.work_destination)])
				temp += '\n'
				fout.write(temp)

class Carpool(object):
	''' Class for maintaining carpool attributes '''

	def __init__(self, ncp, wtype, ttime, wdest):

		self.ID = ncp
		# 'outside' or actual business type if in NR
		self.work_type = wtype
		# Travel time if NR, travel time of just one agent if outside 
		self.travel_time = ttime
		# 0 if NR, zipcode if outside 
		self.work_destination = wdest

class PublicTransit(object):
	''' Class for maintaining a public transit object '''

	def __init__(self, npt, wtype, ttime, wdest, name):

		self.ID = npt
		# 'outside' or actual business type if in NR
		self.work_type = wtype
		# Travel time if NR, travel time of just one agent if outside
		self.travel_time = ttime
		# 0 if NR, zipcode if outside
		self.work_destination = wdest
		# Name of the route
		self.name = name


