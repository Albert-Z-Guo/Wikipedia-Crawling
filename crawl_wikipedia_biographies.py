import os
import json
import time

import requests
import wikipedia


'''
# retrieve people's names
# reference: https://query.wikidata.org
query = """
SELECT DISTINCT ?article ?award ?person ?birth ?death WHERE {  
  ?award (wdt:P31/(wdt:P279*)) wd:Q618779. # instance or subclass of an award
  ?person wdt:P166 ?award ; # person received an award
          wdt:P31 wd:Q5. # person is instance of human
  
  ?article schema:about ?person.
  ?article schema:isPartOf <https://en.wikipedia.org/>. # article is in English
  
  ?person wdt:P569 ?birth;
          wdt:P570 ?death.
  
  FILTER((?birth > "1910-01-01"^^xsd:dateTime) && (?death < "2010-01-01"^^xsd:dateTime))
}
LIMIT 400000
"""
url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
json_data = requests.get(url, params={'query':query, 'format':'json'}).json()
with open('people_test.json', 'w') as outfile:
    json.dump(json_data['results']['bindings'], outfile)
'''

with open('people_test.json') as json_file:
    data = json.load(json_file)
print('raw data length:', len(data))


# count number of unique figure
people = set()
data_deduplicated = []
for item in data:
    if item['person'] not in people:
        people |= {item['person']}
        data_deduplicated.append(item)
print('number of unique figure:', len(people))


def retrieve_content(data):
    article_url = data['article']
    article_name = article_url.split('/')[-1]
    print(article_name, '|', article_url)
    api_response_json = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&titles={}'
                               .format(article_name)).json()
    try:
        content = wikipedia.page(pageid=list(api_response_json['query']['pages'].keys())[0]).content
    except Exception as e:
        try:
            print(e, "\ntrying 'title' instead of 'pageid'...")
            content = wikipedia.page(title=list(api_response_json['query']['pages'].values())[0]['title']).content
            print('alternative method successful!')
        except Exception as e:
            content = ''
            print(e, 'alternative method failed')
    return article_name, article_url, content


i = 0
for item in data_deduplicated:
    print(i, end=' ')
    article_name, article_url, content = retrieve_content(item)
    if not os.path.exists('crawled_biographies'):
        os.mkdir('crawled_biographies')
    with open('crawled_biographies/{}.txt'.format(article_name), 'w') as file:
        file.write(content)
    i += 1
    time.sleep(2)
