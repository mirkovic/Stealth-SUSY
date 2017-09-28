def SumNLargest(n,var):
	newlist = sorted(var,reverse=True)
	fin = 0
	for i in range(min(int(n),len(var))):
		fin+=newlist[i]
	return fin
