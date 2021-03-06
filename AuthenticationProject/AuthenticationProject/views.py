import numpy as np
import pandas as pd 
from sklearn.model_selection import train_test_split 

import nltk
from nltk.corpus import stopwords
from nltk.classify import SklearnClassifier

from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
from subprocess import check_output
import nltk
import glob
import os
import spacy
from spacy import displacy
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models.doc2vec import Doc2Vec
import pandas as pd
from gensim.models.doc2vec import Doc2Vec
from unidecode import unidecode
import re
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords,words
from nltk.probability import FreqDist
from collections import defaultdict
from string import punctuation
from heapq import nlargest
import numpy as np
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.parsers import FileUploadParser, MultiPartParser
import os
import pandas as pd
from django.views.static import serve
import json
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def sample_api(request):
    data = {'sample_data': 123}
    return Response(data, status=HTTP_200_OK)
	
@csrf_exempt
@api_view(["POST"])
def SentimentAnalysis(request):
	if request.method == 'POST':
		print(request.data["sentence"])
		analyzer=SentimentIntensityAnalyzer()
		score=analyzer.polarity_scores(request.data["sentence"])
	return JsonResponse(score)

@csrf_exempt
@api_view(["POST"])
def SpacyAnalysisEntity(request):
    if request.method == 'POST':
        nlp=spacy.load('en')
        doc=nlp(request.data["sentence"])
        svg=displacy.render(doc,style='ent')
    return HttpResponse(svg,content_type="image/svg+xml")

@csrf_exempt
@api_view(["POST"])
def SpacyAnalysisDependency(request):
    if request.method == 'POST':
        nlp=spacy.load('en')
        doc=nlp(request.data["sentence"])
        #options1 = {'compact': True, 'color': 'blue'} 
        options={'color':'#ffffff','bg':'#1a1e23','colors':{'VERB':'yellow'}}
        svg=displacy.render(doc,style='dep',minify=True,options=options)
    return HttpResponse(svg,content_type="image/svg+xml")

@csrf_exempt
@api_view(["GET"])
def WordCloudGeneration(request):
    if request.method == 'GET':
        list_of_files = glob.glob('D:\\TextAnalyticsProject\\AuthenticationProject\\sent_results\\*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        df=pd.read_csv(latest_file)
        sentiment_arr=[]
        for i in df['Compound_Score']:
            if(i>=-10 and i<=-2):
                sentiment_arr.append('Negative')
            elif(i>-2 and i<=4):
                sentiment_arr.append('Neutral')
            else:
                sentiment_arr.append('Positive')
        df['sentiment']=sentiment_arr
        data = df[['Description','sentiment']]
        train = df[df.sentiment != "Neutral"]
        train_pos = train[ train['sentiment'] == 'Positive']
        train_pos = train_pos['Description']
        train_neg = train[ train['sentiment'] == 'Negative']
        train_neg = train_neg['Description']
        tweets = []
        stopwords_set = set(stopwords.words("english"))

        for index, row in train.iterrows():
            words_filtered = [e.lower() for e in row.Description.split() if len(e) >= 3]
            words_cleaned = [word for word in words_filtered
            if 'http' not in word
            and not word.startswith('@')
            and not word.startswith('#')
            and word != 'RT']
            words_without_stopwords = [word for word in words_cleaned if not word in stopwords_set]
            tweets.append((words_without_stopwords, row.sentiment))
        w_features = get_word_features(get_words_in_tweets(tweets))
        wordcloud_draw(w_features)
        imageFile=os.path.join(BASE_DIR, 'media', 'Wordcloud.png')
        with open(imageFile, "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")

def get_words_in_tweets(tweets):
    all = []
    for (words, sentiment) in tweets:
        all.extend(words)
    return all

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    features = wordlist.keys()
    return features

def wordcloud_draw(data, color = 'black'):
    words = ' '.join(data)
    cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and not word.startswith('#')
                                and word != 'RT'
                            ])
    wordcloud = WordCloud(stopwords=STOPWORDS,
                      background_color=color,
                      width=2500,
                      height=2000
                     ).generate(cleaned_word)
    plt.figure(1,figsize=(13, 13))
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
    plt.title('Wordcloud of Ingested Data')
    plt.savefig(os.path.join(BASE_DIR, 'media', 'Wordcloud.png'))
    plt.close()
	
@csrf_exempt
@api_view(["POST"])
def RequestSimilarity(request):
    if request.method == 'POST':
        print(request.data["sentence"])
        print(request.data["application"])
        if(request.data["application"]=="HR"):
            df=pd.read_csv('D:\PythonNoteBooks\data\C&B Dump\DUMP17_SENTSCORES_Cleaned.csv',names=['IncidentNumber','Open Date','Resolve Date','Close Date','Region','Location','Category','SubCat','Description'],skiprows=1,engine='python')
            desc_arr=[]
            for i in df["Description"]:
                sent=i.replace("\n","").replace(","," ")
                desc_arr.append(sent)
            df["Description"]=desc_arr
            #data=df['Description']
            #tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(data)]
            model= Doc2Vec.load("C:\\Users\\nair.gangadharan\\d2v.model")
            test_data = word_tokenize(request.data["sentence"])
            v1 = model.infer_vector(test_data)
            similar_doc = model.docvecs.most_similar([v1])
            similar_tags=[]
            for i in similar_doc:
                similar_tags.append(int(i[0]))
            data_dict=dict()
            for i in similar_tags:
                data_dict[df["IncidentNumber"][i]]=df["Description"][i]

            json_stuff = json.dumps(data_dict)

    return HttpResponse(json_stuff, content_type ="application/json")
	
	
	
	



	
class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser, )

    def post(self, request, format=None):
        #print(request.data)
        with open(os.path.join(BASE_DIR, 'media', request.data['file'].name), 'wb') as f:
            for chunk in request.data['file'].chunks():
                f.write(chunk)
        #print(request.data['tablename'])
        print(os.path.join(BASE_DIR, 'media', request.data['file'].name))
        filepath=os.path.join(BASE_DIR, 'media', request.data['file'].name)
        df=pd.read_csv(filepath,names=['IncidentNumer','Open Date','Close Date','Resolve Date','Region','Location','Category','SubCat','Description'],skiprows=1,engine='python',encoding='latin-1')
        #print(df.head())
        #return serve(request, os.path.basename(filepath), os.path.dirname(filepath))
        #json_data=df.to_json(orient="records")
        #data_json = {'sample_data': 123}
        
        analyzer=SentimentIntensityAnalyzer()
        pos_score=[]
        neg_score=[]
        neu_score=[]
        compound_score=[]
        
        for line in df['Description']:
            score=analyzer.polarity_scores(line)
            compound_score.append(round(10*score['compound'],1))
            pos_score.append(round(10*score['pos'],1))
            neu_score.append(round(10*score['neu'],1))
            neg_score.append(round(10*score['neg'],1))
        df['Pos Score']=pos_score
        df['Neg Score']=neg_score
        df['Neu Score']=neu_score
        df['Compound Score']=compound_score
        sentscorefile=os.path.join(BASE_DIR, 'sent_results', request.data['file'].name)
        df.to_csv(sentscorefile,encoding='utf-8',index=False)
        sent_data = []
        with open(sentscorefile) as f:
            for row in csv.DictReader(f):
                sent_data.append(row)

        vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(2,4), stop_words='english')
        X_vect = vectorizer.fit_transform(df['Description'])

        true_k =5
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=10000, n_init=1)
        model.fit(X_vect)
        cluster_terms=[]
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        for i in range(true_k):
            for ind in order_centroids[i, :100]:
                cluster_terms.append(terms[ind])
        woduplicates = list(set(cluster_terms))
        #print(cluster_terms)
        final = [re.sub(r"[^a-zA-Z0-9]+", ' ', k) for k in woduplicates]
        d=dict()
        for i in final:
            for j in range(0,len(df['Description'])):
                sent=df['Description'][j]
                m = re.findall(r'^(?=.*'+i+').+$', sent.lower(), re.MULTILINE)
                if len(m)!=0:
                    if (i in d):
                        d[i].append(m)
                    else:
                        d[i]=m
        for key, value in d.items():
            org_value = [x for x in value if x != []]
            d[key]=org_value
        value_list=[]
        for key, value in d.items():
            value_list.append(len(value))
        value_dict=dict()
        for key, value in d.items():
            value_dict[key]=len(value)
        desc_sorted=sorted(value_dict.items(), key=lambda x: x[1], reverse=True)
        print(desc_sorted)
        bigram_list=[]
        trigram_list=[]
        fourgram_list=[]
        for i in desc_sorted:
            if len(i[0].split(' ')) == 2:
                bigram_list.append(i)
            elif len(i[0].split(' ')) == 3:
                trigram_list.append(i)
            else:
                fourgram_list.append(i)
        print(bigram_list)
        bi_gram_dict=dict(bigram_list)
        tri_gram_dict=dict(trigram_list)
        four_dict=dict(fourgram_list)

        json_stuff = json.dumps({"list_of_json" : [sent_data,bi_gram_dict,tri_gram_dict,four_dict]})
        
        return HttpResponse(json_stuff, content_type ="application/json")