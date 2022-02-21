# importing libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Input text - to summarize
text = "GeeksForGeeks is one of the most useful websites for competitive programming. it is a great websites"

# Tokenizing the text
stopWords = set(stopwords.words("english"))
words = word_tokenize(text)

# Creating a frequency table to keep the
# score of each word

freqTable = dict()
for word in words:
	word = word.lower()
	if word in stopWords:
		continue
	if word in freqTable:
		freqTable[word] += 1
	else:
		freqTable[word] = 1

print(freqTable)

# Creating a dictionary to keep the score
# of each sentence
sentences = sent_tokenize(text)
sentenceValue = dict()

for sentence in sentences:
	for word, freq in freqTable.items():
		if word in sentence.lower():
			if sentence in sentenceValue:
				sentenceValue[sentence] += freq
			else:
				sentenceValue[sentence] = freq

print(sentenceValue)

sumValues = 0
for sentence in sentenceValue:
	sumValues += sentenceValue[sentence]

print(sumValues)

# Average value of a sentence from the original text

average = int(sumValues / len(sentenceValue))

print(average)

# Storing sentences into our summary.
summary = ''
for sentence in sentences:
	if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
		summary += " " + sentence
print(summary)
