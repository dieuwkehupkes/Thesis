#A program to convert the manual alignments to the correct format

a = open('en-fr_1-100.wa', 'r')
a_new = open('en-fr_manual.100','w')

sentence = 1
new_line = a.readline()

while new_line != "":
	link_list = new_line.split()
	sentence_nr = int(link_list[0])
	source_pos = int(link_list[1]) - 1
	target_pos = int(link_list[2]) - 1
	if sentence_nr == sentence:
		a_new.write(str(source_pos) + '-' + str(target_pos) + ' ')
	else:
		a_new.write('\n'+str(source_pos)+'-'+str(target_pos)+' ')
		sentence += 1
	new_line = a.readline()

	
a.close()
a_new.close()
