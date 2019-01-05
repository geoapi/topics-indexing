#this is to get the details of a keyword e.g. security
#then info of the lemmas for each id extracted from the elements found for each keyword. i.e. security may have many items with ids, we then ask which lemmas exists for each

import sys
import requests
import json
from bs4 import BeautifulSoup

def get_lemmas(keyword):
 dic =[]
 if keyword:
  obj1 = requests.get('https://babelnet.io/v5/getSynsetIds?lemma='+keyword+'&searchLang=EN&key=52aea204-261d-4d7b-80f8-f40bdd740463')

  idsoup = BeautifulSoup(obj1.text,"lxml")
  jsonedgesitem = json.loads(idsoup.html.body.p.string)
  for i in jsonedgesitem:
   url = 'https://babelnet.io/v5/getSynset?id='+i['id']+'&key=52aea204-261d-4d7b-80f8-f40bdd740463' 
   obj2 = requests.get(url)
   obj2soup = BeautifulSoup(obj2.text,"lxml")
   obj2item = json.loads(obj2soup.html.body.p.string)
   for j in obj2item['senses']:
     k = j['properties']['fullLemma']
     if (k not in dic):
      dic.append(k)
 return dic    


def get_related(keyword):
  dic = []
  url = 'http://api.conceptnet.io/c/en/'+keyword
  obj1 = requests.get(url)
  idsoup = BeautifulSoup(obj1.text,"lxml")
  obj2item = json.loads(idsoup.html.body.p.string)
  for item in obj2item['edges']:
    key =item['@id']
    if key not in dic:
      dic.append(key)
  return dic








  









if len(sys.argv) >= 1:
    p = sys.argv[1]
    #res = get_lemmas(p)
    #print(res)
    r2 = get_related(p)
    print('now from ConceptNet \n')
    print(r2)
 
#TODO  try to see rational between keywords and being correct, as similar as possible, and has meaningful relation to the keyword.

"""
computer_security
Computer_insecurity
computer_security
cybersecurity
IT_security
computer_security
cybersecurity
IT_security
computer_security
computer_security
Compsec
COMPUSEC
..
..
..

""" 
