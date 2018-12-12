from collections import defaultdict
import json
import requests
import pickle

def remove_special_char(s):
   a = ''.join(filter(str.isalnum, s))
   return (a)

def remove_numbers_fromStr(s):
    return ''.join([i for i in s if not i.isdigit()])

def create_index(topics_content,topics_index):
    for i in topics_content:
        t = i['name']
        #print(t); #prints all topics names from the json document
        url = "http://localhost:9200/question/so/_search?"
        params = dict(
            q = t
        )
        resp = requests.get(url=url, params=params)
        data = resp.json()
        data2 = data['hits']['hits']
        dic = []
        if ((len(data2)) > 0):
           #k=0
           for j in data2:
              # dic.insert(k,j['_id'])
               topics_index[t].append(j['_id'])
    return (topics_index)

#TODO here we need to search if a keyword exists as is and then we need to add duplicates for keywords based on the main topic name e.g. safty takes posts that has safty keyword and all security posts as well
def create_bok_index(topics_content,topics_index):
    for i in topics_content:
      for j in i['keywords']:
        t = j
        #print(t); #prints all topics names from the json document
        url = "http://localhost:9200/question/so/_search?"
        params = dict(
            q = t
        )
        resp = requests.get(url=url, params=params)
        data = resp.json()
        data2 = data['hits']['hits']
        dic = []
        if ((len(data2)) > 0):
           #k=0
           for j in data2:
              # dic.insert(k,j['_id'])
              if (j['_id'] not in topics_index[t]):
               topics_index[t].append(j['_id'])
    return (topics_index)

def create_we_index(topics_content,topics_index):
    for i in topics_content:
       for j in i['wiki']:
        t = j
        #TODO sanitize the term t for example remove any backslashes from it / \ - or special chars use Elasticsearch analyzers or nlp for this
        #print(t); #prints all topics names from the json document
        url = "http://localhost:9200/question/so/_search?"
        params = dict(
            q = t
        )
        resp = requests.get(url=url, params=params)
        data = resp.json()
        if ( resp.status_code != 400):
            data2 = data['hits']['hits']
            dic = []
            if ((len(data2)) > 0):
               #k=0
               for j in data2:
                  # dic.insert(k,j['_id'])
                   topics_index[t].append(j['_id'])
        else:
            print("resp status code is ",resp.status_code )

    return (topics_index)


def create_topickeyword_index(topics_content,topics_index):
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    for i in topics_content:
        t = i['name']
        for j in i['keywords']:
            k = t + "/" + j
            #print(k)
            if (j != t):
                url = "http://localhost:9200/question/_search?"
                params = json.dumps({
                    "query": {
                        "query_string": {
                            "query": j,
                            "fields": ["_all", "body^2"]
                        }
                    },
                    "_source": ["title", "body"],
                    "highlight": {
                        "fields": {
                            "body": {}
                        }
                    }
                })
                data = es.search(index="question", doc_type="so", body=params)
                #resp = requests.post(url=url, data=params)
                #data = res.json()
                if (data['hits']['total'] > 0):
                  data2 = data['hits']['hits']
                  if ((len(data2)) > 0):
                   for k in data2:
                  # dic.insert(k,j['_id'])
                     topics_index[t].append(k['_id'])

      # for j in i['keywords']:
      #   t = j
      #   #print(t); #prints all topics names from the json document
      #   url = "http://localhost:9200/question/so/_search?"
      #   params = dict(
      #       q = t
      #   )
      #   resp = requests.get(url=url, params=params)
      #   data = resp.json()
      #   data2 = data['hits']['hits']
      #   dic = []
      #   if ((len(data2)) > 0):
      #      #k=0
      #      for j in data2:
      #         # dic.insert(k,j['_id'])
      #         if (j['_id'] not in topics_index[t]):
      #          topics_index[t].append(j['_id'])
    return (topics_index)

def init_simple_keyword_index():
    with open('./topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_index(topics_content,topics_index)
#    print(topics_index)
#    print(topics_index['security'])
    return (topics_index)

def init_bag_of_keywords_index():
    with open('./topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_bok_index(topics_content,topics_index)
    print(topics_index)
    print(topics_index['security'])
    return (topics_index)

def init_we_keyword_index():
    with open('./valid-topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_we_index(topics_content,topics_index)
    print(topics_index)
    print(topics_index['security'])
    return (topics_index)


def init_topic_keywords_index():
    with open('./topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_topickeyword_index(topics_content,topics_index)
#    print(topics_index)
#    print(topics_index['security'])
    return (topics_index)


#saving the index using python pickle module source https://stackoverflow.com/a/19201448/4177087
def save_obj(obj, name ):
    with open('./obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('./obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
# for an index query the returned ids are searched within MongoDB , this will print all the question content. TODO find also the answer TODO show a shrot view of the post for e.g. titlte and first line of the question
def find_post(id):
    import pymongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["api"]
    mycol = mydb["questions"]
    for x in mycol.find({"question_id":int(id)}):
      print(x)

#indexing only API Topics keywords
#init_simple_keyword_index()
#indexing using bag of keywords
a = init_bag_of_keywords_index()
save_obj(a, 'myindex')

f = load_obj('myindex')
print(f['security'])
#here is an example of loading the created index from the pickle file and finding the security keyword
#a1 = init_simple_keyword_index()
#print(a1['authentication'])
#for i in a1:
#    for j in a1[i]:
#      find_post(j)
#EO Example

#print(a['feature'])
#This indexing is using Wiki WE indexing
#init_we_keyword_index()

#TODO cleaning keywords in WE
# K/T index ?
#
#TODO simple bot reply about topics
#TODO
#init_topic_keywords_index()
