# Script to launch DL_POLY runs with changing temperature and simulation time.
# 
# Anastasia Gulenko anastasiya.gulenko@gmail.com

import shlex, subprocess, shutil, os

# Launch DL_POLY

command_line = raw_input('Input the command to launch DL_POLY:\n')
args = shlex.split(command_line)
process = subprocess.Popen(args)

# Move output files to other directory

path_work = ''
path_dst = '' + str(T) + 'K/'
path_dst = "{}{}".format(T, 'K/')
os.makedirs(path_dst)
shutil.move(path_work, path_dst)

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



