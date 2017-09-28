import os
import glob

files = glob.glob('*Two*CharginoPlot*.root')
files += glob.glob('*Weird*')
files += glob.glob('output_*')
files += glob.glob('test*')
files += glob.glob('treebit*')
files += glob.glob('Chargino*.root')
moved = ''
for r in files:
#	os.system('mv '+r+' '+r[8:])
	os.system('mv '+r+' oldbulk/'+r)
	moved+='oldbulk/'+r+'\n'
#for o in outs:
#	os.system('mv '+o+' oldbulk/'+o)
f = file('prevmoved.txt','w')
f.write(moved)
