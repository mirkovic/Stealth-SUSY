import os
import glob
import lib.Cuts as Cuts

Signalcontents = glob.glob('data/Signal/*') + glob.glob('plots/Signal/*')
QCDcontents = glob.glob('data/QCD/*') + glob.glob('plots/QCD/*')
TTBARcontents = glob.glob('data/TTBAR/*') + glob.glob('plots/TTBAR/*')

#Signal has total of 296 files
#QCD has a total of 170 files
#TTBAR has a total of 1507 files
#
#The numbers for splitting indicate how many files were done per run

fyl = open('bin/format','r')
lines=fyl.read().split('\n')

num_signal = (lines[0].split('num_signal=')[1])
num_qcd = (lines[1].split('num_qcd=')[1])
num_ttbar = (lines[2].split('num_ttbar=')[1])
print Cuts.CutsCollection('bin/SignalRegions')
print Cuts.CutsCollection('bin/SignalRegions').GetCombinations()
folders_signal = Cuts.CutsCollection('bin/SignalRegions').GetCombinations()
folders_signal.append('AllSignal')
folders_qcd = ['AllQCD']
folders_ttbar = ['AllTTBAR']
print folders_signal

for i in Signalcontents:
	if len(i.split('-'+num_signal)) == 1 and i[-5:] == '.root':
		print i
		os.system('mv '+i+' oldbulk/'+i)
for i in QCDcontents:
	if len(i.split('-'+num_qcd)) == 1 and i[-5:] == '.root':
		print i
		os.system('mv '+i+' oldbulk/'+i)
for i in TTBARcontents:
	if len(i.split('-'+num_ttbar)) == 1 and i[-5:] == '.root':
		print i
		os.system('mv '+i+' oldbulk/'+i)

