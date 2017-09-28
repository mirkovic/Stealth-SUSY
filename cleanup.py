import os
import glob
from optparse import OptionParser

parser = OptionParser()

parser.add_option('--kill',action='store_true',dest='kill')
parser.set_defaults(kill=False)

(options, args) = parser.parse_args()

if options.kill:
	for fyl in glob.glob('Plots*') + glob.glob('*.root'):
		os.system('rm '+fyl)
	os.system('python movebulk.py')
	exit()
plots = glob.glob('Plots*')
for pl in plots:
	parts = pl.split('_')
	if len(parts) > 1:
		directory = 'plots/'+parts[2]+'/'+parts[1]
		if not os.path.exists(directory):
			os.makedirs(directory)
		os.system('mv ' + pl+ ' ' + directory + '/' + pl)

data = glob.glob('*.root')
for fyl in data:
	parts = fyl.split('_')
	try:
		os.system('mv '+fyl+' data/'+parts[0]+'/'+fyl)
	except:
		os.system('mv '+fyl+' data/'+fyl)

os.system('python movebulk.py')
