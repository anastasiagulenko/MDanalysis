# Script to launch DL_POLY runs with changing temperature and simulation time.
# 
# Anastasia Gulenko anastasiya.gulenko@gmail.com

import shlex, subprocess, shutil, os, sys, fileinput

# Launch DL_POLY

command_line = raw_input('Input the command to launch DL_POLY:\n')
args = shlex.split(command_line)
process = subprocess.Popen(args)

# Move output files to other directory

path_work = os.path.abspath('dlpoly_script.py')
path_dst = '' + str(T) + 'K/'
path_dst = "{}{}".format(T, 'K/')
os.makedirs(path_dst)
output_files = os.listdir(path_work)
for file_name in output_files:
    full_file_name = os.path.join(path_work, file_name)
    if (os.path.isfile(full_file_name)):
        shutil.move(full_file_name, path_dst)


# Archive HISTORY file

archive_name = path_dst
root_dir = path_dst + 'HISTORY'
shutil.make_archive(archive_name, 'zip', root_dir)
os.remove(root_dir)

# Copy CONTROL, FIELD, REVCON files in working directory

path_CONT = path_dst + 'CONTROL'
path_FIEL = path_dst + 'FIELD'
path_REVC = path_dst + 'REVCON'
path_REVC_w = path_work + 'REVCON'
path_CONF = path_work + 'CONFIG'
shutil.copy(path_CONT, path_work)
shutil.copy(path_FIEL, path_work)
shutil.copy(path_REVC, path_work)

# Remane REVCON to CONFIG

shutil.copy(path_REVC_w, path_CONF)

# Change TEMPERATURE and TIME in CONTROL

newline = 'temperature	{0:.3f}\n'.format(T)
newline2 = 'steps  {0:10d}\n'.format(steps)
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

