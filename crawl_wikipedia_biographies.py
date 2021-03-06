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
with open('data/{}.json'.format(filename)) as json_file:
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


# select 20000 random articles' indices
data_selected_indices = np.random.choice(len(articles), 20000)


def retrieve_content(data, directory_name):
    article_url = data['article']
    article_name = article_url.split('/')[-1]
    
    # check if file exists
    content = None
    file_path = '{}/{}.txt'.format(directory_name, article_name)
    if os.path.isfile(file_path):
        print('{:<50} | {:<80} | downloaded'.format(article_name, article_url))
    else:
        print('{:<45} | {:<80} | downloading'.format(article_name, article_url))
        api_response_json = requests.get('https://en.wikipedia.org/w/api.php?action=query&format=json&titles={}'.format(article_name)).json()
        try:
            content = wikipedia.page(title=list(api_response_json['query']['pages'].values())[0]['title']).content
        except Exception as e:
            try:
                print(e, "Trying 'title' instead of 'pageid'...", end=' ')
                content = wikipedia.page(pageid=list(api_response_json['query']['pages'].keys())[0]).content
                print('alternative method successful!')
            except Exception as e:
                print(e, 'alternative method failed!')
        # save file
        if content is not None:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
        
        time.sleep(np.random.default_rng().random() + 0.5)


# crawl randomly selected articles
# for i, data in enumerate(data_selected_indices):
#     print(i, end=' ')
#     retrieve_content(data, filename)
#     i += 1


# crawl articles from start and end indices
start = 0
end = len(data_deduplicated)
for i in range(start, end):
    print(i, end=' ')
    retrieve_content(data_deduplicated[i], filename)
    i += 1