import ROOT
from ROOT import TLorentzVector
from DataFormats.FWLite import Events, Handle

#def EventsElsewhere(files):
#	return Events(files)
def TLV( dic, num, method = 'PtEtaPhiM'):
	vec = TLorentzVector()
	if method == 'PtEtaPhiM':
		vec.SetPtEtaPhiM(dic['pt'][num],dic['eta'][num],dic['phi'][num],dic['mass'][num])
	if method == 'PtEtaPhiE':
		vec.SetPtEtaPhiE(dic['pt'][num],dic['eta'][num],dic['phi'][num],dic['mass'][num])
	return vec

def DeltaRLists(list1,list2,method='PtEtaPhiM'):
	vec1 = TLorentzVector()
	vec2 = TLorentzVector()
	if method == 'PtEtaPhiM':
		vec1.SetPtEtaPhiM(list1[0],list1[1],list1[2],list1[3])
		vec2.SetPtEtaPhiM(list2[0],list2[1],list2[2],list2[3])
	if method == 'PtEtaPhiE':
		vec1.SetPtEtaPhiE(list1[0],list1[1],list1[2],list1[3])
		vec2.SetPtEtaPhiE(list2[0],list2[1],list2[2],list2[3])
	return vec1.DeltaR(vec2)
def MinMass(mass, othermasses):
	mindif = mass
	loc = 0
	for i in range(0,len(othermasses)):
		o = othermasses[i]
		if abs(mass-o) < mindif:
			mindif = abs(mass-o)
			loc = i
	return loc

def MinMomDif(mome, othermome):
	mindif = mome.Mag()
	loc = 0
	for i in range(0,len(othermome)):	
		o = othermome[i]
		dif = mome-o
		mag = dif.Mag()
		if mag < mindif:
			mindif = mag
			loc = i
	return loc
def SortMasses(mass, othermasses):
	mindif = mass
	others
	
def SortByPt(vecs):
	dic = {}
	

	for vec in vecs:
		dic[vec[0]] = vec
	orderedpt = sorted(list(dic.keys()))

	finvecs = []
	for pt in orderedpt:
		finvecs.append(dic[pt])

	return finvecs
			
def SecondMinJetError( vecs_with_match, vecs_get_match, matchdifferent = True, requirement = .4,):
	if len(vecs_with_match) == 0 or len(vecs_get_match) == 0:
		return [{},[]]
	
	if type(vecs_with_match[0]) != tuple:
		first_id = []
		second_id = []
		for i in range(len(vecs_with_match)):
			first_id.append((i,vecs_with_match[i]))
		for i in range(len(vecs_get_match)):
			second_id.append((i,vecs_get_match[i]))
	else:
		first_id = vecs_with_match
		second_id = vecs_get_match

	links = {}
	final_errors = {}
	while len(first_id) != 0 and len(second_id) != 0:
		minerrors = [] 
		for vec1 in first_id:
			errors = []
			for vec2 in second_id:
				errors.append((vec1,vec2,vec1[1].DeltaR(vec2[1])))
			
			minerrors.append(min(errors,key=lambda x: x[2]))
	
		most_min = requirement
		first_index = None
		for i in range(len(minerrors)):
			if minerrors[i][2] < most_min:
				most_min = minerrors[i][2]
				first_index = i
		if first_index == None:
			break
		else:
			id1 = minerrors[first_index][0][0]
			id2 = minerrors[first_index][1][0]
			this_error = minerrors[first_index][2]
			links[id1] = id2
			final_errors[id1] = this_error
			first_id.remove(minerrors[first_index][0])
			second_id.remove(minerrors[first_index][1])
	return links,final_errors	

	
#Takes list of lorentz vectors and uses other function as a qay to measure error
def MinJetError(myjets, montejets, matchdifferent = True, requirement = 4, extra = 0):
	if extra > 10:
		raise Exception()
	#if extra == -1:
	#	print 'best'
	#	print
	#elif extra == -2:
	#	print 'pair'
	#	print
	#else:
	#	print 'initial call'
	#	print
	#print 'my jets:', myjets
	#print
	#print 'monte jets:',montejets
	#print
	#print '\n\n'
	if len(myjets) == 0 or len(montejets) == 0:
		return [{},[]]
	montejets = list(montejets)
	myjets = list(myjets)
	matchedjets = []
	matches = {}
	errors = {}
	for i in range(len(myjets)):#my in myjets:
		my = myjets[i]
		deltars = []
		for monte in montejets:
			deltars.append(my.DeltaR(monte))
		mindelr = min(deltars)
		if mindelr > requirement:
			mindel = -1
#			print 'deltar = ' +str(mindelr)
		else:
			mindel = deltars.index(mindelr)
			matches[i] = mindel
			errors[i] = deltars[mindel]

	if matchdifferent:
		func = {} 
		duplicate = False
		pairs = []
		tmplist = []
		for i in sorted(matches.keys(),reverse=True):
			tmplist.append((i,matches[i]))
		first = 0

		print montejets
		print myjets
		print tmplist
		while 0 != len(tmplist):
			pair = [tmplist[first]]

			for j in range(1, len(tmplist)):
				if tmplist[first][1] == tmplist[j][1]:
					duplicate = True
					pair.append(tmplist[j])

			for i in sorted(pair, reverse = True):
				tmplist.remove(i)
			pairs.append(pair)

		myjetsdel = []
		montejetsdel = []
		if duplicate:
			for pair in pairs:
				if len(pair) > 1:
					jetpair = []
					for p in pair:
						jetpair.append(myjets[p[0]])
					best = MinJetError([montejets[pair[0][1]]],jetpair,matchdifferent = False,extra = -1)[0][0]
				else:
					best = pair[0][0]
				func[best] = matches[best]
				myjetsdel.append(best)
				montejetsdel.append(matches[best])
			for i in myjetsdel:
				myjets[i]
			for i in sorted(montejetsdel, reverse=True):
				del montejets[i]
			newextra = extra+1
			func.update(MinJetError(myjets,montejets,matchdifferent=True,extra=-2)[0])
			matches = func

	return [matches, errors]
		
#list of GenParticle's and list of list of GenParticles
#NumFromList is a list of numbers with the same length as daughterlistlist. The number at index i indicates how many 
#particles must be chosen from the i'th list in daughterlistlist
#
#So far, this function only considers particle mass to determine which combination is best

def BestDaughterCombo( motherlist, daughterlistlist, numfromlist ):
	if not type(motherlist) == list:
		mot = [motherlist]
	else:
		mot = motherlist
	absolutedif = []
	particlesbymassdif = []
	for m in mot:
		absolutedif[m] = []
		particlesbymassdif[m] = []
	# rearrange things so that for each mother particle you have an ordered list of invariant mass differences for each particle
	for m in mot:
		for partnum in range(0,len(daughterlistlist)):
			absolutedif[m].append( {} )
			for p in part:
				absolutedif[m][partnum][abs(InvariantMass(m)-InvariantMass(p))] = p
			absolutedif[m][partnum].sort()
			particlesbymassdif[m].append([])
			for i in absolutedif[m][partnum]:
				particlesbymassdif[m].append((absolutedif[m][partnum][i],i))
	for part in range(0,len(daughterlistlist)):
		for m in motherlist:
			particlesbymassdif[m][par]
	#tootired
	return 0	

def InvariantMass(particles):
	if type(particles) is list:
		p = particles.pop()
		v = TLorentzVector(p.vx(),p.vy(),p.vz(),p.energy())
		for p in particles:
			v+=TLorentzVector(p.vx(),p.vy(),p.vz(),p.energy())
	else:
		v = TLorentzVector(particles.vx(),particles.vy(),particles.vz(),particles.energy())
	return v.Mag()

def Momentum(particles):
	if type(particles) is list:
		p = particles.pop()
		v = TLorentzVector(p.vx(),p.vy(),p.vz(),p.energy())
		for p in particles:
			v+=TLorentzVector(p.vx(),p.vy(),p.vz(),p.energy())
	else:
		v = TLorentzVector(particles.vx(),particles.vy(),particles.vz(),particles.energy())
	return v.Mag()

def DeltaRDic(part1,part2,partnum):
	vec1 = TLorentzVector()
	vec2 = TLorentzVector()
	vec1.SetPtEtaPhiM( part1['pt'][partnum],part1['eta'][partnum],part1['phi'][partnum],part1['mass'][partnum])
	vec2.SetPtEtaPhiM( part2['pt'][partnum],part2['eta'][partnum],part2['phi'][partnum],part2['mass'][partnum])
	return vec1.DeltaR(vec2)

def PrintInfo(gp):
	try:
		mom = gp.mother().pdgId()
	except:
		mom = -1
	if abs(gp.mass())< 1e-1:
		mass = abs(gp.mass())
	else:
		mass = gp.mass()
		if gp.mass() < 0.:
			print "OH NO!"
		pass 
	pdgid = gp.pdgId()
	print  "pdgid: " , pdgid  , " mom: " , mom ," status: " , gp.status()  , " invariant mass:", InvariantMass(gp), " pt: " ,   gp.pt(), " eta: " ,  gp.eta(),  " phi: " ,gp.phi(),  " mass: " , gp.mass()
	return	

def SeparateBranches(particles):
	branches = []
	branchkey = {}
	count = 0
	for m in particles[0]:
#		print m.pdgId()
#		print m
		branchkey[m] = count
		branches.append([])
		for i in range(0,len(particles)):
			branches[count].append([])
		branches[count][0].append(m)
		count+=1
#		print
	for part in range(1,len(particles)):
#		try:
#			print particles[part][0].pdgId()
#		except:
#			print part
		for p in particles[part]:
			mom = p.mother()
#			print mom.pdgId()
#			print mom
#			print mom.mother()
			try:
				while mom.pdgId() == mom.mother().pdgId():
					mom = mom.mother()
			except:
				print "failed"
				pass
			for i in branchkey:
				if i == mom:
					mom = i
			branchkey[p] = branchkey[mom]
			branches[branchkey[p]][part].append(p)
	return branches


#		branches[m] = []
#		for spec in range(1,len(particles)):
#			branches[m].append([])
#		parent = m
#		loc = 0
#		while childindex[loc]!=-1:
#			for p in particles[childinex[loc]]:
#				if p.mother() == m:
				




	
