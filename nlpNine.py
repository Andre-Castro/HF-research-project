'''
Created on Dec 20, 2016

@author: Andre
'''
import re
import psycopg2
import wordcount
import time

start_time = time.time()

urlDict = [] #dict storing url instances and the pid of the post they were found in
ipDict = {} #dict storing instances of ip addressses and pid of thier respective post
keyWords_to_ColumnNums_Dict = {} #dictionary storing the collumn numbers for respective keywords for fast collum num search
replaceURLBool = False #bool for replacing found url's or not

keyWordsFile = open('LimitedKeyWords.txt', 'r')#open the file containing key words
keyWords = re.split(r'\n', keyWordsFile.read().lower()) #split file into list (tuple?) of keyWords

c = 0; #num to keep track of column number
for instance in keyWords: #assign values to keyWord->columNums Dict
    keyWords_to_ColumnNums_Dict[instance] = c
    c = c + 1
urlColNum = len(keyWords)
ipColNum = urlColNum + 1

#DBname = input("Please enter the database name containing the files you want to read)
#Password = input("Password: ")
DBname = "MichalisPrj"
Password = "1"
con = psycopg2.connect(database=DBname, user = "postgres", password=Password) #connect to postgres
curs = con.cursor() #create a cursor for this database, allows us to access info from it

ExecuteStatement = "SELECT pid, tid, pdate, pcontent FROM tbl_wilders_post WHERE pdate > '2016-05-01'"
# testExec = "SELECT pid, username, title, pcontent FROM testgs WHERE pid <= 9"
# insrtExec = "INSERT INTO testgs(title, pcontent) VALUES (title, 'testtest')"
curs.execute(ExecuteStatement) #perform the select defined above

selectDataMatrix = curs.fetchall()

fileOut = open('sparse_Matrix.csv', 'w')# csv file containing table of instances
mapPID = open('map_postInfo.csv', 'w')
prevNumUrls = 0
prevNumIps = 0

mapPID.write("index,pid,tid,pdate\n")

#prompt for whether or not found URL's should be replaced
userOption = input("Would you like to replace found URL's with \"**URLFound**\"? (enter y/n): ")
while(len(userOption) == 0 or (userOption[0].lower() != "y" and userOption[0].lower() != "n")):
    userOption = input("Im sorry, please enter either the letter 'y' or 'n': ")
subuserOp = userOption[0].lower() #prevents repetitive substring code below

if subuserOp == "y":
    print("You selected yes")
    replaceURLBool = True #set bool flag to true if use would like to replace found URL's
elif subuserOp == "n":
    print("You selected no")
    #bool isn't set to false here since it is false by default

#create a map mapping PID's to line numbers in sparse matrix
for i in range(len(selectDataMatrix)): #for each post
    postContent = selectDataMatrix[i][3]
    mapPID.write(str(i)+','+str(selectDataMatrix[i][0])+','+str(selectDataMatrix[i][1])+','+str(selectDataMatrix[i][2])+"\n")
    cleanPostContent = wordcount.clean(postContent)

    wordcount.findIPs(cleanPostContent, ipDict)
    wordcount.findURLs(selectDataMatrix[i], cleanPostContent, urlDict) #pass in urlDict and adds all found URL's from current post  to urlDict
    wordcount.findKeyWords(cleanPostContent, keyWords, fileOut, i, keyWords_to_ColumnNums_Dict) #pass in list of post content and keywords, writes to file keywords
    
    numPostURLS = len(urlDict) - prevNumUrls
    if replaceURLBool and numPostURLS != 0:
        wordcount.replaceURLs(selectDataMatrix[i], urlDict, numPostURLS, curs)
        con.commit()
    if numPostURLS != 0:
        fileOut.write(str(i) + ',' + str(urlColNum) + ',' + str(numPostURLS) + "\n")
    prevNumUrls = len(urlDict)
    
    numPostIPS = len(ipDict) - prevNumIps
    if numPostIPS != 0:
        fileOut.write(str(i) + ',' + str(ipColNum) + ',' + str(numPostIPS) + "\n")
    prevNumIps = len(ipDict)

mapPID.close()
i = 0
mapKeywords = open('map_keyword.csv', 'w')
for i in range(len(keyWords)):
    mapKeywords.write(keyWords[i]+','+str(i)+"\n")
mapKeywords.write("URL,"+str(i+1)+"\n")
mapKeywords.write("IP,"+str(i+2)+"\n")

mapKeywords.close()
fileOut.close()

curs.close()
con.close()

# print(urlDict)
# print(str(len(urlDict)))
print("--- %s seconds ---" % (time.time() - start_time))

#Questions 12/22
    # <img src tags not being found is that ok?
        # almost every img src ive seen in wilders is not an http, thats why I havent grabbed it. offcom is opposite
    # I noticed a <a tag class type called "internalLink" which refers to a url link within the own website, should I find those?    
    # just to make sure, should I be replacing urls in the a tag and where they are actually writting in the case where they are both right next to eachother
    
#URL's to investigate...
    #www.' 2584540
    #www.\\")' 2539705
    #http://www' 2479646
    #wwwwwwwww...' 2518970
    #www.facebook.com<CTRL+Z><enter>Click' 2451103
    
#notes 
    # format sparse matrix a little better
    # fix/replace re so that urls without www or http can be found.
    # include both ip prefix and v6 in ip search
    # Dictionary get updated when SAME KEY is found, only finding one (last) of each URL/IP, fix this.
    # Use NLTK too.
    # make sure URL is being found again in quote section... go to actual post online to check
    
#Questions for 11/17
    #for the keywords, do i want to grab them within other words? Ex: bot being found in botanical
        #FIX THIS: stemming function - nltk could allow for bot & bots beimg found
    #url duplicates, use where 2016 post pid : 2592373
        #account for duplicates of exact same url
        