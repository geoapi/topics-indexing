#check if the string is a number https://stackoverflow.com/a/51652091/4177087
import re
def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False

def scrape_number_of_pages(tag):
    from bs4 import BeautifulSoup
    import requests
    i =1
    url = 'https://stackoverflow.com/questions/tagged/' + tag + "?page=" + str(i) + "&sort=votes&pagesize=50"
    page = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"})
    soup = BeautifulSoup(page.text, 'html.parser')
    nopages = soup.find_all('span',class_='page-numbers')
    d = []
    for item in nopages:
       a= item.get_text()
       if (is_number(a)):
         d.append(a)
    print(d)
    return int(max(d))

def scrape_questions_ids(tag):
    """
    This function scraps a list of questions urls for extracting questions IDs (i.e. qids) purpose, any link then can be examined with another extractor
    """
    from bs4 import BeautifulSoup
    import requests
    #TODO Pass in the tag as an argument
    i = 1
    url ='https://stackoverflow.com/questions/tagged/'+tag+"?page="+str(i)+"&sort=votes&pagesize=50"
    list = []
    nopages = scrape_number_of_pages(tag) # Get the number of pages

    while (i <= nopages):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        a = soup.find_all(class_='question-hyperlink',href=True)
        k=0
        while (k < 50):
        #for item in a:
            print(a[k]['href'])
            list.append(a[k]['href'])
            k+= 1
        i+= 1
        url = 'https://stackoverflow.com/questions/tagged/' + tag + "?page=" + str(i) + "&sort=votes&pagesize=50"

    return list

# Get question title and body
def scrape_question_content(q):
    from bs4 import BeautifulSoup
    import requests
    url = 'https://stackoverflow.com' + q
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    a = soup.find(class_='question-hyperlink', href=True)
    #print(a.get_text()) # getting the title
    title = a.get_text()
    body = soup.find_all("div",class_='post-text') # getting question text
    print(title, body)
    #TODO scrape all answers or just accepted answer

#scrape_questions_ids('winapi')

scrape_question_content('/questions/9479871/flickering-in-cam-video-display-why')

