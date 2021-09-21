# ------------------------------------------------------------------
#
#	Tests for abm_agents module
#
# ------------------------------------------------------------------

import sys
py_path = '../../../tools/'
sys.path.insert(0, py_path)

py_path = '../../../src/mobility/'
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
# Generate New Rochelle population for the COVID model
#
# ------------------------------------------------------------------

#
# Input files
#

# GIS and type data files database
dpath = '../../../town_data/NewRochelle/database/'
cpath = '../../../town_data/NewRochelle/census_data/'
year = '2021'

# File with residential GIS data
res_file = dpath + 'residential.txt'
# File with residential building types
res_type_file = dpath + 'residential_types.txt'
# File with residential units data
units_file = cpath + 'unit_stats.txt'
# File with public places GIS data (used only for special workplaces)
pb_file = dpath + 'public.txt'
# File with regular workplaces inside (with business type)
pb_file_gis = dpath + year + '_core_poi_NewRochelleIn_WorkTrimmed.csv'
# File with regular workplaces inside (with occupation)
pb_file_in = dpath + year + '_core_poi_NewRochelleIn_OccupationTrimmed.csv'
# File with public places GIS data that are outside (with occupation)
pb_file_out = dpath + year + '_core_poi_NewRochelleOut_WorkTrimmed.csv'
# File with building types
pb_type_file = dpath + 'public_types_mobility.txt'
# File with leisure inside of town
pb_leisure_file_in = dpath + year + '_core_poi_NewRochelleIn_LeisureTrimmed.csv'
# File with leisure outside of town
pb_leisure_file_out = dpath + year + '_core_poi_NewRochelleOut_LeisureTrimmed.csv'

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
foccupation = dpath + 'match_occupation.txt'
focc_cap = dpath + 'occupation_capacity.txt'
agent_occ = dpath + 'occupation_stats.txt'

#
# Other input
#

# Total number of units (households + vacancies)
n_tot = 29645
# Fraction of vacant households
fr_vacant = 0.053
# Total number of agents
n_agents = 79205
# Number of employed agents (summed from occupation stats file)
n_employed = 39758
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
# Output files
#

rh_out = 'NR_retirement_homes.txt'
hs_out = 'NR_households.txt' 
wk_out = 'NR_workplaces.txt'
hsp_out = 'NR_hospitals.txt'
sch_out = 'NR_schools.txt'
ag_out = 'NR_agents.txt'
cpool_out = 'NR_carpool.txt'
public_out = 'NR_public.txt'
leisure_out = 'NR_leisure.txt'

#
# Generate places
#

# Households
households = res.Households(n_tot, res_file, res_type_file)
with open(hs_out, 'w') as fout:
	fout.write(repr(households))
	
# Retirement homes
retirement_homes = public.RetirementHomes(pb_file, pb_type_file)
with open(rh_out, 'w') as fout:
	fout.write(repr(retirement_homes))
	
# Hospitals
hospitals = public.Hospitals(pb_file, pb_type_file)
with open(hsp_out, 'w') as fout:
	fout.write(repr(hospitals))

# Schools
schools = public.Schools(pb_file, pb_type_file)
with open(sch_out, 'w') as fout:
	fout.write(repr(schools))
	
# Workplaces
workplaces = public.Workplaces(pb_file_gis, pb_file_out, pb_type_file, foccupation, pb_file_in, focc_cap)
# Merge workplaces for distribution
workplaces.merge_with_special_workplaces(schools.schools, retirement_homes.retirement_homes, hospitals.hospitals)
with open(wk_out, 'w') as fout:
	fout.write(repr(workplaces))

# Leisure/time off locations
leisure = public.LeisureLocations(pb_leisure_file_in, pb_leisure_file_out, True)
with open(leisure_out, 'w') as fout:
	fout.write(repr(leisure))
	
# Transit
transit = travel.Transit(ftimes, fmodes, fcpools, fpt_routes, mode_speed, t_wfh, t_walk)

#
# Create the population
#

agents = agents.Agents(file_age_dist, file_hs_age, file_hs_size, n_agents, max_age, n_tot, fr_vacant, fr_fam, fr_couple, fr_sp, fr_60, n_infected, agent_occ)
agents.distribute_retirement_homes(retirement_homes.retirement_homes)
agents.distribute_hospital_patients(hospitals.hospitals)
agents.distribute_households(households.households, fr_vacant)

agents.distribute_schools(schools.schools)
agents.distribute_transit_and_workplaces(households.households, workplaces.workplaces, transit, max_working_age, n_employed, workplaces.occ_map)

transit.print_public_transit(public_out)
transit.print_carpools(cpool_out)
with open(ag_out, 'w') as fout:
	fout.write(repr(agents))
