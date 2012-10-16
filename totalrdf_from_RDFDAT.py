# This is a program to calculate total RDF from partial RDFs,
# that are obtained with molecular dynamics softwear DL_POLY
# and written in RDFDAT file.
#
# Anastasia Gulenko 06/2012 anastasia.gulenko@unilim.fr
#

import re

atomtyp = ['Te', 'O']
nbpair = len(atomtyp)*(len(atomtyp)+1)/2 # number of the possible pairs
rdfdata = [] 
p = re.compile('\S') # compilation the rule for matching
value = 0
nstr = 0
npair = 0
np = 0
pairname = []
r = []
fav = 0
cat = len(atomtyp)*[0.0] # concentration of atoms
fat = len(atomtyp)*[0.0] # atom diffusion factor (neutron scattaring factor)
#constants
cat[0] = 1./3.
cat[1] = 2./3.
fat[0] = 0.58 # neutron scattaring factor
fat[1] = 0.58 # neutron scattaring factor
cell = [[0, 0, 0] for i in range(3)]
pi = 3.1415926535897932
Qbin = 0.02 # Bin value for wave vector
Qnb = int((18 / Qbin)) # array size for wave vector

from coord_new import count
from math import sin
#
# consideration of doubling of data for atom pairs with i != j
#

def coeff(n, m): 
	"""Defines the coefficient for partial pdf for atom pair.
	
	n, m - indexes of the atoms.
	"""
	c = 0
	if n != m:
		c = 2
	else:
		c = 1
	return c

rdfdat = open('RDFDAT', 'r')
# try to know how many lines of data I have for each pair in general case
def countr(i, j):
	"""Counts the lines of the useful data.
	
	i, j = 0, len(atomtyp) - indexes of atoms.
	"""
	while rdfdat:
		lname = rdfdat.readline()
		if len(lname) == 0:
			break
		data = lname.split()
		if data == [atomtyp[i], atomtyp[j]]:
			global nstr
			while rdfdat:
				lname = rdfdat.readline()
				data = lname.split()					
				m = p.match(lname)
				if m:
					break
				nstr += 1
	return nstr

countr(0, 0)
rdfdat.close()			
print 'Number of RDF points is ', nstr
r = [0 for i in range(nstr)]

#
# Extracting the values of r from the first partial pdf
#

rdfdat = open('RDFDAT', 'r')
while rdfdat:
	lname = rdfdat.readline()
	if len(lname) == 0:
		break
	data = lname.split()
	if data == [atomtyp[0], atomtyp[0]]:
		value = 0
		while rdfdat:
			try:
				lname = rdfdat.readline()
				data = lname.split()
				r[value] += float(data[0])
			except:
				break
			value += 1				
rdfdat.close()

rdfdata = [[0 for row in range(nbpair)] for col in range(nstr)]
pairname = [0 for i in range(nbpair)]


#
# Extracting the data from the file
#

i = 0
while i < len(atomtyp):	# looping for different atom types
	j = i 	
	while j < len(atomtyp):
		rdfdat = open('RDFDAT', 'r')
		rdfdat.readline() # skip 2 first lines
		rdfdat.readline()							
		while rdfdat:			
			lname = rdfdat.readline()
			if len(lname) == 0:	# break when file ends
				break
			data = lname.split()
			if data == [atomtyp[i], atomtyp[j]]: # looking for right atom pairs
				a = atomtyp[i]
				b = atomtyp[j]
				pairname[npair] = a + '-' + b
				value = 0
				while rdfdat: # extracting useful rdf data
					try:
						lname = rdfdat.readline()
						data = lname.split()
						rdfdata[value][npair] += float(data[1])
					except:
						break
					value += 1					
		j +=1
		npair += 1
		rdfdat.close()
	i +=1


#	
# Calculating total RDF
#

j = 0
while j < len(atomtyp):
    fav += cat[j] * fat[j]
    j += 1
fav = fav * fav # average neutron scattaring factor

totalrdf = nstr * [0.0]

while np < nstr:
    i=0
    j=0
    ip=0
    while i < len(atomtyp):
        j=i
        while j < len(atomtyp):
            totalrdf[np] += coeff(i, j) * (cat[i] * cat[j] * fat[i] * fat[j] / fav) * rdfdata[np][ip]
            ip += 1
            j += 1
        i += 1
    np += 1
	

#
# Calculating g(r)=4*pi*pho*(G(r)-1)
#

# counting the number of usful atoms

numte = count(0)
numox = count(1)
numall = numte + numox

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
ccc = A / B

revcon.close()

# calculating density rho (atoms/angstom^3)

rho = numall / (A * B * C)

# Reduced RDF

g = nstr * [0.0] # reduced RDF
np = 0
while np < nstr:
	g[np] += 4 * pi * rho * r[np] * (totalrdf[np] - 1)
	np += 1

#
# Calculating the stucture factor
#

S = Qnb * [0.0] # stucture factor
Q = 0
dr = r[1] - r[0]
while Q < Qnb:
	i = 0
	while i < nstr:
		S[Q] += g[i] * dr * sin((Q * Qbin) * r[i])
		#print S[Q]
		i += 1
	Q += 1

#
# Writing RDF into the file	
#

output = open('total_RDF.txt', 'w')	
output.write('%10s%10s%10s%10s%10s\n' % ('r', pairname[0], pairname[1], pairname[2], 'total'))
for i in range(len(r)):
	output.write('%10f%10f%10f%10f%10f\n' % (r[i], rdfdata[i][0], rdfdata[i][1], rdfdata[i][2], totalrdf[i]))
output.write('\n')
output.close()
output = open('Reduced_RDF.txt', 'w')
output.write('\n')
output.write('%10s%10s\n' % ('r', 'g(r)'))
for i in range(len(r)):
	output.write('%10f%10f\n' % (r[i], g[i]))
output.write('\n')
output.close()
output = open('Sructure factor.txt', 'w')
output.write('\n')
output.write('%10s%10s\n' % ('Q', 'S(Q)'))
for i in range(Qnb):
	output.write('%10f%10f\n' % (i * Qbin, S[i]))
output.write('\n')

output.close()

if __name__ == "__main__":
    import sys
