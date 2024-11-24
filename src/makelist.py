easyWords = []
medWords = []
hardWords = []
with open('words.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        if len(line) <= 5:
            easyWords.append(line)
        elif len(line) > 5 and len(line) <= 8:
            medWords.append(line)
        else:
            hardWords.append(line)

with open('easyWords.txt', "w") as file:
    for word in easyWords:
        file.write(word)

with open('medWords.txt', "w") as file:
    for word in medWords:
        file.write(word)

with open('hardWords.txt', "w") as file:
    for word in hardWords:
        file.write(word)