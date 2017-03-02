'''
Created on Mar 1, 2017

@author: Andre
'''
import wordcount
import time


start_time = time.time()

DBname = "MichalisPrj"
Password = "1"
filepath = 'C:\\Users\\Andre\\Desktop\\requestedtool\\ZeroDay Tids.csv'
keyWordsFilePath = "C:\\Users\\Andre\\Desktop\\requestedtool\\LimitedKeyWords2.txt"
tableName = "tbl_wilders_post"

wordcount.plot(DBname, Password, filepath, tableName, keyWordsFilePath)

print("done: --- %s seconds ---" % (time.time() - start_time))