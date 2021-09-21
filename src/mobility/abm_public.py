# ------------------------------------------------------------------
#
#	Module for generation of public places in an ABM population
#
# ------------------------------------------------------------------

import math
import random

class Workplaces(object):
	''' Class for generation of workplaces '''

	def __init__(self, fname_gis, fname_outside, fmap, foccupation, fname_safegraph, focc_cap):
		''' Generate individual workplaces from input data.
				Generates all workplaces, including outside town. '''

		# fname_gis - all public places from gis data
		# fname_outside - all public places outside	
		# fmap - name of the file with types and descriptions
		# foccupation - file for map from business type to occupation type
		# fname_safegraph - file for SafeGraph data
		# focc_map - file for occupation type's capacity
		#

		# Total number of workplaces
		self.ntot = 0

		# Data
		# Buildings
		self.workplaces = []
		# Type map
		self.workplace_map = {}
		# Type representing daycares
		self.daycare_type = 'FF'

		# Load occupation map
		self.occ_map = self.read_occupation_map(foccupation)
		# Load Occupation capacity
		self.occ_cap = self.read_occupation_capacity(focc_cap)

		# Load the buildings and the map
		# (first the map)
		self.read_gis_types(fmap)
		self.read_gis_data(fname_gis)
		# self.read_safegraph_data(fname_safegraph)
		# Outside of town 
		self.read_outside_data(fname_outside)
		
	def read_occupation_map(self, fname):
		''' Read and map workplace letter type to occupation type '''
		
		occupation_map = {}
		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			for line in fin:
				infoList = line.split()
				occupation_map[infoList[0]] = infoList[1].strip()

		return occupation_map

	def read_gis_data(self, fname_data):
		''' Read and store workplace data for 
				all workplaces in the town '''
		
		with open(fname_data, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Exclude hospitals, retirement homes, 
				# and schools
				if (line[0] == 'H') or ('AA' in line[0]) or (line[0] == 'F'):
					continue

				ID += 1
				# Common information
				temp['ID'] = ID
				# Non zero only for schools, retirement homes, and hospitals
				temp['specialID'] = 0
				temp['occupation'] = self.occ_map[line[0]]
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])
				# Current number of employees
				temp['N_emp'] = 0
				# Min and max number of employees for that type
				temp['N_min'] = self.workplace_map[temp['type']][1]
				temp['N_max'] = self.workplace_map[temp['type']][2]

				self.workplaces.append(temp)
		self.ntot = ID
		print('Loaded ' + str(ID) + ' workplaces from GIS')
		
	def read_occupation_capacity(self, fname):
		''' Read and map occupation letter type to occupation capacity '''

		occupation_capacity = {}
		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			for line in fin:
				line = line.strip().split()
				occupation_capacity[line[0]] = [line[0], int(line[-2]), int(line[-1])]

		return occupation_capacity

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions, 
				minimum and maximum capacity of that type '''

		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.workplace_map[line[0]] = [(' ').join(line[1:-2]), int(line[-2]), int(line[-1])]
	

	def read_safegraph_data(self, fname):
		''' Read and store SafeGraph data for in-town workplaces ''' 
		
		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = self.ntot
			for line in fin:
				temp = {}
				line = line.strip().split()

				ID += 1
				temp['ID'] = ID
				# Non zero only for schools, retirement homes, and hospitals
				temp['specialID'] = 0
				temp['occupation'] = line[1]
				temp['type'] = 'none'
				temp['lon'] = float(line[3])
				temp['lat'] = float(line[2])
				# Current number of employees
				temp['N_emp'] = 0
				# Min and max number of employees for t
				# hat occupation
				temp['N_min'] = self.occ_cap[temp['occupation']][1]
				temp['N_max'] = self.occ_cap[temp['occupation']][2]

				self.workplaces.append(temp)
		self.ntot = ID
		print('Loaded ' + str(ID) + ' workplaces from SafeGraph')
		
	
	def read_outside_data(self, fname):
		''' Read and store workplace data for 
				all workplaces outside of town. 
				It groups the workplaces by zipcode,
				all the places with the same zipcode will 
				be treated as a single workplaces with 
				average coordinate of all of them. '''

		ID = self.ntot

		# Read and group by zipcodes 
		all_out = {}
		with open(fname, 'r') as fin:
			next(fin)
			for line in fin:
				line = line.strip().split()
				zipcode = str(int(line[2]))
				if zipcode in all_out:
					all_out[zipcode][0].append(float(line[0]))
					all_out[zipcode][1].append(float(line[1]))
					all_out[zipcode][2] += 1
				else:
					all_out[zipcode] = [[float(line[0])],[float(line[1])], 1]
		
		# Add each zipcode as a workplace
		# Coordinates are averaged GIS
		for key, value in all_out.items():
			lat = sum(value[0])/value[2]
			lon = sum(value[1])/value[2]

			temp = {}
			ID += 1

			temp['ID'] = ID
			# Non zero only for schools, retirement homes, and hospitals
			temp['specialID'] = 0
			temp['type'] = 'outside'
			temp['occupation'] = 'outside'
			temp['lat'] = lat 
			temp['lon'] = lon 
			temp['zip'] = int(key)

			self.workplaces.append(temp)

		print('Loaded ' + str(ID-self.ntot) + ' outside workplaces')
		self.ntot = ID		

	def merge_with_special_workplaces(self, schools, retirement_homes, hospitals):
		''' Add the workplace categories that are modeled separately otherwise '''
	
		ID = self.ntot
		for school in schools:
			ID += 1
			temp = {}
			temp['ID'] = ID
			temp['specialID'] = school['ID']
			temp['occupation'] = 'A'
			temp['type'] = 'F'
			temp['lon'] = school['lon']
			temp['lat'] = school['lat']
			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			if school['school type'] == 'daycare':  
				temp['N_min'] = self.workplace_map[self.daycare_type][1]
				temp['N_max'] = self.workplace_map[self.daycare_type][2]
			else:
				temp['N_min'] = self.workplace_map[temp['type']][1]
				temp['N_max'] = self.workplace_map[temp['type']][2]
		
			self.workplaces.append(temp)
		
		for rh in retirement_homes:
			ID += 1
			temp = {}
			temp['ID'] = ID 
			temp['specialID'] = rh['ID']
			temp['occupation'] = 'B'
			temp['type'] = 'AA'
			temp['lon'] = rh['lon']
			temp['lat'] = rh['lat'] 

			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			temp['N_min'] = self.workplace_map[temp['type']][1]
			temp['N_max'] = self.workplace_map[temp['type']][2]

			self.workplaces.append(temp)

		for hospital in hospitals:
			ID += 1
			temp = {}
			temp['ID'] = ID 
			temp['specialID'] = hospital['ID']
			temp['occupation'] = 'A'
			temp['type'] = 'H'
			temp['lon'] = hospital['lon']
			temp['lat'] = hospital['lat']

			# Current number of employees
			temp['N_emp'] = 0
			# Min and max number of employees for that type
			temp['N_min'] = self.workplace_map[temp['type']][1]
			temp['N_max'] = self.workplace_map[temp['type']][2]

			self.workplaces.append(temp)

		self.ntot = ID

	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.workplaces:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon']), str(place['occupation']), str(place['specialID'])]))
	
		return ('\n').join(temp)
			
class Schools(object):
	''' Class for generation of schools '''

	def __init__(self, fname, fmap):
		''' Generate individual schools from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of schools 
		self.ntot = 0

		# Data
		# Buildings
		self.schools = []
		# Type map
		self.schools_map = {}

		# Type hierarhy
		self.school_types = {'daycare' : 1, 'primary' : 2, 'middle' : 3, 'high' : 4, 'college' : 5}
		self.school_strings = ['daycare', 'primary', 'middle', 'high', 'college']

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)

	def read_gis_data(self, fname):
		''' Read and store school data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				line = line.strip().split()

				# Include only schools
				if line[0] != 'F':
					continue

				# If one school has multiple levels,
				# split into each level but keep min/type
				# info for reference

				# Add lowest and highest type
				school_type = line[5].split(',')
				min_type = 1000
				max_type = 0

				for sc in school_type:
					sc = sc.strip().strip('"')
					if sc == '':
						continue

					temp_type = self.school_types[sc]
					if temp_type < min_type:
						min_type = temp_type
						min_str = sc
					if temp_type > max_type:
						max_type = temp_type
						max_str = sc
			
				i0 = self.school_strings.index(min_str)
				iF = self.school_strings.index(max_str)
				for ii in range(i0, iF+1):
					temp = {}
					temp['school min type'] = self.school_strings[i0]
					temp['school max type'] = self.school_strings[iF]

					ID += 1
					# Common information
					temp['ID'] = ID
					temp['type'] = line[0]
					temp['lon'] = float(line[2])
					temp['lat'] = float(line[1])
					temp['school type'] = self.school_strings[ii]

					# Number of students always second after
					# coordinates; round and ignore differences
					# is is approximate
					num_types = iF-i0+1
					temp['num students'] = math.floor(float(line[4])/num_types)
					self.schools.append(temp)
				self.ntot = ID

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.schools_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.schools:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon']), place['school type']])) 
	
		return ('\n').join(temp)

class Hospitals(object):
	''' Class for generation of hospitals '''

	def __init__(self, fname, fmap):
		''' Generate individual hospitals from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of hospitals
		self.ntot = 0

		# Data
		# Buildings
		self.hospitals = []
		# Type map
		self.hospitals_map = {}

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)

	def read_gis_data(self, fname):
		''' Read and store hospital data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Include only hospitals 
				if line[0] != 'H':
					continue
				
				ID += 1
				# Common information
				temp['ID'] = ID
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])

				# Number of patients
				temp['num patients'] = int(line[4])

				self.hospitals.append(temp)

		self.ntot = ID

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.hospitals_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.hospitals:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon'])])) 
	
		return ('\n').join(temp)

class RetirementHomes(object):
	''' Class for generation of retirement and nursing homes '''

	def __init__(self, fname, fmap):
		''' Generate individual retirement and nursing homes from input data '''

		#
		# fname - input file name with all public places
		# fmap - name of the file with types and descriptions
		#

		# Total number of retirement and nursing homes
		self.ntot = 0

		# Data
		# Buildings
		self.retirement_homes = []
		# Type map
		self.retirement_homes_map = {}

		# Load the buildings and the map
		self.read_gis_data(fname)
		self.read_gis_types(fmap)
	
	def read_gis_data(self, fname):
		''' Read and store retirement homes data '''

		with open(fname, 'r') as fin:
			# Skip the header
			next(fin)
			ID = 0
			for line in fin:
				temp = {}
				line = line.strip().split()

				# Include only retirement homes
				if not (line[0] in 'AA'):
					continue
				
				ID += 1
				# Common information
				temp['ID'] = ID
				temp['type'] = line[0]
				temp['lon'] = float(line[2])
				temp['lat'] = float(line[1])

				# Number of residents
				temp['num residents'] = int(line[4])

				self.retirement_homes.append(temp)

		self.ntot = ID-1

	def read_gis_types(self, fname):
		''' Loads a map with GIS public building types and descriptions '''
	
		with open(fname, 'r') as fin:
			for line in fin:
				line = line.strip().split()
				self.retirement_homes_map[line[0]] = (' ').join(line[2:])
	
	def __repr__(self):
		''' String output for stdout or files '''
		
		temp = []
		for place in self.retirement_homes:
			temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon'])])) 
	
		return ('\n').join(temp)

class LeisureLocations(object):
    ''' Class for generation of leisure locations '''

    def __init__(self, fname1, fname2=None, outOfTown=False):
        ''' Load and pre-process leisure locations - in a broad sense,
                grocerry stores are also included. '''

        #
        # fname1 - input file name with all public places in-town
        #			that are also counted as leisure locations
        # outOfTown - boolean flag indicating if the input file has locations
	#			out-of-town (optional, default = False)
	# fname2 - input file name with all public places out-of-town
        #			that are also counted as leisure locations
	#			(optional, default = None)
	#


        # Total number of leisure locations
        self.ntot = 0

        # Data
        # Buildings
        self.leisure_locations = []

        # Load the buildings
        self.read_gis_data(fname1, fname2, outOfTown)

    def read_gis_data(self, fname1, fname2=None, outOfTown=False):
        ''' Read and store data for
                all leisure locations in town '''
        count1 = self.loadInfo(fname1)
        count2 = 0
        if fname2 != None:
 			# Loding the out-of-town location from fname2
            count2 = self.loadInfo(fname2, outOfTown, count1)
        self.ntot = count1 + count2
        print('Loaded ' + str(self.ntot) + ' leisure locations') 

    def loadInfo(self, fname, outOfTown=False, ID=0):
        with open(fname, 'r') as fin:
            # Skip the header
            next(fin)
            for line in fin:
                temp = {}
                line = line.strip().split(',')
                ID += 1
                # Common information
                temp['ID'] = ID
                temp['name'] = line[0]
                temp['type'] = ','.join(line[:-2][1:]).strip('"')
                temp['lat'] = float(line[-2])
                temp['lon'] = float(line[-1])

                if outOfTown:
                    temp["in/out"] = "outside"
                else:
                    temp["in/out"] = "intown"

                self.leisure_locations.append(temp)

        return ID

    def __repr__(self):
        ''' String output for stdout or files '''

        temp = []
        for place in self.leisure_locations:
            temp.append((' ').join([str(place['ID']), str(place['lat']), str(place['lon']), str(place["in/out"])]))

        return ('\n').join(temp)


