import os
import ROOT
from ROOT import TFile,TTree
from DataFormats.FWLite import Events, Handle
import glob
from optparse import OptionParser
from array import array


def PrintOptions():
	print "Options summary"
	print "=================="
	for  opt,value in options.__dict__.items():
		print str(opt) +': '+ str(value)
	print "=================="
	print ""



def ChoseFolder(files_folder):
	signal_folder = '/eos/uscms/store/group/lpcrutgers/knash/SMS-T7WgStealth_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_SMS-T7WgStealth_GENfiltered_take1_Slim_V11/170609_175318/0000/'
	QCD_folder = '/eos/uscms/store/group/lpcrutgers/knash/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Slim_V11/170609_182234/0000/'
	TTBAR_folder = '/eos/uscms/store/group/lpcrutgers/knash/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/crab_TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_Slim_V11/170609_184530/*/'
	if options.set == 'Signal':
		files_folder = [signal_folder]
	elif options.set == 'QCD':
		files_folder = [QCD_folder]
	elif options.set == 'TTBAR':
		files_folder = [TTBAR_folder]
	elif options.set == 'All':
		files_folder = [signal_folder,QCD_folder,TTBAR_folder]

	return files_folder

def DealWithOptions(split_vals,tree_file):
	#########
	### Get values used to split jobs
	#########

	split_vals = options.j.split('-')
	try:
		split_vals = map(int,split_vals)
		if len(split_vals) != 2:
			raise Exception()
	except:
		print 'incorrect options format'
		print 'exiting'
		exit()

	#########
	### names output root files
	#########

	if options.destination == '':
		tree_file = options.set + '_' + str(split_vals[0]) + '.root'
	else:
		tree_file = options.destination + '_' + str(split_vals[0]) + '.root'

	return split_vals, tree_file

def GetRootFilesFromFolders():
	tmpfiles = []
	for folder in files_folder:
		indir = glob.glob(folder+'*')
		for thing in indir:
			if thing[-5:] == '.root':
				tmpfiles.append(thing)


	files = []
	for i in range(len(tmpfiles)):
		if i % split_vals[1] == split_vals[0]:
			files.append( tmpfiles[i].replace('/eos/uscms','root://cmsxrootd.fnal.gov//') )


	return files


def HandleLabelFloat(category,variables):
	return_handles = {}
	return_labels = {}
	for var in variables:
		return_handles[var] = Handle (  "vector<float>" )
		return_labels[var] = ( category, var )
	return (return_handles,return_labels)

def DealWithHandlesAndLabels():
	Handles = {}
	Labels = {}

	AK8returns = HandleLabelFloat(jetsAK8,jetsAK8vars)
	AK4returns = HandleLabelFloat(jetsAK4,jetsAK4vars)

	Handles[jetsAK8] = AK8returns[0]
	Labels[jetsAK8] = AK8returns[1]

	Handles[jetsAK4] = AK4returns[0]
	Labels[jetsAK4] = AK4returns[1]

	return Handles, Labels


def MakeTFileAndTTree(loc,file_name):
	if not os.path.exists:
		os.makedirs( loc , exist_ok=True )
	f = TFile( os.path.join(loc,file_name+'.root') , 'RECREATE' )
	tree = TTree('tree','tree')

	return f, tree

def FillBranches():
	for var in jetsAK4vars:
		tree_vars[var] = array('d',[0]*32)
		tree.Branch(var,tree_vars[var],var+'[32]/D')
	for var in jetsAK8vars:
		tree_vars[var] = array('d',[0]*12)
		tree.Branch(var,tree_vars[var],var+'[12]/D')

def GetValuesFromHandles(vars_set):
	### vars_set should be dictionary of lists
	### tree_values should be dectionary of dictionaries

	tree_values = {}
	for collection in vars_set:
		tree_values[collection] = {}	
		for var in vars_set[collection]:
			ev.getByLabel ( Labels[collection][var], Handles[collection][var] )
			
			tree_values[var] =  Handles[collection][var].product()
	
	return tree_values


def SetTreeVars():
	
	for collection in vars_set:
		for var in vars_set[collection]:
			tree_vars[var] = values[var]


parser = OptionParser()

parser.add_option('-s','--set', metavar='F', type='string', action='store',
                  default       =       'Signal',
                  dest          =       'set',
                  help          =       'dataset to analyze')

parser.add_option('-f', metavar='F', type='string', action='store',
                  default       =       '',
                  dest          =       'destination',
                  help          =       'what to save tree as')

parser.add_option('-j', '--files', metavar='F', type='string', action='store',
                  default       =       '0-1',
                  dest          =       'j',
                  help          =       'selects which files to scan')

parser.add_option('--grid',action='store_true',dest='grid')
parser.set_defaults(grid=False)

(options, args) = parser.parse_args()




#########
### Find folders according to data type
#########
files_folder = []
files_folder = ChoseFolder(files_folder)
print files_folder


#########
### Convert options to variables
#########
split_vals = []
tree_file = ''
split_vals, tree_file = DealWithOptions(split_vals,tree_file)



#########
### Fix files according to where this program is run and which portion of data will be analyzed
#########
files = GetRootFilesFromFolders()			



#########
### Create float handles (necessary to read data)
#########

jetsAK8 = 'jetsAK8'
jetsAK8vars = ['jetAK8PuppiEta','jetAK8PuppiMass','jetAK8PuppiPhi','jetAK8PuppiPt','jetAK8PuppiCorrectedsoftDropMass','jetAK8Puppitau1','jetAK8Puppitau2']

jetsAK4 = 'jetsAK4CHS'
jetsAK4vars = ['jetAK4CHSE','jetAK4CHSEta','jetAK4CHSPhi','jetAK4CHSPt']

vars_set = {jetsAK8:jetsAK8vars,jetsAK4:jetsAK4vars}


Handles,Labels = DealWithHandlesAndLabels()



#########
### Create output root file and ttree
#########

loc = 'data/'+ options.set
f,tree = MakeTFileAndTTree(loc,tree_file)
print 



#########
### Create branches on output root file
#########
tree_vars = {}
FillBranches()



#########
### Convert events into iterable
events = Events(files)


count = 0
for ev in events:
	count+=1
	print count

        if count % 100000 == 0 :
                print  '--------- Processing Event ' + str(count) #+'   -- percent complete ' + str(100*count/totevents) + '% -- '

	values = {}
	
	values = GetValuesFromHandles(vars_set)

	SetTreeVars()

	tree.Fill()

f.cd()
tree.Write()
f.Write()
f.Close()


