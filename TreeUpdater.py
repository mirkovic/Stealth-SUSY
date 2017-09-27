import os
import ROOT
from ROOT import TFile,TTree,TLorentzVector
from DataFormats.FWLite import Events, Handle
import glob
from optparse import OptionParser
from array import array
import lib.Cuts as Cuts
import lib.functions as functions
def PrintOptions():
	print "Options summary"
	print "=================="
	for  opt,value in options.__dict__.items():
		print str(opt) +': '+ str(value)
	print "=================="
	print ""



#def ChoseFolder():
#	files_folder = []
#	signal_folder = '/eos/uscms/store/group/lpcrutgers/knash/SMS-T7WgStealth_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_SMS-T7WgStealth_GENfiltered_take1_Slim_V11/170609_175318/0000/'
#	QCD_folder = '/eos/uscms/store/group/lpcrutgers/knash/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Slim_V11/170609_182234/0000/'
#	TTBAR_folder = '/eos/uscms/store/group/lpcrutgers/knash/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/crab_TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_Slim_V11/170609_184530/*/'
#	if options.set == 'Signal':
#		files_folder = [signal_folder]
#	elif options.set == 'QCD':
#		files_folder = [QCD_folder]
#	elif options.set == 'TTBAR':
#		files_folder = [TTBAR_folder]
#	elif options.set == 'All':
#		files_folder = [signal_folder,QCD_folder,TTBAR_folder]
#
#	return files_folder

def DealWithOptions():
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
		tree_file = options.set + '_' + options.j + '.root'
	else:
		tree_file = options.destination + '_' + options.j + '.root'

	return split_vals, tree_file

def GetRootFilesFromFolders():
	#tmpfiles = []
	#print files_folder	
	#for folder in files_folder:
	files = []
	files1=open(di+'Files_susy_'+options.set+'.txt').readlines()
	for i in range(0,len(files1)):
		files1[i] = files1[i].replace('/eos/uscms','root://cmsxrootd.fnal.gov//').replace('\n','')
		if i%split_vals[1]==split_vals[0]:
			files.append(files1[i])
	#	indir = glob.glob(folder+'*')
	#	for thing in indir:
	#		if thing[-5:] == '.root':
	#			tmpfiles.append(thing)


	#files = []
	#for i in range(len(tmpfiles)):
	#	if i % split_vals[1] == split_vals[0]:
	#		files.append( tmpfiles[i].replace('/eos/uscms','root://cmsxrootd.fnal.gov//') )


	return files


def HandleLabelFloat(category,variables):
	return_handles = {}
	return_labels = {}
	if category == 'filteredPrunedGenParticles':
		return_handles['GenParticles'] = Handle (  "vector<reco::GenParticle>" )
		return_labels['GenParticles'] = ( category, "" )	
	else:
		for var in variables:
			return_handles[var] = Handle (  "vector<float>" )
			return_labels[var] = ( category, var )
	return return_handles, return_labels

def TreeVarsCollections():
	
	with open(di+'bin/'+options.set+'branches','r') as fyl:
		for branch in fyl.read().splitlines():
			part = branch.split(',')
			### part 0 is branch collection, part 1 is branch name, part 2 is number of values per event
			if part[0] not in collections:
				collections[part[0]] = {part[1]:int(part[2])}
				types[part[0]] = {part[1]:part[3]} 
			else:
				collections[part[0]][part[1]] = int(part[2])
				types[part[0]][part[1]] = part[3]
	#cuts_names = my_cuts.GetCombinations()
	#cuts_dict = dict(zip(cuts_names,[1]*len(cuts_names)))
	#collections['cuts'] = cuts_dict
	#types['cuts'] = dict(zip(cuts_names,['b']*len(cuts_names)))
	
	return collections
	#if options.mode in ['convert','both']:
	#	collection['jetsAK8']=['jetAK8PuppiEta','jetAK8PuppiMass','jetAK8PuppiPhi','jetAK8PuppiPt','jetAK8PuppiCorrectedsoftDropMass','jetAK8Puppitau1','jetAK8Puppitau2']
	#	collection['jetsAK4CHS']=['jetAK4CHSE','jetAK4CHSEta','jetAK4CHSPhi','jetAK4CHSPt']
	#if options.mode in ['cuts','both']:
	#	collection['cuts'] = CutsTool.Names()

	#return collection
def DealWithHandlesAndLabels():
	Handles = {}
	Labels = {}
	
	### if a collection is not in ntuple, add it tothe if statement
	for collection in collections:
		if collection != 'cuts':
			Handles[collection], Labels[collection] = HandleLabelFloat(collection,collections[collection])
	
	return Handles, Labels

	#AK8returns = HandleLabelFloat(jetsAK8,jetsAK8vars)
	#AK4returns = HandleLabelFloat(jetsAK4,jetsAK4vars)

	#Handles[jetsAK8] = AK8returns[0]
	#Labels[jetsAK8] = AK8returns[1]

	#Handles[jetsAK4] = AK4returns[0]
	#Labels[jetsAK4] = AK4returns[1]

	#return Handles, Labels


def MakeTFileAndTTree(loc,file_name):
	if not os.path.exists:
		os.makedirs( loc , exist_ok=True )
	print os.path.join(loc,file_name)
	print file_name
	print loc
	f = TFile( os.path.join(loc,file_name) , 'RECREATE' )
	tree = TTree('tree','tree')

	return f, tree

def FillBranches():
	tree_vars = {}
	### collection -> collections of jets, collection[collection] -> branch names, collection[collection][var] -> number of values per event
	for collection in collections:
		for var in collections[collection]:
			array_type = ArrayType(types[collection][var])
			root_type = RootType(types[collection][var])
			#if collection == 'cuts':
			#	print root_type
			tree_vars[var] = array(array_type,[0]*collections[collection][var])
			tree.Branch(var,tree_vars[var],var+'['+str(collections[collection][var])+']/'+root_type)
	return tree_vars
			
	#for var in jetsAK4vars:
	#	tree_vars[var] = array('d',[0]*32)
	#	tree.Branch(var,tree_vars[var],var+'[32]/D')
	#for var in jetsAK8vars:
	#	tree_vars[var] = array('d',[0]*12)
	#	tree.Branch(var,tree_vars[var],var+'[12]/D')

particles_id_names = {1000021:'Gluino',1000022:'Chargino',1000023:'Chargino',1000024:'Chargino',22:'W',24:'W',25:'W',3000001:'Singlino',3000002:'Singlet',1:'GluinoQuarks',2:'GluinoQuarks',3:'GluinoQuarks',4:'GluinoQuarks',5:'GluinoQuarks',6:'GluinoQuarks'}
pdgid = {'Gluino':[1000021],'Chargino':[1000022,1000023,1000024],'W':[22,24,25],'Singlino':[3000001],'Singlet':[3000002],'GluinoQuarks':[1,2,3,4,5,6]}
momid = {'Gluino':[None,21,1,2,3,4,5,6],'Chargino':[1000021],'W':[1000022,1000023,1000024],'Singlino':[1000022,1000023,1000024],'Singlet':[3000001],'GluinoQuarks':[1000021]}
bad_status = {'Gluino':[],'Chargino':[],'W':[],'Singlino':[],'Singlet':[],'GluinoQuarks':[71]}
pdgids = particles_id_names.keys()
particle_names = ['Gluino','GluinoQuarks','Chargino','W','Singlino','Singlet'] 
particles = [[]]*len(particle_names)
PARTICLE = dict(zip(particle_names,range(len(particle_names))))
def GetValuesFromHandles(vars_set):
	### vars_set should be dictionary of lists
	### tree_values should be dectionary of dictionaries
	def FourVals(particle_name,particle_vals):
		tree_values[particle_name+'Mass'].append(particle_vals.mass())
		tree_values[particle_name+'Pt'].append(particle_vals.pt())
		tree_values[particle_name+'Eta'].append(particle_vals.eta())
		tree_values[particle_name+'Phi'].append(particle_vals.phi())

	def MakeParticleJets(particles_final):
		jets = {}
		for part in particles_final:
			jets[part] = []
			for k in range(collections['filteredPrunedGenParticles'][part+'Pt']):
				this_vec = TLorentzVector()
				this_vec.SetPtEtaPhiM(tree_values[part+'Pt'][k],tree_values[part+'Eta'][k],tree_values[part+'Phi'][k],tree_values[part+'Mass'][k])
				jets[part].append(this_vec)
		
		return jets
	def MakeAK8Jets():
		jets = []
		for k in range(collections['jetsAK8']['jetAK8PuppiPt']):
			this_vec = TLorentzVector()
			if k < len(tree_values['jetAK8PuppiPt']):
				this_vec.SetPtEtaPhiM(tree_values['jetAK8PuppiPt'][k],tree_values['jetAK8PuppiEta'][k],tree_values['jetAK8PuppiPhi'][k],tree_values['jetAK8PuppiCorrectedsoftDropMass'][k])
				jets.append(this_vec)
			else: break
		return jets

	tree_values = {}
	particles = []#[[]]*len(particle_names)
	for i in particle_names:
		particles.append([])
	for collection in vars_set:
		if collection == 'cuts':
			pass	
		elif collection == 'filteredPrunedGenParticles':
			tree_values['filteredPrunedGenParticles'] = {}
			ev.getByLabel ( Labels[collection]['GenParticles'], Handles[collection]['GenParticles'] )
			for i in Handles[collection]['GenParticles'].product():
				absid = abs(i.pdgId())
				if absid in pdgids:
					particle = particles_id_names[absid]
					mom = momid[particle]
					if None not in mom:
						if abs(i.mother().pdgId())not in mom:
							continue
					else:
						try:
							if abs(i.mother().pdgId())not in mom:
								continue
						except:
							pass
					ok_status = True
					for st in bad_status[particle]:
						if i.status() == st:
							ok_status = False
							break
					if not ok_status:
						continue
					particles[PARTICLE[particle]].append(i)
			

				#try:
				#	mom = i.mother().pdgId()
				#except:
				#	mom = 0
				#if absid == 1000021 and mom != absid:
				#	#tree_values['filteredPrunedGenParticles']['GluinoMass'] = i.mass()
				#	tree_values['GluinoMass'] = [i.mass()]
				#elif (absid == 1000022 or absid == 1000023 or absid == 1000024) and abs(mom) != absid:
				#	#tree_values['filteredPrunedGenParticles']['CharginoMass'] = i.mass()
				#	tree_values['CharginoMass'] = [i.mass()]
			##### Maybe find more elegant solution in future
			error = False
			for i in range(len(particles)):
				if particle_names[i] == 'GluinoQuarks':
					if len(particles[i]) != 4:
						error = True
				else:
					if len(particles[i]) != 2:
						error = True
			if error:
				print 'Wrong number of particles counted, skipping event'
				return None
				for i in range(len(particle)):
					if particle_names[i] == 'GluinoQuarks':
						tree_values['GluinoQuarksMass'] = [0]*4
						tree_values['GluinoQuarksPt'] = [0]*4
						tree_values['GluinoQuarksEta'] = [0]*4
						tree_values['GluinoQuarksPhi'] = [0]*4
					else:
						tree_values[particle_names[i]+'Mass'] = [0]*2
						tree_values[particle_names[i]+'Pt'] = [0]*2
						tree_values[particle_names[i]+'Eta'] = [0]*2
						tree_values[particle_names[i]+'Phi'] = [0]*2
						
			branches = functions.SeparateBranches(particles)
			branch_count = 0
			for br in branches:
				
				for k in range(len(br)):
					particle_type = particle_names[k]
					if branch_count == 0:
						tree_values[particle_type+'Mass'] = []
						tree_values[particle_type+'Pt'] = []
						tree_values[particle_type+'Eta'] = []
						tree_values[particle_type+'Phi'] = []
					for particle in br[k]:
						FourVals(particle_type,particle)
				branch_count += 1
		elif collection == 'Analysis':
			continue
		else:
			tree_values[collection] = {}				
			for var in vars_set[collection]:
				ev.getByLabel ( Labels[collection][var], Handles[collection][var] )
				tree_values[var] =  Handles[collection][var].product()
	if 'Analysis' in vars_set:
		particle_jets = MakeParticleJets(['W','Singlet'])
		AK8_jets = MakeAK8Jets()
		matches,errors = functions.SecondMinJetError(particle_jets['W']+particle_jets['Singlet'],AK8_jets,requirement=.6,matchdifferent=False)
		tree_values['WAK8'] = [0,0]
		tree_values['WAK8Deviance'] = [0,0]
		tree_values['SingletAK8'] = [0,0]
		tree_values['SingletAK8Deviance'] = [0,0]
		for match in matches.keys():
			if match < 2: this_particle = 'W'
			else: this_particle = 'Singlet'
			tree_values[this_particle+'AK8'][match%2] = matches[match]+1
			tree_values[this_particle+'AK8Deviance'][match%2] = errors[match]+1
	
	return tree_values


def SetTreeVars():
	
	for collection in vars_set:
		if collection == 'cuts':
			for var in vars_set[collection]:
				tree_vars[var][0] = values[var]
		else:
			for var in vars_set[collection]:
#				if len(vars_set[collection]) > 6:
#					print len(vars_set[collection])
				for i in range(len(values[var])):
					tree_vars[var][i] = values[var][i]
				for i in range(len(values[var]),len(tree_vars[var])):
					tree_vars[var][i] = 0

def ArrayType(char):
	if char == 'd':
		return 'd'
	if char == 'b':
		return 'B'

def RootType(char):
	if char == 'd':
                return 'D'
        if char == 'b':
                return 'O'

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

#########
### 'convert' to only convert data from ntuple to tree,
### 'cuts' to update cut branches on already converted trees
### 'both' to convert data and update cuts
parser.add_option('-m', '--mode', metavar='F', type='string', action='store',
                  default       =       'both',
                  dest          =       'mode',
                  help          =       'determines mode')

parser.add_option('--grid',action='store_true',dest='grid')
parser.add_option('--disorganize',action='store_false',dest='organize')
parser.set_defaults(organize=True)
parser.set_defaults(grid=False)

(options, args) = parser.parse_args()


if options.grid:
	di = 'tardir/'
else:
	di = ''

#########
### Make sure you are analyzing the correct data set
#########
if not options.grid:
	os.system('python Flist.py -s '+options.set)

#########
### Bogus variables
#########
maxAK4 = 0

###################
### Begins Here ###
##################



PrintOptions()


#########
### Find folders that correspond to the data types selected in options
#########
#files_folder = ChoseFolder()
#print files_folder


#########
### Convert some options to more usable variables
#########
split_vals, tree_file = DealWithOptions()



#########
### Fix files according to where this program is run and which portion of data will be analyzed
#########
files = GetRootFilesFromFolders()			

#########
### Create branch names and organize them by type (type could be jetAK8, jetAK4, event passing cut, or more if I add them after writing this)
#########
handle_collections = ['jetsAK8','jetsAK4CHS']
#if options.grid:
#	my_cuts = Cuts.CutsCollection('tardir/bin/'+options.set+'cuts')
#else:
#	my_cuts = Cuts.CutsCollection('bin/'+options.set+'cuts')

collections = {}
types = {}
vars_set = TreeVarsCollections()#{jetsAK8:jetsAK8vars,jetsAK4:jetsAK4vars}


#########
### Create handles and labels. These are used to loop through data in the ntuple in selected folders
#########
Handles,Labels = DealWithHandlesAndLabels()



#########
### Create output root file and ttree
#########
organize = options.organize 
if options.grid:
	organize = False
if organize == False:
	print 'not hidden in folder'
	loc = ''
else:
	loc = 'data/'+ options.set
f,tree = MakeTFileAndTTree(loc,tree_file)
print 



#########
### Create branches on output root file and connect them to tree_vars
#########
tree_vars = FillBranches()



#########
### Convert events in selected files to iterable (I think)
#########
events = Events(files)

count = 0
for ev in events:
	count+=1
#	if count == 1000:
#		break

        if count % 100000 == 0 :
                print  '--------- Processing Event ' + str(count) #+'   -- percent complete ' + str(100*count/totevents) + '% -- '

	values_handles = {}
	values_cuts = {}
	
	values_handles = GetValuesFromHandles(vars_set)
	if values_handles == None:
		continue
	#my_cuts.CheckAllCuts(values_handles)
	#values_cuts = my_cuts.GetComboResults()
	#values_handles.update(values_cuts)
	values = values_handles

	
	SetTreeVars()

	tree.Fill()
#combo = my_cuts.GetCombinations()
#
#for c in my_cuts.combinations:
#	print my_cuts.GetComboString(c) + ':  ', my_cuts.counts[my_cuts.GetComboString(c)]

print 'total events:  ', + count
print	 
print 'done'

f.cd()
f.Write()
f.Close()


