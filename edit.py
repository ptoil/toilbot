wordFile = open("collins_scrabble.txt", "r")
newFile = open("newList.txt", "w")

wordsList = wordFile.read().split("\n")
delWords = []

i = 0
while i < len(wordsList):
	if len(wordsList[i]) <= 3:
		del wordsList[i]
		i -= 1
	i += 1 

newFile.write("\n".join(wordsList))
newFile.close()