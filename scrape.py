
def scrape_questions_ids():
    """
    This function scraps a list of questions urls for extracting questions IDs (i.e. qids) purpose, any link then can be examined with another extractor
    """
    from bs4 import BeautifulSoup
    import requests
    #TODO Pass in the tag as an argument

    url ='https://stackoverflow.com/questions/tagged/api'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    a = soup.find_all(class_='question-hyperlink',href=True)

    #TODO NEXT PAGE looks like https://stackoverflow.com/questions/tagged/api?page=2&sort=votes&pagesize=50
    #soup.find_all(class_='question-hyperlink',href=True)[0]['href']
    list = []
    for item in a:
        print(item['href'])
        list.append(item['href'])
    return list

scrape_questions_ids()
