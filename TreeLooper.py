import ROOT
from ROOT import TFile, TTree, TH1D, TH2D, TLorentzVector
from optparse import OptionParser
from array import array
import numpy as np
import lib.Cuts as Cuts
import time

parser = OptionParser()

parser.add_option('-s','--set', metavar='F', type='string', action='store',
                  default       =       'Signal',
                  dest          =       'set',
                  help          =       'dataset to analyze')

parser.add_option('-o', metavar='F', type='string', action='store',
                  default       =       '', 
                  dest          =       'output',
                  help          =       'what to save output as')

parser.add_option('-f', metavar='F', type='string', action='store',
                  default       =       '', 
                  dest          =       'destination',
                  help          =       'where to find tree')

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
parser.set_defaults(grid=False)

(options, args) = parser.parse_args()
def CheckSignal(word):
        return word in ['Signal','H']

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


def TreeVarsCollections():
        collections = {}
        types = {}

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
        #my_cuts.GetCombinations() = cuts_dict
        #types['cuts'] = dict(zip(cuts_names,['b']*len(cuts_names)))

        return collections, types


def SetBranches(tree):
        ### collection -> collections of jets, collection[collection] -> branch names, collection[collection][var] -> number of values per event
        tree_vars = {}
        for collection in collections:
                for var in collections[collection]:
                        array_type = ArrayType(types[collection][var])
                        root_type = RootType(types[collection][var])

                        tree_vars[var] = array(array_type,[0]*collections[collection][var])
                        tree.SetBranchAddress(var,tree_vars[var])

        return tree_vars


def MakeHistograms(com,tmparrays):
        def StandardHistograms(this_cut,category):
                directories[this_cut+var] = directories[this_cut].mkdir(this_cut+var)
                directories[this_cut+var].cd()

                histograms[this_cut][var] = {}

                histograms[this_cut][var]['Pt'] = TH1D('Pt','Pt',50,-10,3000)
                histograms[this_cut][var]['Eta'] = TH1D('Eta','Eta',100,0,5)
                histograms[this_cut][var]['Phi'] = TH1D('Phi','Phi',140,0,7)

        def StandardHistogramsMass(this_cut,category):
                directories[this_cut+category] = directories[this_cut].mkdir(category)
                directories[this_cut+category].cd()

                histograms[this_cut][category] = {}

                histograms[this_cut][category+'Pt'] = TH1D('Pt','Pt',50,-10,3000)
                histograms[this_cut][category+'Mass'] = TH1D('Mass','Mass',100,0,5000)
                histograms[this_cut][category+'Eta'] = TH1D('Eta','Eta',100,0,5)
                histograms[this_cut][category+'Phi'] = TH1D('Phi','Phi',140,0,7)
                histograms[this_cut][category+'doubleb'] = TH1D('double B','Doubel B Tag',20,-1,1)

	def SetEventBranches(ttree):
		some_branches = {}
		for i in ['H','NH','S1','S2']:
			some_branches[i] = {}
			for j in ['Pt','Eta','Phi','M','t21','db']:
				some_branches[i][j] = array('d',[0])
				ttree.Branch(i+j,some_branches[i][j],'[1]/d')
		return some_branches

        def MatchedHistograms(this_cut,histo_direc):
                def VarHist(name):
                        if name == '':
                                directories[this_cut+histo_direc+name] = directories[this_cut].mkdir(this_cut+histo_direc)
                        else:
                                name = ', ' + name
                                directories[this_cut+histo_direc+name] = directories[this_cut].mkdir(name.replace(',','').replace(' ',''))
                        directories[this_cut+histo_direc+name].cd()
                        histograms[this_cut][histo_direc+name+', W Pt'] = TH1D('Pt of W jets','Pt of matched W Jets',100,0,1000)
                        histograms[this_cut][histo_direc+name+', W Mass'] = TH1D('Mass of W jets','Mass of matched W Jets',60,0,600)
                        histograms[this_cut][histo_direc+name+', W tau21'] = TH1D('tau21 of W jets','tau21 of matched W Jets',30,0,1)
                        histograms[this_cut][histo_direc+name+', W deviance'] = TH1D('Deviance of W jets','Deviance of matched W Jets',30,0,1)
                        histograms[this_cut][histo_direc+name+', W doubleb'] = TH1D('Double B Tag of W(Higgs) jets','Double B Tag of matched W(Higgs) Jets',30,0,1)
                        histograms[this_cut][histo_direc+name+', Singlet Pt'] = TH1D('Pt of Singlet jets','Pt of matched Singlet Jets',100,0,1000)
                        histograms[this_cut][histo_direc+name+', Singlet Mass'] = TH1D('Mass of Singlet jets','Mass of matched Singlet Jets',60,0,600)
                        histograms[this_cut][histo_direc+name+', Singlet tau21'] = TH1D('tau21 of Singlet jets','tau21 of matched Singlet Jets',30,0,1)
                        histograms[this_cut][histo_direc+name+', Singlet deviance'] = TH1D('Deviance of Singlet jets','Deviance of matched Singlet Jets',30,0,1)
                        histograms[this_cut][histo_direc+name+', Singlet doubleb'] = TH1D('Double B Tag of Singlet jets','Double B Tag of matched Singlet Jets',40,-1,1)

                if not CheckSignal(options.set):
                        return
                VarHist('')
                histograms[this_cut][histo_direc+', W matches'] = TH1D('number of W(Higgs) matches and number of events','Number of W(Higgs) Matches (0) and number of events (1)',2,0,2)
                histograms[this_cut][histo_direc+', Singlet matches'] = TH1D('number of Singlet matches and number of events','Number of Singlet Matches (0) and number of events (1)',2,0,2)
                histograms[this_cut][histo_direc+', maxtau21'] = TH1D('Largest tau21 of matched AK8 jets','Largest tau21 of matched AK8 jets',30,0,1)
#########
#this next plot must be changed every time you add or remove a condition to special jet
#########
                histograms[this_cut][histo_direc+', Failure'] = TH1D('Number of times a variable has caused an error','Number of times condition has not met requirement for Special',7,0,7)
                histograms[this_cut][histo_direc+', Failure Normalization'] = TH1D('Dont look','This plot is used for normalization',7,0,7)
                histograms[this_cut][histo_direc+', FailureW'] = TH1D('Number of times a variable has caused W to not be Special','Number of times condition for W has not met requirement for Special',7,0,7)
                histograms[this_cut][histo_direc+', Failure NormalizationW'] = TH1D('Dont lookW','This plot is used for normalization',7,0,7)
                histograms[this_cut][histo_direc+', FailureSinglet'] = TH1D('Number of times a variable has cause Singlet to not be Special','Number of times condition for Singlet has not met requirement for Special',7,0,7)
                histograms[this_cut][histo_direc+', Failure NormalizationSinglet'] = TH1D('Dont lookSinglet','This plot is used for normalization',7,0,7)
                VarHist('Not Special')
                VarHist('Special')


        Fyl = TFile('Plots_'+com+'_'+tree_file,'RECREATE')
        Fyl.cd()
        histograms = {}
        directories = {}
        directories['cuts'] = Fyl.mkdir('cuts')
        histograms['CutsCounts'] = TH1D('Number of events per cut','Number of events per cut',len(my_cuts.GetCombinations())+1,0,len(my_cuts.GetCombinations())+1)
        for cut in my_cuts.GetCombinations()+['No Cut']:
                directories[cut] = directories['cuts'].mkdir(cut)
                histograms[cut] = {}

                #########
                ### Histograms for AK8 jets
                directories[cut].cd()
                if CheckSignal(options.set):
                        histograms[cut]["SpecialJet"] = TH2D("Special jets", "Average number of \"special\" jets", (1750-800)/50, 800, 1750,34,100,1800)
                        histograms[cut]["SpecialJetCount"] = TH2D("Special jets counts", "Average number of \"special\" jets counts", (1750-800)/50, 800, 1750,34,100,1800)
                else:
                        histograms[cut]["SpecialJet"] = TH1D("Special jets", "Average number of \"special\" jets", 1,0,1)
                        histograms[cut]["SpecialJetCount"] = TH1D("Special jets counts", "Average number of \"special\" jets counts", 1, 0, 1)
                var = 'AK8'
		title = ''
		for ai in range(len(fakenames)):
			title += str(ai) + '-' + fakenames[ai] + ', '
		title = title[:-1]
		histograms[cut]['Prediction'] = TH1D('Prediction',title, len(fakenames),0,len(fakenames))
		histograms[cut]['NoBPrediction'] = TH1D('Prediction Without Double B',title, len(fakenames),0,len(fakenames))
                histograms[cut]['FailureReasons'] = TH1D('Reason for a jet to not be special','Reasons why jet is not Special',3,0,3)
                histograms[cut]['NumSpecial'] = TH1D('Number of special jets per event','Number of Special Jets per event',12,0,12)
                histograms[cut]['NumSpecialNotH'] = TH1D('Number of special jets not tagged as H per event','Number of Special Jets not also H per event',12,0,12)
                histograms[cut]['NumH'] = TH1D('Number of H tagged jets per event','Number of H tagged Jets per event',12,0,12)
		histograms[cut]['NumAK8'] = TH1D('Number of AK8 jets per event','Number of AK8 jets per event',12,0,12)
		histograms[cut]['NumAK4'] = TH1D('Number of AK4 jets per event','Number of AK4 jets per event',24,0,24)
                histograms[cut]['AK8HT'] = TH1D('HT of top four AK8','HT of top four AK8 jets',12,0,12)
                directories[cut+' top four'] = directories[cut].mkdir('top four jets')
                histograms[cut+ ' top four'] = {}
                StandardHistograms(cut+ ' top four', var)
                histograms[cut+ ' top four'][var]['softDropMass'] = TH1D('softDropMass','Soft Drop Mass',200,0,600)
                #histograms[cut+ ' top four'][var]['Top4softDropMass'] = TH1D('softDropMass of four highest pt jets','Soft Drop Mass of four highest pt jets',100,0,1200)
                histograms[cut+ ' top four'][var]['tau21'] = TH1D('tau21','tau21',100,0,1)

                directories[cut+' single jets'] = directories[cut].mkdir('single jets')
                histograms[cut+ ' single jets'] = {}
                directories[cut+' single jets tau21'] = directories[cut].mkdir('single jets tau21')
                directories[cut+' single jets pt'] = directories[cut].mkdir('single jets pt')
                directories[cut+' single jets mass'] = directories[cut].mkdir('single jets mass')
                directories[cut+' single jets doubleb'] = directories[cut].mkdir('single jets doubleb')
                directories[cut+' When Four Special'] = directories[cut].mkdir('When Four Special')
                directories[cut+' When Four Special'].cd()
                histograms[cut]['AK8HTSpecial'] = TH1D('HT of selected special jets','HT of Selected special jets',100,0,4500)
                histograms[cut]['AK8largesttau21'] = TH1D('Largest tau21 of Selected special jets','Largest tau21 of Selected Special Jets',50,0,1)
                histograms[cut]['NeutralinoMass'] = TH1D('Neutralino Mass','Neutralino Mass',50,-10,3000)
                histograms[cut]['MassAsyNeutralinoMass'] = TH2D('Mass difference vs Neutralino Mass','Mass difference of Neutralinos vs Neutralino Mass',250,0,2500,50,0,2000)
                directories[cut+' When Two H and Two Singlet'] = directories[cut].mkdir('When Two H and Two Singlet')
                directories[cut+' When Two H and Two Singlet'].cd()
                histograms[cut]['HNeutralinoMass'] = TH1D('Neutralino Mass','Neutralino Mass',50,-10,3000)
		for n in fakenames:
			StandardHistogramsMass(cut,n)
			histograms[cut]['PredictionMass'+n] = TH1D('Prediction Mass, '+n,'Mass of Failed Higgs Jet', 50,-10,3000)
			histograms[cut]['TreeFakeEvents'+n] = TTree(n,n)
			tmparrays[n] = SetEventBranches(histograms[cut]['TreeFakeEvents'+n])
			StandardHistogramsMass(cut,'NoB'+n)
			histograms[cut]['NoBPredictionMass'+n] = TH1D('Prediction Mass Without Double B, '+n,'Mass of Failed Higgs Jet', 50,-10,3000)
		#StandardHistogramsMass(cut,'OtherIsH')
		#StandardHistogramsMass(cut,'OtherIsLowMassH')
		#StandardHistogramsMass(cut,'OtherIsNotH')
		#StandardHistogramsMass(cut,'NoBOtherIsH')
		#StandardHistogramsMass(cut,'NoBOtherIsLowMassH')
		#StandardHistogramsMass(cut,'NoBOtherIsNotH')
                #histograms[cut]['MassAsyNeutralinoMass'] = TH2D('Mass difference vs Neutralino Mass','Mass difference of Neutralinos vs Neutralino Mass',250,0,2500,50,0,2000)
                #histograms[cut]['NumMatched'] = TH1D('Fraction matched special jets','Fraction of Special Jets that are tagged as W (1) or Singlet (2)',2,0,2)
                #MatchedHistograms(cut,'Matched Attributes, Four Special')
                #directories[cut+' When Three Special'] = directories[cut].mkdir('When Three Special')
                #directories[cut+' When Three Special'].cd()
                #histograms[cut]['AK8HTSpecial3'] = TH1D('HT of three special jets','HT of three special jets',100,0,4500)
                #histograms[cut]['AK8largesttau213'] = TH1D('Lowest tau21 of Selected 4 special jets','Lowest tau21 of Slected 4 Special Jets',50,0,1)
                #histograms[cut]['NeutralinoMass3'] = TH1D('Neutralino Mass','Neutralino Mass',100,0,2500)
                #histograms[cut]['MassAsyNeutralinoMass3'] = TH2D('Mass difference vs Neutralino Mass','Mass difference of Neutralinos vs Neutralino Mass',250,0,2500,50,0,2000)
                #histograms[cut]['NumMatched3'] = TH1D('Fraction matched special jets','Fraction of Special Jets that are tagged as W (1) or Singlet (2)',2,0,2)
                #MatchedHistograms(cut,'Matched Attributes, Three Special')

                #MatchedHistograms(cut,'Matched Attributes, <4 Special')
                #MatchedHistograms(cut,'Matched Attributes, <3 Special')
                #MatchedHistograms(cut,'Matched Attributes, 2 Special')
                #MatchedHistograms(cut,'Matched Attributes, 1 Special')
                #MatchedHistograms(cut,'Matched Attributes, 0 Special')
                MatchedHistograms(cut,'Matched Attributes')
                for i in range(6):
                        directories[cut+' single jets tau21'].cd()
                        histograms[cut+ ' single jets']['tau21 '+str(i)] = TH1D('tau21 '+str(i),'tau21',100,0,1)
                        directories[cut+' single jets pt'].cd()
                        histograms[cut+ ' single jets']['pt '+str(i)] = TH1D('pt '+str(i),'pt',200,0,1800)
                        directories[cut+' single jets mass'].cd()
                        histograms[cut+ ' single jets']['mass '+str(i)] = TH1D('mass '+str(i),'mass',200,0,1800)
                        directories[cut+' single jets doubleb'].cd()
                        histograms[cut+ ' single jets']['doubleb '+str(i)] = TH1D('doubleb '+str(i),'doubleb',40,-1,1)


                #########
                ### Histograms for AK4 jets
                var = 'AK4'
                StandardHistograms(cut, var)
                directories[cut+var] = directories[cut].mkdir(var)
                directories[cut+var].cd()

                histograms[cut][var] = {}

                histograms[cut][var]['Pt'] = TH1D('Pt','Pt',100,0,200)
                histograms[cut][var]['Eta'] = TH1D('Eta','Eta',100,0,5)
                histograms[cut][var]['Phi'] = TH1D('Phi','Phi',140,0,7)
                histograms[cut][var]['Mass'] = TH1D('Mass','Mass of separate AK4 jets',50,0,100)
                histograms[cut][var]['Num'] = TH1D('Num Separate AK4','Number of separate AK4 jets',32,0,32)

                #########
                ### Histograms for cuts 


        return Fyl, histograms, directories


def Analyze(histograms,combo,tmparrays):
        def ListFunction(this_list,index):
                return this_list[index]
        def Gettau21(it):
                if tree_vars['jetAK8Puppitau1'][it] != 0:
                        return tree_vars['jetAK8Puppitau2'][it]/tree_vars['jetAK8Puppitau1'][it]
                else:
                        return 0
	def VectorSum(vectors):
                return_vector = TLorentzVector()
                for vec in vectors:
                        return_vector+=vec
                return return_vector
	
	def NotH(it):
		 return ak8_vecs[it].M() <= 50 and tree_vars['jetAK8PuppiDoubleBAK8'][it] > .3
	def InvertedH(it):
		 return ak8_vecs[it].M() <= 50 and tree_vars['jetAK8PuppiDoubleBAK8'][it] <= .3
        def Special(it):
                def CheckMass(this_mass):
                        return 50 < tree_vars['jetAK8PuppiCorrectedsoftDropMass'][it]
                def CheckTau21(this_tau21):
                        return this_tau21 < .6
                def CheckPt(this_pt):
                        return this_pt > 200
                conditions = [CheckMass,CheckTau21,CheckPt]
                values = [tree_vars['jetAK8PuppiCorrectedsoftDropMass'][it],Gettau21(it),tree_vars['jetAK8PuppiPt'][it]]
                reasons = []
                good_jet = True
                for reas in range(0,len(conditions)):
                        if not conditions[reas](values[reas]):
                                reasons.append(1)
                                good_jet = False
                        else:
                                reasons.append(0)

                return good_jet, reasons

        def IsH(it):
                cut_group = my_cuts.cuts['variables']['all']
                boundaries = cut_group[cut_group.keys()[0]].boundaries
                def CheckMass(this_mass):
                        return boundaries[0] < tree_vars['jetAK8PuppiCorrectedsoftDropMass'][it] < boundaries[1]
                def CheckTau21(this_tau21):
                        return this_tau21 < boundaries[2]
                def CheckDoubleB(this_doubleb):
                        return this_doubleb > boundaries[3]
                def CheckPt(this_pt):
                        return this_pt > boundaries[4]
                conditions = [CheckMass,CheckTau21,CheckDoubleB,CheckPt]
                values = [tree_vars['jetAK8PuppiCorrectedsoftDropMass'][it],Gettau21(it),tree_vars['jetAK8PuppiDoubleBAK8'][it],tree_vars['jetAK8PuppiPt'][it]]
                reasons = []
                good_jet = True
                for reas in range(0,len(conditions)):
                        if not conditions[reas](values[reas]):
                                reasons.append(1)
                                good_jet = False
                        else:
				reasons.append(0)

                return good_jet, reasons

        def SpecialNot21(it):
                return 50 < tree_vars['jetAK8PuppiCorrectedsoftDropMass'][it]
        def FindBestFour():
                best = []
                count = 0
                for j in range(len(tree_vars['jetAK8PuppiCorrectedsoftDropMass'])):
                        is_special,reasons = Special(j)
                        for r in range(len(reasons)):
                                histograms[cut]['FailureReasons'].Fill(r,reasons[r])
                        if is_special:
                                best.append(j)
                                count+=1
                        if count == 4:
                                break
                return best
        def FindSpecials(condition=Special):
                best = []
                for j in range(len(ak8_vecs)):
                        is_special,reasons = condition(j)
                        for r in range(len(reasons)):
                                histograms[cut]['FailureReasons'].Fill(r,reasons[r])
                        if is_special:
                                best.append(j)
                return best
        def MakeTLorentzVector(var_dic,index,jet_type='AK8'):
                return_vec = TLorentzVector()
                branch_prefix = ''
                for branch_type in collections:
                        if branch_type.find('jets'+jet_type) != -1:
                                branches = collections[branch_type].keys()

                if branches[0].find(jet_type+'CHS') != -1:
                        branch_prefix += 'jet'+jet_type+'CHS'
                elif branches[0].find(jet_type+'Puppi') != -1:
                        branch_prefix += 'jet'+jet_type+'Puppi'

                energy = False
                sofdrop = False
                for branch in branches:
                        if branch[-1] == 'E':
                                energy = True
			if branch[-4:] == 'Mass':
                                if branch.find('CorrectedsoftDropMass') != -1:
                                        mass_suffix = 'CorrectedsoftDropMass'
                                elif branch.find('softDropMass') != -1:
                                        mass_suffix = 'softDropMass'
                                elif branch.find('Mass') != -1:
                                        mass_suffix = 'Mass'
                if var_dic[branch_prefix+'Pt'][index] == 0:
                        return None
                if energy:
                        return_vec.SetPtEtaPhiE(var_dic[branch_prefix+'Pt'][index],var_dic[branch_prefix+'Eta'][index],var_dic[branch_prefix+'Phi'][index],var_dic[branch_prefix+'E'][index])
                else:
                        return_vec.SetPtEtaPhiM(var_dic[branch_prefix+'Pt'][index],var_dic[branch_prefix+'Eta'][index],var_dic[branch_prefix+'Phi'][index],var_dic[branch_prefix+mass_suffix][index])
                return return_vec


        def AK4Indices(var_dic):
                return_indices = []
                #start = time.time()
                #for branch_type in collections:
                #       if branch_type[:7] == 'jetsAK4':
                #               AK4_branches = collections[branch_type].keys()
                #       elif branch_type[:7] == 'jetsAK8':
                #               AK8_branches = collections[branch_type].keys()
                #print 'first loop:',time.time()-start
                #start = time.time()
                #ak8_vecs = []
                #for i in range(len(var_dic[AK8_branches[0]])):
                #       ak8_vecs.append(MakeTLorentzVector(var_dic,i,jet_type='AK8'))
                #print 'second loop:', time.time()-start
                count = 0
                for ak4_vec in ak4_vecs:#range(len(var_dic[AK4_branches[0]])):
                        ok = True
                        #ak4_vec = ak4_vecs[i]#MakeTLorentzVector(var_dic,i,jet_type='AK4')

                        for ak8_vec in ak8_vecs:
                                if ak4_vec.DeltaR(ak8_vec) < .8:
                                        ok = False
                                        break
                        if ok and ak4_vec.Pt() != 0:
                                return_indices.append(count)
                        count += 1
                return return_indices

        def MatchHtoSpecial(Hs,Specials):
                return_pairs = [((Hs[0],Specials[0]),(Hs[1],Specials[1])),((Hs[0],Specials[1]),(Hs[1],Specials[0]))]
                H_vecs = [ak8_vecs[Hs[0]],ak8_vecs[Hs[1]]]
                special_vecs = [ak8_vecs[Specials[0]],ak8_vecs[Specials[1]]]

                mass_dif0 = abs((H_vecs[0]+special_vecs[0]).M() - (H_vecs[1]+special_vecs[1]).M())
                mass_dif1 = abs((H_vecs[0]+special_vecs[1]).M() - (H_vecs[1]+special_vecs[0]).M())

                #print mass_dif0,mass_dif1
                #print (H_vecs[0]+special_vecs[0]).M(), (H_vecs[1]+special_vecs[1]).M()
                #print (H_vecs[0]+special_vecs[1]).M(), (H_vecs[1]+special_vecs[0]).M()
                return return_pairs[int(mass_dif0 > mass_dif1)]

        def TwoEqualPairs(vectors,_print=False,asymmetry=2000,extra_vecs = []):
                all_pairs = []
                #case_three = len(vectors) == 3
                #if case_three:
                #       vectors.append(extra_vecs[0])

                for i in range(len(vectors)):
                        for j in range(i+1,len(vectors)):
                                all_pairs.append((i,j))

                good_pairs = []
                for i in range(len(all_pairs)):
                        for j in range(i+1,len(all_pairs)):
                                if len(all_pairs[i]) == 1 and len(all_pairs[j]) == 1:
                                        continue
                                this_good = True
                                for k in all_pairs[i]:
                                        for l in all_pairs[j]:
                                                if k == l:
                                                        this_good = False
                                if this_good:
                                        #if case_three:
                                        #       if len(all_pairs[i]) == 1:
                                        #               all_pairs[i].append(-1)
                                        #       else:
                                        #               all_pairs[j].append(-1)                                        					
					good_pairs.append((all_pairs[i],all_pairs[j]))
                minmass = asymmetry
                minmass_loc = -1
                count = 0
                tmp_masses = []
                is_pair = False
                for pairs in good_pairs:
                        newvec1 = VectorSum(map(vectors.__getitem__,pairs[0]))
                        newvec2 = VectorSum(map(vectors.__getitem__,pairs[1]))
                        mass_dif = abs(newvec1.M()-newvec2.M())
                        if mass_dif < minmass:
                                minmass = mass_dif
                                minmass_loc = count
                                tmp_masses = [newvec1.M(),newvec2.M()]
                        count+=1
                if minmass_loc == -1:
                        return None, None
                else:
                        return good_pairs[minmass_loc],minmass

        def MakeAllTVectors(var_dic):
                for branch_type in collections:
                        if branch_type[:7] == 'jetsAK4':
                                AK4_branches = collections[branch_type].keys()
                        elif branch_type[:7] == 'jetsAK8':
                                AK8_branches = collections[branch_type].keys()
                ak8_vecs = []
                ak4_vecs = []
                for i in range(len(var_dic[AK8_branches[0]])):
                        vec = MakeTLorentzVector(tree_vars,i,jet_type='AK8')
                        if vec != None:
                                ak8_vecs.append(vec)
                for i in range(len(var_dic[AK4_branches[0]])):
                        vec = MakeTLorentzVector(tree_vars,i,jet_type='AK4')
                        if vec != None:
                                ak4_vecs.append(vec)
                return ak8_vecs,ak4_vecs

        def GetCutVals(this_cut):
                return map(float,this_cut.split(',')[3:])


        def FillMatched(histo_direc,special_index):
                if not CheckSignal(options.set):
                        return
		maxtau21 = 0
                all_reasons = {'W':[0]*7,'Singlet':[0]*7}
                all_reasons_entries = {'W':[0]*7,'Singlet':[0]*7}
		num_matches_all = 0
                for part in ['W','Singlet']:
                        num_special_here = len(special_index)
                        num_matches = 0
                        for i in range(2):
                                num = tree_vars[part+'AK8'][i]
				if num != 0.:
					num_matches_all += 1
                                all_reasons[part][0] += int(num == 0.)
                                all_reasons_entries[part][0] += 1
                                if num != 0.:
                                        num_matches+=1
                                        ak8_num = int(num) - 1
                                        this_tau21 = Gettau21(ak8_num)
                                        if this_tau21 > maxtau21:
                                                maxtau21 = this_tau21
##### these steps make assumptions about cut because I am lazy
                                        if options.set == 'H' and part == 'W':
                                                rando_jets, some_reasons = IsH(ak8_num)

                                        else:
                                                rando_jets, some_reasons = Special(ak8_num)
                                        for x in range(len(some_reasons)):
                                                all_reasons[part][x+2] += some_reasons[x]
                                                all_reasons_entries[part][x+2] += 1
####
                                        histograms[cut][histo_direc+', '+part+' Pt'].Fill(tree_vars['jetAK8PuppiPt'][ak8_num])
                                        histograms[cut][histo_direc+', '+part+' Mass'].Fill(tree_vars['jetAK8PuppiCorrectedsoftDropMass'][ak8_num])
                                        histograms[cut][histo_direc+', '+part+' tau21'].Fill(this_tau21)
                                        histograms[cut][histo_direc+', '+part+' deviance'].Fill(tree_vars[part+'AK8Deviance'][i]-1)
                                        histograms[cut][histo_direc+', '+part+' doubleb'].Fill(tree_vars['jetAK8PuppiDoubleBAK8'][ak8_num])
                                        if ak8_num not in special_index:
                                                histograms[cut][histo_direc+', Not Special, '+part+' Pt'].Fill(tree_vars['jetAK8PuppiPt'][ak8_num])
                                                histograms[cut][histo_direc+', Not Special, '+part+' Mass'].Fill(tree_vars['jetAK8PuppiCorrectedsoftDropMass'][ak8_num])
                                                histograms[cut][histo_direc+', Not Special, '+part+' tau21'].Fill(this_tau21)
                                                histograms[cut][histo_direc+', Not Special, '+part+' deviance'].Fill(tree_vars[part+'AK8Deviance'][i]-1)
                                                histograms[cut][histo_direc+', Not Special, '+part+' doubleb'].Fill(tree_vars['jetAK8PuppiDoubleBAK8'][ak8_num])


                                        else:
                                                histograms[cut][histo_direc+', Special, '+part+' Pt'].Fill(tree_vars['jetAK8PuppiPt'][ak8_num])
                                                histograms[cut][histo_direc+', Special, '+part+' Mass'].Fill(tree_vars['jetAK8PuppiCorrectedsoftDropMass'][ak8_num])
                                                histograms[cut][histo_direc+', Special, '+part+' tau21'].Fill(this_tau21)
                                                histograms[cut][histo_direc+', Special, '+part+' deviance'].Fill(tree_vars[part+'AK8Deviance'][i]-1)
                                                histograms[cut][histo_direc+', Special, '+part+' doubleb'].Fill(tree_vars['jetAK8PuppiDoubleBAK8'][ak8_num])
                        histograms[cut][histo_direc+', '+part+' matches'].Fill(0,num_matches)
                        histograms[cut][histo_direc+', '+part+' matches'].Fill(1,1)
                        map(lambda x: histograms[cut][histo_direc+', Failure'].Fill(x,all_reasons[part][x]),range(len(all_reasons[part])))
                        map(lambda x: histograms[cut][histo_direc+', Failure Normalization'].Fill(x,all_reasons_entries[part][x]),range(len(all_reasons_entries[part])))
                        map(lambda x: histograms[cut][histo_direc+', Failure'+part].Fill(x,all_reasons[part][x]),range(len(all_reasons[part])))
                        map(lambda x: histograms[cut][histo_direc+', Failure Normalization'+part].Fill(x,all_reasons_entries[part][x]),range(len(all_reasons_entries[part])))
		histograms[cut][histo_direc+', Failure'].Fill(1, int(len(ak8_vecs)<4) * (4-len(ak8_vecs)) )
		histograms[cut][histo_direc+', Failure Normalization'].Fill(1,1)
                histograms[cut][histo_direc+', maxtau21'].Fill(maxtau21)

        def DoAK4():
                AK4_indices = AK4Indices(tree_vars)
                histograms[cut]['AK4']['Num'].Fill(len(AK4_indices))
                for i in AK4_indices:
                        histograms[cut]['AK4']['Pt'].Fill(ak4_vecs[i].Pt())
                        histograms[cut]['AK4']['Eta'].Fill(ak4_vecs[i].Eta())
                        histograms[cut]['AK4']['Phi'].Fill(ak4_vecs[i].Phi())
                        histograms[cut]['AK4']['Mass'].Fill(ak4_vecs[i].M())

	def FindHiggsNeutralinos(specials,Hs):
		specials = [x for x in specials if x not in Hs]
		num_special = len( specials)
		num_H = len(Hs)
		histograms[cut]['NumSpecialNotH'].Fill(num_special)
		histograms[cut]['NumH'].Fill(num_H)
		if num_H > 1 and num_special > 1:
			pairs = MatchHtoSpecial(Hs,specials)
			neut1 = VectorSum([ak8_vecs[pairs[0][0]],ak8_vecs[pairs[0][1]]])
			neut2 = VectorSum([ak8_vecs[pairs[1][0]],ak8_vecs[pairs[1][1]]])
			histograms[cut]['HNeutralinoMass'].Fill(neut1.M())
			histograms[cut]['HNeutralinoMass'].Fill(neut2.M())

	def EstimateBackground():
		def CheckIsH( jetnum ):
			return IsH(jetnum)[0]
		def AnyJet( jetnum ):
			return True
		otherjets = [AnyJet,CheckIsH,InvertedH,NotH]
		def FillTypes(eventselection,jetNum):
			for ci in range(len(otherjets)):
				if otherjets[ci](jetNum):
					histograms[cut][eventselection+'Prediction'].Fill(ci,1)
					FillCharacteristics(eventselection+fakenames[ci],jetNum)
					#FillCharacteristics(eventselection+'OtherIs'+fakenames[ci],jetNum)
				
			#if IsH( jetNum )[0]:
			#	histograms[cut]['Prediction'].Fill(3,1)
			#	FillCharacteristics(eventselection+'OtherIsH',jetNum)
			#elif InvertedH( jetNum ):
			#	histograms[cut]['Prediction'].Fill(2,1)
			#	FillCharacteristics(eventselection+'OtherIsLowMassH',jetNum)
			#elif NotH( jetNum ):
			#	histograms[cut]['Prediction'].Fill(1,1)
			#	FillCharacteristics(eventselection+'OtherIsNotH',jetNum)
			
		not_found = True
		if len(ak8_vecs) < 2:
			return
		for i in [0,1]:
			other = (i+1)%2
			if i == 0:
				FillTypes('NoB',other)
			
			if NotH(i) and not_found:
				FillTypes('',other)
				not_found = False
		new_specials = [x for x in specials if x not in Hs]
		num_special = len(new_specials)
		
		founds = [False for asdfasd in otherjets]
		if num_special >= 2 and num_H == 1 and len(ak8_vecs) > 3:
			for i in not_anything:
				for ci in range(len(otherjets)):
					if not founds[ci] and otherjets[ci](i):
						for p in ['H','S1','S2']:
							current_i = Hs[0] if p == 'H' else new_specials[int(p[1])-1]
							tmparrays[fakenames[ci]][p]['Pt'][0] = ak8_vecs[current_i].Pt()
							tmparrays[fakenames[ci]][p]['Eta'][0] = ak8_vecs[current_i].Eta()
							tmparrays[fakenames[ci]][p]['Phi'][0] = ak8_vecs[current_i].Phi()
							tmparrays[fakenames[ci]][p]['M'][0] = ak8_vecs[current_i].M()
							tmparrays[fakenames[ci]][p]['t21'][0] = Gettau21(current_i)
							tmparrays[fakenames[ci]][p]['db'][0] = tree_vars['jetAK8PuppiDoubleBAK8'][current_i] 
						tmparrays[fakenames[ci]]['NH']['Pt'][0] = ak8_vecs[i].Pt()
						tmparrays[fakenames[ci]]['NH']['Eta'][0] = ak8_vecs[i].Eta()
						tmparrays[fakenames[ci]]['NH']['Phi'][0] = ak8_vecs[i].Phi()
						tmparrays[fakenames[ci]]['NH']['M'][0] = ak8_vecs[i].M()
						tmparrays[fakenames[ci]]['NH']['t21'][0] = Gettau21(i)
						tmparrays[fakenames[ci]]['NH']['db'][0] = tree_vars['jetAK8PuppiDoubleBAK8'][i] 
						histograms[cut]['TreeFakeEvents'+fakenames[ci]].Fill()
						founds[ci] = True
						new_specials = [x for x in specials if x not in Hs]
						pairs = MatchHtoSpecial(Hs+[i],new_specials)
						histograms[cut]['PredictionMass'+fakenames[ci]].Fill((ak8_vecs[pairs[0][0]]+ak8_vecs[pairs[0][1]]).M())
						histograms[cut]['PredictionMass'+fakenames[ci]].Fill((ak8_vecs[pairs[1][0]]+ak8_vecs[pairs[1][1]]).M())
						
				#if NotH(i):
				#	new_specials = [x for x in specials if x not in Hs]
				#	pairs = MatchHtoSpecial(Hs+[i],new_specials)
				#	histograms[cut]['PredictionMass'].Fill((ak8_vecs[pairs[0][0]]+ak8_vecs[pairs[0][1]]).M())
				#	histograms[cut]['PredictionMass'].Fill((ak8_vecs[pairs[1][0]]+ak8_vecs[pairs[1][1]]).M())
			
			

	def FillCharacteristics(group,index):
		histograms[cut][group+'Pt'].Fill(ak8_vecs[index].Pt())
		histograms[cut][group+'Mass'].Fill(ak8_vecs[index].M())
		histograms[cut][group+'Eta'].Fill(ak8_vecs[index].Eta())
		histograms[cut][group+'Phi'].Fill(ak8_vecs[index].Phi())
		histograms[cut][group+'doubleb'].Fill(tree_vars['jetAK8PuppiDoubleBAK8'][index])

        histograms['CutsCounts'].Fill(0,1)
        cut_count = 0
        ak8_vecs, ak4_vecs = 0,0
        first_cut = True
        for cut in my_cuts.GetCombinations()+['No Cut']:
                if cut == 'No Cut' or cuts_vals[cut] == 1:
                        histograms['CutsCounts'].Fill(cut_count,1)
                        if first_cut:
                        #       start = time.time()
                                ak8_vecs, ak4_vecs = MakeAllTVectors(tree_vars)
                                first_cut = False
                        #       print 'make vectors:',time.time()-start
                        #nogood = False
                        #for vec in ak4_vecs:
                        #       if vec.Pt() != 0:
                        #               print vec.Pt()
                        #               nogood = False
                        #       elif not nogood:
                        #               nogood = True
                        #               print '-'
                        ht = 0
			histograms[cut]['NumAK8'].Fill(len(ak8_vecs))
			histograms[cut]['NumAK4'].Fill(len(ak4_vecs))
                        for i in range( min(6,len(ak8_vecs) )):
                        #       
                                tau21 = Gettau21(i)
                                doubleb = tree_vars['jetAK8PuppiDoubleBAK8'][i]                       			#       histograms[cut+ ' top four']['AK8']['tau21'].Fill(tau21)
                        #       histograms[cut+ ' top four']['AK8']['softDropMass'].Fill(ak8_vecs[i].M())
                        #       histograms[cut+ ' top four']['AK8']['Pt'].Fill(ak8_vecs[i].Pt())
                        #       histograms[cut+ ' top four']['AK8']['Eta'].Fill(ak8_vecs[i].Eta())
                        #       histograms[cut+ ' top four']['AK8']['Phi'].Fill(ak8_vecs[i].Phi())
                        #       ht+=ak8_vecs[i].Pt()

                                histograms[cut+ ' single jets']['tau21 '+str(i)].Fill(tau21)
                                histograms[cut+ ' single jets']['pt '+str(i)].Fill(ak8_vecs[i].Pt())
                                histograms[cut+ ' single jets']['mass '+str(i)].Fill(ak8_vecs[i].M())
                                histograms[cut+ ' single jets']['doubleb '+str(i)].Fill(doubleb)
                        #print 'top four:',time.time()-start

                        #histograms[cut]['AK8HT'].Fill(ht)
                        #num_special = 0
                        if CheckSignal(options.set):
                                for i in range(len(ak8_vecs)):
                                        if Special(i)[0]:
                        #                       num_special += 1
                                                histograms[cut]["SpecialJet"].Fill(tree_vars['GluinoMass'][0],tree_vars['CharginoMass'][0])
                                histograms[cut]["SpecialJetCount"].Fill(tree_vars['GluinoMass'][0],tree_vars['CharginoMass'][0])
                        else:
                                for i in range(len(ak8_vecs)):
                                        if Special(i)[0]:
                        #                       num_special += 1
                                                histograms[cut]["SpecialJet"].Fill(.5)
                                histograms[cut]["SpecialJetCount"].Fill(.5)
                        specials = FindSpecials()
                        Hs = FindSpecials(condition=IsH)
                        vecs = []
                        maxt21 = 0
                        num_special = len(specials)
                        num_H = len(Hs)
                        histograms[cut]['NumSpecial'].Fill(num_special)
                        histograms[cut]['NumSpecial'].Fill(num_special)
                        for i in specials:
                                vecs.append(ak8_vecs[i])
                                if Gettau21(i) > maxt21: maxt21 = Gettau21(i)
                        not_vecs = []
                        not_specials = []
                        for i in range(len(ak8_vecs)):
                                if i not in specials:
                                        not_vecs.append(ak8_vecs[i])
                                        not_specials.append(i)
			not_anything = []
			for i in range(len(ak8_vecs)):
				if i not in Hs and i not in specials:
					not_anything.append(i)
                        histograms[cut]['AK8largesttau21'].Fill(maxt21)
                        if num_special >= 3:
                                ht = 0
                                should_print = False
                                if num_special == 3 and not_vecs != []:
                                        vecs.append(not_vecs[0])
					difs = []
					for som_index in range(len(not_vecs)):
						other_vec = not_vecs[som_index]
						difs.append((TwoEqualPairs(vecs+[other_vec],False,asymmetry=2000),som_index))
					best_pair_info = min(difs,key=lambda x: x[0][1])
					vecs.append(not_vecs[best_pair_info[1]])
					pairs, mass_dif = best_pair_info[0]
				else:
					pairs, mass_dif = TwoEqualPairs(vecs,should_print,asymmetry=2000)

                                if pairs == None:
                                        continue
                                for i in range(len(pairs)):
                                        for j in pairs[i]:
                                                ht += vecs[j].Pt()#tree_vars['jetAK8PuppiPt'][j]
                                histograms[cut]['AK8HTSpecial'].Fill(ht)
                                neut1 = VectorSum(map(vecs.__getitem__,pairs[0]))
                                neut2 = VectorSum(map(vecs.__getitem__,pairs[1]))
                                histograms[cut]['NeutralinoMass'].Fill(neut1.M())
                                histograms[cut]['NeutralinoMass'].Fill(neut2.M())
                                histograms[cut]['MassAsyNeutralinoMass'].Fill(neut1.M(),mass_dif)
                                histograms[cut]['MassAsyNeutralinoMass'].Fill(neut2.M(),mass_dif)



                        FillMatched('Matched Attributes',specials)

			FindHiggsNeutralinos(specials,Hs)

                        DoAK4()

			EstimateBackground()

                cut_count+=1

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


if options.grid:
        di = 'tardir/'
else:
        di = ''

Run_Info, tree_file = DealWithOptions()

print '/uscms_data/d3/mirkovic/CMSSW_8_0_10_patch2/src/CutsAnalysis/data/'+options.set+'/'+tree_file
tfile = TFile('/uscms_data/d3/mirkovic/CMSSW_8_0_10_patch2/src/CutsAnalysis/data/'+options.set+'/'+tree_file,'READ')
tree = tfile.Get('tree')

if options.grid:
        my_cuts = Cuts.CutsCollection('tardir/bin/cuts')
else:
        my_cuts = Cuts.CutsCollection('bin/cuts')

collections, types = TreeVarsCollections()

tree_vars = SetBranches(tree)
my_signals = Cuts.CutsCollection(di+'bin/'+options.set+'Regions')
fakenames = ['Any','H','InvertedH','LowMassH']
F = {}
ComboHistograms = {}
ComboDirectories = {}
tmparrays = {}
for i in ['H','NH','S1','S2']:
	for j in ['Pt','Eta','Phi','M','t21','db']:
		tmparrays[i] = {}
for combo in my_signals.GetCombinations()+['All'+options.set]:
        F[combo],ComboHistograms[combo],ComboDirectories[combo] = MakeHistograms(combo,tmparrays)
count = 0
saved = 0
not_saved = 0
for ev in tree:
        #if count == 2000:
        #       break
        #count+=1
	#print count
        my_cuts.CheckAllCuts(tree_vars)
        my_signals.CheckAllCuts(tree_vars)
        cuts_vals = my_cuts.GetComboResults()
        signal_vals = my_signals.GetComboResults()
        for combo in my_signals.GetCombinations()+['All'+options.set]:
                if combo == 'All'+options.set or signal_vals[combo]:
                        Analyze(ComboHistograms[combo],combo,tmparrays)
print 'done'
for fyl in F:
	for cut in ComboHistograms[fyl]:
		for histo in ComboHistograms[fyl][cut]:
			if type(histo) == str and len(histo) > 3:
				if histo[1:4] == 'ree':
					print histo
					ComboHistograms[fyl][cut][histo].Write()
        F[fyl].Write()
        F[fyl].Close()





