# Wikipedia Crawling
This project crawls biographies in English from [Wikipedia](https://en.wikipedia.org/wiki/Main_Page).

The biographies are first selected using [Wikidata Query Service](https://query.wikidata.org/). Example queries are like the following:
```sparql
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
```

```sparql
SELECT DISTINCT ?article WHERE {
    ?person wdt:P31 wd:Q5; # person is instance of human
            wdt:P106/wdt:P279* wd:Q901. # person is a scientist

    ?article schema:about ?person.
    ?article schema:isPartOf <https://en.wikipedia.org/>. # article is in English
  
    ?person wdt:P569 ?birth;
            wdt:P570 ?death.
    FILTER((?birth > "1500-01-01"^^xsd:dateTime) && (?death < "2010-01-01"^^xsd:dateTime))
}
```

Selected biographies' Wikipedia links are then stored in a JSON file from which each corresponding Wikipedia webpage is then downloaded.

## Environment Setup
To install all libraries/dependencies used in this project, run
```bash
pip3 install -r requirement.txt
```

## Experiment
```bash
python3 crawl_wikipedia_biographies.py
```