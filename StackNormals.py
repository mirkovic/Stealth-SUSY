import ROOT
from ROOT import TFile,TDirectory,TH1D,TH1I,TH2D,TH2I,TCanvas,kTRUE,TLegend
import os
from optparse import OptionParser
import lib.Cuts as Cuts
import time

ROOT.gROOT.SetBatch(kTRUE)
def GetFileGroups(file_name):
	if file_name == '':
		signal_regions = Cuts.CutsCollection('bin/SignalRegions').GetCombinations()
		signal_regions.append('AllSignal')
		qcd_regions = ['AllQCD']
		ttbar_regions = ['AllTTBAR']
		H_regions = ['AllH']
		groups = {}
		for i in signal_regions:
			groups[i] = ['plots/Signal/'+i+'.root', 'plots/QCD/'+qcd_regions[0]+'.root', 'plots/TTBAR/'+ttbar_regions[0]+'.root','plots/H/'+H_regions[0]+'.root']
			print groups[i]
		return groups
		
def CreateTH1s(root_file,other_file='',mimic=False):
	structures = {}
	structures['dir'] = {}
	structures['TH1'] = {}
	structures['TH2'] = {}
	structures['TH1']['maindir'] = {}
	structures['TH2']['maindir'] = {}
	if mimic:
		F = TFile(root_file, 'RECREATE')
		F_other = TFile(other_file,'READ')
		main_path = F_other.GetPath()
		structures['histodump'] = F.mkdir('histodump')
	else:
		F = TFile(root_file,'READ')
		main_path = F.GetPath()
	structures['dir']['maindir'] = F

	if mimic:
		loop_folders = [F_other]
	else:
		loop_folders = [F]
	while len(loop_folders) != 0:
		new_folders = []
		for i in loop_folders:
			for item in i.GetListOfKeys():
				item = item.ReadObj()
				if item.InheritsFrom('TDirectoryFile'):
					parent_path = i.GetPath()
					this_path = item.GetPath()
					if this_path == main_path:
						this_path = 'maindir'
					else:
						this_path = this_path.split(':')[1]
					if parent_path == main_path:
						parent_path = 'maindir'
					else:
						parent_path = parent_path.split(':')[1]
					new_folders.append(item)
					if mimic:
						structures['dir'][this_path] = structures['dir'][parent_path].mkdir(item.GetName())
						structures['TH1'][this_path] = {}
						structures['TH2'][this_path] = {}
					else:
						structures['dir'][this_path] = item
						structures['TH1'][this_path] = {}
						structures['TH2'][this_path] = {}
		loop_folders = new_folders
	if mimic:
		loop_folders = [F_other]
	else:
		loop_folders = [F]
	while len(loop_folders) != 0:
		new_folders = []
		for i in loop_folders:
			for item in i.GetListOfKeys():
				item = item.ReadObj()
				if item.InheritsFrom('TDirectoryFile'):
					new_folders.append(item)
				if item.InheritsFrom('TH1'):
					this_path = i.GetPath()
					if this_path == main_path:
						this_path = 'maindir'
					else:
						this_path = this_path.split(':')[1]
					if mimic:
						structures['dir'][this_path].cd()
						structures['TH1'][this_path][item.GetName()] = TCanvas(item.GetName())
						structures['TH1'][this_path][item.GetName()].Close()
					else:
						structures['TH1'][this_path][item.GetName()] = item
				if item.InheritsFrom('TH2'):
					this_path = i.GetPath()
					if this_path == main_path:
						this_path = 'maindir'
					else:
						this_path = this_path.split(':')[1]
					if mimic:
						structures['dir'][this_path].cd()
						structures['TH2'][this_path][item.GetName()+F_other.GetName()]=item
						item.Write(item.GetName()+F_other.GetName()) 
						print F_other.GetName()
					else:
						structures['TH2'][this_path][item.GetName()+F.GetName()]=item
						
		loop_folders = new_folders
	return structures
			
	

def AddToCanvases(mimic, other_group):
	for canvas_folder in mimic['TH1'].keys():
		for canvas in mimic['TH1'][canvas_folder].keys():
			ROOT.gPad = mimic['TH1'][canvas_folder][canvas]
			legend = TLegend(.8,1,1,.8)
			mimic['histodump'].cd()
			for group in range(len(other_group)):
#### this next thing might be real sketchy
				try:
					norm = other_group[group]['TH1'][canvas_folder][canvas].Integral()
					if norm == 0:
						norm = 1
					other_group[group]['TH1'][canvas_folder][canvas].Scale(1./norm)
					other_group[group]['TH1'][canvas_folder][canvas].Write(other_group[group]['TH1'][canvas_folder][canvas].GetName()+other_group[group]['dir']['maindir'].GetName())
					other_group[group]['TH1'][canvas_folder][canvas].Draw('same')
					if group < 3:
						color_code = group+2
					else:
						color_code = group+3
					other_group[group]['TH1'][canvas_folder][canvas].SetLineColor(color_code)
					legend.AddEntry(other_group[group]['TH1'][canvas_folder][canvas],Names(group),'l')
				except:
					pass

			ROOT.gPad = mimic['TH1'][canvas_folder][canvas]
			legend.Draw()
			legend.Write()
				
			mimic['dir'][canvas_folder].cd()
			mimic['TH1'][canvas_folder][canvas].Write()
			

def Names(data_index):
	if data_index == 0:
		return 'Signal'
	elif data_index == 1:
		return 'QCD'
	elif data_index == 2:
		return 'ttbar'
	elif data_index == 3:
		return 'H'

parser = OptionParser()


parser.add_option('-f', metavar='F', type='string', action='store',
                  default       =       '',
                  dest          =       'files',
                  help          =       'list of root files to stack')

parser.add_option('-j', '--files', metavar='F', type='string', action='store',
                  default       =       '0-1',
                  dest          =       'j',
                  help          =       'selects which files to scan')

parser.add_option('--notnormal',action='store_false',dest='normalize')

parser.set_defaults(normalize=True)

(options, args) = parser.parse_args()


fyls = GetFileGroups(options.files)
structures = {}
combined_structures = {}

for group in fyls:
	structures[group] = []
	for fyl in fyls[group]:
		structures[group].append( CreateTH1s(fyl) )

	combined_structures[group] = CreateTH1s(fyls[group][0].replace('/Signal',''), other_file=fyls[group][0], mimic = True)
for group in fyls:
	AddToCanvases(combined_structures[group],structures[group])
for group in fyls:
	combined_structures[group]['dir']['maindir'].Write()
time.sleep(5)	

