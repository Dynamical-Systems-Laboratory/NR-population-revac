# ------------------------------------------------------------------
#
#	Check generated population 
#
# ------------------------------------------------------------------

import sys
py_path = '../../../src/mobility/'
sys.path.insert(0, py_path)

py_path = '../../../input_verification/'
sys.path.insert(0, py_path)

import check_agents as ca
import check_households as ch
import abm_residential as res
import abm_public as public
import abm_agents as agents
import abm_transit as travel

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

ad_file = 'check_age_dist.txt'
rh_file = 'check_retirement_home_size.txt'
hs_file = 'check_household_size.txt'
wk_file = 'check_workplace_size.txt'
sch_file = 'check_school_size.txt'

hs_age_file = 'household_age_dist.txt'
hs_work_file = 'household_work_dist.txt'
fm_work_file = 'family_work_dist.txt'
hs_work_ID_file = 'household_work_ID_dist.txt'
hs_school_file = 'household_school_dist.txt'

# Household coordinates and sizes
hs_coords_sizes = 'check_hs_size_w_coords.txt'
building_coords_sizes = 'check_bld_size_w_coords.txt'

#
# Generate places
#

# Households
households = res.Households(n_tot, res_file, res_type_file)
	
# Retirement homes
retirement_homes = public.RetirementHomes(pb_file, pb_type_file)
	
# Hospitals
hospitals = public.Hospitals(pb_file, pb_type_file)

# Schools
schools = public.Schools(pb_file, pb_type_file)

# Workplaces
workplaces = public.Workplaces(pb_file_gis, pb_file_out, pb_type_file, foccupation, pb_file_in, focc_cap)
# Merge workplaces for distribution
workplaces.merge_with_special_workplaces(schools.schools, retirement_homes.retirement_homes, hospitals.hospitals)
	
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

#
# Check the generated population
# 

# Age distribution
age_groups = [(0,4),(5,9),(10,14),(15,19),(20,24),(25,34),(35,44),(45,54),(55,59),(60,64),(65,74),(75,84),(85,max_age)]
ca.print_age_distribution(ad_file, age_groups, agents.agents)

# Retirement home sizes - employees and residents
ca.print_other_sizes(rh_file, agents.agents, 'worksRH', 'RetirementHome', 'houseID')
# Schools - employees and schools
ca.print_other_sizes(sch_file, agents.agents, 'worksSchool', 'student', 'schoolID')

# Household sizes
ca.print_household_sizes(hs_file, agents.agents)
ca.print_household_sizes_w_coords(hs_coords_sizes, agents.agents)
ca.print_building_sizes_w_coords(building_coords_sizes, agents.agents)

# Workplace sizes
ca.print_workplace_sizes(wk_file, agents.agents)

# Household characteristics
ch.print_houses_and_age(hs_age_file, agents.agents)
ch.print_houses_and_work_status(hs_work_file, fm_work_file, agents.agents)
ch.print_houses_and_work_ID(hs_work_ID_file, agents.agents)
ch.print_houses_and_student_status(hs_school_file, agents.agents)

