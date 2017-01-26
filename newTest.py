import re
# import psycopg2
# import wordcount
# import nltk
# from nltk.stem import PorterStemmer
import enchant
# import time
# from nltk.corpus import wordnet as wn
'''
Created on Oct 13, 2016

@author: Andre
'''

sample = "This, is._ a@ te$%s^$t!!!"
sample = re.sub(r'[^\s\w]|_','',sample)
print(sample)



#This code below shows that almost all the words on the LimitedKeyWord list are marekd as NNP on thier own.
# file = open('LimitedKeyWords.txt' , 'r')
# keyWords = file.read().split("\n")
# ps = PorterStemmer()
# # tokensPOS = nltk.pos_tag(keyWords)
# keyWordsStemmed = []
# for word in keyWords:
#     keyWordsStemmed.append(" " + ps.stem(word.strip(" ")))
# 
# file.close()
# print(keyWords)
# print(keyWordsStemmed)

# file = open('LimitedKeyWords.txt', 'r')
# # print(file.read())
# foundkeWords = [a for a in keyWordsStemmed if a in file.read()]
# print(foundkeWords)

# print(tokensPOS)

#--------------------------------------------------------------------------------------------------------------------------
#                                                        BREAK
#--------------------------------------------------------------------------------------------------------------------------

# for token in tokensPOS:
#     if token[1] != "NNP":# or token[1] != "NNPS":
#         print(token[0])
        
#Here's what I'm proposing. We have to get an example of each keyword in a sentence so that NLTK can mark what 
#Part Of Speech each word is, (otherwise it marks all key"words" without spaces as NNP). This requires that I first
#complete the keywords list. Also, we need plenty, (maybe 100 is a good sample size?) of examples where the key
#word is used and maybe even more samples if we used all conjugations of the word (ex: suffer, suffering, suffered etc.)
#Then we take the most assigned part of Speech tag that NLTK gives it and we can either assign that word to that tag
#hard coded probably like in a file like the current LimitedKeyWords.txt, or we can see the percentages for how often NLTK
#assigns what parts of speech and then (do statistical math this part isnt thought out as well) etc. Then, when we find
#possible conjugations or misspellings of a keyWords, we compare the Parts of Speech? 

# ps = PorterStemmer()
# attackSentences = open('POSTesting.txt', 'r')
# attackWords = re.findall('[\S]*attack[^\s\.\?\!]*', attackSentences.read().lower())
# english_vocab = sorted(set(w.lower() for w in nltk.corpus.words.words()))
# file = open("SuperDuperTemp.txt", 'w')
# for word in english_vocab:
#     file.write(word+"\n")
# file.close()

# for word in attackWords: 
#     print(ps.stem(word))
# file = open("SuperUltraTesting.txt", 'w')
# english_stem = sorted(set(w.lower() for w in nltk.stem.wordnet))
# for word in attackWords:
#     if word in english_vocab:#nltk.corpus.words.words():
#         print(word, "is an english word!")

# posTags = nltk.pos_tag(attackWords)
# nltk.help.upenn_tagset("NNP")
# print(posTags)

#ok new problem, different conjugations of each word have different parts of speech naturally, "running" is a verb while
#"run" is a command. Which means if we used the method described above we would have to have seperate part of speech
#assignemnts for each conjugation meaning we cant just search for attack, wed have to search for attacks and attacked etc.
#which heavily defeats the purpose.
#secondly, the way nltk does pos_tagging is affected by misspellings, tpyos etc.
# sentences = attackSentences.read().split("\n")
#POS TAGGER IS TRAINABLE :O

#so I tried to see if There was a dictionary so I could perform a spell check, but NLTK's dictionary doesnt have all the
#permutations of each word, for example from the POSTesting with 6 different permutations of the word "attack", the NLTK
#dictionary only has the words "attack" and "attacker" ("attackable" was also there but it was not used in POSTesting.txt)
#SOOOO what I should focus on doing then is being able to extract the root word from the parsed words and then compare THOSE
#Key word, "Lemmatize"

#--------------------------------------------------------------------------------------------------------------------------
#                                                        BREAK
#--------------------------------------------------------------------------------------------------------------------------


# keyWordsFile = open('LimitedKeyWords.txt', 'r')#open the file containing key words
# keyWords = re.split(r'\n', keyWordsFile.read().lower()) #split file into list (tuple?) of keyWords
# keyWordsFile.close()
# 
# DBname = "MichalisPrj"
# Password = "1"
# con = psycopg2.connect(database=DBname, user = "postgres", password=Password) #connect to postgres
# curs = con.cursor() #create a cursor for this database, allows us to access info from it
#   
# # ExecuteStatement = "SELECT pid, tid, pdate, pcontent FROM tbl_wilders_post WHERE pdate > '2016-05-01'"
# testExec = "SELECT pid, username, title, pcontent FROM testgs WHERE pid = 4"
# # insrtExec = "INSERT INTO testgs(title, pcontent) VALUES (title, 'testtest')"
# curs.execute(testExec)#uteStatement) #perform the select defined above
#   
# selectDataMatrix = curs.fetchall()
# 
# for post in selectDataMatrix:
#     pContent = wordcount.clean(post[3])
#     pContentWords = pContent.split(" ")
#     pConWords = [] 
#     for word in pContentWords:
#         pConWords.append(word.strip("./,?><{}[]:\'\"\)\(*&^%$#@!_-"))
#     print(pConWords)
    
#     stemWordDict = {}
#     for word in pConWords:
#         keyWord = str(" " + ps.stem(word) + " ").lower()
#         if keyWord in keyWords:
#             print(word+",",ps.stem(word))
#             if keyWord not in stemWordDict:
#                 stemWordDict[keyWord] = 1
#             else:
#                 stemWordDict[keyWord] = stemWordDict[keyWord] + 1
# print(stemWordDict)  
#  

# for i in range(0, len(selectDataMatrix)):
#     pcont = wordcount.clean(selectDataMatrix[i][3])
#     for word in keyWordsStemmed:
#         if word.lower() in pcont:
#             print(word, str(selectDataMatrix[i][0]))

#--------------------------------------------------------------------------------------------------------------------------
#                                                        BREAK
#--------------------------------------------------------------------------------------------------------------------------


# # urlFinds = re.findall(r"(https*://+|www+)([\S]+)", stri)
# 
# #This can be used to grab non www/http(s) url's if certain characters are not taught to be split into new words.
# #maybe but best method yetproblem is, doesnt grab the http:// if it exists in front of it. But this can be fixed
# #and is really mostly neccessary for replacing URL's a check can be done for the previous word... consider this.
# for elem in selectDataMatrix:
#     PstCnt = wordcount.clean(elem[3])
#     tekons = nltk.word_tokenize(PstCnt)
#     tokens = nltk.pos_tag(tekons)
#     for word in tokens:
# #         print(word[1][:2])
#         if word[1][:2] == "NN" and "." in word[0]: #check if word is "Noun, singular or mass" (NN)
#             print(word[0].encode("utf-8"))
# #         i = 0
# #         for werd in word:
# #             if i == 0:
# #                 print("("+ str(werd.encode("utf-8")) +", ", end = "")
# #             else:
# #                 print(werd+")", end = "")
# #             i = 1                
# #             print(werd.encode("utf-8")," ", end = "")
#     print()
#     urlFinds = re.findall(r"[\S]+\.[\S]+", wordcount.clean(elem[3]))
#     print(urlFinds)
#     if elem[0] == 8:
#         stri = elem[3]
#         stri = stri.replace("http://www.wilderssecurity.com/threads/ransomware-and-recent-variants.384890/page-3#post-2589982","****YOOOO****", 1)
#         print("THE REPLACED STRING:", stri)
     
# curs.close()
# con.close()
# test = wn.synset('test')


#--------------------------------------------------------------------------------------------------------------------------
#                                                        BREAK
#--------------------------------------------------------------------------------------------------------------------------


# for char in jao:
#     diff += ord(char) - ord(jbo[i])
#     i += 1

# wordList = []
# quoteList = []
# totalWords = 0;
# # 
# file = open("itmanPID_2589982.txt", 'r')
# file = re.split(r'\n', file.read())
# for i in file: #i is a string for each line in the file represented by the list "file"
#     word = re.findall(r"(https?://+|www+)([\S]+)", i) #here word is a list, NOT AN INDIVIDUAL WORD
# #     word = re.findall(r" (?:(<a))([\w\W])", i)
# #     quote = re.findall(r"quote",i,re.I)
#     quote = re.finditer(r"quote",i,re.I)
#     for iterator in quote:
#         print(iterator.group(), "on line {}".format(iterator.span()))
#     #                #(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?
#     if len(word) != 0:
#         wordList.append(word)
#     if len(quote) != 0:
#             quoteList.append(quote)
# print(wordList)
# print(quoteList)


#ADD MORE KEYWORDS up to 1000
# in wilders security, there is a subtrhead called "malware problems and news" Go there and select keywords based off that
#change current stemming method, stem the keywords that should be stemmed and then compare stems to stems of words in
#pcontent
#look at current tab open for tons for keyWords
#misspellings if time USE LIBRARIES
#GIThub
#generate csv for all uses of keywords per Database (contain Ip's and URL's)
#ctrl+shift+esc = task manager
#create two options, run one without stemming, one with