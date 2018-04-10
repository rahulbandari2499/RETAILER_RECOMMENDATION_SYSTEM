class trie:
	def __init__(self, count, name):
		self.count = count
		self.name = name
		self.child = {}

	def insertNode(self, itemset, count):
		f = self.child
		for i in itemset:
			if i in f:
				f[i].count+=1
				f = f[i].child
			else:
				f[i] = trie(count, i)
				f = f[i].child

	def getcount(self,itemset):
		f=self.child
		val=0
		if len(itemset)==0:
			return 0
		for i in f:
			if itemset[0]==i:
				if len(itemset)>1:
					val+=f[i].getcount(itemset[1:])
				else:
					val+=f[i].count
			else:
				val+=f[i].getcount(itemset) 
		return val

	# def printAll(self, prevStr):
	# 	for i in self.child:
	# 		a = prevStr + i
	# 		print a
	# 		self.child[i].printAll(a + ",")