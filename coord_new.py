import re

atomtyp = ['Te', 'O']
cell = [[0, 0, 0] for i in range(3)]
# print 'Input unit cell multiplication (a):'
# l = int(raw_input()) # unit cell multiplication (a)
# print 'Input unit cell multiplication (b):'
# m = int(raw_input()) # unit cell multiplication (b)
# print 'Input unit cell multiplication (c):'
# n = int(raw_input()) # unit cell multiplication (c)
p = re.compile('\S')
numat = [] # list for counting number of atoms
xxx = [] # list of exctracted coordinates x
yyy = [] # list of exctracted coordinates y
zzz = [] # list of exctracted coordinates z
vvx = [] # list of exctracted velocities Vx
vvy = [] # list of exctracted velocities Vy
vvz = [] # list of exctracted velocities Vz
ffx = [] # list of exctracted forces Fx
ffy = [] # list of exctracted forces Fy
ffz = [] # list of exctracted forces Fz
redxxx = [] # list of the reduced coordinates x
redyyy = [] # list of the reduced coordinates y
redzzz = [] # list of the reduced coordinates z


#
# defining functions
#

def count(i):
	""" Count the number of usful atooms in the file.
	
	i - atom index in atomtyp list.
	"""
	numat = 0
	revcon = open('REVCON', 'r')
	while revcon:
		lname = revcon.readline()
		if len(lname) == 0:
			break
		data = lname.split()
		if data[0] == atomtyp[i]:
			numat += 1
	revcon.close()
	return numat


def extract(n, i):
	"""Extracting coordinates, velocities and forces.
	
	n = numte for Te, numox for O.
	i - index for atom. 0 for Te, 1 for O.
	"""
	global coord, vel, force
	xxx = [0] * n
	yyy = [0] * n
	zzz = [0] * n
	vvx = [0] * n
	vvy = [0] * n
	vvz = [0] * n
	ffx = [0] * n
	ffy = [0] * n
	ffz = [0] * n
	revcon = open('REVCON', 'r')
	k = 0
	while revcon:
		lname = revcon.readline()
		if len(lname) == 0:
			break
		data = lname.split()
		if data[0] == atomtyp[i]:
			rline = revcon.readline()
			rrr = rline.split()
			xxx[k] = float(rrr[0]) 
			yyy[k] = float(rrr[1])
			zzz[k] = float(rrr[2])
			vline = revcon.readline()
			vvv = vline.split()
			vvx[k] = float(vvv[0])
			vvy[k] = float(vvv[1])
			vvz[k] = float(vvv[2])
			fline = revcon.readline()
			fff = fline.split()
			ffx[k] = float(fff[0])
			ffy[k] = float(fff[1])
			ffz[k] = float(fff[2])		
			k += 1
	revcon.close()
	coord = [xxx, yyy, zzz]	
	return coord


#
#  reading cell parameters
#
	
revcon = open('REVCON', 'r')
revcon.readline()
revcon.readline()
i = 0
while i < 3:
	try:
		lname = revcon.readline()
		data = lname.split()
		j = 0
		while j < len(data):			
			cell[j][i] += float(data[j])
			j += 1	
	except:
		break
	i += 1
	
# unit cell parameters
	
# a = cell[0][0] / l
# b = cell[1][1] / m
# c = cell[2][2] / n
# ccc = cell[2][2] / cell[0][0]

revcon.close()

# counting the number of usful atoms

numte = count(0)
numox = count(1)

#
# extracting coordinates
#

coordte = extract(numte, 0)
coordox = extract(numox, 1)

xxxte = coordte[0]
yyyte = coordte[1]
zzzte = coordte[2]
xxxox = coordox[0]
yyyox = coordox[1]
zzzox = coordox[2]

xxxall = xxxte + xxxox
yyyall = yyyte + yyyox
zzzall = zzzte + zzzox

#
# reducing coordinates (box with an origin at (a*l/2, b*m/2, c*n/2))
#

redxxx = len(xxxall) * [0]
redyyy = len(xxxall) * [0]
redzzz = len(xxxall) * [0]

for i in range(len(xxxall)):
	redxxx[i] = (xxxall[i]) / (cell[0][0] / 2)
	redyyy[i] = (yyyall[i]) / (cell[1][1] / 2)
	redzzz[i] = (zzzall[i]) / (cell[2][2] / 2)

#
# writing out data in a file
#

output = open('input.cfg', 'w')
output.write(' (Version 3 format configuration file)\
 file created by coord.py from DL_POLY REVCON output file\n')
output.write(' TeO2 glass network\n')
output.write('\n')
output.write('\n')
output.write(' %10d%10d%10d%35s\n' % (0, 0, 0, 'moves generated, tried,\
 accepted'))
output.write(' %10d%45s\n' % (0, 'configurations saved'))
output.write('\n')
output.write(' %10d%45s\n' % (numte + numox, 'molecules of all types'))
output.write(' %10d%45s\n' % (len(atomtyp), 'types of molecules'))
output.write(' %10d%45s\n' % (1, 'is the largest number of atoms in a molecule'))
output.write(' %10d%45s\n' % (0, 'Euler angles are provided '))
output.write('\n')
output.write('%35s\n' % ('F Box is parallelepiped'))
output.write('%35s\n' % 'Defining vectors are:')
for i in range(len(cell[0])):
	output.write('%11s%11f%11f%11f\n' % (' ', cell[0][i] / 2, cell[1][i] / 2, cell[2][i] / 2))
output.write('\n')
output.write(' %10d%45s\n' % (numte, 'molecules of type  1'))
output.write(' %10d%45s\n' % (1, 'atomic sites '))
output.write(' %10f%10f%10f\n' % (0, 0, 0))
output.write('\n')
output.write(' %10d%45s\n' % (numox, 'molecules of type  2'))
output.write(' %10d%45s\n' % (1, 'atomic sites '))
output.write(' %10f%10f%10f\n' % (0, 0, 0))
output.write('\n')
for i in range(len(redxxx)):
	output.write('%11f%11f%11f\n' % (redxxx[i], redyyy[i], redzzz[i]))
output.write('\n')
output.close()
