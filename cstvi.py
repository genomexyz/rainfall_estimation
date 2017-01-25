#!/usr/bin/python

import math
import numpy
import imread
import re

def read_pgm(filename, byteorder='>'):
	"""Return image data from a raw PGM file as numpy array.

	Format specification: http://netpbm.sourceforge.net/doc/pgm.html

	"""
	with open(filename, 'rb') as f:
		buffer = f.read()
	try:
		header, width, height, maxval = re.search(
			b"(^P5\s(?:\s*#.*[\r\n])*"
			b"(\d+)\s(?:\s*#.*[\r\n])*"
			b"(\d+)\s(?:\s*#.*[\r\n])*"
			b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", buffer).groups()
	except AttributeError:
		raise ValueError("Not a raw PGM file: '%s'" % filename)
	return numpy.frombuffer(buffer,
							dtype='u1' if int(maxval) < 256 else byteorder+'u2',
							count=int(width)*int(height),
							offset=len(header)
							).reshape((int(height), int(width)))

#all of constant of CST method
a = -0.0492
b = 15.27
R_c = 20.0
R_s = 3.5
A = 202.12

#define location and all preparation of input for algorithm
#N70 - S20, E70 - E160 => area of pgm data
#resolution of our data is 0.05 degree, so luasan = 100 means the perimeter is 1 degree
X = 119.8
Y = -0.8
luasan = 100	#please edit this variable value if you not satisfied with its default value

#initialization of all container
data = numpy.ones(256)*-99.0;								#container of calibrate data
d = numpy.zeros((9), dtype = int)							#container of env temperature to calculate slope
temp = numpy.zeros((9), dtype = float)						#container of temp to calculate slope
hsl = numpy.zeros(((2 * luasan + 1)**2, 4), dtype = float)	#container of output


idx = 0

filepgm = "/home/genomexyz/dataset/HMW817011910IR1.pgm"
cor_pgm = "/home/genomexyz/dataset/HMW817011910CAL.dat"

irdat = read_pgm(filepgm) #read pgm data

with open(cor_pgm,'r') as fid:	#read calibrate data
	for line in fid:
		if line:
			if not line.find('IR1 Temperature of'):
				val = re.findall("\d+\.\d+", line)
				data [idx] = val [0]
				idx += 1
fid.close

pos_X = (X-70)*20
pos_Y = 1800-((Y+20)*20)
pospix_X = int(round(pos_X))
pospix_Y = int(round(pos_Y))

iterasi = 0
for hr in range (pospix_X-luasan-1, pospix_X+luasan):
	for vt in range (pospix_Y-luasan-1, pospix_Y+luasan):
		d[0] = irdat[vt][hr]
		d[1] = irdat[vt][hr-1]
		d[2] = irdat[vt][hr-2]
		d[3] = irdat[vt][hr+1]
		d[4] = irdat[vt][hr+2]
		d[5] = irdat[vt+1][hr]
		d[6] = irdat[vt+2][hr]
		d[7] = irdat[vt-1][hr]
		d[8] = irdat[vt-2][hr]

#translate the brightness of pgm data to temperature
		for hitung in range (9):
			idx       = d[hitung]
			temp[hitung] = data[idx]
			
#calculate the variability index -> 1/ N * sigma (xi - x0)
		VI_hitung = 0
		for hitung in range (1,9):
			VI_hitung += temp[hitung] - temp[0]
		VI = VI_hitung / 8.0
		VI_hitung = 0

#calculate area of precipitation
		Area = numpy.exp(a * temp[0] + b)

#categorize core -> convective or stratifoam...tipe=2 for convective and 1 for stratifoam
#=> c/s = number of convective/stratifoam cell in grid
#=> A_c/A_s = area of convective/stratifoam rain
#=> A = average area covered by each pixel
#=> T = length of period in hour (in this program, 1 hour)
#=> R_c/R_s = convective/stratifoam rain rate in mm/h
		if VI > 8.0: #it convective
			res = (Area / A) * R_c  #equation for convective c * ( A_c / A ) * T * R_c
			tipe = 2
		else: #it stratifoam
			res = (Area / A) * R_s  #equation for stratifoam s * ( A_s / A ) * T * R_s
			tipe = 1

		VI = 0
#define lon and lat
		lintang1 = (1800-vt)/20.0-20;
		bujur1 = (hr/20.0)+70;

		print res
		hsl[iterasi][0:6]= [lintang1, bujur1, tipe, res]
		iterasi += 1

#finishing act
print hsl
print len(hsl)
numpy.savetxt('ctmVI.txt', hsl)
