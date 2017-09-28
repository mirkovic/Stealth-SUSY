import os
import ROOT
from optparse import OptionParser
import glob
import lib.Cuts as Cuts

parser = OptionParser()

parser.add_option('-s', metavar='F', type='string',action='store',
	default = 'All',
	dest    = 'set', 
	help    = 'which section of data to analyze')

(options, args) = parser.parse_args()

if options.set == 'All':
	sections = ['Signal','QCD','TTBAR','H']
else:
	sections = [options.set]
folders = {}
folders['Signal'] = Cuts.CutsCollection('bin/SignalRegions').GetCombinations()
folders['Signal'].append('AllSignal')
folders['QCD'] = Cuts.CutsCollection('bin/QCDRegions').GetCombinations()
folders['QCD'].append('AllQCD')
folders['TTBAR'] = Cuts.CutsCollection('bin/TTBARRegions').GetCombinations()
folders['TTBAR'].append('AllTTBAR')
folders['H'] = Cuts.CutsCollection('bin/HRegions').GetCombinations()
folders['H'].append('AllH')
print sections
for i in sections:	

	for j in folders[i]:
		fold = 'plots/'+i+'/'+j+'/*'
		plots = glob.glob(fold)
		print i
		if len(plots) == 0:
			continue
		print i
		command = 'hadd -f plots/'+i+'/'+j+'.root'
		for pl in plots:
			
			print 'adding '+pl
			print 'size: ' + str(os.path.getsize(pl))
			command += ' ' + pl
		print 'executing: ' + command
		os.system(command)

