import re

atomtyp = ['Te', 'O']
cell = [[0, 0, 0] for i in range(3)]
l = 6 # unit cell multiplication (a)
m = 6 # unit cell multiplication (b)
n = 4 # unit cell multiplication (c)
a = b = c = 0 # unit cell parameters
A = B = C = 0 # MD box parameters
rcut = 3.0 # cutoff radius for bond valence
R0 = 1.977
bbb = 0.37
maxangle = 180
step = 0.5
nbbin = int(maxangle / step)

anglete = nbbin * [0] # distribution of angles O-Te-O
angleox = nbbin * [0] # distribution of angles Te-O-Te

maxval = 6.0
valstep = 0.1
valbin = int(maxval / valstep)

valencete = valbin * [0] # distribution of Te valence
valenceox = valbin * [0] # distribution of O valence

p = re.compile('\S')
numat = 0 # list for counting number of atoms
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

from math import sqrt, exp, fsum, hypot, acos, degrees

#
# defining functions
#

from coord_new import count, extract


def vec(i, j):
	"""Calculates reduced vector between 2 atoms with pbc.

	i, j - indexes for atoms in a list of reduced coordinates.
	"""
	dxxx = redxxx[i] - redxxx[j]
	dyyy = redyyy[i] - redyyy[j]
	dzzz = redzzz[i] - redzzz[j]
	dxpbc = [dxxx, dxxx + 1, dxxx - 1]
	dxmod = [abs(dxxx), abs(dxxx + 1), abs(dxxx - 1)]
	# print 'dxpbc=', dxpbc
	xmin = min(dxmod[0], dxmod[1], dxmod[2])
	lx = dxmod.index(xmin)
	dx = dxpbc[lx]
	dypbc = [dyyy, dyyy + 1, dyyy - 1]
	dymod = [abs(dyyy), abs(dyyy + 1), abs(dyyy - 1)]
	# print 'dypbc=', dypbc
	ymin = min(dymod[0], dymod[1], dymod[2])
	ly = dymod.index(ymin)
	dy = dypbc[ly]
	dzpbc = [dzzz, dzzz + 1, dzzz - 1]
	dzmod = [abs(dzzz), abs(dzzz + 1), abs(dzzz - 1)]
	# print 'dzpbc=', dzpbc
	zmin = min(dzmod[0], dzmod[1], dzmod[2])
	lz = dzmod.index(zmin)
	dz = dzpbc[lz]
	r = [dx, dy, dz]
	# print r
	return r

def modr(r):
	"""Calculates modulus of reduced vector.

	r = from function vec.
	"""
	
	rrr = abs(sqrt(r[0] ** 2
	+ r[1] ** 2	+ (r[2] * ccc) ** 2))
	return rrr

def mod(r):
	"""Calculates modulus of vector.

	r = from function vec.
	"""
	
	rrr = abs(sqrt((r[0] * A) ** 2
	+ (r[1] * B) ** 2
	+ (r[2] * C) ** 2))
	# print rrr
	return rrr
	

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
A = cell[0][0]
B = cell[1][1]
C = cell[2][2]
a = A / l
b = B / m
c = C / n
ccc = A / B

revcon.close()

# counting the number of usful atoms

numte = count(0)
numox = count(1)
numall = numte + numox

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
# reducing coordinates (box with an origin at (A/2, B/2, C/2))
#

redxxx = len(xxxall) * [0]
redyyy = len(xxxall) * [0]
redzzz = len(xxxall) * [0]

for i in range(len(xxxall)):
	redxxx[i] = (xxxall[i] + A / 2) / A
	redyyy[i] = (yyyall[i] + B / 2) / B
	redzzz[i] = (zzzall[i] + C / 2) / C

#
# looping over Te atoms
#

k = 0
coordnbte = numte * [0] # list of coordination number for Te
valte = numte * [0] # list of valencies for Te
while k < numte:
	nbneigh = 0
	vte = 0 # valence for each Te
	l = numte
	neighlist = numox * [0] # list of neighbours of Te
	dist = numox * [0]
	while l < len(xxxall):
		r = vec(l, k)
		dr = mod(r)
		if dr < rcut:
			# print 'r=', dr
			neighlist[nbneigh] = l
			dist[nbneigh] = dr # list of distances for neighbours
			vte += exp((R0 - dr) / bbb) # calcutating valence
			# print 'v=', vte
			# print neighlist
			# print dist
			nbneigh += 1
		l += 1		
	n = 0
	while n < nbneigh:
		p = n + 1
		while p < nbneigh:
			r1 = vec(neighlist[n], k)
			rrr1 = mod(r1)
			r2 = vec(neighlist[p], k)
			rrr2 = mod(r2)
			# calculating cosine of O-Te-O angle
			cosin = (r1[0] * r2[0] * A ** 2 + r1[1] * r2[1] * B ** 2 +
			 r1[2] * r2[2] * C ** 2) / (rrr1 * rrr2)
			# calculating O-Te-O angle
			alpha = degrees(acos(cosin))
			anglete[int(alpha / step)] += 1 # angle distribution
			p += 1
		n += 1
	coordnbte[k] = nbneigh
	valte[k] = vte
	# print valte
	# print int(vte / valstep), len(valencete)
	valencete[int(vte / valstep)] += 1	#valence distribution
	
	k += 1

#
# looping over O atoms
#

k = numte
coordnbox = numall * [0] # list of coordination number for Te
valox = numall * [0] # list of valencies for Te
while k < len(xxxall):
	nbneigh = 0
	vox = 0 # valence for each Te
	l = 0
	neighlist = numte * [0] # list of neighbours of Te
	dist = numte * [0]
	while l < numte:
		r = vec(l, k)
		dr = mod(r)
		if dr < rcut:
			neighlist[nbneigh] = l
			dist[nbneigh] = dr # list of distances for neighbours
			vox += exp((R0 - dr) / bbb) # calcutating valence
			nbneigh += 1
		l += 1		
	n = 0
	while n < nbneigh:
		p = n + 1
		while p < nbneigh:
			r1 = vec(neighlist[n], k)
			rrr1 = mod(r1)
			r2 = vec(neighlist[p], k)
			rrr2 = mod(r2)
			# calculating cosine of Te-O-Te angle
			cosin = (r1[0] * r2[0] * A ** 2 + r1[1] * r2[1] * B ** 2 +
			 r1[2] * r2[2] * C ** 2) / (rrr1 * rrr2)
			# calculating Te-O-Te angle
			alpha = degrees(acos(cosin))
			angleox[int(alpha / step)] += 1 # angle distribution
			p += 1
		n += 1
	coordnbox[k] = nbneigh
	valox[k] = vox
	valenceox[int(vox / valstep)] += 1	#valence distribution
	k += 1




output = open('bondval', 'w')
output.write('Bond valence distribution for Te:\n')
for i in range(valbin):
	output.write('%11f%8d\n' % (i * valstep, valencete[i]))
output.write('\n')
output.write('Bond valence distribution for O:\n')
for i in range(valbin):
	output.write('%11f%8d\n' % (i * valstep, valenceox[i]))
output.write('\n')
output.close()
output = open('angles', 'w')
output.write('O-Te-O angle distribution:\n')
for i in range(nbbin):
	output.write('%11f%8d\n' % (i * step, anglete[i]))
output.write('\n')
output.write('Te-O-Te angle distribution:\n')
for i in range(nbbin):
	output.write('%11f%8d\n' % (i * step, angleox[i]))
output.write('\n')
output.close()
