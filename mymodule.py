#https://stackoverflow.com/questions/tagged/box-api
#https://stackoverflow.com/questions/tagged/box-api?page=1&sort=votes&pagesize=50
# To search for say scoups API posts where there is scoups keyword in general in the post and api keyword in the body and title https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&q=scopus&body=api&title=api&site=stackoverflow
import json
from bson import ObjectId
from timeit import default_timer as timer
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
#JSONEncoder().encode(analytics) #here analytics is a variable of type dict which will be turned into string

# #make request to get questions based on tag and for one page at time
def get_qs(tag,page,i):
    import requests
    import json
    import time, threading
    from timeit import default_timer as timer
    s = timer()
    #i = 1 initilize at the start so that a timing thread call can be used to the last page number after the quota if finished.

    url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("
#    url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100"
    url = url + '&tagged=' + tag + "&page=" + str(i)
    res = requests.get(url)
    list1 = res.json()
    dump_Qs_to_mongoDB(list1)
    i += 1
    while (i <= page and list1['has_more'] and list1['quota_remaining'] > 0):
#        url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100"
        #TODO Get the key stored into a seperate text file and load it here instead
        url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("
        url = url + '&tagged=' + tag + "&page=" + str(i)
        res = requests.get(url)
        list1 = res.json()
        dump_Qs_to_mongoDB(list1)
        i += 1
        if (list1['has_more'] and list1['quota_remaining']==0):
          print('Quota issue, process will resume in 1 day!')
          threading.Timer(86400, get_qs(tag,i)).start()
    e = timer()
    print (e - s)
    return

    #accepts number of questions ids as string, get answers for Qids
def get_answers(str1):
      import requests
      url1 = "https://api.stackexchange.com/2.2/questions/"
      url2= "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody&key=keqVr01zTBktmTggfO2lMg(("
      #url2 = "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody"
      url = url1 + str(str1) + url2
      headers ={"Accept":"application/json", "User-Agent": "RandomHeader"}
      res = requests.get(url,headers)
      if (res.status_code == 502 or res.status_code == 400):
          print("You have used your quota for today, will resume later tomorrow!")
          return None
      return res.json()

    #Save one obj into questions collection DB
def dump_Qs_to_mongoDB(data):
    import pymongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["questions"]
    list1 = data['items']
    for item in list1:
        mycol.update(item,item,upsert=True) # To make sure the document is updated not duplicated
    #x = mycol.insert_many(list1)
    return

    #Save one obj into answers collection DB
def dump_As_to_mongoDB(data):
      import  pymongo
      myclient = pymongo.MongoClient("mongodb://localhost:27017/")
      mydb = myclient["api"]
      mycol = mydb["answers"]
      #x = mycol.insert_one(data)
      mycol.update(data, data, upsert=True)
      return


def delete_qs_and_as():
        import pymongo
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["api"]
        mycol1 = mydb["questions"]
        mycol2 = mydb["answers"]
        x = mycol1.delete_many({})
        y = mycol2.delete_many({})
        return
#TODO Need optimization i.e. we can have the accepted answer id from the question during its extraction and get it stored immediatly instead of searching all records in mongodb?
def insert_As_into_Qs_MongoDB():
        import pymongo
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["api"]
        mycol = mydb["questions"]
        for x in mycol.find(no_cursor_timeout=True):
            if (x['is_answered']):
               try:
                ans_obj = get_answers(x['question_id'])
    #            print(ans_obj['items'])
                for i in ans_obj['items']:
                    if(i['is_accepted']):
                     #print(i['is_accepted'],i)
                     #update_Q_add_AcceptedAnswer(i['question_id'], i) #this overwrites the body of the question! instead let us store the answer body in the answers collection
                      dump_As_to_mongoDB(i)
                    # send the object i of the question i['question_id'] to be stored into mongodb, question id to help find the question
               except KeyError as error:
                   print(error)
        mycol.close()

        return None

    # reads posts from questions collections and get useful information like title body etc. and index its content using elk
def index_all_questions_records():
        import pymongo, json
        from bson import Binary, Code, json_util
        from bson.json_util import dumps
        import json

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["api"]
        mycol = mydb["questions"]
        #docs=[]
        for doc in mycol.find(no_cursor_timeout=True):
            loaded_doc =  json.loads(json_util.dumps(doc))
            try:
                obj = {
                "body":loaded_doc['body'],
                "title":loaded_doc['title'],
                "tags":loaded_doc['tags'],
                "view_count": loaded_doc['view_count'],
                "owner":loaded_doc['owner']['user_id'],
                "question_id":loaded_doc['question_id'],
                "score":loaded_doc['score'],
                "my_join_field": {
                    "name": "q",
                 }
                }
            except KeyError as error:
                print(error)
            elasticsearch_questions_posts(obj)
        return None

def elasticsearch_questions_posts(doc):
        #from datetime import datetime
        from elasticsearch import Elasticsearch, helpers
        es = Elasticsearch()
        #print(doc)
        #get Qs from the DB
        # for each Q or doc make an index post for example a test-index type as tweet post doc
        res = es.index(index="question", doc_type='so', id=doc['question_id'], body=doc)
        print(res['result'])
        # get request to Elk
        res = es.get(index="question", doc_type='so', id=doc['question_id'])
        print(res['_source'])
        es.indices.refresh(index="question")
        #docs = get_all_records()
        #helpers.bulk(es, docs, chunk_size=1000, request_timeout=200)
        return

def elasticsearch_answers_posts(doc):
        from datetime import datetime
        from elasticsearch import Elasticsearch, helpers
        es = Elasticsearch()
        print(doc)
        # for each A or doc make an index post for example a test-index type as  post doc
        res = es.index(index="answer", doc_type='so', id=doc['answer_id'], body=json.dumps(doc), params={"routing": doc['question_id']})
        print(res['result'])
        # get request to Elk
        res = es.get(index="answer", doc_type='so', id=doc['answer_id'], params={"routing": doc['question_id']})
        print(res['_source'])
        es.indices.refresh(index="answer")
        #docs = get_all_records()
        #helpers.bulk(es, docs, chunk_size=1000, request_timeout=200)
        return


def index_all_answers_records():
        import pymongo, json
#        from bson import Binary, Code, json_util
#        from bson.json_util import dumps
#       import json

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["api"]
        mycol = mydb["answers"]
        #docs=[]
        for loaded_doc in mycol.find(no_cursor_timeout=True):
            #docs =[doc]
            #doc = json.dumps(doc)
            #print(loaded_doc)
           # json.dumps(result, default=json_util.default)
            #loaded_doc =  json.loads(json_util.dumps(doc))
           # TODO make a question document as the mapping in the index please, and make sure you create the relation to the answer, then get useful answer content as well
            #loaded_doc['title']
            try:
              obj = {
                "answer_body":loaded_doc['body'],
               # "answer_title":loaded_doc['title'],
               # "tags":loaded_doc['tags'],
                #"view_count": loaded_doc['view_count'],
                "answer_owner":loaded_doc['owner']['user_id'],
                "answer_id":loaded_doc['answer_id'],
                "score":loaded_doc['score'],
                "question_id":loaded_doc['question_id'],
                "my_join_field": {
                     "name": "a",
                     "parent":loaded_doc['question_id']
                     }
              }
            except KeyError as error:
                print(error)
            mycol.close()
            elasticsearch_answers_posts(obj)
        return



    # Here you can specify the number of pages where each page is 100 Questions
    #This is where the requests to store questions begins here only 300 questions
    #get_qs('api',3) #first
    #insert_As_into_Qs_MongoDB() #second or store As seperately
#delete_qs_and_as() #restart and reset DB
    #index all questions posts
    #index_all_questions_records()
    #index all answers posts, make sure each answer is linked to the question and the relation is properly set
    #index_all_answers_records()
    # if creating initilization (start with resetting exisiting data (delete_qs_and_as()) then 1- get_qs('tag',10) tag=api. 1000 posts. 2- Store the Qs 3- get As 4- Store As insert_As_into_Qs_MongoDB() 5- index questions at elk 6- index As using Elk. Now that Elasticsearch has everything, we can simply use our indexing.py

#get_qs('api',1000,1) #first call get questions assuming there are thousand posts starting from the first page  ###1
#insert_As_into_Qs_MongoDB() #store As seperately                                                                 ###2
#print(e-s, " timing Answers insertion to MongoDB ")
#Elasticsearch basic keywords Inverted indexing
s = timer()
index_all_questions_records()
index_all_answers_records()
e = timer()
print(e-s, " timing Questions and Answers indexing by ELK ")
    # if creating initilization (start with resetting exisiting data (delete_qs_and_as()) then 1- get_qs('tag',10) tag=api. 1000 posts. 2- Store the Qs 3- get As 4- Store As insert_As_into_Qs_MongoDB() 5- index questions at elk 6- index As using Elk. Now that Elasticsearch has everything, we can simply use our indexing.py

#TODO make an advanced search against SO API looking for posts that conatins API keyword in titlte or in the body for a given tag posts
