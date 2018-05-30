#!/usr/bin/python

# parameter sweep wrapper for INVMEL (McKenzie & O'Nions, 1991; https://doi.org/10.1093/petrology/32.5.1021)
# sweep through variable DTOP, XR, EPSIL and record RMS misfit for each run
# starting melt distribution, xr, is calculated using RIDALL program (McKenzie & Bickle, 1988; https://doi.org/10.1093/petrology/29.3.625)

import re
import os
import numpy

###########################################################
#----------------------- FUNCTIONS -----------------------#
###########################################################

def generate_input_file(params, filename):

    fd = open("template_input.dat", "r")
    template_data = fd.readlines()
    fd.close()

    # Convert input list of floats to string
    xrparsed = ''
    for x in params['XR']:
        xrparsed += str(x) + ','
    params['XR'] = xrparsed

    fd = open(filename, "w")

    for line in template_data:
        for s in ['EPSIL', 'DTOP', 'XR', 'NV']:
            line = re.sub(s, str(params[s]), line)
        fd.write(line)
    fd.close()


def extract_rms_error(filename):
    fd = open(filename, "r")
    data = fd.readlines()
    fd.close()

    xr = None
    error = None
    for i, line in enumerate(data):
        if (line[:26] == 'Best fitting melt fraction'):
            xr = data[i+2]
            if (nv < 8):
              error = data[i+3]
            elif (nv < 14):
              error = data[i+4]
            elif (nv < 20):
              error = data[i+5]
            else:
              error = data[i+6]

    if (xr == None):
    	xr = "0.1, 0.8E-01, 0.5E-01, 0.4E-01, 0.3E-01, 0.2E-01, 0.1E-01, 0"
    	error = "rms error = 10"

    # Get last part of line (after = sign) and convert to float
    error = float(error.split("=")[-1])

    # Split line on comma, and convert to list of floats, cutting last element
    xr = [ float(x) for x in xr.split(",")[:-1] ]

    return (error, xr) 

    
def do_run_invmel():
    os.system("./invmel")


def find_melt_fractions():		#  extract the starting melt distribution, xr, that correspond to the temperature and depth of each run from look-up file "isentropes.dat"

    fd = open("isentropes.dat", "r")
    daten = fd.readlines()
    fd.close()

    for k, line in enumerate(daten):
       	if (line[:8] == '%01d %01d ' %(temp, dtop)):
		xr = daten[k]
    print xr
    
    # Split line on space, and convert to list of floats, cutting out the first two and the last element
    xr = [ float(x) for x in xr.split(" ")]
    
#    xr = [xr[l] for l in range(2,26)]   # zbstep=1, nv=25 (max nv possible for INVMEL)
#    xr = [xr[l] for l in (2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30)]   # zbstep=2, nv=16
#    xr = [xr[l] for l in (2, 5, 8, 11, 14, 17, 20, 23, 26, 29)]   # zbstep=3, nv=11
#    xr = [xr[l] for l in (2, 6, 10, 14, 18, 22, 26, 30)]   # zbstep=4, nv=9
    xr = [xr[l] for l in (2, 7, 12, 17, 22, 27)]   # zbstep=5, nv=7
#    xr = [xr[l] for l in (2, 8, 14, 20, 26)]   # zbstep=6, nv=6
#    xr = [xr[l] for l in (2, 9, 16, 23, 30)]   # zbstep=7, nv=6
#    xr = [xr[l] for l in (2, 10, 18, 26)]   # zbstep=8, nv=5
#    xr = [xr[l] for l in (2, 11, 20, 29)]   # zbstep=9, nv=5
#    xr = [xr[l] for l in (2, 12, 22, 32, 42, 52)]   # zbstep=10, nv=4
    
    xr2 = []
    for number in xr:
      if ( number > 1e-6) :    # to ensure variable nv, take all entries in adiabats file, then chuck out any redundancies (zero-values)
        xr2.append(number) 
    xr = xr2
    print xr
    return (xr)


############################################################
#---------------------- MAIN PROGRAM ----------------------#
############################################################

# initiate output file and write headers
out=open('misfit.dat', 'w')
out.write('Tp dtop epsil rms \n')

dtop_range = range(50, 61)
rms_range = []
temp_range = range(135,141)
for temp in temp_range:
	temp = temp * 10
	for dtop in dtop_range:
		enrich_range = range(0, 10)
	
		for epsil in enrich_range:
			xr = find_melt_fractions()
			nv = len(xr) + 1   # calculate nv based on xr
			epsil = float(epsil) / 10
			params = {'EPSIL': epsil, 'DTOP': dtop, 'XR': xr, 'NV': nv}
        		generate_input_file(params, "input.dat")
        	
			# Run invmel
        		do_run_invmel()
        	
        		# Analyse output
        		rms_error, xr = extract_rms_error("output.dat")
        		
			rms_range.append(rms_error)	# write rms values of runs for all dtop and Fenrich to same array
			out.write(str(temp) + ' ' + str(dtop) + ' ' + str(epsil) + ' ' + str(rms_error) + '\n')


