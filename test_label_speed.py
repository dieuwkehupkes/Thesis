from labelling import *
from file_processing import *
import sys
import time

alignments =sys.argv[1]
sentences = sys.argv[2]
dependencies = sys.argv[3]

f = ProcessDependencies(alignments, sentences, dependencies)
new = f.next()
total = 0
while new:
	sentence = new[1].split()
	if len(sentence) < 40:
		dependencies = Dependencies(new[2],new[1])
		l = Labels(dependencies.dependency_labels())
		t1 = time.time()
		labels = l.label_most
		t2 = time.time()
		labelling_time = t2-t1
		print 'labelling time:', labelling_time
		total += labelling_time
	new = f.next()

print 'total labelling time:', total
