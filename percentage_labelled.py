import sys
from file_processing import *

alignments = sys.argv[1]
sentences = sys.argv[2]
trees = sys.argv[3]

f = ProcessDependencies(alignments, sentences, trees)
l = f.percentage_labelled(40, Dependencies.label_most)
print 'total: %i\n' % l[0]
print 'labelled: %i\n' % l[1]
percentage = float(l[1])/l[0]
print 'average labelled: %f' % percentage
#print 'average labelled: %f' % float(l[1])/float(l[0])
