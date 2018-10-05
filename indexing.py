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

def create_we_index(topics_content,topics_index):
    for i in topics_content:
       for j in i['wiki']:
        t = j
        #TODO sanitize the term t for example remove any backslashes from it / \ - or special chars
        #print(t); #prints all topics names from the json document
        url = "http://localhost:9200/question/so/_search?"
        params = dict(
            q = t
        )
        resp = requests.get(url=url, params=params)
        data = resp.json()
        if ( resp.status_code !==400):
            data2 = data['hits']['hits']
            dic = []
            if ((len(data2)) > 0):
               #k=0
               for j in data2:
                  # dic.insert(k,j['_id'])
                   topics_index[t].append(j['_id'])

    return (topics_index)

def init_simple_keyword_index():
    with open('./topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_index(topics_content,topics_index)
    print(topics_index)
    print(topics_index['oauth configuration'])
    return (topics_index)


def init_we_keyword_index():
    with open('./valid-topics.json','r') as f:
        doc = json.load(f)
    topics_index = defaultdict(list)
    topics_content = doc['topics']
    topics_index = create_we_index(topics_content,topics_index)
    print(topics_index)
    print(topics_index['oauth configuration'])
    return (topics_index)

#indexing only API Topics keywords
#init_simple_keyword_index()
init_we_keyword_index()
