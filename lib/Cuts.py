import Functions
import os

#########
### Structure:
###
### Creates a Cut object for each cut in the csv. A cut object can convert event vector into 1 or 0.
###
### Creates a 

class CutsCollection:
	def __init__( self, cuts_loc ):
		if not os.path.isfile(cuts_loc):
			self.cuts = []
			self.combinations = []
			self.counts = {}
			self.used_variables = []
			return
		cuts_file = open(cuts_loc,'r')
		cuts_file_sections = cuts_file.read().split('\n\n\n')

		cuts_lines = cuts_file_sections[1].split('\n')
		cuts_combinations = cuts_file_sections[2].split('\n')

		self.used_variables = []

		self.cuts = self.AddVariables(cuts_lines)
		self.combinations = self.Combinations(cuts_combinations)
		self.counts = {}
		for i in self.combinations:
			self.counts[self.GetComboString(i)] = 0 
	def AddVariables( self, lines ):
		variables_dic = {}
		variables_dic['nums'] = {}
		variables_dic['variables'] = {}
		for i in lines:
			cut = Cut(i)
			variables_dic['nums'][cut.num] =  cut

			var = cut.variable_name
			if var not in self.used_variables:
				self.used_variables.append(var)
				variables_dic['variables'][var] = {}

			variables_dic['variables'][var][cut.num] = cut	

		return variables_dic

	def Combinations( self, combos ):
		return_combos = []
		for combo in combos:
			if combo == '':
				continue
			fin_combo = map( int, [item.replace('\n','').replace(' ','') for item in combo.split(',')] )
			if fin_combo != []:
				return_combos.append( fin_combo )
		return return_combos

	def Names( self ):
		names = []
		for c in self.cuts['variables']:
			names.append(c)
		return names

	def CheckAllCuts( self, vec ):
		return_cuts = {}
		for br in self.used_variables:
			for cu in self.cuts['variables'][br]:
				if br == 'all': self.GetCut(cu).Check( vec ) 
				else: self.GetCut(cu).Check( vec[br] )
					

	def GetCutName( self, cut_number ):
		if isinstance(cut_number,list):
			name = ''
			for i_cut in cut_number:
				name += self.cuts['nums'][i_cut].name + ','
			return name[:-1]
		return self.cuts['nums'][cut_number].name
	
	def GetCut( self, cut_number ):
		try:
			return self.cuts['nums'][cut_number]
		except:
			return self.cuts['variables'][cut_number]
	
	def GetCombinations( self ):
		return map( self.GetCutName, self.combinations )

	def GetComboResults( self ):
		return_good = {}
		for combo in self.combinations:
			is_good = 1
			for cu in map( self.GetCut, combo ): 
				is_good *= cu.is_good

			return_good[ self.GetCutName( combo ) ] = is_good
			self.counts[self.GetComboString(combo)]+=int(is_good)
		
		return return_good
	
	def GetComboString(self,combo):
		combo_name = ''
		for c in combo:
			combo_name+=str(c)
		return combo_name
	
	def PrintCuts(self):
		print self.cuts
		print self.combinations
			
class Cut:
	def __init__( self, csv_line ):

		self.is_good = 0

		self.name = csv_line

		split_line = [ item.replace('\n','').replace(' ','') for item in csv_line.split(',') ]

		itervals = iter(split_line)
		self.num = int(next(itervals))
		self.variable_name = next(itervals) 
		self.restriction = next(itervals)
		self.boundaries = []
		self.num_pass = 0
		for i in itervals:
			self.boundaries.append(float(i))
	def Check(self,var):
		#if '-' in self.restriction:
		#	def less(a,b): return a < b
		#	def greater(a,b): return a > b
		#	functions = {'less':less,'greater':greater}
		#	restrictions = self.restriction.split('-')
		#	n = 0
		#	for i in range(len(var[0])):
		#		count_this = True
		#		for r in range(len(restrictions)):
		#			if not functions[restrictions[r]](var[r][i],self.boundaries[r]):
		#				count_this = False
		#		if count_this: n+=1
		#	if n > self.boundaries[len(restrictions)]:
		#		self.is_good = True
				
				
				
		if self.restriction == 'mass>t21<pt>>':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiPt'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if mass > self.boundaries[0] and tau21 < self.boundaries[1] and pt > self.boundaries[2]: n += 1
			self.is_good = n > self.boundaries[3]
		elif self.restriction == 'mass>t21<pt><':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiPt'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if mass > self.boundaries[0] and tau21 < self.boundaries[1] and pt > self.boundaries[2]: n += 1
			self.is_good = n < self.boundaries[3]
				
		elif self.restriction == 'mass>t21<pt>=':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiPt'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if mass > self.boundaries[0] and tau21 < self.boundaries[1] and pt > self.boundaries[2]: n += 1
			self.is_good = n == self.boundaries[3]
		elif self.restriction == 'mass<>t21<btag>>':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiDoubleBAK8'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if self.boundaries[1] > mass > self.boundaries[0] and tau21 < self.boundaries[2] and pt > self.boundaries[3]: n += 1
			self.is_good = n > self.boundaries[4]
		elif self.restriction == 'mass<>t21<btag><':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiDoubleBAK8'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if self.boundaries[1] > mass > self.boundaries[0] and tau21 < self.boundaries[2] and pt > self.boundaries[3]: n += 1
			self.is_good = n < self.boundaries[4]
		elif self.restriction == 'mass<>t21<btag>=':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass, pt = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i], var['jetAK8PuppiDoubleBAK8'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if self.boundaries[1] > mass > self.boundaries[0] and tau21 < self.boundaries[2] and pt > self.boundaries[3]: n += 1
			self.is_good = n == self.boundaries[4]
		elif self.restriction == 'mass>t21<>':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if mass > self.boundaries[0] and tau21 < self.boundaries[1]: n += 1
			self.is_good = n > self.boundaries[2]
				
		elif self.restriction == 'mass>t21<=':
			n = 0
			for i in range(len(var['jetAK8Puppitau1'])):
				tau1, tau2, mass = var['jetAK8Puppitau1'][i], var['jetAK8Puppitau2'][i], var['jetAK8PuppiCorrectedsoftDropMass'][i]
				tau21 = 1 if tau1 == 0 else tau2/tau1
				if mass > self.boundaries[0] and tau21 < self.boundaries[1]: n += 1
			self.is_good = n == self.boundaries[2]
		#########
		### Cut on number of entries with value greater than boundaries[1] is greater than boundaries[0]
		elif self.restriction == 'ngreater':
			self.is_good = sum([ item > self.boundaries[1] for item in var])   >   self.boundaries[0]
		elif self.restriction == 'nless':
			self.is_good = sum([ item < self.boundaries[1] for item in var])   >   self.boundaries[0]
		#########
		### 
		elif self.restriction == 'sumgreater':
			self.is_good = Functions.SumNLargest(self.boundaries[0],map(float,var)) > self.boundaries[1]
		elif self.restriction == 'range':
			self.is_good = self.boundaries[0]<var[0]<self.boundaries[1]
		elif self.restriction == 'greater':
			self.is_good = var[0] > self.boundaries[0]
		elif self.restriction == 'All' or self.restriction == 'all':
			self.is_good = True
		self.num_pass+=int(self.is_good)
		return self.is_good
