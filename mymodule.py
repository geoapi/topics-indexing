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
key = "keqVr01zTBktmTggfO2lMg((" #get this outside in a config file for example so that the user can define his own

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
    dump_Qs_to_mongoDB(list1,api_name,keyword)
    i += 1
    while (i <= page and list1['has_more'] and list1['quota_remaining'] > 0):
#        url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100"
        #TODO Get the key stored into a seperate text file and load it here instead
        url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("
        url = url + '&tagged=' + tag + "&page=" + str(i)
        res = requests.get(url)
        list1 = res.json()
        dump_Qs_to_mongoDB(list1,api_name,keyword)
        i += 1
        if (list1['has_more'] and list1['quota_remaining']==0):
          print('Quota issue, process will resume in 1 day!')
          threading.Timer(86400, get_qs(tag,i)).start()
    e = timer()
    print (e - s)
    return

    #/ 2.2 / search / advanced?order = desc & sort = activity & q = API + api + winapi & tagged = winapi & site = stackoverflow
def get_api_qs_with_content(api_name, tag, keyword, page, i):
        import requests
        url = "http://api.stackexchange.com/2.2/search/advanced?order=desc&filter=withbody&sort=activity&q="+keyword+"&tagged="+tag+"&site=stackoverflow&pagesize=100&key="+key+ "&page="+ str(i)
        #    url = "http://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&filter=withbody&pagesize=100"
       # url = url + '&tagged=' + tag
        res = requests.get(url)
        list1 = res.json()
        dump_Qs_to_mongoDB(list1,api_name, keyword)
        i += 1
        while (i <= page and list1['has_more'] and list1['quota_remaining'] > 0):
            url ="http://api.stackexchange.com/2.2/search/advanced?order=desc&filter=withbody&sort=activity&q="+keyword+"&tagged="+tag+"&site=stackoverflow&pagesize=100&key="+key+ "&page=" + str(i)
            res = requests.get(url)
            list1 = res.json()
            dump_Qs_to_mongoDB(list1,api_name, keyword)
            i += 1
            if (list1['has_more'] and list1['quota_remaining'] == 0):
                print('Quota issue, process will resume in 1 day!')
                threading.Timer(86400, get_api_qs_with_content(api_name,tag,keyword,page, i)).start()
        #e = timer()
        #print(e - s)
        return

    #accepts number of questions ids as string, get answers for Qids
def get_answers(str1):
      import requests
      url1 = "https://api.stackexchange.com/2.2/questions/"
      url2= "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody&key="+key
      #url2 = "/answers?order=desc&sort=activity&site=stackoverflow&filter=withbody"
      url = url1 + str(str1) + url2
      headers ={"Accept":"application/json", "User-Agent": "RandomHeader"}
      res = requests.get(url,headers)
      if (res.status_code == 502 or res.status_code == 400):
          print("You have used your quota for today, will resume later tomorrow!")
          return None
      return res.json()

    #Save one obj into questions collection DB
def dump_Qs_to_mongoDB(data,api_name, k):
    import pymongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["questions"]
    list1 = data['items']
    for item in list1:
        item['api']=api_name
        mycol.update(item, item, upsert=True) # To make sure the document is updated not duplicated
    #x = mycol.insert_many(list1)
    myclient.close()
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



#index based on specific API
def index_one_api_questions_records(api_keyword):
    import pymongo, json
    from bson import Binary, Code, json_util
    from bson.json_util import dumps
    import json
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["questions"]

    for doc in mycol.find({ "$and":[{'api':{'$regex': api_keyword}}]},no_cursor_timeout=True):
        api_name = []
        topic_name = []
        loaded_doc = json.loads(json_util.dumps(doc))
        for api_mention in api_dict:
            try:
                if (check_keyword_mention(api_mention['name'], loaded_doc['title']) or check_keyword_mention(
                        api_mention['name'], loaded_doc['body']) or check_keyword_mention(api_mention['name'],
                                                                                          loaded_doc['tags'])):
                    api_name.append(api_mention['name'])
                for item in topic_dict:
                    for key in item['keywords']:
                        if (check_keyword_mention(key, loaded_doc['title']) or check_keyword_mention(key, loaded_doc[
                            'body'])):
                            topic_name.append(item['name'])
                            # TODO ADD to an api mention elements from the enrichment Word Embedding and Word Net
                            for syn1 in synonyms_wordnet:
                                if (syn1["keywords"] == item['name']):
                                    for key_syn in syn1["synonyms"]:
                                        topic_name.append(key_syn)
            except KeyError as error:
                print(error)
        api_name = remove_dup(api_name)
        topic_name = remove_dup(topic_name)
        try:
            obj = {
                "body": loaded_doc['body'],
                "title": loaded_doc['title'],
                "tags": loaded_doc['tags'],
                # "view_count": loaded_doc['view_count'],
                # "owner":loaded_doc['owner']['user_id'],
                "question_id": loaded_doc['question_id'],
                # "score":loaded_doc['score'],
                "api": api_name,  # TODO makeit a function detector
                "topic": topic_name,
                "my_join_field": {
                    "name": "q"
                }
            }
        except KeyError as error:
            print(error)

        elasticsearch_questions_posts(obj)
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

        for doc in mycol.find(no_cursor_timeout=True):
            api_name = []
            topic_name = []
            loaded_doc =  json.loads(json_util.dumps(doc))
            for api_mention in api_dict:
               try:
                if (check_keyword_mention(api_mention['name'],loaded_doc['title']) or check_keyword_mention(api_mention['name'],loaded_doc['body'])  or check_keyword_mention(api_mention['name'],loaded_doc['tags'])):
                    api_name.append(api_mention['name']);
                for item in topic_dict:
                    for key in item['keywords']:
                        if (check_keyword_mention(key, loaded_doc['title']) or check_keyword_mention(key, loaded_doc['body'])):
                            topic_name.append(item['name'])
               except KeyError as error:
                    print(error)
            api_name = remove_dup(api_name)
            topic_name = remove_dup(topic_name)
            try:
                obj = {
                "body":loaded_doc['body'],
                "title":loaded_doc['title'],
                "tags":loaded_doc['tags'],
                #"view_count": loaded_doc['view_count'],
                #"owner":loaded_doc['owner']['user_id'],
                "question_id":loaded_doc['question_id'],
                #"score":loaded_doc['score'],
                "api":api_name, #TODO makeit a function detector
                "topic":topic_name,
                "my_join_field": {
                    "name": "q"
                 }
                }
            except KeyError as error:
                print(error)

            elasticsearch_questions_posts(obj)
        return None

def remove_dup(it):
    seen = set()
    uniq = []
    for x in it:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return (uniq)


def elasticsearch_questions_posts(doc):
        #from datetime import datetime
        from elasticsearch import Elasticsearch, helpers
        es = Elasticsearch()
        res = es.index(index="question", doc_type='so', id=doc['question_id'], body=doc)
        print(res['result'])
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
                #"answer_owner":loaded_doc['owner']['user_id'],
                "answer_id":loaded_doc['answer_id'],
                #"score":loaded_doc['score'],
                "question_id":loaded_doc['question_id'],
                "my_join_field": {
                     "name": "a",
                     "parent":loaded_doc['question_id']
                     }
              }
            except KeyError as error:
                print(error)
#            mycol.close()
            elasticsearch_answers_posts(obj)
        return

#This is good to find the number of hits
def elasticsearch_topic_search_hits(keyword):
    # from datetime import datetime
    from elasticsearch import Elasticsearch, helpers
    import elasticsearch.helpers
    # from elasticsearch_dsl import Search
    # s = Search(using=client, index="my-index") \
    #     .filter("term", category="search") \
    #     .query("match", title="python") \
    #     .exclude("match", description="beta")

    es = Elasticsearch()
    # res = es.search(index="question", body={"query": {
    #     "match" : {
    #         "title" : keyword
    #     }
    # },
    # "size": 2,
    # "from": 0,
    # "_source": [ "title", "body", "tags" ],
    # "highlight": {
    #     "fields" : { "title" : {} }
    # }})

    res = es.search(index="question", body={"query": {
        "match": {
            "body": keyword
        }
    },
        "size": 2,
        "from": 0,
        "_source": ["body", "tags"],
        "highlight": {
            "fields": {"body": {}}
        }})
    print("Got %d Hits:" % res['hits']['total'])
    for hit in res['hits']['hits']:
        print("%(tags)s : %(body)s" % hit["_source"])
    return



#TODO this function returns the first ten posts only, read about scan and pagination at https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#hits
def elasticsearch_topic_search_content(keyword):
    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search
    client = Elasticsearch()
    s = Search(using=client)
    s = s.using(client)
    s = Search().using(client).query("match", title=keyword)
    response = s.execute()
    for hit in s:
         print(hit.title)
    return

def check_keyword_mention(keyword,text):
    if keyword in text:
        return True
    else:
        return False

# Get synonyms from WordNet
def get_syn(keyword):
 import nltk
 from nltk.corpus import wordnet
 synonyms = []
 for syn in wordnet.synsets(keyword):
   for l in syn.lemmas():
     synonyms.append(l.name())
 return synonyms


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

api_dict = [
             # {"name":"facebook","keywords":["facebook graph api", "facebook API", "facebook api", "FB API", "fb api"],"tag":"facebook-graph-api"},
             # {"name":"twitter", "keywords":["twitter api", "Twitter API"], "tag":"twitter-api"},
             # {"name":"winapi","keywords":["Winapi","win api", "WINAPI", "win32 api", "Windows API","The Windows API"],"tag":"winapi"},
             # {"name":"gmail", "keywords":["Google GMail api", "Gmail API"], "tag":"gmail-api"},
             # {"name":"java", "keywords":["Java api", "Java API"], "tag":"java-api"},
             # {"name": "youtube", "keywords": ["YouTube API"], "tag": "youtube-api"},
             # {"name": "googleplaces", "keywords": ["Google Places API"], "tag": "google-places-api"},
             # {"name": "instagram", "keywords": ["instagram api","Instagram API"], "tag": "instagram-api"}
             #  ,
             #  {"name": "youtube", "keywords": ["youtube api"], "tag": "youtube-api"}
             # ,
              {"name": "gmail", "keywords": ["gmail api"], "tag": "gmail-api"}
             #,
             # {"name": "", "keywords": [""], "tag": ""}
             # # ,
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},
             # {"name": "", "keywords": [""], "tag": ""},

            ]

topic_dict = [
    {"id":0,"name":"security","category_id":0, "keywords":["security"]},
    {"id":1,"name":"oauth configuration","category_id":0,"keywords":["oauth","authentication","configuration","settings"]},
    {"id":2,"name":"oauth clarification","category_id":0,"keywords":["oauth"]}, #,"understand","clarify" take out as they are not necessarly related to oauth
 #   {"id":3,"name":"api constraints","category_id":1,"parent":true,"keywords":["restrictions"]},
 #   {"id":4,"name":"possibility of a functionality","category_id":1,"parent":false,"keywords":["possible","feasible","functionality"]},
 #   {"id":5,"name":"understanding usage limitation","category_id":1,"parent":false,"keywords":["limited","restricted","understanding"]},
    {"id":6,"name":"debugging","category_id":2,"keywords":["debug","fix","error","bug"]},
 #   {"id":7,"name":"request","category_id":2,"keywords":["request","call","invocation"]},
    {"id":8,"name":"behaviour","category_id":2,"keywords":["behaviour"]},
    {"id":9,"name":"parameters","category_id":2,"keywords":["param","parameter"]},
    {"id":10,"name":"returned data","category_id":2,"keywords":["returned","requested","data"]},
    {"id":11,"name":"settings","category_id":3,"keywords":["settings","configuration"]},
    {"id":12,"name":"usage","category_id":4,"keywords":["usage","use","example"]},
 #   {"id":13,"name":"features implementation feasibility","category_id":4,"parent":false,"keywords":["feature","feasible","possible"]},
 #   {"id":14,"name":"understanding functionality","category_id":4,"keywords":["how to do"]},
 #   {"id":15,"name":"seeking alternative implementation","category_id":4,"parent":false,"keywords":["alternative","way","another"]},
 #   {"id":16,"name":"development environment","category_id":4,"parent":false,"keywords":["environment","development"]},
 #   {"id":17,"name":"examples","category_id":4,"parent":false,"keywords":["example","code"]},
    {"id":18,"name":"documentation","category_id":5,"keywords":["documentation","docs","reference"]},
    {"id":19,"name":"redirection","category_id":5,"keywords":["redirect"]},
    {"id":20,"name":"reporting issues","category_id":5,"keywords":["typo","mistake","error"]},
  #  {"id":21,"name":"definition","category_id":6,"parent":true,"keywords":["definition"]},
    {"id":22,"name":"design patterns","category_id":6,"keywords":["design","design-pattern","design-patterns"]},
    {"id":23,"name":"version management","category_id":6,"keywords":["version"]},
    {"id":24,"name":"setting parameters","category_id":6,"keywords":["setting","parameter"]},
    {"id":25,"name":"recommendation","category_id":6,"keywords":["recommend"]}
    ]



synonyms_wordnet = [
    {"keywords": "security","synonyms":[ "protection", "certificate"]},
    {"keywords":"authentication","synonyms":["authentication", "certification"]},
    {"keywords": "configuration",
     "synonyms":[ "shape", "form", "contour", "conformation"]},
    {"keywords": "settings",
     "synonyms":
         ["setting", "scene", "setting", "background", "scope", "mise_en_scene", "stage_setting", "setting", "context", "circumstance"]},
    {"keywords": "understand",
     "synonyms":
         ["understand", "understand", "realize", "realise", "see", "read", "interpret", "translate", "infer", "sympathize"]},
    {"keywords": "clarify",
     "synonyms":
         ["clarify", "clear_up", "elucidate", "clarify"]},
    {"keywords": "fix",
     "synonyms":
         ["fix", "repair", "fixing", "fixture", "mend", "mending", "reparation", "localization", "localisation","set"]},
    {"keywords": "error",
     "synonyms":
         ["mistake", "error", "fault", "erroneousness", "error", "wrongdoing", "computer_error", "error", "mistake"]},
    {"keywords": "behaviour",
     "synonyms":
      ['behavior', 'demeanor', 'demeanour', 'behavior', 'behaviour', 'conduct', 'doings']},
    {"keywords": "parameters",
     "synonyms":['parameter', 'argument']},
    {"keywords": "returned",
     "synonyms":['return', 'render', 'revert', 'retrovert', 'regress', 'recall', 'rejoin', 'refund', 'repay']},
    {"keywords": "requested",
         "synonyms":['request', 'bespeak', 'quest', 'request', 'request', 'requested']},
    {"keywords": "data",
         "synonyms":['data', 'information', 'datum']},
    {"keywords": "settings",
         "synonyms":['setting', 'scene', 'background', 'scope', 'context', 'circumstance', 'mount']},
    {"keywords": "usage",
         "synonyms":['use', 'utilization', 'utilisation', 'employment', 'exercise', 'custom', 'usance']},
    {"keywords": "use",
         "synonyms":['usage', 'utilization', 'utilisation', 'employment', 'exercise', 'function', 'purpose', 'role', 'consumption', 'usance']},
    {"keywords": "example",
         "synonyms":['illustration', 'instance', 'representative', 'model', 'exemplar', 'case', 'instance', 'exercise']
    },
    {"keywords": "documentation",
         "synonyms":['certification','support']},
    {"keywords": "mistake",
         "synonyms":['error', 'fault', 'misunderstanding', 'misapprehension', 'misidentify', 'err', 'mistake', 'slip']},
    {"keywords": "design",
         "synonyms":['designing', 'plan', 'blueprint', 'figure', 'purpose', 'intent', 'intention', 'aim', 'invention', 'conception']},
    {"keywords": "recommend",
         "synonyms":['urge', 'advocate', 'commend']}
    ]










def extractor(api_dict):
#iterate through all apis taking all possible searches keywords for 10 pages each with 100 items(Qs)
 for item in api_dict:
    tag = item['tag']
    item_keywords = item['keywords']
    api_name = item['name']
    for k in item_keywords:
        get_api_qs_with_content(api_name,tag, k , 999, 1)


#get all the answers content to DB
#insert_As_into_Qs_MongoDB()
#for idx count 5 lines
s = timer()

#extractor(api_dict)
#index_all_questions_records()

#useful for one API extraction
index_one_api_questions_records("gmail")

#index_all_answers_records()

#This need TODO while extracting api inspect topics as well

#Search result without content , useful to find number of hits
#res = elasticsearch_topic_search("API")


#now return search results with content using keyword in title? 1/12/2018
#elasticsearch_topic_search_content("API")

#update_elk_index_add_topic("security", res)

e = timer()
print(e-s, " timing Questions and Answers indexing by ELK ")
# if creating initilization (start with resetting exisiting data (delete_qs_and_as()) then 1- get_qs('tag',10) tag=api. 1000 posts. 2- Store the Qs 3- get As 4- Store As insert_As_into_Qs_MongoDB() 5- index questions at elk 6- index As using Elk. Now that Elasticsearch has everything, we can simply use our indexing.py

#TODO make an advanced search against SO API looking for posts that conatins API keyword in titlte or in the body for a given tag posts
