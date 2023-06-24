#!/usr/bin/env python
# coding: utf-8

# In[1]:


import twint
import csv #Import csv
import os
import re
from datetime import date, timedelta
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from flair.models import TextClassifier
from flair.data import Sentence
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from wordcloud import WordCloud
import nest_asyncio
import json
from PIL import Image
import numpy as np

nest_asyncio.apply()
classifier = TextClassifier.load('en-sentiment')
stop_words = stopwords.words('english')

keyword = input("Keyword : ")

stop_words.append(keyword.lower())

now = date.today() - timedelta(days=1)
yesterday = now - timedelta(days=1)

df = pd.DataFrame(columns=['tweet', 'value'])

### 트위처 서치 세팅
config = twint.Config()
config.Search = '%s -filter:retweets lang:en' % (keyword)
#config.Search = 'nft lang:en'
config.Lang = 'en'
config.Since = '%s' % (now)
config.Until = '%s' % (yesterday)
config.Limit = 10000
config.Store_json = True
config.Output = "nft_2022-09-29.json"
#config.Hide_output = True

cnt = 0
tot = 0

twint.run.Search(config)

### Json으로 저장된 키워드 파일 불러오기 (twint)
tweets = []
for line in open('./%s_%s.json' % (keyword, now), 'r', encoding = 'UTF-8'):
    tweets.append(json.loads(line))
    
documents = []
docu_dict = {}

docu_dict['sentence'] = []
docu_dict['value'] = []

for i in tweets:
    ### 정규화를 통한 1차 전처리
    text = i['tweet']
    text = text.lower()
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub('@[\w]*', ' ', text)
    text = re.sub('[$][\w]*', ' ', text)
    text = re.sub('#[\w]*', ' ', text)
    text = re.sub('&[\w]*', ' ', text)
    text = re.sub('https\S+', ' ', text)
    text = re.sub('\s+', ' ', text)
    
    ### 감성분석
    sentence = Sentence(text)
    classifier.predict(sentence)
    
    value = 0
    cnt += 1

    try :
        #print(sentence.labels[0])
        
        ### 긍-부정 평가 후 필요한 값 추출
        if str(sentence.labels[0]).split()[-2] == 'POSITIVE':
            value += float(str(sentence.labels[0]).split()[-1][1:-1])
            df.loc[cnt-1] = [text, 1]
            
        else :
            value -= float(str(sentence.labels[0]).split()[-1][1:-1])
            df.loc[cnt-1] = [text, 0]
            
        tot += value
        
        ### 정규화를 통한 2차 전처리
        senten = str(sentence.labels[0]).split('"')[1]
        senten = re.sub('''\s's''',''''s''', senten)
        senten = re.sub('\s+', ' ', senten)
    
        documents.append(senten)
        
        docu_dict['sentence'].append(senten)
        docu_dict['value'].append(value)
            
    except :
        cnt -= 1
        print(senten)

print('------------')

### 긍-부정 종합 값 평가 (100% 이상도 가능)
if tot/cnt > 0 :
    print('%s is Positive %s' % (keyword, str(tot/cnt*100) + '%'))
elif tot/cnt < 0 :
    print('%s is Negative %s' % (keyword, str(tot/cnt*100) + '%'))
else :
    print('%s is Neutral' % (keyword))
    
print('------------')

docu_dict['score'] = tot/cnt*100

with open('./%s_%s_senti.json' % (keyword, now), 'w') as f:
    json.dump(docu_dict, f, indent = 4)

### 워드클라우드 shape
im = Image.open('./wing.jpg')
mask_arr = np.array(im)

### TF-IDF 분석
vectorizer = TfidfVectorizer(stop_words=stop_words, min_df=3)
#vectorizer = TfidfVectorizer()

tfid_vect = vectorizer.fit_transform(documents)

tfid = pd.DataFrame(tfid_vect.toarray(), columns=vectorizer.get_feature_names())

cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=50, mask=mask_arr).generate_from_frequencies(tfid.T.sum(axis=1))
# cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=200).generate_from_frequencies(tfid.T.sum(axis=1))

cloud.to_file('%s_%s_tf_idf.jpg' % (keyword, now))

### Count 분석
vectorizer2 = CountVectorizer(stop_words=stop_words, min_df=3)

count_vect = vectorizer2.fit_transform(documents)

count = pd.DataFrame(count_vect.toarray(), columns=vectorizer2.get_feature_names())
      
cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=50, mask=mask_arr).generate_from_frequencies(count.T.sum(axis=1))
# cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=200).generate_from_frequencies(count.T.sum(axis=1))

cloud.to_file('%s_%s_count.jpg' % (keyword, now))

### 긍-부정 평가 트윗 중 긍정 키워드 분석
positive = df[df['value'] == 1]
pos = " ".join(review for review in positive.tweet)

cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=50, mask=mask_arr).generate(pos)
# cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=200).generate(pos)

cloud.to_file('%s_%s_positive.jpg' % (keyword, now))

### 긍-부정 평가 트우시 중 부정 키워드 분석
negative = df[df['value'] == 0]
neg = " ".join(review for review in negative.tweet)

cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=50, mask=mask_arr).generate(neg)
# cloud = WordCloud(stopwords=stop_words, background_color="white", max_words=200).generate(neg)

cloud.to_file('%s_%s_negative.jpg' % (keyword, now))


# In[ ]:




