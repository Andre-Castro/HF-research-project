from __future__ import print_function
'''
Created on Jan 25, 2017

@author: Andre
'''
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import re
import pylab
import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from operator import itemgetter
from datetime import date
import datetime
import math

'''
/*---------------------------------------------- findAllWords -----
Function: findAllWords(cleanPostContent, wordDict)

Purpose:  Finds all words and stores them in a dictionary for a
          given *CLEANED* postContent string

Notes:    See 'clean' function below for postContent cleaning

Parameters:
    cleanPostContet (string) -- the text of the post, cleaned
    wordDict (Dictionary) -- Dictionary holding instances of found
                             words dict[word] = number of instances
                             of that word

Returns:  nothing, words are added to the passed-in dictionary
-------------------------------------------------------------------*/
'''
def findAllWords(cleanPostContent, wordDict):
    pConWords = cleanPostContent.split()
    for word in pConWords:
        word = re.sub(r'[^\s\w]|_','',word)
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] = wordDict[word] + 1
    return

'''
/*---------------------------------------------- findKeyWords -----
Function: findKeyWords(cleanPostContent, wordDict, keyWordsList)

Purpose:  Finds all specified "key" words and stores them in a 
          dictionary for a given *CLEANED* postContent string

Notes:    See 'clean' function below for postContent cleaning.
          This functions uses word "stemming" (ex: the stem of 
          attacks, attacking, attacked is attack) to search for
          all keyWord instances.
          
Parameters:
    cleanPostContet (string) -- the text of the post
    wordDict (Dictionary) -- Dictionary holding instances of found
                             words dict[keyWord] = number of 
                             instances of that keyWord
    keyWordsList (list) -- List of keywords to be found

Returns:  nothing, words are added to the passed-in dictionary
-------------------------------------------------------------------*/
'''
def findKeyWords(cleanPostContent, wordDict, keyWordsList):
    ps = PorterStemmer()
    keyWordsStemmed = []
    for word in keyWordsList: #first, get the stem of all the keywords in a list
        keyWordsStemmed.append(" " + ps.stem(word.strip(" ")))
    #second, zip the list with the base of the word.
    keyWordsZip = zip(keyWordsList, keyWordsStemmed)
    
    for word in keyWordsZip: #for each keyWord
        if word[1].lower() in cleanPostContent: #only check if word stem exists in file, doesn't take into account how many times its in file
            amount = 0
            pattern = word[1] + "[\S]*" #build regex pattern to search for word, doesn't work for all word permutations?, ex: fly vs. flown
            wordInstances = re.findall(pattern,cleanPostContent)
            for instance in wordInstances: #for each instance of a found keyWord stem + misc characters
                if word[1] == ps.stem(re.sub(r'[^\s\w]|_','',instance)): #check if the stems of the found words are the same, re is there to remove punctuation and unnecessary characters
                    amount = amount + 1 #if so count as a keyWord instance
            if amount != 0: #if there was indeed a word found, add it wordDict dictionary
                if word[0] not in wordDict:
                    wordDict[word[0]] = amount
                else:
                    wordDict[word[0]] = wordDict[word[0]] + 1
    return
            
'''
/*----------------------------------------- findAllWordsfromPID -----
Function: findAllWordsfromPID(PIDList, wordDict, DBname, pword)

Purpose:  Given a list of PID's (post ID's), this function find
          and adds all words from specified posts to a dictionary

Notes:    This function is psycopg2 specific, a python library
          used to connect to your local postgres database
          
Parameters:
    cleanPostContet (string) -- the text of the post
    wordDict (Dictionary) -- Dictionary holding instances of found
                             words dict[Word] = number of 
                             instances of that Word
    DBname (string) -- the name of your local postgres table or
                       database
    pword (strong) -- the password for the specified postgres
                      table or data

Returns:  nothing, words are added to the passed-in dictionary
---------------------------------------------------------------------*/
'''
def findAllWordsfromPID(PIDList, wordDict, DBname, pword):
    con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
    curs = con.cursor()
    for pid in PIDList: #for each PID in the list of PID's
        ExecuteStatement = "SELECT pid, pcontent FROM " + DBname + " WHERE pid = '" + str(pid) + "'" #build SQL statment to execute
        curs.execute(ExecuteStatement)
        selectDataMatrix = curs.fetchall() #fetch all post contents for the specified PID
        cleanPostContent = clean(selectDataMatrix[0][1]) #clean the post content
        pConWords = cleanPostContent.split()
        for word in pConWords:
            word = re.sub(r'[^\s\w]|_','',word)
            if word not in wordDict:
                wordDict[word] = 1
            else:
                wordDict[word] = wordDict[word] + 1
    return

'''
/*-------------------------------------------- findKeyWordsfromPID -----
Function: findKeyWordsfromPID(PIDList, wordDict, keyWordsList, DBname)

Purpose:  Given a list of PID's (post ID's), this function find
          and adds all "key" words from specified posts to a dictionary

Notes:    This function is psycopg2 specific, a python library
          used to connect to your local postgres database
          This function 
          
Parameters:
    cleanPostContet (string) -- the text of the post
    wordDict (Dictionary) -- Dictionary holding instances of found
                             words dict[keyWord] = number of 
                             instances of that keyWord
    keyWordsList -- List of keywords to be found in postContent
    DBname (string) -- the name of your local postgres table or
                       database
    pword (strong) -- the password for the specified postgress
                      table or data

Returns:  nothing, words are added to the passed-in dictionary
------------------------------------------------------------------------*/
'''
def findKeyWordsFromPid(PIDList, wordDict, keyWordsList, DBname, pword):
    con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
    curs = con.cursor()
    for pid in PIDList: #for each PID (post essentially) in the list of PID's
        ExecuteStatement = "SELECT pid, pcontent FROM " + DBname + " WHERE pid = '" + str(pid) + "'" #build SQL statment to execute
        curs.execute(ExecuteStatement)
        selectDataMatrix = curs.fetchall() #fetch post content
        cleanPostContent = clean(selectDataMatrix[0][1]) #clean post content
        findKeyWords(cleanPostContent, wordDict, keyWordsList) #call findKeyWords on cleaned post content
    return
'''           
/*-------------------------------------------- findKeyWordsPreStemmed -----
Function: findKeyWordsPreStemmed(cleanPostContent, wordDict, keyWordsZip)

Purpose:  Given a preZipped list of keyWords and their stems, this 
          function find and adds all keyWords to a dictionary.

Notes:    The main purpose of this function is to optimize key word
          searching by having the user create a zip list of key words
          and their stems and passing it in rather than having to create
          a new one each function call. 
          
Parameters:
    cleanPostContet (string) -- the text of the post
    wordDict (Dictionary) -- Dictionary holding instances of found
                             words dict[keykeyWord] = number of 
                             instances of that Word
    keyWordsZip (zip list) -- *Zipped* list of keywords to be found in
                              postContent the format is:
                              (key word, key word stem)

Returns:  nothing, words are added to the passed-in dictionary
------------------------------------------------------------------------*/
'''
def findKeyWordsPreStemmed(cleanPostContent, wordDict, keyWordsZip):
    ps = PorterStemmer()
    for word in keyWordsZip: #for each keyword
        if word[1].lower() in cleanPostContent: #only check if word stem exists in file, doesn't take into account how many times its in file
            amount = 0
            pattern = word[1] + "[\S]*" #build regex pattern to search for word, doesn't work for all word permutations?, ex: fly vs. flown
            wordInstances = re.findall(pattern,cleanPostContent)
            for instance in wordInstances:  #for each instance of a found keyWord stem + misc characters
                if word[1] == ps.stem(re.sub(r'[^\s\w]|_','',instance)): #check if the stems of the found words are the same, re is there to remove punctuation and unnecessary characters
                    amount = amount + 1 #if so count as a keyWord instance
            if amount != 0: #if there was indeed a word found, add it wordDict dictionary
                if word[0] not in wordDict:
                    wordDict[word[0]] = amount
                else:
                    wordDict[word[0]] = wordDict[word[0]] + 1
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


'''
/*--------------------------------------------------- replaceURLS -----
Function replaceURLS

Purpose:  
          
Notes:    This function is very psycopg2 specific, a python 
          library used to connect to your local postgres
          database. It requires the user to pass in an object of
          type cursor and an object of type connection (both 
          defined in the psycopg2 library). It is done this way 
          to use just one connection to the database rather
          than having to create a new connection each time.

Parameters:
    postDataTuple (tuple) -- A tuple containing information about a
                   specific post. The tuple has to have at least two
                   elements, pid and postContent. This specific
                   function assumes the tuple has 4 elements as
                   follows: (pid, tid, pdate, pcontent).
    urlDict (Dictionary) -- 
    specificNumPostURLS (int) -- 
    cursor (<class 'psycopg2.extensions.cursor'>) -- a predefined
            object that allows for SQL statements to be executed
            for the database the cursor is linked with.
    con (<class 'psycopg2.extensions.connection'>) -- a predefined
         object that represents the connection to a local postgres
         database. Allows us to save the changes we made with the
         replace statements.

Returns:  nothing
-------------------------------------------------------------------*/
'''
def replaceURLs(postDataTuple, urlDict, specificNumPostURLS, cursor, con):
    postContent = postDataTuple[3] #grab the postContent text
    i = len(urlDict) - specificNumPostURLS #this makes sure that only the URLS found in this specific post are checked and replaced and not previous urls
    while i < len(urlDict): 
        postContent = postContent.replace(urlDict[i][0], "**URLFOUND**", 1) #the one is there to make sure only one instances gets replaced. incase bs4 urls are similar but different (have same characters up to a certain point)
        i += 1
    postContent = postContent.replace('\'', '\'\'') #replaces all '\' with '\\' so the replace statement below can execute correctly
    replaceStatement = "UPDATE tbl_wilders_post SET new_pcontent = \'{}\' WHERE pid = ".format(postContent) + str(postDataTuple[0])+";" #build the replace statement to be executed
    cursor.execute(replaceStatement) #edit the database with the replace statement above
    con.commit() #save the edits made to the database with the execution above
    return

'''
/*--------------------------------------------------- findIPs -----
Function findIPs(postContent, ipDict)

Purpose:  Takes in a string (postContent) 
          and adds any found IP addresses to a dictionary (ipDict).
          
Notes:    Currently only works on ipv4 addresses.

Parameters:
    postContet (string) -- the text of the post
    ipDict (Dictionary) -- Dictionary holding instances of found IP's
                            dict[ip] = number of instances of that ip
    prefix (bool) -- Bool telling whether or not ip Prefixes should
                     be taken into account

Returns:  Dictionary (ipDict) with added newly found IP's
-------------------------------------------------------------------*/
'''
def findIPs(postContent, ipDict, prefix):
    ipMatchRe = "(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5]))"
    ipPrefixMatchRe = "(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])/([0-9]|[0-2][0-9]|3[0-2]))($|\D)"
    ipNums = []
    if not prefix:
        ipNums = re.findall(ipMatchRe, postContent) #regex doesn't let IP's be greater than 255 
    else:
        ipNums = re.findall(ipPrefixMatchRe, postContent)
        validateIPPrefix(ipNums)
    if len(ipNums) is not 0:
        for ip in ipNums:
            if ip[0] not in ipDict:
                ipDict[ip[0]] = 1
            else:
                ipDict[ip[0]] = ipDict[ip[0]] + 1
    ####------- INCLUDE BOOL PASSED IN that is for whether or not to include prfixes or not
    ####
    return
'''
/*------------------------------------------ validateIPPrefix -----
Function validateIPPrefix(ipList)

Purpose:  This helper function to findIPs.
          
Notes:    Currently only works on ipv4 addresses.

Parameters:
    ipList (list) -- list of IP's found using the regex in
                     function findIPs

Returns:  Nothing, list is edited in place
-------------------------------------------------------------------*/
'''
def validateIPPrefix(ipList):
    if len(ipList) is not 0:
        for ip in ipList:
            if len(ip) > 5: #if there were 4 parts to the ip found (part1.2.3.4/prefix) (should alwasy be?)
                prefix = 32 - int(ip[5]) #grab the prefix
                bitmaskList = [] #the 4 masking values used to verify the prefix
                count = 4 #count variable to see how many ip parts are left after following calculation
                
                #we are going to create a bitmask to see if the ip prefix is valid or not
                #first we will see how many 8 bit parts are all 1's
                for i in range(int(prefix/8)): #for all the multiples of 8 in the prefix
                    bitmaskList = [255] + bitmaskList #add 'FF' or '255' to the list of bits to mask
                    count -= 1 #we added one value to bitMaskList so decrement count
                #now we will check if there is an ip part that has 1-7 ones
                bitmask = 0;
                for i in range(prefix%8):
                    bitmask += int(math.pow(2,i))
                if prefix% 8 != 0:
                    bitmaskList = [bitmask] + bitmaskList
                    count -= 1
                #lastly, if there are any unaccounted for parts, make them 0
                for i in range(count):
                    bitmaskList = [0]+bitmaskList
                # At this point in the code the BitMask list should be complete
#                 print(bitmaskList)

                #Now that we have made the list of Bits that we will mask with, we need to make a the list of the IP numbers
                ipSplit = ip[0].split('/') #isolate out the prefix
                ipSplit = ipSplit[0].split('.') #this was much easier than the bitmask
                
                result = 0
                for i in range(len(bitmaskList)): #now mask all the parts individually and sum the result
                    result += int(ipSplit[i]) & bitmaskList[i] #and bitmask and ip part
                
                if result != 0: #if bitmask is not 0, prefix is invalid
                    #print("Error! "+ip[0], "is invalid!")
                    ipList.remove(ip)
    return
'''
/*----------------------------------------------------- clean -----
Function clean(postContent)

Purpose:  Takes in a string (postContent) and removes html
          formatting returning purely the characters typed
          by the user.

Parameters:
    postContet (string) -- the text of the post

Returns:  string containing the postContent without html formatting
-------------------------------------------------------------------*/
'''
def clean(postContent):
    postContent = re.sub(r'(\\t)*(\\n)*','',postContent) #removes all \n and \t
    soup = BeautifulSoup(postContent, "html.parser")
    postContent = soup.get_text(separator=" ")
    postContent = postContent.lower() #lowercase it all to make searching easier
#     print(postContent.encode("utf-8")) #for testing purposes
    return postContent


def plotkeyWords(DBname, pword, TIDfilepath, tableName, keyWordsfilepath, keyWordsfilepath2, aggregate):
    con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
    curs = con.cursor()
    
    keyWordsFile = open(keyWordsfilepath, 'r')#open the file containing key words
    keyWords = re.split(r'\n', keyWordsFile.read().lower()) #split file into list (tuple?) of keyWords
    ps = PorterStemmer()
    keyWordsStemmed = []
    for word in keyWords:
        keyWordsStemmed.append(" " + ps.stem(word.strip(" "))) #the stem of all the specified keyWords
    
    keyWordsZip = list(zip(keyWords, keyWordsStemmed))
    
    TIDlist = np.genfromtxt(TIDfilepath, delimiter = ',')
#     print(TIDlist)
    pdateList = []
    plotData = {}
    aggreDict = {}
    wordDict = {}
    numNone = 0
    BOOLEANJ = False
    for tid in TIDlist[1:]:
        #print(str(tid))
        ExecuteStatement = "SELECT pid, tid, pdate, pcontent FROM " + tableName + " WHERE tid = " + str(tid) + " AND pdate > '2013-12-31' AND pdate < '2016-01-01'"
        curs.execute(ExecuteStatement)
        selectDataMatrix = curs.fetchall()
        
        for i in range(len(selectDataMatrix)):
            if selectDataMatrix[i][2] is not None:
                findKeyWordsPreStemmed(clean(selectDataMatrix[i][3]), wordDict, keyWordsZip)
                y, m, d = str(selectDataMatrix[i][2]).split('-') #character could change per table
                pdate = date(int(y), int(m), int(d))
                if pdate not in pdateList:
                    pdateList.append(pdate)
#                 tocompare = date(2015,12,31)
#                 if pdate > tocompare:
                for word in wordDict:
                    if word in plotData:
                        sameDate = False
                        for tpl in plotData[word]:
                            if pdate == tpl[0]: #if word found on same date
                                numIntances = tpl[1] + wordDict[word] #add num instances from that date
                                newTpl = (tpl[0], numIntances)
                                tpl = newTpl #update tuple pair in list
                                sameDate = True
                        if not sameDate: #first time this word is found on this day
                            plotData[word].append((pdate, wordDict[word]))
                    else:
                        pair = (pdate, wordDict[word])
                        plotData[word] = []
                        plotData[word].append(pair)
#                 print(wordDict)
                for word in keyWordsZip:
                    word = word[0]
                    if word not in wordDict: #if word was not found in post
#                         print(word+ " keyword was not found on " + str(pdate))
                        if word in plotData: #found word exists in plotData
                            sameDate = False
                            for tpl in plotData[word]: #check each pdate for this word and see if it matches current pdate
                                if pdate == tpl[0]: #if same pdate, 
                                    sameDate = True #word already found for this day on different post
                            if not sameDate:
                                plotData[word].append((pdate,0))
                        else: #word does not exist in plotData yet
                            pair = (pdate, 0) #creaste a pair of 0 instances on pdate
                            plotData[word] = [] #initialize empty list
                            plotData[word].append(pair) #add pair to list
                wordDict.clear()
            else:
                numNone = numNone + 1
#             if i > 15: #use this code to limit how many posts get plotted for testing reasons
#                 BOOLEANJ = True
#         if BOOLEANJ:
#             break
         
    #So theres an issue with the way the above code works, it only plots points on the dates where there are posts
    #so if someone is trying to select a few specific threads that happen two years apart, there is no data for all
    #time in between those two years so no points are being plotted. So to fix: for every MONTH (this can be changed
    #where the user wants to change over what time period these plot points can be viewed) that doesnt have any data,
    #plug in 0 for all words.
    pdateList = sorted(pdateList)
    for i in range(len(pdateList)-1):
        dateDifference = pdateList[i+1] - pdateList[i]
#         print("Difference: " + str(dateDifference.days))
        if dateDifference.days > 5:
#             print("0's plotted on this day:", pdateList[i] + datetime.timedelta(days=1))
#             print("0's plotted on this day:", pdateList[i+1] - datetime.timedelta(days=1))
            for word in keyWordsZip:
                word = word[0]
                pair = (pdateList[i] + datetime.timedelta(days=1), 0) #creaste a pair of 0 instances on pdate
                pair2 = (pdateList[i+1] - datetime.timedelta(days=1), 0)
                plotData[word].append(pair) #add pair to list
                plotData[word].append(pair2)
    #at this point in code, all keywords should have been found and organized away into plottable data
#     for element in pdateList:
#         print(element)
    for word in plotData:
        wordList = plotData[word]
        for pair in wordList:
            if pair[0] not in aggreDict:
                aggreDict[pair[0]] = pair[1]
            else:
                aggreDict[pair[0]] = aggreDict[pair[0]] + pair[1]
    
    mpl.rcParams['font.size'] = 20
    fig = plt.figure(figsize=(200, 6))
    fig.set_size_inches(50, 10) #adjustable, (width, height)
    ax  = fig.add_subplot('111')
    outputFile = open('plotCSV.csv', 'w')
    outputFile.write("Pdate, KeyWord, numInstances\n")
    lineStyle = ['-', '--', '-.', ':']
    markerStyle = ['.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'D', 'd', '|', '_']
    
    i=0
    if not aggregate:
        for word in plotData:
            plotData[word] = sorted(plotData[word],key=itemgetter(0))
            pdates = []
            instances = []
            for item in plotData[word]:
                pdates.append(item[0])
                instances.append(item[1])
                outputFile.write(str(item[0]) + "," + word + "," + str(item[1]) + "\n")
    #         print(pdates)
            ax.plot(pdates, instances, 'o-', c=np.random.rand(3,1), lw=2, alpha=0.8, label= word, linestyle= lineStyle[i%4], marker = markerStyle[i%20])
            legend = pylab.legend(bbox_to_anchor=(0., (-.04 * len(plotData)/7 + .002), 1., .102), ncol = 8, mode = "expand", borderaxespad = 0, fontsize = 'small')
            i = i + 1
        
    if aggregate:
        tempList = []
        for dates in aggreDict:
            tempList.append((dates, aggreDict[dates])) #get all the dates and instances into a list to sort them
        tempList = sorted(tempList, key=itemgetter(0))
        
        pdates = []
        instances = []
        for word in tempList:
            pdates.append(tempList[i][0])
            instances.append(tempList[i][1])
            i = i + 1
            
        ax.plot(pdates, instances, 'o-', c=np.random.rand(3,1), lw=2, alpha=0.8, label= "Key_wordsMal", linestyle= lineStyle[i%4], marker = markerStyle[i%20])
        legend = pylab.legend(bbox_to_anchor=(0., (-.04 * len(plotData)/7 + .002), 1., .102), ncol = 8, mode = "expand", borderaxespad = 0, fontsize = 'small')
        
        
    if keyWordsfilepath2 is not None:
        keyWordsFile = open(keyWordsfilepath2, 'r')#open the file containing key words
        keyWords = re.split(r'\n', keyWordsFile.read().lower()) #split file into list (tuple?) of keyWords
        keyWordsStemmed = []
        for word in keyWords:
            keyWordsStemmed.append(" " + ps.stem(word.strip(" "))) #the stem of all the specified keyWords
        
        keyWordsZip = list(zip(keyWords, keyWordsStemmed))
        
        TIDlist = np.genfromtxt(TIDfilepath, delimiter = ',')
    #     print(TIDlist)
        pdateList = []
        plotData = {}
        aggreDict = {}
        wordDict = {}
        numNone = 0
        BOOLEANJ = False
        for tid in TIDlist[1:]:
            ExecuteStatement = "SELECT pid, tid, pdate, pcontent FROM " + tableName + " WHERE tid = " + str(tid) + " AND pdate > '2013-12-31' AND pdate < '2016-01-01'"
            curs.execute(ExecuteStatement)
            selectDataMatrix = curs.fetchall()
            for i in range(len(selectDataMatrix)):
                if selectDataMatrix[i][2] is not None:
                    findKeyWordsPreStemmed(clean(selectDataMatrix[i][3]), wordDict, keyWordsZip)
                    y, m, d = str(selectDataMatrix[i][2]).split('-') #character could change per table
                    pdate = date(int(y), int(m), int(d))
                    if pdate not in pdateList:
                        pdateList.append(pdate)
                    for word in wordDict:
                        if word in plotData:
                            sameDate = False
                            for tpl in plotData[word]:
                                if pdate == tpl[0]: #if word found on same date
                                    numIntances = tpl[1] + wordDict[word] #add num instances from that date
                                    newTpl = (tpl[0], numIntances)
                                    tpl = newTpl #update tuple pair in list
                                    sameDate = True
                            if not sameDate: #first time this word is found on this day
                                plotData[word].append((pdate, wordDict[word]))
                        else:
                            pair = (pdate, wordDict[word])
                            plotData[word] = []
                            plotData[word].append(pair)
    #                 print(wordDict)
                    for word in keyWordsZip:
                        word = word[0]
                        if word not in wordDict: #if word was not found in post
    #                         print(word+ " keyword was not found on " + str(pdate))
                            if word in plotData: #found word exists in plotData
                                sameDate = False
                                for tpl in plotData[word]: #check each pdate for this word and see if it matches current pdate
                                    if pdate == tpl[0]: #if same pdate, 
                                        sameDate = True #word already found for this day on different post
                                if not sameDate:
                                    plotData[word].append((pdate,0))
                            else: #word does not exist in plotData yet
                                pair = (pdate, 0) #creaste a pair of 0 instances on pdate
                                plotData[word] = [] #initialize empty list
                                plotData[word].append(pair) #add pair to list
                    wordDict.clear()
                else:
                    numNone = numNone + 1
#                 if i > 15: #use this code to limit how many posts get plotted for testing reasons
#                     BOOLEANJ = True
#             if BOOLEANJ:
#                 break
    #         
        #So theres an issue with the way the above code works, it only plots points on the dates where there are posts
        #so if someone is trying to select a few specific threads that happen two years apart, there is no data for all
        #time in between those two years so no points are being plotted. So to fix: for every MONTH (this can be changed
        #where the user wants to change over what time period these plot points can be viewed) that doesnt have any data,
        #plug in 0 for all words.
        pdateList = sorted(pdateList)
        for i in range(len(pdateList)-1):
            dateDifference = pdateList[i+1] - pdateList[i]
    #         print("Difference: " + str(dateDifference.days))
            if dateDifference.days > 5:
    #             print("0's plotted on this day:", pdateList[i] + datetime.timedelta(days=1))
    #             print("0's plotted on this day:", pdateList[i+1] - datetime.timedelta(days=1))
                for word in keyWordsZip:
                    word = word[0]
                    pair = (pdateList[i] + datetime.timedelta(days=1), 0) #creaste a pair of 0 instances on pdate
                    pair2 = (pdateList[i+1] - datetime.timedelta(days=1), 0)
                    plotData[word].append(pair) #add pair to list
                    plotData[word].append(pair2)
        #at this point in code, all keywords should have been found and organized away into plottable data
    #     for element in pdateList:
    #         print(element)
        for word in plotData:
            wordList = plotData[word]
            for pair in wordList:
                if pair[0] not in aggreDict:
                    aggreDict[pair[0]] = pair[1]
                else:
                    aggreDict[pair[0]] = aggreDict[pair[0]] + pair[1]
        
        
        i=0
        if not aggregate:
            for word in plotData:
                plotData[word] = sorted(plotData[word],key=itemgetter(0))
                pdates = []
                instances = []
                for item in plotData[word]:
                    pdates.append(item[0])
                    instances.append(item[1])
                    outputFile.write(str(item[0]) + "," + word + "," + str(item[1]) + "\n")
        #         print(pdates)
                ax.plot(pdates, instances, 'o-', c=np.random.rand(3,1), lw=2, alpha=0.8, label= word, linestyle= lineStyle[i%4], marker = markerStyle[i%20])
                legend = pylab.legend(bbox_to_anchor=(0., (-.04 * len(plotData)/7 + .002), 1., .102), ncol = 8, mode = "expand", borderaxespad = 0, fontsize = 'small')
                i = i + 1
            
        if aggregate:
            tempList = []
            for dates in aggreDict:
                tempList.append((dates, aggreDict[dates])) #get all the dates and instances into a list to sort them
            tempList = sorted(tempList, key=itemgetter(0))
            
            pdates = []
            instances = []
            for word in tempList:
                pdates.append(tempList[i][0])
                instances.append(tempList[i][1])
                i = i + 1
                
            ax.plot(pdates, instances, 'o-', c=np.random.rand(3,1), lw=2, alpha=0.8, label= "Key_wordsFear", linestyle= lineStyle[i%4], marker = markerStyle[i%20])
            legend = pylab.legend(bbox_to_anchor=(0., (-.04 * len(plotData)/7 + .002), 1., .102), ncol = 8, mode = "expand", borderaxespad = 0, fontsize = 'small')
            
        
#---------------------------------------------------------------------------------------------------------------
#     fig.tight_layout()
    fig.savefig('timeseries.png', bbox_extra_artists=(legend,), bbox_inches='tight')
    outputFile.close()
    
    print("A total of", str(numNone) + " posts with no p-date that weren't accounted for.")
    return

#---------------------------------------------------------------------------------------------------------------

def plotNoTid(DBname, pword, tableName, keyWordsfilepath):
    con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
    curs = con.cursor()
    
    keyWordsFile = open(keyWordsfilepath, 'r')#open the file containing key words
    keyWords = re.split(r'\n', keyWordsFile.read().lower()) #split file into list (tuple?) of keyWords
    ps = PorterStemmer()
    keyWordsStemmed = []
    for word in keyWords:
        keyWordsStemmed.append(" " + ps.stem(word.strip(" "))) #the stem of all the specified keyWords
    
    keyWordsZip = list(zip(keyWords, keyWordsStemmed))
    
    pdateList = []
    plotData = {}
    wordDict = {}
    numNone = 0
    ExecuteStatement = "SELECT pid, tid, pdate, pcontent FROM " + tableName + " WHERE pdate > '2013-12-31' AND pdate < '2015-01-01'"
    curs.execute(ExecuteStatement)
    selectDataMatrix = curs.fetchall()
    
    for i in range(len(selectDataMatrix)):
        if selectDataMatrix[i][2] is not None:
            findKeyWordsPreStemmed(clean(selectDataMatrix[i][3]), wordDict, keyWordsZip)
            y, m, d = str(selectDataMatrix[i][2]).split('-') #character could change per table
            pdate = date(int(y), int(m), int(d))
            if pdate not in pdateList:
                pdateList.append(pdate)
#                 tocompare = date(2015,12,31)
#                 if pdate > tocompare:
            for word in wordDict:
                if word in plotData:
                    sameDate = False
                    for tpl in plotData[word]:
                        if pdate == tpl[0]: #if word found on same date
                            numIntances = tpl[1] + wordDict[word] #add num instances from that date
                            newTpl = (tpl[0], numIntances)
                            tpl = newTpl #update tuple pair in list
                            sameDate = True
                    if not sameDate: #first time this word is found on this day
                        plotData[word].append((pdate, wordDict[word]))
                else:
                    pair = (pdate, wordDict[word])
                    plotData[word] = []
                    plotData[word].append(pair)
#                 print(wordDict)
            for word in keyWordsZip:
                word = word[0]
                if word not in wordDict: #if word was not found in post
#                         print(word+ " keyword was not found on " + str(pdate))
                    if word in plotData: #found word exists in plotData
                        sameDate = False
                        for tpl in plotData[word]: #check each pdate for this word and see if it matches current pdate
                            if pdate == tpl[0]: #if same pdate, 
                                sameDate = True #word already found for this day on different post
                        if not sameDate:
                            plotData[word].append((pdate,0))
                    else: #word does not exist in plotData yet
                        pair = (pdate, 0) #creaste a pair of 0 instances on pdate
                        plotData[word] = [] #initialize empty list
                        plotData[word].append(pair) #add pair to list
            wordDict.clear()
        else:
            numNone = numNone + 1
#         if i > 150: #use this code to limit how many points get plotted for testing reasons
#             break
#         
    #So theres an issue with the way the above code works, it only plots points on the dates where there are posts
    #so if someone is trying to select a few specific threads that happen two years apart, there is no data for all
    #time in between those two years so no points are being plotted. So to fix: for every MONTH (this can be changed
    #where the user wants to change over what time period these plot points can be viewed) that doesnt have any data,
    #plug in 0 for all words.
    pdateList = sorted(pdateList)
    for i in range(len(pdateList)-1):
        dateDifference = pdateList[i+1] - pdateList[i]
#         print("Difference: " + str(dateDifference.days))
        if dateDifference.days > 15:
#             print("0's plotted on this day:", pdateList[i] + datetime.timedelta(days=1))
#             print("0's plotted on this day:", pdateList[i+1] - datetime.timedelta(days=1))
            for word in keyWordsZip:
                word = word[0]
                pair = (pdateList[i] + datetime.timedelta(days=1), 0) #creaste a pair of 0 instances on pdate
                pair2 = (pdateList[i+1] - datetime.timedelta(days=1), 0)
                plotData[word].append(pair) #add pair to list
                plotData[word].append(pair2)
    #at this point in code, all keywords should have been found and organized away into plottable data
#     for element in pdateList:
#         print(element)

    mpl.rcParams['font.size'] = 20
    fig = plt.figure(figsize=(200, 6))
    fig.set_size_inches(50, 10) #adjustable, (width, height)
    ax  = fig.add_subplot('111')
    outputFile = open('plotCSV.csv', 'w')
    outputFile.write("Pdate, KeyWord, numInstances\n")
    lineStyle = ['-', '--', '-.', ':']
    markerStyle = ['.', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'D', 'd', '|', '_']
    
    i=0
    for word in plotData:
        plotData[word] = sorted(plotData[word],key=itemgetter(0))
        pdates = []
        instances = []
        for item in plotData[word]:
            pdates.append(item[0])
            instances.append(item[1])
            outputFile.write(str(item[0]) + "," + word + "," + str(item[1]) + "\n")
#         print(pdates)
        ax.plot(pdates, instances, 'o-', c=np.random.rand(3,1), lw=2, alpha=0.8, label= word, linestyle= lineStyle[i%4], marker = markerStyle[i%20])
#         plt.legend(handles=temp)
        pylab.legend(loc='upper right', fontsize = 'small')
        i = i + 1
    fig.tight_layout()
    fig.savefig('Andre\'s_Outputs\Plots\2014keyWords_mal(noTidList).png')
    outputFile.close()
    
    print("A total of", str(numNone) + " posts with no p-date that weren't accounted for.")
    return