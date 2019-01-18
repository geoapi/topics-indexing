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
                            #for syn1 in synonyms_wordnet:
                            for syn1 in so_embedding:
                                if (syn1["keywords"] == item['name']):
                                    for key_syn in syn1["embeddings"]:
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
       if x:
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
    es = Elasticsearch()
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

#search for a specific topic based on the topic mentions
def elasticsearch_topic_search_keyword(keyword):
    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search
    client = Elasticsearch()
    s = Search(using=client)
    s = s.using(client)
    s = Search().using(client).query("match", topic=keyword)
    response = s.execute()
    for hit in s:
         print(hit.title)
    return



#search for a specific topic based on the topic mentions
def elasticsearch_api_search_keyword(keyword):
    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search
    client = Elasticsearch()
    s = Search(using=client)
    s = s.using(client)
    s = Search().using(client).query("match", api=keyword)
    response = s.execute()
    for hit in s:
         print(hit.title)
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


def findWholeWord(w):
  import re
  return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
def check_keyword_mention(keyword,text):
    #if keyword in text: #this would return true for here in there!
     if findWholeWord(str(keyword))(str(text)):
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



def elastic_request_api(api_name):
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    #url = "http://localhost:9200/question/_search?"
    params = json.dumps({
        "query": {
            "query_string": {
                "query": api_name,
                "fields": ["api"],
            }
        }
    })
    data = es.search(index="question", doc_type="so", body=params, size=20)
    if (data['hits']['total'] > 0):
        data2 = data['hits']['hits']
    else:
        data2 =[]
    return (data['hits']['total'], data2)


def elastic_request_topic(topic_name):
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    #url = "http://localhost:9200/question/_search?"
    params = json.dumps({
        "query": {
            "query_string": {
                "query": topic_name,
                "fields": ["topic"],
            }
        }
    })
    data = es.search(index="question", doc_type="so", body=params, size=20)
    if (data['hits']['total'] > 0):
        data2 = data['hits']['hits']
    else:
        data2 =[]
    return (data['hits']['total'], data2)



def elastic_request_apiAndtopic(topic_name,api_name):
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    if (len(topic_name) > 1):
        topic = ' '.join(topic_name)
    else:
        topic = topic_name[0]
    if (len(api_name) > 1):
        api = ' '.join(api_name)
    else:
        api = api_name[0]

    params = json.dumps({
        "query": {
            "bool": {
              "must": [{
                  "match": {
                      "api": api
                  }
              }, {
                  "match": {
                      "topic": topic
                  }
              }]
            }
        }
    })
    data = es.search(index="question", doc_type="so", body=params, size=20)
    if (data['hits']['total'] > 0):
        data2 = data['hits']['hits']
    else:
        data2 =[]
    return (data['hits']['total'], data2)



#A DSL that consider topic colon and keyword e.g. topic:security and api colon keyword e.g. api:facebook
#returns array of topic names and array of api names
def check_dsl_string(dsl_string):
    import spacy
    nlp = spacy.load('en')
    topic_name = []
    api_name = []
    document = nlp(dsl_string)
    lemmas = [token.lemma_ for token in document if not token.is_stop]
    j = 0
    while j < len(lemmas):
        if (lemmas[j]=="topic"):
            topic_name.append(lemmas[j+2])
        if (lemmas[j]=="api"):
            api_name.append(lemmas[j+2])
        j=j+3
    return(topic_name,api_name)


# A DSL that is similar to Blekko
def check_bdsl_string(dsl_string):
    dsl_string = dsl_string.split(' ')
    #prepare a bare-list of api names and another for topic names so we can match
    topic_dict_temp = []
    api_dict_temp = []
    topic_name = []
    api_name = []
    for item in api_dict:
        if item['name']:
          api_dict_temp.append(item['name'].lower())
        for key in item['keywords']:
           if key:
               api_dict_temp.append(key.lower())
    topics_dict_temp = []
    for item in topic_dict:
        topics_dict_temp.append(item['name'].lower())
        for key in item['keywords']:
            if key:
                topics_dict_temp.append(key.lower())
    not_included_dict = []
    for one_item in dsl_string:
        user_keyword = ''.join(filter(str.isalnum,one_item))
        operator = one_item[0]
        if (user_keyword in topics_dict_temp and operator == '/'):
            topic_name.append(user_keyword)
        if (user_keyword in api_dict_temp and operator == '/'):
            api_name.append(user_keyword)
        if (operator == '-'):
            not_included_dict.append(user_keyword)

    return(topic_name,api_name,not_included_dict)


# Dynamic Construction of ELK DSL
def construct_dynamic_dsl(topic_name,api_name,not_included_dict):
    i = 0
    op = ''
    match_ = ''
    while (len(topic_name) > 1 and i < len(topic_name)):
       match_ = match_ +op+' {"match":{"topic":"'+topic_name[i]+'"}}'
       op = ','
       i +=1
    i = 0
    while (len(api_name) >= 1 and i < len(api_name)):
        match_ = match_ + op + ' {"match":{"api":"' + api_name[i] + '"}}'
        op = ','
        i += 1
    if (len(topic_name) >1 or len(api_name) > 1):
        match_ = '{"bool": {"must": ['+match_+']}}'
# MUST NOT
    i = 0
    op = ''
    match2_ = ''
    while (len(not_included_dict) >= 1 and i < len(not_included_dict)):
        match2_ = match2_ + op + ' {"match":{"tags":"' + not_included_dict[i] + '"}}'
        op = ','
        i += 1
    if not_included_dict:
        match2_ = ',{"bool":{"must_not":['+match2_+']}'
    dsl = '{"query":{"bool":{"must":['+match_+match2_+'}]}}}'
    return dsl

#only for topic AND api MUST
def construct_dynamic_dsl_api_topic(topic_name,api_name,not_included_dict):
    i = 0
    op = ''
    match_ =''
    while (len(topic_name) > 1 and i < len(topic_name)):
       match_ = match_ +op+' {"match":{"topic":"'+topic_name[i]+'"}}'
       op = ','
       i +=1
    i = 0
    op = ','
    while (len(api_name) > 1 and i < len(api_name)):
        match_ = match_ + op + ' {"match":{"api":"' + api_name[i] + '"}}'
        op = ','
        i += 1
    dsl = '{"query":{"bool":{"must":['+match_+']} }}'
    return dsl
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
             {"name":"facebook","keywords":["facebook graph api", "facebook API", "facebook api", "FB API", "fb api"],"tag":"facebook-graph-api"},
             {"name":"twitter", "keywords":["twitter api", "Twitter API"], "tag":"twitter-api"},
             {"name":"winapi","keywords":["Winapi","win api", "WINAPI", "win32 api", "Windows API","The Windows API"],"tag":"winapi"},
             {"name":"gmail", "keywords":["Google GMail api", "Gmail API"], "tag":"gmail-api"},
             {"name":"java", "keywords":["Java api", "Java API"], "tag":"java-api"},
             {"name": "youtube", "keywords": ["YouTube API"], "tag": "youtube-api"},
             {"name": "googleplaces", "keywords": ["Google Places API"], "tag": "google-places-api"},
             {"name": "instagram", "keywords": ["instagram api","Instagram API"], "tag": "instagram-api"},
              {"name": "youtube", "keywords": ["youtube api"], "tag": "youtube-api"},
             {"name": "", "keywords": [""], "tag": ""},
             {"name": "googlecalendar", "keywords": ["google calendar api"], "tag": "google-calendar-api"},
              {"name": "dropbox", "keywords": ["dropbox api"], "tag": "dropbox-api"},
              {"name": "slack", "keywords": ["slack api"], "tag": "slack-api"},
              {"name": "heresdk", "keywords": ["HERE sdk"], "tag": "here-api"},
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
    {"id":0,"name":"API security","category_id":0, "keywords":["security"]},
    {"id":1,"name":"oauth configuration","category_id":0,"keywords":["oauth","authentication","configuration","settings"]},
    {"id":2,"name":"oauth clarification","category_id":0,"keywords":["oauth"]}, #,"understand","clarify" take out as they are not necessarly related to oauth
    {"id":3,"name":"api constraints","category_id":1,"keywords":["restrictions"]},
    {"id":4,"name":"possibility of a functionality","category_id":1,"keywords":["possible","feasible","doable"]},
    {"id":5,"name":"understanding usage limitation","category_id":1,"keywords":["limited","restricted","impossible"]},
    {"id":6,"name":"debugging","category_id":2,"keywords":["debug","fix","error","bug"]},
    {"id":7,"name":"request","category_id":2,"keywords":["request","call","invocation"]},
    {"id":8,"name":"behaviour","category_id":2,"keywords":["behaviour"]},
    {"id":9,"name":"parameters","category_id":2,"keywords":["param","parameter"]},
    {"id":10,"name":"returned data","category_id":2,"keywords":["returned","requested","data"]},
    {"id":11,"name":"settings","category_id":3,"keywords":["settings","configuration"]},
    {"id":12,"name":"usage","category_id":4,"keywords":["usage","use","example"]},
    #{"id":13,"name":"features implementation feasibility","category_id":4,"parent":false,"keywords":["feature","feasible","possible"]},
    {"id":14,"name":"understanding functionality","category_id":4,"keywords":["how to","need to","know"]},
    {"id":15,"name":"seeking alternative implementation","category_id":4,"keywords":["alternative","way","another"]},
    {"id":16,"name":"development environment","category_id":4,"keywords":["environment","development","development-mode"]},
    {"id":17,"name":"examples","category_id":4,"keywords":["example","code"]},
    {"id":18,"name":"documentation","category_id":5,"keywords":["documentation","docs","reference"]},
    {"id":19,"name":"redirection","category_id":5,"keywords":["redirect"]},
    {"id":20,"name":"reporting issues","category_id":5,"keywords":["typo","mistake","error"]},
    {"id":21,"name":"definition","category_id":6,"keywords":["definition"]},
    {"id":22,"name":"design patterns","category_id":6,"keywords":["design","design-pattern","design-patterns"]},
    {"id":23,"name":"version management","category_id":6,"keywords":["version"]},
    {"id":24,"name":"setting parameters","category_id":6,"keywords":["setting","parameter"]},
    {"id":25,"name":"recommendation","category_id":6,"keywords":["recommend"]}
    ]



synonyms_wordnet = [
    {"keywords": "security","synonyms":[ "protection", "certificate"]},
    {"keywords":"authentication","synonyms":["authentication", "certification"]},
#    {"keywords": "configuration","synonyms":[ "shape", "form", "contour", "conformation"]},
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

so_embedding = [
{"keywords": "security","embeddings":["secuirty" ,"secutiry","secruity","securty","protection","privacy","securtiy","authentication"]},
{"keywords": "oauth","embeddings":["oauth2" ,"openid","oauth1","oath","ouath"]},
{"keywords":"authentication","embeddings":["auth", "authentification","authorization","authenication","authetication","authenticate","authorisation"]},
{"keywords":"auth","embeddings":["authentication", "authorization","authentification","authenication","authetication","authetication","autentication","authentcation","authenticate","auths","authorisation"]},
{"keywords": "configuration","embeddings":["config" ,"configurations","configuation","configuraiton","configration","configs","configuartion","configurtion","configuraton","settings"]},
{"keywords": "settings","embeddings":["setings" ,"setttings","configuration","preferences","configurations","settins","configration","settigs"]},
{"keywords": "understand","embeddings":["understanding" ,"understood","comprehend","grasp","explain","figure","realize","describe","undertand","undestand"]},
{"keywords": "clarify","embeddings":["elaborate" ,"clarification","explain","clarified","clarifying","clearify","rephrase","unclear","illustrate"]},
{"keywords": "debugging","embeddings":["debuging" ,"debug","debuggin","debugger","debbuging","debbugging","debuggers","debuger","tracing"]},
{"keywords": "fix","embeddings":["remedy" ,"fixing","fixes","solve","overcome","rectify","resolve","fixed","solved"]},
{"keywords": "error","embeddings":["errors" ,"exception","warning","errror","erorr","eror","erro","erros"]},
{"keywords": "bug","embeddings":["defect" ,"bugs","issue","incompatibility","quirk"]},
{"keywords": "behaviour","embeddings":["behavior" ,"behavour","behaviors","behaviours","behavoir","bahaviour","behaivour","bahavior","behavious","behaivor"]},
{"keywords": "parameters","embeddings":["paramters" ,"paramaters","parameter","arguments","params","paremeters","paramenters","parameteres","parms","parametes"]},
{"keywords": "param","embeddings":["parameter" ,"paramater","paramter","params","paramenter","parmeter","paremeter","parm","parametr","parameters"]},
{"keywords": "returned","embeddings":["return" ,"returns","returning","retuned","retuns","retured","retun","retuning","returing","retrieved"]},
{"keywords": "data","embeddings":["datas" ,"values","dataset","records","information","objects","table","record"]},
{"keywords": "requested","embeddings":["requesting" ,"specified","request","supplied","response","fetched","given"]},
{"keywords": "usage","embeddings":["consumption" ,"useage","utilization","utilisation","usages","usefulness","usuage"]},
{"keywords": "use","embeddings":["using" ,"used","uses","utilize","define","specify","create","expose","rely"]},
{"keywords": "example","embeddings":["exemple" ,"exmaple","similarly","illustration"]},
{"keywords": "documentation","embeddings":["docs" ,"documenation","documention","documentations","doco","docu","documentaion","documentaiton","documetation","doc"]},
{"keywords": "redirect","embeddings":["redirects" ,"redirecting","redirected","redirection","redirct","rediret"]},
{"keywords": "error","embeddings":["errors" ,"exception","warning","errror","erorr","eror","erro","erros"]},
{"keywords": "mistake","embeddings":["mistakes" ,"typo","misstake","blunder","oversight","idiot","stupid","typos","stupidly"]},
{"keywords": "design-patterns","embeddings":["gof" ,"ooad","ood","priciples","pattens","principles","patters"]},
{"keywords": "version","embeddings":["versions" ,"verison","verion","vesion","verson","versio","versione","verions","releases"]},
{"keywords": "setting","embeddings":["set" ,"seting","changing","resetting","setted","settting","adjusting","adding"]},
{"keywords": "recommend","embeddings":["suggest" ,"reccomend","reccommend","recomment","recomend","recommended","encourage","insist","discourage"]}
]

def check_spelling(keyword):
    import enchant
    d = enchant.Dict("en_US")
    if d.check(keyword):
        return True
    else:
        return False


#This is used to remove any typo word from the dictionary of word embeddings
def remove_typos_from(so_embedding):
  for item in so_embedding:
    i=0
    while (i < len(item['embeddings'])):
        if not check_spelling(item['embeddings'][i]):
            del item['embeddings'][i]
        i+=1
  return so_embedding



def extractor(api_dict):
#iterate through all apis taking all possible searches keywords for 999 pages each with 100 items(Qs)
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

#cleanup so word embedding from words with typos, please note that oauth1 may be deleted as its not an English word. Required when you want to index
#so_embedding = remove_typos_from(so_embedding)

#useful for one API extraction for effiecieny and speed. Esepcially when monitoring only one API of interest
#for key1 in api_dict:
#  index_one_api_questions_records(key1['name'])

#elasticsearch_topic_search_keyword("security")
#index_all_answers_records()

#This need TODO while extracting api inspect topics as well

#Search result without content , useful to find number of hits
#res = elasticsearch_topic_search("API")


#now return search results with content using keyword in title? 1/12/2018
#elasticsearch_topic_search_content("API")

#update_elk_index_add_topic("security", res)

#Get number of posts that we tagged with an API e.g. facebook and the top 20 posts, the size can be changed to whatever needed
#a = elastic_request_api("facebook")
#print(a)

#Get number of posts that is related to topic e.g. debugging and the top 20 posts content
#a= elastic_request_topic("debugging")
#print(a)



#get string that contains dsl query and identify topic names and api names and return dictionary for both
#a = check_dsl_string("topic:security topic:debugging api:facebook")
#print(a)
#get search results for a topic and an API as returned by the query.
#k = elastic_request_apiAndtopic(a[0],a[1]) #TODO Extend it to include NOT and to include more than just one API and one topic
#print(k)

import json
#get string that contains dsl query similar to blekko and identify topic names and api names and return dictionary for both
#It works!!!! Al Hamdo Lil Allah
#a = check_bdsl_string("/security /debugging /facebook -python")

a = check_bdsl_string("/security /facebook -python -cython")
print(a)
a= construct_dynamic_dsl(a[0],a[1],a[2])
print(a)

#k = elastic_request_apiAndtopic(a[0],a[1]) #TODO Extend it to include NOT and to include more than just one API and one topic
#print(k)

e = timer()
print(e-s, " timing Questions and Answers indexing by ELK ")
# if creating initilization (start with resetting exisiting data (delete_qs_and_as()) then 1- get_qs('tag',10) tag=api. 1000 posts. 2- Store the Qs 3- get As 4- Store As insert_As_into_Qs_MongoDB() 5- index questions at elk 6- index As using Elk. Now that Elasticsearch has everything, we can simply use our indexing.py

#TODO make an advanced search against SO API looking for
# posts that conatins API keyword in titlte or in the body for a given tag posts
