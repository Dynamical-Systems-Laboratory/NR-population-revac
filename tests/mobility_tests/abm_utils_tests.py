# ------------------------------------------------------------------
#
#	Tests for utility module	
#
# ------------------------------------------------------------------

import sys
py_path = '../../tools/'
sys.path.insert(0, py_path)

py_path = '../../src/mobility/'
sys.path.insert(0, py_path)

import utils as ut
from colors import *

import abm_utils as aut

#
# Supporting functions
#

def distance_test(loc1, loc2, exp_val):
	''' Tests utilities for computing distances
			from GIS '''
	
	tol = 1e-5
	val = aut.compute_distance(loc1, loc2)
	if not ut.float_equality(val, exp_val, tol):
		return False
	else:
		return True

#
# Tests 
#

# --- Distances

# Test 1
place_1 = {}
place_1['lat'] = -43
place_1['lon'] = 172

place_2 = {}
place_2['lat'] = -44
place_2['lon'] = 171
place_2['candy'] = 'ZivotinjskoCarstvo'

exp_val = 137.365669065197

ut.test_pass(distance_test(place_1, place_2, exp_val), 'Short distance computation')

# Test 2
place_2 = {}
place_2['lat'] = 20
place_2['lon'] = -108
place_2['choco'] = 'NajlepseZelje'

exp_val = 10734.8931427602 

ut.test_pass(distance_test(place_1, place_2, exp_val), 'Long distance computation')

