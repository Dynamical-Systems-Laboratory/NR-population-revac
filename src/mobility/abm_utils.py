# ------------------------------------------------------------------
#
#	Utility module for generating the ABM population
#
# ------------------------------------------------------------------

import math

def compute_distance(loc1, loc2):
	''' Calculates the distance between loc1 and loc2 in km.

			loc1, loc2 - dictionary objects of any kind with 
				GIS defined, both dictionaries need to have 
				a 'lat' and 'lon' property.

			Returns distance in km according to Haversine formula,
			
			http://en.wikipedia.org/wiki/Haversine_formula

	'''

	latlon1 = [loc1['lat'], loc1['lon']]
	latlon2 = [loc2['lat'], loc2['lon']]
	
	radius=6371

	lat1=latlon1[0]*math.pi/180
	lat2=latlon2[0]*math.pi/180
	lon1=latlon1[1]*math.pi/180
	lon2=latlon2[1]*math.pi/180
	
	deltaLat=lat2-lat1
	deltaLon=lon2-lon1

	a=math.sin((deltaLat)/2)**2 + math.cos(lat1)*math.cos(lat2) * math.sin(deltaLon/2)**2
	c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
	d1km=radius*c

	return d1km    

