# ------------------------------------------------------------------
#
#   Tests for transit module    
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
from collections import Counter

import abm_utils as aut
import abm_transit as travel

#
# Supporting functions
#

def check_loading_times(transit, forig):
    ''' Tests if the file with transit times was loaded correctly '''

    tol = 1e-5
    with open(forig, 'r') as fin:
        for line in fin:
            temp = line.strip().split()
            val = float(temp[1])
            if not ut.float_equality(val, transit.travel_times[temp[0]], tol):
                return False
    return True
    
def check_loading_modes(transit, forig):
    ''' Tests if the file with transit modes was loaded correctly '''

    tol = 1e-5
    with open(forig, 'r') as fin:
        for line in fin:
            temp = line.strip().split()
            val = float(temp[1])/100.0
            if not ut.float_equality(val, transit.travel_modes[temp[0]], tol):
                return False
    return True

def check_loading_cpool(transit, forig):
    ''' Tests if the file with carpool statistics was loaded correctly '''

    tol = 1e-5
    with open(forig, 'r') as fin:
        for line in fin:
            temp = line.strip().split()
            val = float(temp[1])
            if not ut.float_equality(val, transit.carpool_stats[temp[0]], tol):
                return False
    return True

def check_times_sampling(transit):
    ''' Verifies if travel times are correctly sampled '''

    tol = 1e-3
    nsamples = 1e6
    samples, times = transit.sample_travel_times(nsamples)

    for key, value in Counter(samples).items():
        comp = value/nsamples
        exp = transit.travel_times[transit.match_time(key)]
        if not ut.float_equality(comp, exp, tol):
            return False
    return True

def check_modes_sampling(transit):
    ''' Verifies if travel modes are correctly sampled '''

    tol = 1e-2
    nsamples = 1e6
    samples = transit.sample_travel_modes(nsamples)

    for key, value in Counter(samples).items():
        comp = value/nsamples
        exp = transit.travel_modes[key]
        if not ut.float_equality(comp, exp, tol):
            return False
    return True

def check_carpool_sampling(transit):
    ''' Verifies if carpool number of passengers is correctly sampled '''

    tol = 1e-2
    nsamples = 1e6
    samples = transit.sample_carpool_numbers(nsamples)

    for key, value in Counter(samples).items():
        comp = value/nsamples
        exp = transit.carpool_stats[key]
        if not ut.float_equality(comp, exp, tol):
            return False
    return True

def check_loading_public_routes(transit, fname):
    ''' Just compare with the original file '''

    with open(fname, 'r') as fin:
        for line in fin:
            temp = line.strip().split()
            if not (temp[1] in transit.transit_routes):
                return False 
            for zp in temp[2].split(','):
                if not (zp in transit.transit_routes[temp[1]][0]):
                    return False
            if transit.transit_routes[temp[1]][1] != 0:
                return False
    return True

def creating_carpool_objects(transit):
    ''' Tests for correct generation of carpool objects '''

    tol = 1e-5

    cp1 = [1, 'outside', 30.0, 11101]
    cp2 = [1, 'outside', 30.0, 11101]
    cp3 = [2, 'here', 10.0, 0]
    
    transit.create_carpools(cp1[0], cp1[1], cp1[2], cp1[3])
    transit.create_carpools(cp2[0], cp2[1], cp2[2], cp2[3])
    transit.create_carpools(cp3[0], cp3[1], cp3[2], cp3[3])

    carpools = transit.carpools
    if len(carpools) != 2:
        print('Too many carpools created')
        return False

    if (int(carpools[0].ID) != int(cp1[0])) or (int(carpools[1].ID) != int(cp3[0])):
        print('Carpool object has a wrong ID')
        return False

    if (carpools[0].work_type != 'outside') or  (carpools[1].work_type != 'here'):
        print('Carpool object has a wrong type')
        return False

    if (not(ut.float_equality(carpools[0].travel_time, cp1[2], tol))) or (not(ut.float_equality(carpools[1].travel_time, cp3[2], tol))):
        print('Carpool object has a wrong travel to work time')
        return False

    if (carpools[0].work_destination != cp1[3]) or  (carpools[1].work_destination != 0):
        print('Carpool object has a wrong work destination label')
        return False

    return True

def creating_public_transit_objects(transit):
    ''' Tests for correct generation of public transit objects '''

    tol = 1e-5

    cp1 = [1, 'outside', 30.0, '11581']
    cp2 = [1, 'outside', 30.0, '11581']
    cp3 = [2, 'here', 10.0, 'NR']
    
    transit.create_public_transit(cp1[1], cp1[2], cp1[3])
    transit.create_public_transit(cp2[1], cp2[2], cp2[3])
    transit.create_public_transit(cp3[1], cp3[2], cp3[3])

    public_transit = transit.GSP
    if len(public_transit) != 2:
        print('Too many busses created')
        return False

    if (int(public_transit[0].ID) != int(cp1[0])) or (int(public_transit[1].ID) != int(cp3[0])):
        print('Ikarbus object has a wrong ID')
        return False

    if (public_transit[0].work_type != 'outside') or  (public_transit[1].work_type != 'here'):
        print('Trola object has a wrong type')
        return False

    if (not(ut.float_equality(public_transit[0].travel_time, cp1[2], tol))) or (not(ut.float_equality(public_transit[1].travel_time, cp3[2], tol))):
        print('Trojka object has a wrong travel to work time')
        return False

    if (public_transit[0].work_destination != cp1[3]) or  (public_transit[1].work_destination != cp3[3]):
        print('Tramvaj object has a wrong work destination label')
        return False

    return True

def saving_carpool_objects(transit, fname):
    ''' Tests saving carpools to file '''

    tol = 1e-5

    cp1 = [1, 'outside', 30.0, 11000]
    cp2 = [1, 'outside', 30.0, 11000]
    cp3 = [2, 'here', 10.0, 0]
    
    transit.create_carpools(cp1[0], cp1[1], cp1[2], cp1[3])
    transit.create_carpools(cp2[0], cp2[1], cp2[2], cp2[3])
    transit.create_carpools(cp3[0], cp3[1], cp3[2], cp3[3])

    transit.print_carpools(fname)
    carpools = transit.carpools

    n_count = 0
    with open(fname, 'r') as fin:
        for line in fin:
            n_count += 1
            line = line.strip().split()
            if int(line[0]) != carpools[n_count-1].ID:
                print('Carpool saved with a wrong ID')
                return False
            if line[1] != carpools[n_count-1].work_type:
                print('Carpool saved with a wrong work type')
                return False
            if not math.isclose(float(line[2]), carpools[n_count-1].travel_time):
                print('Carpool saved with wrong travel time')
                return False
            if not math.isclose(float(line[3]), carpools[n_count-1].work_destination):
                print('Carpool saved with wrong work destination')      
                return False
    
    if n_count != len(carpools):
        print('Saved wrong number of carpools')
        return False

    return True

def saving_public_transit_objects(transit, fname):
    ''' Tests saving public transit to file '''

    tol = 1e-5

    cp1 = [1, 'outside', 30.0, '6830']
    cp2 = [1, 'outside', 30.0, '6830']
    cp3 = [2, 'here', 10.0, 'NR']
    
    transit.create_public_transit(cp1[1], cp1[2], cp1[3])
    transit.create_public_transit(cp2[1], cp2[2], cp2[3])
    transit.create_public_transit(cp3[1], cp3[2], cp3[3])

    transit.print_public_transit(fname)

    public_transit = transit.GSP
    n_count = 0
    with open(fname, 'r') as fin:
        for line in fin:
            n_count += 1
            line = line.strip().split()
            if int(line[0]) != public_transit[n_count-1].ID:
                print('Public transit saved with a wrong ID')
                return False
            if line[1] != public_transit[n_count-1].work_type:
                print('Public transit saved with a wrong work type')
                return False
            if not math.isclose(float(line[2]), public_transit[n_count-1].travel_time):
                print('Public transit saved with wrong travel time')
                return False
            if not (line[3] == public_transit[n_count-1].work_destination):
                print('Public transit saved with wrong work destination')       
                return False
    
    if n_count != len(public_transit):
        print('Saved wrong number of public transit objects')
        return False

    return True

#
# Tests
#

# Input files
ftimes = '../../town_data/NewRochelle/census_data/travel_time_to_work.txt'
fmodes = '../../town_data/NewRochelle/census_data/transit_mode.txt'
fcpools = '../../town_data/NewRochelle/census_data/carpool_stats.txt'
fpt_routes = '../../town_data/NewRochelle/database/public_transit_routes.txt'
cp_fpt_routes = 'test_data/public_transit_routes_copy.txt'

# Output files
cp_fout = 'test_data/carpools.txt'
pt_fout = 'test_data/public_transit.txt'

for file_rm in [cp_fout, pt_fout]:
    if os.path.exists(file_rm):
        os.remove(file_rm)

# Speed of each travel mode used to compute distance
mode_speed = {'car': 30, 'carpool': 30, 'public': 20, 
                    'walk': 2, 'other': 3, 'wfh': 0}
t_wfh = 5.0
t_walk = 12.0

# Transit class
transit = travel.Transit(ftimes, fmodes, fcpools, fpt_routes, mode_speed, t_wfh, t_walk)

ut.test_pass(check_loading_times(transit, ftimes), 'Loading travel times')
ut.test_pass(check_loading_modes(transit, fmodes), 'Loading travel modes')
ut.test_pass(check_loading_cpool(transit, fcpools), 'Loading carpool statistics')
ut.test_pass(check_loading_public_routes(transit, cp_fpt_routes), 'Loading public transit routes')

ut.test_pass(check_times_sampling(transit), 'Sampling times')
ut.test_pass(check_modes_sampling(transit), 'Sampling modes')
ut.test_pass(check_carpool_sampling(transit), 'Sampling carpool counts')

# Carpools and public transit
ut.test_pass(creating_carpool_objects(transit), 'Carpool objects')
ut.test_pass(creating_public_transit_objects(transit), 'Ikarbus objects')

# Savingng to file
ut.test_pass(saving_carpool_objects(transit, cp_fout), 'Saving carpool objects')
ut.test_pass(saving_public_transit_objects(transit, pt_fout), 'Saving Lasta objects')
