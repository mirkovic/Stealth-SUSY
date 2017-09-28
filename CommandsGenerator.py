from optparse import OptionParser


parser = OptionParser()

parser.add_option('-s','--set', metavar='F', type='string', action='store',
                  default       =       'Signal',
                  dest          =       'set',
                  help          =       'dataset to analyze')

parser.add_option('-f', metavar='F', type='string', action='store',
                  default       =       '',
                  dest          =       'destination',
                  help          =       'what to save tree as')

parser.add_option('-n', '--number', metavar='F', type='int', action='store',
                  default       =       300,
                  dest          =       'n',
                  help          =       'number of jobs to be split into')
#########
### 'convert' to only convert data from ntuple to tree,
### 'cuts' to update cut branches on already converted trees
### 'both' to convert data and update cuts
parser.add_option('-m', '--mode', metavar='F', type='string', action='store',
                  default       =       'both',
                  dest          =       'mode',
                  help          =       'determines mode')

parser.add_option('-p', metavar='F', type='string', action='store',
                  default       =       '',
                  dest          =       'program',
                  help          =       'which program to use in command')

parser.add_option('--append',action='store_true',dest='append')
parser.add_option('--disorganize',action='store_false',dest='organize')
parser.set_defaults(organize=True)
parser.set_defaults(append=False)

(options, args) = parser.parse_args()


text = ''

for i in range(options.n):
	text+= 'python tardir/'+options.program+' --grid -s '+options.set+' -f '+options.destination+' -j '+str(i)+'-'+str(options.n)
	if i != options.n-1:
		text+='\n'

if not options.append:
	with open('susy.listOfJobs','w') as f:
		f.write(text)
else:
	with open('susy.listOfJobs','a') as f:
		f.write('\n'+text)


