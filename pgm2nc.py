#!/usr/bin/python

import numpy as np
from netCDF4 import Dataset
import os
import errno
import gdal
import re

#setting
direktori = '/home/genomexyz/teswget'
resol = 0.05
startlon = 70.
endlon = 160.
startlat = -20.
endlat = 70.

#spasial, start from bottom left!!!
lat = np.arange(startlat+resol,endlat+resol/2,resol)
lon = np.arange(startlon+resol,endlon+resol/2,resol)

diriter = sorted(os.listdir(direktori))

#iter file
for i in xrange(0, len(diriter), 2):
	corfile = diriter[i]
	pgmfile = diriter[i+1]
	print corfile, pgmfile

	#read pgm
	ds = gdal.Open(pgmfile)
	irdat = np.array(ds.GetRasterBand(1).ReadAsArray())
	#matrix of correction table
	idx = 0
	cortable = np.zeros(256)
	with open(corfile,'r') as fid:	#read calibrate data
		for line in fid:
			if line:
				if not line.find('IR1 Temperature of'):
					val = re.findall("\d+\.\d+", line) #get val according to format
					cortable[idx] = val[0]
					idx += 1
	#flip matrix
	irdat = np.flipud(irdat)

	#create matrix of IR map
	IR = np.zeros((len(irdat), len(irdat[0])))

	for i in xrange(len(lat)):
		for j in xrange(len(lon)):
			IR[i,j] = cortable[irdat[i,j]]

	###############
	#create netcdf#
	###############

	dset = Dataset(pgmfile+'.nc', 'w', format = 'NETCDF4_CLASSIC')

	#create dimension
	latdim = dset.createDimension('lat', len(lat))
	londim = dset.createDimension('lon', len(lon))

	#create variable
	latvar = dset.createVariable('latitude', np.float32, ('lat',)) 
	lonvar = dset.createVariable('longitude', np.float32, ('lon',))
	irvar = dset.createVariable('IR', np.float32, ('lat','lon',))

	#fill variable
	latvar[:] = lat
	lonvar[:] = lon
	irvar[:] = IR
	
	#delete old file
#	os.remove(corfile)
#	os.remove(pgmfile)

	print irvar[:]
	print np.sum(irvar[:])
