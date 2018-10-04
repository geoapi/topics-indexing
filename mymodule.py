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

# Here you can specify the number of pages where each page is 100 Questions
#This is where the requests to store questions begins here only 300 questions
#get_qs('api',3)
insert_As_into_Qs_MongoDB()
#delete_qs_and_as()
   




            
