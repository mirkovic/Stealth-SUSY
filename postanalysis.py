from ROOT import TFile, TDirectory, TH1D, gPad, TCanvas, TLorentzVector
import time
import glob
from array import array

def FindTheseMasses(some_branches):
	vectors = {}
	for part in ['H','NH','S1','S2']:
		coords = []
		vectors[part] = TLorentzVector()

		for data in ['Pt','Eta','Phi','M']:
			coords.append(some_branches[part][data][0])

		vectors[part].SetPtEtaPhiM(*coords)
	
	pairs = MatchHToSinglet( [vectors['H'],vectors['NH']] , [vectors['S1'],vectors['S2']] )
	mass0 = ( pairs[0][0] + pairs[0][1] ).M()
	mass1 = ( pairs[1][0] + pairs[1][1] ).M()
	
	return [mass0,mass1]
	
def MatchHToSinglet(Hs,Singlets):
	return_pairs = [((Hs[0],Singlets[0]),(Hs[1],Singlets[1])),((Hs[0],Singlets[1]),(Hs[1],Singlets[0]))]

	mass_dif0 = abs((Hs[0]+Singlets[0]).M() - (Hs[1]+Singlets[1]).M())
	mass_dif1 = abs((Hs[0]+Singlets[1]).M() - (Hs[1]+Singlets[0]).M())

	return return_pairs[int(mass_dif0 > mass_dif1)]

#### ******* This method assumes information about the histogram *******
def GetBinNumber(val):
	return int( .03125 * val  ) + 1
	
fyl_names = ['plots/QCD/AllQCD.root', 'plots/H/AllH.root', 'plots/TTBAR/AllTTBAR.root'] + glob.glob('plots/Signal/*.root')
fyls = []
#new_fyls = []
for fyl in fyl_names:
	print fyl
	fyls.append(TFile(fyl,'UPDATE'))
#	new_fyls.append(TFile(fyl.split('/')[-1][:-5],'RECREATE'))



fakenames = ['Any','H','InvertedH','LowMassH']

tmpcanvas = TCanvas()
F = TFile('BackgroundEstimation.root','RECREATE')
print gPad
for f in fyls:
	print f.GetName()
	f_name = f.GetName().split('/')[-1]
	print f_name
	this_directory = f.FindObjectAny('cuts').FindObjectAny('No Cut')
	trees = {}
	entries = {}
	for i in fakenames:
#### Find tree
		fake_directory = this_directory.FindObjectAny(i)
		trees[i] = fake_directory.FindObjectAny(i)
#### Create Pt Fake Rate Histogram
		this = fake_directory.FindObjectAny('Pt')
		entries[i] = this
		

#### Calculate Pt Ratio Histograms
	num_den_list = [('H','InvertedH'),('H','Any'),('H','LowMassH')]
	rates = {}
	for ratio in num_den_list:
		ratio_name = ratio[0] + '/' + ratio[1]
#### Calculate Pt rates
		den = entries[ratio[1]]
		rate = entries[ratio[0]].Clone()
		rate.Divide(den)

#### Use this to obtain Fake event details
		branches = {}
		for part in ['H','NH','S1','S2']:
			branches[part] = {}
			for data in ['Pt','Eta','Phi','M']:
				branches[part][data] = array('d',[0])
				trees[ratio[1]].SetBranchAddress(part+data,branches[part][data])
				
#### Make Mass Estimation Histogram
		MassEstimation = TH1D(f_name+', Prediction from '+ratio[1]+' to '+ratio[0],f_name+', Prediction from '+ratio[1]+' to '+ratio[0],50,0,1600)


		count = 0
		for ev in trees[ratio[1]]:
			try:
				this_ratio = rate.GetBinContent(GetBinNumber(branches['NH']['Pt'][0]))
			except:
				#print branches['NH']['Pt'][0]
				continue
			masses = FindTheseMasses(branches)
			MassEstimation.Fill(masses[0],this_ratio)
			MassEstimation.Fill(masses[1],this_ratio)
			count += 1
		#print count

		F.cd()
		MassEstimation.Write()
		rate.SetTitle(ratio_name)
		rate.SetName(f_name + ', ' + ratio_name)
		rate.Write()
			


#### Create fake rates by Pt

		
	#den = this_directory.FindObjectAny('OtherIsNotH').FindObjectAny('Pt')	
	#num = this_directory.FindObjectAny('OtherIsH').FindObjectAny('Pt')	
	#this_directory.cd()
	#num.Divide(den)
	#num.Write('Pt Not H / Pt of H')
