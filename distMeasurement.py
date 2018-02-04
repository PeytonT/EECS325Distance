# Peyton Turner
# EECS 325 Project 2
# A script for loading a list of addresses stored in a file "targets.txt" and for each of those targets computing the RTT, the number of hops
# between you and the destination, and the number of bytes of the original datagram included in the ICMP error message
# Might also optionally determine the physical distance from you to the target

import socket
import select
import struct
import time

if __name__ == "__main__":

	# ICMP packets should not be longer than 576 bytes
	max_length_of_expected_packet = 576
	# The first packet will be sent to port 50000, the port will be incremented after each packet
	dest_port = 50000
	# Create a payload from the provided message
	msg = 'measurement for class project. questions to student dpt14@case.edu or professor mxr136@case.edu'
	payload = bytes(msg + 'a'*(1472 - len(msg)),'ascii')

	# Turn the file of targets into a list of addresses to send packets to
	with open(file = 'targets.txt') as file: 
		targets = file.read().splitlines()
		num_targets = len(targets)
		addresses = [(x, socket.gethostbyname(x)) for x in targets]

	# Keys are the desination port of a packet, values are a tuple of the address and the time the packet was sent out
	port_table = {}

	# Create a raw socket to receive ICMP messages
	recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

	# I am making the (I think) reasonable assumption that I can send all packets before any ICMP packets get back to me
	for address, dest_ip in addresses:
		# Create a socket to send a packet
		send_sock = socket.socket(type = socket.SOCK_DGRAM)	
		# Set the time to live to some stupidly huge value (100) to ensure it arrives.
		send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, 100)
		# Send the payload to the desination IP on the destination port
		send_sock.sendto(payload, (dest_ip, dest_port))
		# Save the time the packet was sent
		start_time = time.time()
		# And add it to the table under the destination port
		port_table[dest_port] = (address, start_time)
		print("Sent packet to address " + address + " to port " + str(dest_port))
		# Increment the destination port so each address has a unique destination port
		dest_port += 1

	packet_list = []

	# Spend 2 seconds checking for incoming packets once each millisecond. Store arrived packets with their arrival time
	for i in range(2000):
		readable, writable, exceptional = select.select([recv_sock], [], [], 0.001)
		if len(readable) != 0:
			icmp_packet = recv_sock.recv(max_length_of_expected_packet)
			arrival_time = time.time()
			packet_list.append((icmp_packet, arrival_time))

	# Create a list to hold the results (hops, ttl, etc.)
	results_list = []

	# Go through the list of received packets. Find the destination port number of their UDP header and try to match it to an outgoing packet.
	# If there's a match, compute the number of hops and the RTT.
	for icmp_packet, arrival_time in packet_list:

		contents_length = len(icmp_packet) - 56 # 56 bytes worth of headers, remainder is from the sent packet

		# 20 bytes of IP header, 8 bytes of ICMP header, 20 bytes of IP header, 8 bytes of UDP header
		# We want the 8th byte of the second IP header
		ttl_from_packet = icmp_packet[28 + 8]

		# 20 bytes of IP header, 8 bytes of ICMP header, 20 bytes of IP header, 8 bytes of UDP header
		# We want the short stored in the 3d and 4th byte of the UDP header
		port_from_packet = struct.unpack("!H", icmp_packet[48 + 2:48 + 4])[0]

		# Let's just assume no port collisions since we're in the 50000+ range
		if port_from_packet in port_table:
			address, send_time = port_table[port_from_packet]
			results_list.append((address, 100 - ttl_from_packet, 1000 * (arrival_time - send_time), contents_length))

	# Display the results
	for result in results_list:
		print("Address: " + result[0] + 
			', Hops: ' + str(result[1]) + 
			", RTT: " + str(result[2]) + " ms" + 
			", Amount of Original Datagram: " + str(result[3]) + " bytes")

	# And save the results
	with open('dist_results', 'w') as output:
		for result in results_list:
			output.write("" + str(result)[1:-1] + "\n")