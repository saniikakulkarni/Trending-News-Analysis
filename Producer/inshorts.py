import requests
from bs4 import BeautifulSoup
import datetime
import json
import time
from kafka import KafkaProducer, KafkaConsumer

topic_name='headlines'

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer=KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=json_serializer)

def get_inshorts_news(category):
    newsDictionary = []
    try:
        htmlBody = requests.get('https://www.inshorts.com/en/read/' + category)
    except requests.exceptions.RequestException as e:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = str(e.message)
        return newsDictionary

    soup = BeautifulSoup(htmlBody.text, 'lxml')
    newsCards = soup.find_all(class_='news-card')
    if not newsCards:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = 'Invalid Category'
        return newsDictionary
    for card in newsCards:
        try:
            title = card.find(class_='news-card-title').find('a').text
        except AttributeError:
            title = None
        try:
            content = card.find(class_='news-card-content').find('div').text
        except AttributeError:
            content = None

        try:
            date = card.find(class_='date').text
        except AttributeError:
            date = None

        try:
            time = card.find(class_='time').text
        except AttributeError:
            time = None

        newsObject = {
            '_id':time+"-"+date,
            'text': title,
            'source':"inshorts"
        }
        print(newsObject)
        print('\n')
        producer.send(topic_name,newsObject)
        producer.flush()
       

categories=["national","business","sports","world","politics","technology","startup","entertainment","miscellaneous","hatke","science","automobile"]

def store_inshorts_news():
    for category in categories:
        get_inshorts_news(category)

store_inshorts_news()
