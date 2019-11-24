import os
import json
import time

import requests
import wikipedia
import numpy as np


'''
# reference: 
# https://query.wikidata.org

# retrieve articles of people (born after 1500 and die before 2010) who received an award
query = """
SELECT DISTINCT ?article WHERE {  
  ?award (wdt:P31/(wdt:P279*)) wd:Q618779. # instance or subclass of an award
  ?person wdt:P31 wd:Q5; # person is instance of human
          wdt:P166 ?award. # person received an award
  
  ?person wdt:P569 ?birth;
          wdt:P570 ?death.
  
  ?article schema:about ?person.
  ?article schema:isPartOf <https://en.wikipedia.org/>. # article is in English
  
  FILTER((?birth > "1900-01-01"^^xsd:dateTime) && (?death < "2010-01-01"^^xsd:dateTime))
}
"""

# retrieve articles of people (born after 1500 and die before 2010) who are scientists
query = """
SELECT DISTINCT ?article WHERE {
	?person wdt:P31 wd:Q5; # person is instance of human
            wdt:P106/wdt:P279* wd:Q901. # person is a scientist

    ?article schema:about ?person.
    ?article schema:isPartOf <https://en.wikipedia.org/>. # article is in English
  
    ?person wdt:P569 ?birth;
            wdt:P570 ?death.
    FILTER((?birth > "1500-01-01"^^xsd:dateTime) && (?death < "2010-01-01"^^xsd:dateTime))
}
"""

url = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'
json_data = requests.get(url, params={'query':query, 'format':'json'}).json()
with open('people_test.json', 'w') as outfile:
    json.dump(json_data['results']['bindings'], outfile)
'''

# filename = 'people_won_awards_1910_2010_en'
filename = 'scientists_1500_2010_en'
with open('{}.json'.format(filename)) as json_file:
    data = json.load(json_file)
print('data length:', len(data))


# count number of unique articles
articles = set()
data_deduplicated = []
for item in data:
    if item['article'] not in articles:
        articles |= {item['article']}
        data_deduplicated.append(item)
print('number of unique articles:', len(articles))


# select 20000 random articles
data_selected = [data_deduplicated[i] for i in np.random.choice(20000, len(articles))]


def retrieve_content(data, directory_name):
    article_url = data['article']
    article_name = article_url.split('/')[-1]
    print(article_name, '|', article_url)
    
    # check if file exists
    file_path = '{}/{}.txt'.format(directory_name, article_name)
    if os.path.isfile(file_path):
        print('{}.txt exists'.format(article_name))
    else:
        api_response_json = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&titles={}'.format(article_name)).json()
        try:
            content = wikipedia.page(title=list(api_response_json['query']['pages'].values())[0]['title']).content
        except Exception as e:
            try:
                print(e, "Trying 'title' instead of 'pageid'...", end=' ')
                content = wikipedia.page(pageid=list(api_response_json['query']['pages'].keys())[0]).content
                print('alternative method successful!')
            except Exception as e:
                content = ''
                print(e, 'alternative method failed!')
        # save file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(content)


start = 20
end = len(data_selected)
for i in range(start, end):
    print(i, end=' ')
    retrieve_content(data_selected[i], filename)
    i += 1
    if i % 5 == 0:
        time.sleep(1)
