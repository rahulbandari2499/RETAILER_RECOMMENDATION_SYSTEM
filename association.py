import sys,math
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
	csv_reader = reader(file)
	for row in csv_reader:
		if not row:
			continue
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

print len(freqitems)
for i in range(len(freqitems)):
	print (",").join(freqitems[i])
left=[]
right=[]
if dic["flag"]=='1':
	for i in freqitems:
		for j in range(1,len(i)):
			for k in itertools.combinations(i,j):
				val=1.0*freq_trie.getcount(i)/freq_trie.getcount(k)
				if val>=dic["confidence"]:
					left.append(list(k))
					right.append(list(set(i)-set(k)))
	print len(left)
	for i in range(len(left)):
		print (",").join(left[i]+['=>']+right[i])
sys.stdout.close()
