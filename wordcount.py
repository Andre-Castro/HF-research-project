'''
Created on Jan 13, 2017

@author: Andre
'''
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import re

def findKeyWords(postContent, keyWords, file, row, colNums):
#     for keyWord in keyWords: #for each keyWord
#         numKeyWord = postContent.count(keyWord) #part where i should change the matching algorithm
# #         numKeyWord = len(re.findall(keyWord, postContent))
#         if numKeyWord != 0:
#             col = colNums[keyWord]
#             file.write(str(row) + ',' + str(col) + ',' + str(numKeyWord) + "\n")
    ps = PorterStemmer()
    
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
                    print(row, instance, amount)
            if amount != 0:
                if word[0] not in wordDict:
                    wordDict[word[0]] = amount
                else:
                    print(word[0])
                    wordDict[word[0]] = wordDict[word[0]] + 1
                    #FIIIIIXXXEDDDD got it grabbing stems and phrases :)
    for instance in wordDict:
        col = colNums[instance]
        file.write(str(row) + ',' + str(col) + ',' + str(wordDict[instance]) + ',' + "\n")
#         print(row, instance, wordDict[instance])
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
    ipNums = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", postContent)
    if len(ipNums) is not 0:
        for ip in ipNums:
            ipDict[ip] = "v4"
    return

def clean(postContent):
    postContent = re.sub(r'(\\t)*(\\n)*','',postContent) #removes all \n and \t
    soup = BeautifulSoup(postContent, "html.parser")
    postContent = soup.get_text(separator=" ")
#     print(postContent.encode("utf-8"))
    return postContent

#POSSIBLE OPTIMIZATION
    # in replaceURL's instead of having to find the URL's again using re.finditer, you can just do re.findIter in findURL's
        #and get the span() there and save that as the second part of the tuple to urlDict rather than the PID since the pid
        #isnt really being used. However, problem with this is that since findURLs is split up into the bs4 part and the
        #cleanpostContent part, there are duplicate URLS found... which is why I'm not currently doing it this way.
        #BUT, if there was a way to avoid this duplicate url finding this would most likely speed up the program having
        #already found the URL position ahead of time
        #speaking of which, the current method doesnt even need to be a list of tuples, it could just be a list of URL strings
        
#notes
    #You either improve the regex to get a perfect URL, or you replace by index and risk cutting something you dont need to
    # or leaving behind something uncur which is not as bad.

#Notes
    #whitespace
    #capital matters
    #root words
    #misspellings (use edit distances, parameter in func, let user specify how forgiving they want to be)
    #for phrases like "black goat" if somewhere it is seperated by somethign elsee besides a sapce you can compare the pid's to see if the phrase is actually there
    # 
    # ip prefixes, and v6
    # acount for duplicates
    # compare ip's to blacklists / visual inspection
    #
    #Hidden url's spaces, or character replacements for www. such as ,,, or something