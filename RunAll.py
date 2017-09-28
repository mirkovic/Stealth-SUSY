import os
import glob
import time
import subprocess
from optparse import OptionParser

parser = OptionParser()

parser.add_option('--trees',action='store_true',dest='trees')
parser.set_defaults(trees=False)

(options, args) = parser.parse_args()

if options.trees:
	program = 'TreeUpdater.py'
else:
	program = 'TreeLooper.py'
fyl = open('bin/format','r')
lines=fyl.read().split('\n')

num_signal = int(lines[0].split('num_signal=')[1])
num_qcd = int(lines[1].split('num_qcd=')[1])
num_ttbar = int(lines[2].split('num_ttbar=')[1])
num_h = int(lines[3].split('num_h=')[1])
os.system('python CommandsGenerator.py -n '+str(num_signal)+' --disorganize -s Signal -f Signal -p '+program)
os.system('python CommandsGenerator.py -n '+str(num_qcd)+' --append --disorganize -s QCD -f QCD -p '+program)
os.system('python CommandsGenerator.py -n '+str(num_ttbar)+' --append --disorganize -s TTBAR -f TTBAR -p '+program)
os.system('python CommandsGenerator.py -n '+str(num_h)+' --append --disorganize -s H -f H -p '+program)
os.system('python cleanup.py') 

subprocess.call('. ~/Cuts/grid_susy_sub.csh',shell=True)
exit()
command = 'python RunOnGrid.py --nocommands -p '+program+' -s All -n '+str(num_signal+num_qcd+num_ttbar)
os.system(command)
print command

this_time = 0
while len(glob.glob('output*')) != num_signal:
        time.sleep(5)
        this_time+=5
        if this_time%30 == 0:
                print str(this_time) + ' seconds'
os.system('python cleanup.py')

command = 'python RunOnGrid.py -p '+program+' -s QCD -n '+str(num_qcd)
os.system(command)
print command

this_time = 0
while len(glob.glob('output*')) != num_qcd:
        time.sleep(5)
        this_time+=5
        if this_time%30 == 0:
                print str(this_time) + ' seconds'
os.system('python cleanup.py')

command = 'python RunOnGrid.py -p '+program+' -s TTBAR -n '+str(num_ttbar)
os.system(command)
print command

this_time = 0
while len(glob.glob('output*')) != num_ttbar:
        time.sleep(5)
        this_time+=5
        if this_time%30 == 0:
                print str(this_time) + ' seconds'
os.system('python cleanup.py')

print 'done'
