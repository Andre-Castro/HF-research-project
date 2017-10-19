from bs4 import BeautifulSoup
import re
import psycopg2

def clean(postContent):
    postContent = re.sub(r'(\\t)*(\\n)*','',postContent) #removes all \n and \t
    soup = BeautifulSoup(postContent, "html.parser")
    postContent = soup.get_text(separator=" ")
    postContent = postContent.lower() #lowercase it all to make searching easier
#     print(postContent.encode("utf-8")) #for testing purposes
    return postContent

def replaceContent(cleanPContent, pid, cursor, con, tableName):
    cleanPContent = cleanPContent.replace('\'', '\'\'') #replaces all '\' with '\\' so the replace statement below can execute correctly
    replaceStatement = "UPDATE " + tableName + " SET new_pcontent = \'{}\' WHERE pid = ".format(cleanPContent) + str(pid) + ";" #build the replace statement to be executed
    cursor.execute(replaceStatement) #edit the database with the replace statement above
    con.commit() #save the edits made to the database with the execution above
    return
    
    
if __name__ == '__main__':
    DBname = input("Please enter the database name containing the files you want to read: ")
    pword = input("Password: ")
    tableName = input("Table name: ")
    con = psycopg2.connect(database=DBname, user = "postgres", password=pword) #connect to postgres
    curs = con.cursor() #create a cursor for this database, allows us to access info from it

    ExecuteStatement = "SELECT pcontent, pid FROM " + tableName #WARNING: might need to change "pcontent" to "post_content" depending on database...
    curs.execute(ExecuteStatement) #perform the select defined above

    pTuple = curs.fetchall()
    for pContent in pTuple:
        cleanPContent = clean(pContent[0])
        pid = pContent[1]
        replaceContent(cleanPContent, pid, curs, con, tableName)