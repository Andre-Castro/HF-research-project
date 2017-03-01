'''
Created on Jan 25, 2017

@author: Andre
'''
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import re
# import enchant
import psycopg2

def findAllWords(cleanPostContent, wordDict): #passing the pcontent (cleaned with clean function) this function adds word instances to wordDict dictionary
    pConWords = cleanPostContent.split()
    for word in pConWords:
        word = re.sub(r'[^\s\w]|_','',word)
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] = wordDict[word] + 1
    return
# '''
# KEYWORD LIST SPECIFICATIONS:
# '''
def findKeyWords(cleanPostContent, wordDict, keyWordsList): #passing the pcontent (cleaned with clean function) this function adds KEYword instances to wordDict dictionary
    ps = PorterStemmer()
    keyWordsStemmed = []
    for word in keyWordsList:
        keyWordsStemmed.append(" " + ps.stem(word.strip(" "))) #the stem of all the specified keyWords
        
    keyWordsZip = zip(keyWordsList, keyWordsStemmed)#going to zip as a quick-fix for now, in the future use only stemmed keywords? seems the base form is not important...
    #KEY WORDS ZIP COULD BE PASSED IN AS PARAMETER RATHER THAN BEING MADE EACH TIME FOR OPTIMIZAITON
        #requires user to know how to code that however
    for word in keyWordsZip:
        if word[1].lower() in cleanPostContent: #only check if word stem exists in file, doesnt take into account how many times its in file
            amount = 0
            pattern = word[1] + "[\S]*"
            wordInstances = re.findall(pattern,cleanPostContent)
            for instance in wordInstances:
                if word[1] == ps.stem(re.sub(r'[^\s\w]|_','',instance)): #check if the stems of the found words are the same, re is there to remove punctuation and unnecessary characters
                    amount = amount + 1
            if amount != 0:
                if word[0] not in wordDict:
                    wordDict[word[0]] = amount
                else:
                    wordDict[word[0]] = wordDict[word[0]] + 1
    return
            
def findAllWordsfromPID(PIDList, wordDict, curs, DBname): #given a list of PID's, this function goes through and stores every instnace of a word in the wordDict dictionary
    for pid in PIDList:
        ExecuteStatement = "SELECT pid, pcontent FROM " + DBname + " WHERE pid = '" + str(pid) + "'"
        curs.execute(ExecuteStatement)
        selectDataMatrix = curs.fetchall()
        cleanPostContent = clean(selectDataMatrix[0][1])
        pConWords = cleanPostContent.split()
        for word in pConWords:
            word = re.sub(r'[^\s\w]|_','',word)
            if word not in wordDict:
                wordDict[word] = 1
            else:
                wordDict[word] = wordDict[word] + 1
    return

def findKeyWordsFromPid(PIDList, wordDict, keyWordsList, curs, DBname): #passing the pcontent (cleaned with clean function) this function adds KEYword instances to wordDict dictionary
    for pid in PIDList:
        ExecuteStatement = "SELECT pid, pcontent FROM " + DBname + " WHERE pid = '" + str(pid) + "'"
        curs.execute(ExecuteStatement)
        selectDataMatrix = curs.fetchall()
        cleanPostContent = clean(selectDataMatrix[0][1])
        findKeyWords(cleanPostContent, wordDict, keyWordsList)
    return
            
def findKeyWordsCSV(postContent, keyWords, file, row, colNums, permutationsBool):
    if not permutationsBool:
        for keyWord in keyWords: #for each keyWord
            numKeyWord = postContent.count(keyWord) #part where i should change the matching algorithm
    #         numKeyWord = len(re.findall(keyWord, postContent))
            if numKeyWord != 0:
                col = colNums[keyWord]
                file.write(str(row) + ',' + str(col) + ',' + str(numKeyWord) + "\n")
    else:
        ps = PorterStemmer()
#         d = enchant.Dict("end_US")
        
        keyWordsStemmed = []
        wordDict = {}
        
        for word in keyWords:
            keyWordsStemmed.append(" " + ps.stem(word.strip(" ")))
        
        keyWordsZip = zip(keyWords, keyWordsStemmed)#going to zip as a quick-fix for now, in the future use only stemmed keywords? seems the base form is not important...
        for word in keyWordsZip:
            if word[1].lower() in postContent: #only check if word stem exists in file, doesnt take into account how many times its in file
                #amount = postContent.count(word[1]) #fixes that but now botanical being found for bot...
                #FIX: have to check stems of both keyword AND everyword in the file to do this correctly... no other way
                #FIX: USE REGEX
                amount = 0
                pattern = word[1] + "[\S]*"
                wordInstances = re.findall(pattern,postContent)
                #print(wordInstances, row)
                for instance in wordInstances:
                    if word[1] == ps.stem(re.sub(r'[^\s\w]|_','',instance)): #check if the stems of the found words are the same, re is there to remove punctuation and unnecessary characters
                        amount = amount + 1
#                         print(row, instance, amount)
                if amount != 0:
                    if word[0] not in wordDict:
                        wordDict[word[0]] = amount
                    else:
#                         print(word[0])
                        wordDict[word[0]] = wordDict[word[0]] + 1
                        #FIIIIIXXXEDDDD got it grabbing stems and phrases :)
        for instance in wordDict:
            col = colNums[instance]
            file.write(str(row) + ',' + str(col) + ',' + str(wordDict[instance]) + ',' + "\n")
#             print(row, instance, wordDict[instance])
    return

def findURLs(postDataTuple, cleanPostContent, urlDict):
    postContent = postDataTuple[3]
    soup = BeautifulSoup(postContent, "html.parser")
    for aTag in soup.find_all('a'):
        if aTag.get('class') is not None: 
            aTagClass = aTag.get('class')[0].strip("\\\"") #removes '\' and '"' from the class string
            if(aTagClass == "externalLink" or aTagClass == "internalLink"):
#                 print("bs4 pos:", )
#                 print("found externalLink tag with pid: " + str(postDataTuple[0]))
#                 indexes = re.finditer(aTag.get('href')[2:-2], postContent, flags= re.I)
#                 if indexes is not None:
#                     for matchObj in indexes:
#                         print(matchObj.span())
                urlDict.append((aTag.get('href')[2:-2],postDataTuple[0])) # appends tuple to url "dict" man I need to do alot of re-commenting
    userPostURLs = re.findall(r"(https*://+|www+)([\S]+)", cleanPostContent)
    #I NEED TO MAKE THIS REGEX BETTER
    for element in userPostURLs:
        urlStr = element[0] + element[1]
        urlDict.append((urlStr, postDataTuple[0]))
    #below is the code for getting span aka position of url to store in url dict as opposed to pid
#     userPostURLS = re.finditer(r"(https*://+|www+)([\S]+)", cleanPostContent, flags= re.I)
#     if userPostURLS is not None:
#         for element in userPostURLS:
#             urlStr = str(element.group(0))
# #             if urlStr not in urlDict:
#             urlDict [urlStr] = element.span()
#             else:
#                 urlDict [urlStr + "**DUPL**:" + str(dupl)] = element.span()
    return #userPostURL's might count to many times

#left to do in findURLS function:
    #once strictly post content has been extracted, find "simpleUrls", things like "google.com" etc without www / http
    #deal with duplicates? //  CHECK "issue" BELOW
    
def replaceURLs(postDataTuple, urlDict, specificNumPostURLS, cursor):
    newPContent = postDataTuple[3]
    i = len(urlDict) - specificNumPostURLS #this makes sure that only the URLS found in this specific post are checked and replaced and not previous urls
    while i < len(urlDict):
#         print("URL:", element[0])
        newPContent = newPContent.replace(urlDict[i][0], "**URLFOUND**", 1) #the one is there to make sure only one instances gets replaced. incase bs4 urls are similar but different (have same characters up to a certain point)
        i += 1
#         userPostURLS = re.finditer(pattern= element[0], string= postDataTuple[3], flags= re.I)
#         if userPostURLS is not None:    
#             for matchObj in userPostURLS:
#                 positions = matchObj.span()
#                 newPContent = newPContent[0:positions[0]] + "**URLFOUND**" + newPContent[positions[1]:]
#     print(newPContent)
    newPContent = newPContent.replace('\'', '\'\'')
    replaceStatement = "UPDATE tbl_wilders_post SET new_pcontent = \'{}\' WHERE pid = ".format(newPContent) + str(postDataTuple[0])+";"
    cursor.execute(replaceStatement)
    return

def findIPs(postContent, ipDict): #currently only ipv4
    ipMatchRe = "(([0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))"
#     ipNums = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", postContent)
    ipNums = re.findall(ipMatchRe, postContent)
    if len(ipNums) is not 0:
        for ip in ipNums:
            if ip[0] not in ipDict:
                ipDict[ip[0]] = 1
            else:
                ipDict[ip[0]] = ipDict[ip[0]] + 1
    return

def clean(postContent):
    postContent = re.sub(r'(\\t)*(\\n)*','',postContent) #removes all \n and \t
    soup = BeautifulSoup(postContent, "html.parser")
    postContent = soup.get_text(separator=" ")
#     print(postContent.encode("utf-8"))
    return postContent

#notes for 1/26
#    - Word permutations should be 100% functional.
#        -Still need to double check hypthenated words or words that SOMETIMES have space see how those are working...
#    - Downloaded pyeEnchant
#    - opened github project (https://github.com/Andre-Castro/HF-research-project)
#    - Inlcuded option for searching for word permutations or not
#    - Added about ~50 keywords, check to see if they are ok


#notes
#- use pyenchant for the space issues with keywords, hopefully find mispellings
# for keywords with mulitple words where one of the words is a keyword independently, subtract to find sole uses
#try wordcount on wilders to get keywords
#googlw some stuff to
#prepare good corpus of active words
#generate keywords list based off wilders and offcomm tables, pick important words
#email github link
#include ALL words, not just malcioius intent ones
#ultimately, combine generated keywords


#2/3
#for ip:
# IP addresses take prefernce over URL's.
# Once IP is found, decide if IP is malicitous, can check same post (use PID) to see if nearby words are the
#'concren words. In the end report malicious IP's.
#also all the posts where the IP appeared, first is most important
#also see what is being said around the malicious IP's
#    for this think about whether more false positive or false negatives are worse

#for keywords:
#percentage of posts per word
#have to compare number of word instances to time 
#Consider throwing out blockQuotes, dont want to find the same text repeated 5 times

