from collections import defaultdict;
import json;
import requests;


with open('./topics.json','r') as f:
    doc = json.load(f);
topics_index = defaultdict(list)
topics_content = doc['topics'];
for i in topics_content:
    t = i['name']
    #print(t); #prints all topics names from the json document
    url = "http://localhost:9200/qpost1/so/_search?"
    params = dict(
        q = t
    )
    resp = requests.get(url=url, params=params)
    data = resp.json()
    data2 = data['hits']['hits']
    dic = [];
    if ((len(data2)) > 0):
       #k=0
       for j in data2:
          # dic.insert(k,j['_id'])
           topics_index[t].append(j['_id'])
           #k +=1
           #print(j['_id'])

      # print (dic) # ids of the documents that elasticsearch found containing T keyword
     #   print(data['hits'])
       #topics_index[t].append(dic)
print(topics_index)
print(topics_index['oauth configuration'])
