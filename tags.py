import xml.etree.ElementTree
from collections import defaultdict
import pickle

def get_info(tag):
    import requests
    import time, threading
    from timeit import default_timer as timer
    s = timer()
    #i = 1 initilize at the start so that a timing thread call can be used to the last page number after the quota if finished.
    # example wiki excerpt from SO API https: // api.stackexchange.com / 2.2 / tags / winapi / wikis?site = stackoverflow
    url1 = "http://api.stackexchange.com/2.2/tags/"
    url = url1 + tag +  "/wikis?site=stackoverflow&filter=withbody&pagesize=100&key=keqVr01zTBktmTggfO2lMg(("

    res = requests.get(url)
    if (res.status_code != 200):
        return 0
    list1 = res.json()
    #dump_Qs_to_mongoDB(list1)
    return list1

def save_obj(obj, name ):
    with open('./obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)




my_list = defaultdict(list)
e = xml.etree.ElementTree.parse('/home/george/Downloads/tags/Tags.xml').getroot()
for atype in e.findall('row'):
    tag_n = (atype.get('TagName'))
    a= get_info(atype.get('TagName'))
    if a and a['items']:
       try:
        k= (a['items'][0]['excerpt'])
        if 'framework' in k:
            print("framework found")
            my_list['framework'].append(tag_n)
        if 'API' in k:
            print("API found Capital letters")
            my_list['API'].append(tag_n)
        if 'library' in k:
            print("API library found")
            my_list['library'].append(tag_n)
        if 'SDK' in k:
            print("SDK found")
            my_list['sdk'].append(tag_n)
        if 'prgramming language' in k:
            print("Prog. Lang. found")
            my_list['pl'].append(tag_n)    
       except KeyError:
           pass
save_obj(my_list, 'my_api_framework') #save the output dictionary to this file

#TODO load obj and print api keywords
