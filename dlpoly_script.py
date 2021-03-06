# Script to launch DL_POLY runs with changing temperature and simulation time.
# 
# Anastasia Gulenko anastasiya.gulenko@gmail.com

import shlex, subprocess, shutil, os, sys, fileinput

# sys.path.append('/home/anastasia/MDanalysis')


# Set the number of steps in cycle

cycle_name = raw_input('Input the name for MD cycle:\n')
N = int(raw_input('Input the number of steps in the cycle:\n'))

# Set the temperature and simulation time for each step

params = [[0, 0] for i in range(N)] # dictionary for temperature:steps pair
print 'Input temperature and number of steps for each MD run in "T S" format'

i = 0
while i < N:
	data = raw_input()
	datain = data.split()
	key = datain[0] # Temepature is a key
	value = int(datain[1]) # Number of steps is a value
	params[i][0] = key
	params[i][1] = value
	i += 1

# Launch DL_POLY

command_line = raw_input('Input the command to launch DL_POLY:\n')
args = shlex.split(command_line)
args1 = shlex.split('python /home/anastasia/MDanalysis/totalrdf_from_RDFDAT.py')
args2 = shlex.split('python /home/anastasia/MDanalysis/revcon_analysis.py')
path_work = os.getcwd() + '/'
j = 0
T = params[0][0]
t = params[0][1]
newline = 'temperature	{0:.3f}\n'.format(float(T))
newline2 = 'steps  {0:10d}\n'.format(t)
lnum = 1
for line in fileinput.FileInput("CONTROL",inplace=1):
	if lnum == 3:
		result = newline
	elif lnum == 7:
		result = newline2
	else:
		result = line
	lnum += 1
	sys.stdout.write(result)

while j < N: 
	process = subprocess.call(args)

	# Analysis of REVCON and RDFDAT files

	process1 = subprocess.call(args1)
	process2 = subprocess.call(args2)
		
	# Move output files to other directory

	path_dst = '/home/anastasia/MD_data/{}/{}{}'.format(cycle_name, params[j][0], 'K/')
	os.makedirs(path_dst)
	output_files = os.listdir(path_work)
	for file_name in output_files:
		full_file_name = os.path.join(path_work, file_name)
		if file_name == 'dlpoly_script.py':
			pass
		elif (os.path.isfile(full_file_name)):
			shutil.move(full_file_name, path_dst)


	# Archive HISTORY file

	archive_name = path_dst + 'HISTORY'
	root_dir = path_dst
	shutil.make_archive(archive_name, 'bztar', root_dir)
	os.remove(archive_name)

	# Copy CONTROL, FIELD, REVCON files in working directory

	path_CONT = path_dst + 'CONTROL'
	path_FIEL = path_dst + 'FIELD'
	path_REVC = path_dst + 'REVCON'
	path_REVC_w = path_work + 'REVCON'
	path_CONF = path_work + 'CONFIG'
	shutil.copy(path_CONT, path_work)
	shutil.copy(path_FIEL, path_work)
	shutil.copy(path_REVC, path_work)

	# Rename REVCON to CONFIG

	shutil.move(path_REVC_w, path_CONF)

	# Change TEMPERATURE and TIME in CONTROL
	if j + 1 < N:
		T = params[j + 1][0]
		t = params[j + 1][1]
		newline = 'temperature	{0:.3f}\n'.format(float(T))
		newline2 = 'steps  {0:10d}\n'.format(t)
		lnum = 1
		for line in fileinput.FileInput("CONTROL",inplace=1):
			if lnum == 3:
				result = newline
			elif lnum == 7:
				result = newline2
			else:
				result = line
			lnum += 1
			sys.stdout.write(result)
	else:
		break
	j += 1
