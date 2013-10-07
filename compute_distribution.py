"""
Use to create a dictionary such that a picture of the distribution of the outputted scores can be made.
"""

import sys

input_file = open(sys.argv[1], 'r')
stepsize = 0.1
distr = {}

cur_score= 0
while cur_score <= 1:
	cur_score += stepsize
	distr[cur_score] = 0

scores = []

for line in input_file:
	l = line.split()
	if len(l) == 8:
		score = float(l[5])
		scores.append(score)

scores.sort()

cur_limit = 0
for score in scores:
	while score > cur_limit:
		cur_limit += stepsize
	distr[cur_limit] +=1

distribution_list = []

for key in distr:
	if distr[key] != 0:
		dstring = "(%f,%i)" % (key, distr[key])
		distribution_list.append(dstring)

texstring = []
texstring.append("\\begin{tikzpicture}\n\\begin{axis}\n [ybar,bar width = 17\n]\n\\addplot coordinates\n{")
distribution_list.sort()
texstring = texstring + distribution_list
texstring.append("};\n\end{axis}\n\end{tikzpicture}")

print " ".join(texstring)




