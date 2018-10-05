import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#JSONEncoder().encode(analytics) #here analytics is a variable of type dict which will which will be turned into string

#make request to get questions based on tag and for one page at time
def get_qs(tag,page):
   import requests
   import json
   i=1
   url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("
   url = url + '&tagged='+ tag + "&page="+str(i)
   res = requests.get(url)
   list1 = res.json()
   dump_Qs_to_mongoDB(list1)
   i+=1
   while (i <= page and list1['has_more'] and list1['quota_remaining']>0):
     url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("
     url = url + '&tagged='+ tag + "&page="+str(i)
     res = requests.get(url)
     list1 = res.json() 
     dump_Qs_to_mongoDB(list1)
     i+=1
   return

#accepts number of questions ids as string, get answers for Qids
def get_answers(str1):
  import requests
  import json 
  url1 = "https://api.stackexchange.com/2.2/questions/"
  url2= "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody&key=keqVr01zTBktmTggfO2lMg(("

  url = url1 + str(str1) + url2
  headers ={"Accept":"application/json", "User-Agent": "RandomHeader"}

  res = requests.get(url,headers)
  return res.json()

#Save one obj into questions collection DB
def dump_Qs_to_mongoDB(data):
  import  pymongo
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  mydb = myclient["api"]
  mycol = mydb["questions"]
  list1 = data['items'] 
  x = mycol.insert_many(list1)
  return

#Save one obj into answers collection DB
def dump_As_to_mongoDB(data):
  import  pymongo
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  mydb = myclient["api"]
  mycol = mydb["answers"]
  x = mycol.insert_one(data)
  return 

# def update_Q_add_AcceptedAnswer(id,ans_obj):
#     import pymongo
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     mydb = myclient["api"]
#     mycol = mydb["questions"]
#     mycol.update({'question_id':id},{'$set':ans_obj})
#     return

#delete content of the collections
def delete_qs_and_as():
    import pymongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol1 = mydb["questions"]
    mycol2 = mydb["answers"]
    x = mycol1.delete_many({})
    y = mycol2.delete_many({})
    return

def insert_As_into_Qs_MongoDB():
    import pymongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["questions"]
    for x in mycol.find():
        if (x['is_answered']):
            ans_obj = get_answers(x['question_id'])
#            print(ans_obj['items'])
            for i in ans_obj['items']:
                if(i['is_accepted']):
                 #print(i['is_accepted'],i)
                 #update_Q_add_AcceptedAnswer(i['question_id'], i) #this overwrites the body of the question! instead let us store the answer body in the answers collection
                 dump_As_to_mongoDB(i)
                # send the object i of the question i['question_id'] to be stored into mongodb, question id to help find the question


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
    for doc in mycol.find():
        #docs =[doc]
        #doc = json.dumps(doc)
       # json.dumps(result, default=json_util.default)
        loaded_doc =  json.loads(json_util.dumps(doc))
       # TODO make a question document as the mapping in the index please, and make sure you create the relation to the answer, then get useful answer content as well
        #loaded_doc['title']
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
        #print(obj)
        # for element in loaded_doc:
        #    element.pop('_id', None)
        #    element.pop('answer_count', None)
        #    element.pop('is_answered', None)
        #    element.pop('last_activity_date', None)
        #    element.pop('last_edit_date', None)
        #    element.pop('owner', None)
        #    element.pop('view_count', None)
        #    element.pop('__len__', None)
        #
        elasticsearch_questions_posts(obj)
    return

def elasticsearch_questions_posts(doc):
    from datetime import datetime
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
    from bson import Binary, Code, json_util
    from bson.json_util import dumps
    import json

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["answers"]
    #docs=[]
    for loaded_doc in mycol.find():
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
        #print(obj)
        # for element in loaded_doc:
        #    element.pop('_id', None)
        #    element.pop('answer_count', None)
        #    element.pop('is_answered', None)
        #    element.pop('last_activity_date', None)
        #    element.pop('last_edit_date', None)
        #    element.pop('owner', None)
        #    element.pop('view_count', None)
        #    element.pop('__len__', None)
        #
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
index_all_answers_records()
# if creating initilization (start with resetting exisiting data (delete_qs_and_as()) then 1- get_qs('tag',10) tag=api. 1000 posts. 2- Store the Qs 3- get As 4- Store As insert_As_into_Qs_MongoDB() 5- index questions at elk 6- index As using Elk. Now that Elasticsearch has everything, we can simply use our indexing.py
