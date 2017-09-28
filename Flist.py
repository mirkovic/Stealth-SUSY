#! /usr/bin/env python

import os
import sys
from DataFormats.FWLite import Events, Handle
from optparse import OptionParser
from array import *
import glob

parser = OptionParser()

parser.add_option('-s','--set', metavar='F', type='string', action='store',
                  default       =       'Signal',
                  dest          =       'set',
                  help          =       'dataset to analyze')

(options, args) = parser.parse_args()

def ChoseFolder():
	files_folder = []
        #signal_folder = '/eos/uscms/store/group/lpcrutgers/knash/SMS-T7WgStealth_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_SMS-T7WgStealth_GENfiltered_take1_Slim_V11/170609_175318/0000/'
        #QCD_folder = '/eos/uscms/store/group/lpcrutgers/knash/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Slim_V12/170718_151248/0000/' 
        #TTBAR_folder = '/eos/uscms/store/group/lpcrutgers/knash/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/crab_TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_Slim_V11/170609_184530/*/'
	signal_folder = '/eos/uscms/store/group/lpcrutgers/knash/SMS-T7WgStealth_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_SMS-T7WgStealth_GENfiltered_take1_Slim_V12/170724_161057/0000/' 
	QCD_folder = '/eos/uscms/store/group/lpcrutgers/knash/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_Slim_V12/170718_151248/0000/' 
	TTBAR_folder = '/eos/uscms/store/group/lpcrutgers/knash/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/crab_TT_TuneCUETP8M2T4_13TeV-powheg-pythia8_Slim_V12/170718_162356/0000/' 
	H_folder = '/eos/uscms/store/group/lpcrutgers/knash/GGtoHH_1500_1400_100/crab_GGtoHH_1500_1400_100_Slim_V12/170731_184031/0000/'

	if options.set == 'Signal':
		files_folder = [signal_folder]
	elif options.set == 'QCD':
		files_folder = [QCD_folder]
	elif options.set == 'TTBAR':
		files_folder = [TTBAR_folder]
	elif options.set == 'H':
		files_folder = [H_folder]
	elif options.set == 'All':
		files_folder = [signal_folder,QCD_folder,TTBAR_folder,H_folder]

	return files_folder
saveout = sys.stdout
#Based on what set we want to analyze, we find all Ntuple root files 


Outf1   =   open('Files_susy_'+options.set+'.txt', "w")

sys.stdout = Outf1
files = []
folders = ChoseFolder()
for folder in folders: 
	files += glob.glob(folder+'*')
for file1 in files:
	if file1.find("root")!=-1:
		print file1
sys.stdout = saveout
Outf1.close()

