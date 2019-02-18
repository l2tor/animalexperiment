import subprocess
import shlex
import os

import signal
import sys
import getopt
import time

import webbrowser

# Conditions:
# 1 = random, no gestures
# 2 = random, gestures
# 3 = adaptive, no gestures
# 4 = adaptive, gestures

def main(argv):
	strategy = 'random'
	ip = '192.168.1.97'
	condition = 0
	gestures = 0

	# Create the log file directory if it doesn't exist yet.
	if not os.path.exists('interactionmanager/data'):
		os.makedirs('interactionmanager/data')

	if not os.path.exists('interactionmanager/data/vp'):
		os.makedirs('interactionmanager/data/vp')

	try:
		opts, args = getopt.getopt(argv,"hi:c:",["ip=","condition="])
	except getopt.GetoptError:
		print 'start.py -i <robot_ip> -c <condition>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'start.py -i <robot_ip> -c <condition>'
			sys.exit()
		elif opt in ("-i", "--ip"):
			ip = arg
		elif opt in ("-c", "--condition"):
			try:
				if int(arg) > 0 and int(arg) < 5:
					condition = int(arg)
			except ValueError:
				pass

	if condition == 0:
		print 'start.py -i <robot_ip> -c <condition>'
		sys.exit(2)

	if condition == 3 or condition == 4:
		strategy = 'adaptive'

	if condition == 2 or condition == 4:
		gestures = 1

	# Write robot IP to file
	f = open('robotip.js', 'w')
	f.write('ROBOT_IP = "' + ip + '";')
	f.close()

	# No need to change directory for our service as it doesn't need file system
	p1 = subprocess.Popen(shlex.split("python \"animalexperimentservice/app/scripts/myservice.py\" --qi-url " + ip))

	# Interaction manager, however, does!
	os.chdir('interactionmanager/src')
	p2 = subprocess.Popen(shlex.split("python interaction_manager.py --ip " + ip + " --port 9559 --sysip 127.0.0.1 --mode \"" + strategy + "\" --sgroups \"type\" --L1 \"German\" --L2 \"English\" --concepts \"../data/study_1/animals_concepts.csv\" --cbindings \"../data/study_1/animals_concept_bindings.csv\" --rnr=30 --gestures=" + str(gestures)))

	time.sleep(2)

	dir_path = os.path.dirname(os.path.realpath(__file__))
	webbrowser.get('C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open('file://' + dir_path + '/web/index.html')

	def signal_handler(signal, frame):
		print('Ctrl+C detected, stopping the services..')
		p1.kill()
		p2.kill()
		time.sleep(1)
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)
	print('Press Ctrl+C to stop experiment')

	loop = True

	while loop:
		time.sleep(1)
		loop = p1.poll() == None or p2.poll() == None

if __name__ == "__main__":
   main(sys.argv[1:])