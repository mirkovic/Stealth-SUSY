#!/bin/sh

python Flist.py
tar czvf tarball.tgz Files_susy*.txt TreeUpdater.py TreeLooper.py lib bin

./development/runManySections.py --createCommandFile --cmssw --addLog --setTarball=tarball.tgz \susy.listOfJobs commands.cmd
./runManySections.py --submitCondor commands.cmd

condor_q mirkovic
