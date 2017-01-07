#!/usr/bin/python

import math
import numpy
import imread
import re

#ye ye ye, i know...messy code and comment

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


#Modul untuk baca data Calibrasi


luasan=10

data = numpy.ones(256)*-99.0;			#definisikan var data sbg tempat penyimpanan data temperatur  

idx = 0

with open('HMW816112504CAL.dat','r') as fid:	#buka file Calibrasi untuk dibaca denga option read-only
	for line in fid:
		if line:							#string berisi booleannya adalah true, sedangkan kosong adalah false
			if not line.find('IR1 Temperature of'):
				val = re.findall("\d+\.\d+", line)
				data [idx] = val [0]
				idx += 1
fid.close

#Modul untuk baca data pgm

nama_file = 'HMW816112504IR1.pgm'			#nama file pgm
irdat = read_pgm(nama_file, byteorder='<')	#simpan nilai file pgm dengan fungsi read_pgm

#RUBAH NILAI X DAN Y NYA !!!!!!!!!!!!
#ITB Bandung
X = 107.611
Y = -6.890

p=(X-70)*20
q=1800-((Y+20)*20)
ccc = 0									#index untuk hasil akhir
totemp = 0								#untuk perhitungan suhu index 2-9
hr1 = int(round(p))
vt1 = int(round(q))

tester = 0
#membuat array untuk keperluan pehitungan sebenarnya
d = numpy.zeros((9), dtype = int)
temp = numpy.zeros((9), dtype = float)
hsl = numpy.zeros(((2 * luasan + 1)**2, 6), dtype = float)

for hr in range (hr1-luasan-1,hr1+luasan):
	for vt in range (vt1-luasan-1,vt1+luasan):
		d[0] = irdat[vt][hr]
		d[1] = irdat[vt][hr-1]
		d[2] = irdat[vt][hr-2]
		d[3] = irdat[vt][hr+1]
		d[4] = irdat[vt][hr+2]
		d[5] = irdat[vt+1][hr]
		d[6] = irdat[vt+2][hr]
		d[7] = irdat[vt-1][hr]
		d[8] = irdat[vt-2][hr]

#Modul untuk mengconvert data index ke data temperatur
		for hitung in range (9):
			idx       = d[hitung]		#baca nilai pixel dan simpan ke variabel idx
			temp[hitung] = data[idx]	#konversi nilai pixel menjadi nilai temperatur dan simpan ke variabel temp
		
		if tester == 0:
			print temp
		
#S=0.125*(temp(2,1)+temp(3,1)+temp(4,1)+temp(5,1)+temp(6,1)+temp(7,1)+temp(8,1)+temp(9,1)-8*temp(1,1));
		for hitung in range (1,9):
			totemp += temp [hitung]
		S = 0.125*(totemp - (8.0 * temp[0]))
		print totemp,8 * temp[0]
		totemp = 0
#FFF=(temp(1,1)-207)*0.0826;
		FFF = (temp[0] - 207.0) * 0.0826
#Th=exp(FFF);
		TH = numpy.exp(FFF)
#B=15.27 +((-0.0492)* temp(1,1));
		B = 15.27 + ((-0.0492) * temp[0])
#A= exp (B);
		A = numpy.exp(B)
		
# Nilai 3 adalah konvektif dan 1 adalah Stratiform

		if S >= TH:
			passes = 3.0
			R1 = (A / 121.0) * 20.0
			R2 = (A / 202.1243) * 26.0
		else:
			passes = 1.0
			R1 = (A / 121.0) * 3.5
			R2 = (A / 202.1243) * 0.8

		lintang1 = (1800-vt)/20.0-20;
		bujur1=(hr/20.0)+70;

#R1 adalah hasil estimasi dari metode CST
#R2 adalah hasil estimasi dari metode CSTm
#passes adalah klasifikasi stratiform (1) atau konvektif (3)

		hsl[ccc][0:6]= [lintang1, bujur1, ccc, passes, R1, R2]
		ccc=ccc+1;
		tester = 1
		
print hsl
print len(hsl)
numpy.savetxt('ctms.txt', hsl)
