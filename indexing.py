from collections import defaultdict
import json
import requests

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

def init_simple_keyword_index():
    with open('./topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_index(topics_content,topics_index)
    print(topics_index)
    print(topics_index['security'])
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

#indexing only API Topics keywords
#init_simple_keyword_index()

#indexing using bag of keywords
init_bag_of_keywords_index()

#This indexing is using Wiki WE indexing
#init_we_keyword_index()
