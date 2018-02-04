# Peyton Turner
# EECS 325 Project 2
# A script for loading a list of addresses stored in a file "targets.txt" and computing the geographical distance to their hosts

import geoip2.database
import socket
from urllib.request import urlopen
from math import radians, cos, sin, asin, sqrt

# A function for computing the shortest distance across the surface of the earth from one latitude/longitude pair to another
def distance(lat_1, lon_1, lat_2, lon_2):

    lon_1, lat_1, lon_2, lat_2 = map(radians, [lon_1, lat_1, lon_2, lat_2])

    lon_dist = lon_2 - lon_1 
    lat_dist = lat_2 - lat_1 
    earth_rad = 6371

    # The Haversine Formula, see https://en.wikipedia.org/wiki/Haversine_formula
    return 2 * earth_rad * asin(sqrt(sin(lat_dist/2) ** 2 + cos(lat_1) * cos(lat_2) * sin(lon_dist/2) ** 2))

if __name__ == "__main__":

	# Open the targets file and prepare the list of addresses to be measured
	with open(file = 'targets.txt') as file: 
		targets = file.read().splitlines()
		num_targets = len(targets)
		addresses = [(x, socket.gethostbyname(x)) for x in targets]

	# Use AWS to find the IP of the machine the script is running on
	link = "http://checkip.amazonaws.com"
	aws_page = urlopen(link)
	local_ip = str(aws_page.read())[2:-3]

	# Create a goeip2 reader to query information from
	reader = geoip2.database.Reader('GeoLite2-City.mmdb')

	# Obtain the latitude and longitude of the local machine
	response = reader.city(local_ip)
	local_lat = response.location.latitude
	local_lon = response.location.longitude

	# Print the local latitude and longitude
	print("Local location: Latitude: " + str(local_lat) + ", Longitude: " + str(local_lon))

	# Results are written to geo_results.txt
	with open('geo_results.txt', 'w') as output:
		for address, ip in addresses:

			# Get the latitude and longitude of the address, use it to compute the distance to the local machine
			response = reader.city(ip)
			lat = response.location.latitude
			lon = response.location.longitude
			dist = distance(local_lat, local_lon, lat, lon)

			# Print the results
			print("Address: " + address + ", IP: " + ip + ", Latitude: " + str(lat) + ", Longitude: " + str(lon), ", Distance: " + str(dist) + " km")
			# And save them to a file
			output.write(address + "," + str(dist) + "\n")





