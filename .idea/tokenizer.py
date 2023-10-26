import numpy as np
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv) # Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will # print(os.listdir("../input"))

from nltk.tokenize import * #Tokenization Library import can be specific book of the library i.e import word_tokenize
from nltk.corpus import stopwords
import os
import csv
import queue


# Reading CSV

pd.read_csv("../input/Sample.csv")
###read row_by_row code snippet (WIP)###

## Notes (Saeed)## #Filename.txt/csv/xlsx csv is preferred

# TO-DO: Tokenizing Strings from CSV # Add a function that tokenizes from input, ex: E-nr


# General Tokenization
tokens = nltk.word_tokenize(data["sample.xlsx"][0]) 
# this code tokenizes and outputs results of general tokenization in one-line
#Can be modified to .ipnyb for seperate code-line data["input_file"][search_loop_numberi.e 0,1,2...]

#Expected Output
#['https',':','/','/','www','.','e','-','nummersok','.','se','/','lista,...,-#kabelmarkning-apparats/plintsystem-for-#skenmontage/weidmuller/plint-sakr-pa-m-2920154-14020]
# ['brand_name=string']
#data["sample.xlsx"][0] # Output show of General tokenized results i.e No #Specifiers

# Stopwords

#Stop Words: A stop word is a commonly used word (such as “the”, “a”, “an”, “in”) that a search engine has been programmed to ignore, both when indexing entries for searching and when retrieving them as the result of a search query.#

nltk.download('stopwords')
print(stopwords.words('english')) #generates list of stopwords index


#/*|||||||||||||||||||||||||||||||||||||||||||||*/
#####Saeed Notes Code needs to be modified for specificity i.e
### Example 1: Tokenize using the white spaces ##
# nltk.tokenize.WhitespaceTokenizer().tokenize(data["sample.text"][0])
### Example 2: Tokenize using Punctuations ##
#nltk.tokenize.WordPunctTokenizer().tokenize(data["sample.text"][0])
### Example 3: Tokenization using grammer rules
#nltk.tokenize.TreebankWordTokenizer().tokenize(data["reviews.text"][0])

####################################################################
## Research In Progress for Token Normalization i.e stemming and lemmatization (limit-tization)##
#Stemming: A process of removing and replacing suffixes to get to the root form of the #word, which is called stem.
#Notes
#STEMMING i.e constructing specifiers list i.e Tokenize based on WhiteSpaces, PorterStemmer etc.
#Lemmatization: returns the base or dictionary form of a word.

## Idea ## stemming using seperate csv as placeholder specifier i.e compare and see in text

####################################################################

# TO_DO Stemming


words  = nltk.tokenize.WhitespaceTokenizer().tokenize(data["reviews.text"][0])
df = pd.DataFrame()
df['OriginalWords'] = pd.Series(words)
#porter's stemmer
porterStemmedWords = [nltk.stem.PorterStemmer().stem(word) for word in words]
df['PorterStemmedWords'] = pd.Series(porterStemmedWords)
#SnowBall stemmer
snowballStemmedWords = [nltk.stem.SnowballStemmer("english").stem(word) for word in words]
df['SnowballStemmedWords'] = pd.Series(snowballStemmedWords)
df

data['sample.xlsx']

/*##
text = """Founded in 2002, SpaceX’s mission is to enable humans to become a spacefaring civilization and a multi-planet
species by building a self-sustaining city on Mars. In 2008, SpaceX’s Falcon 1 became the first privately developed
liquid-fuel launch vehicle to orbit the Earth."""
word_tokenize(text)
##*/

# Need own Grammar Database called "Specific_Items" so once reading "scraped.txt" data, all words are searched for specified textstring i.e e_numer, product_name
# Do we need Corpus from NLTK???
