import sys,math
import numpy as np
import numpy.ma as ma
from csv import reader
from trie import *
import sets
import itertools

def subsets(itemset):
	temp = []
	for i in range(len(itemset)):
		s = itemset[:i] + itemset[i+1:]
		temp.append(s)
	return temp

def generator(curr_items):
	next_items=[]
	for i in range(len(curr_items)):
		for j in range(i+1,len(curr_items)):
			a=[]
			if curr_items[i][:-1] == curr_items[j][:-1]:
				a=curr_items[i][:]
				a.append(curr_items[j][-1])
				next_items.append(a)
			else:
				break
	return next_items

def prune(next_items,curr_items):
	prunedList = []
	for i in next_items:
		subs = subsets(i)
		flag = 1
		for j in subs:
			if j not in curr_items:
				flag = 0
				break
		if flag:
			prunedList.append(i)
	return prunedList

dic={}
with open('config.csv', 'r') as file:
	csv_reader = reader(file)
	for row in csv_reader:
		if not row:
			continue
		dic[row[0]]=row[1]

dic["support"] = float(dic["support"])
dic["confidence"] = float(dic["confidence"])

sys.stdout = open(dic["output"], 'w')
singleitems = []
singlecnts = []
cnt=0
freq_trie=trie(1,"root")
with open(dic["input"], 'r') as file:
	csv_reader = file.read()
	csv_reader = csv_reader.split('\n')[:-1]
	no_transactions = len(csv_reader)
	for row in csv_reader:
		if not row:
			continue
		row = [str(x) for x in row.split(' ')]
		row.sort()
		freq_trie.insertNode(row,1)
		for i in range(len(row)):
			if row[i] not in singleitems:
				singleitems.append(row[i])
				singlecnts.append(int(1))
			else:
				singlecnts[singleitems.index(row[i])] += 1
		cnt+=1

singleitems.sort()
mincnt = int(math.ceil(cnt*dic["support"]))
freqitems = []

for i in range(len(singleitems)):
	if singlecnts[i]>=mincnt:
		freqitems.append([singleitems[i]])
curr_items = freqitems

while True:
	next_items=generator(curr_items)
	# print(next_items)
	pruned_items=prune(next_items,curr_items)
	# print(pruned_items)
	if len(pruned_items)==0:
		break
	a=[]
	for i in pruned_items:
		ff=freq_trie.getcount(i)
		# print ff
		if ff>=mincnt:
			a.append(i)
	if len(a)==0:
		break
	freqitems = freqitems + a
	curr_items=a

# print len(freqitems)
# for i in range(len(freqitems)):
# 	print (",").join(freqitems[i])
# left=[]
# right=[]

no_items = len(singlecnts)
#csp = {}
csp_matrix = np.array([[0 for i in range(int(no_items))] for j in range(int(no_items))],dtype = float)

for i in xrange(0,no_items-1):
	for j in xrange(i+1,no_items):
		confidence = 1.0*freq_trie.getcount(str(i)+str(j))/freq_trie.getcount(str(j))
		support = 1.0*freq_trie.getcount(str(i ))
		lift = (confidence/support) * no_transactions
		if lift < 1.0:
			# csp[(i,j)] = 0
			# csp[(j,i)] = 0
			csp_matrix[int(i)][int(j)]=0
			csp_matrix[int(j)][int(i)]=0
		else:
			# csp[(i,j)] = lift
			# csp[(j,i)] = lift
			csp_matrix[int(i)][int(j)]= lift
			csp_matrix[int(j)][int(i)] = lift

print 'START_OF_CSP'
for i in range(no_items):
	for j in range(no_items):
		print csp_matrix[i][j],
	print
print 'END_OF_CSP\n'


## assignment step #########
var = int(round(math.sqrt(no_items))**2)
site = np.array([-1 for x in range(var)])

i = 0
j = i + 1
val = np.unravel_index(np.argmax(csp_matrix,axis=None),csp_matrix.shape)

site[i] = val[0]
site[j] = val[1]
prev = val[1]
#creating a mask of indices used already
index = [val[0],val[1]]
mask = np.zeros(no_items,dtype = bool)
for i in range(1,no_items-1):
	mask[index] = True
	new_csp = np.ma.array(csp_matrix[prev],mask = mask)
	val = np.argmax(new_csp)
	index.append(val)
	site[i+1] = val
	prev = val

#grid_site = np.reshape(site,(int(math.sqrt(var)),int(math.sqrt(var))))

print 'INITIAL SITE LAYOUT'
print np.reshape(site,(int(math.sqrt(var)),int(math.sqrt(var)))),'\n'

#calculation of total possibilty of cross selling

def total_csp_calc(site):
	grid_site = np.reshape(site,(int(math.sqrt(var)),int(math.sqrt(var))))
	site_shape = grid_site.shape[0]
	total_csp = 0.0
	for i in range(site_shape):
		for j in range(site_shape-1):
			a = grid_site[i][j]
			b = grid_site[i][j+1]
			if a!=-1 or b!=-1:
				total_csp += csp_matrix[a][b]

	for i in range(site_shape):
		for j in range(site_shape-1):
			a = grid_site[j][i]
			b = grid_site[j+1][i]
			if a!=-1 or b!=-1:
				total_csp += csp_matrix[a][b]

	return total_csp

total_csp = total_csp_calc(site)
print 'Intial Total_CSP  ',total_csp
print
####updation step ########

for i in range(no_items-1):
	for j in range(i+1,no_items):
		prev1 = site[i]
		prev2 = site[j]
		site[i] = prev2
		site[j] = prev1

		new_total_csp = total_csp_calc(site)

		if new_total_csp > total_csp:
			total_csp = new_total_csp
			break
		else:
			site[i] = prev1
			site[j] = prev2
			continue

print 'FINAL CSP  ',total_csp,'\n\n'
print 'FINAL SITE LAYOUT'
grid_site = np.reshape(site,(int(math.sqrt(var)),int(math.sqrt(var))))
print grid_site
sys.stdout.close()
