import tkinter
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from string import punctuation
import nltk
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

main = Tk()
main.title("Twitter Trend Mining")
main.geometry("1300x1200")

global filename
tweets = []
trend_hashtag_weight = {}
trend_words_weight = {}
global dataset
global tfidf_vectorizer
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
global count1, count2
sid = SentimentIntensityAnalyzer()
global education,sports,health,movie,politics

def cleanPost(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

def convertToWords(array):
    words = []
    for i in range(len(array)):
        data = str(array[i][0])
        arr = data.split(" ")
        for j in range(len(arr)):
            words.append(arr[j])
    return set(words)        

def uploadDataset():
    global education,sports,health,movie,politics
    global filename
    global dataset
    text.delete('1.0', END)
    filename = filedialog.askopenfilename(initialdir="Dataset")
    tf1.insert(END,str(filename))
    dataset = pd.read_csv(filename)
    dataset = dataset['tweet']
    education=pd.read_csv('topics/education.csv')
    sports = pd.read_csv('topics/sports.csv')
    movie = pd.read_csv('topics/movies.csv')
    health = pd.read_csv('topics/health.csv')
    politics = pd.read_csv('topics/politics.csv')
    education = education.values[:,0:1]
    sports = sports.values[:,0:1]
    health = health.values[:,0:1]
    movie = movie.values[:,0:1]
    politics = politics.values[:,0:1]
    politics = convertToWords(politics.tolist())
    sports = convertToWords(sports.tolist())
    education = convertToWords(education.tolist())
    health = convertToWords(health.tolist())
    movie = convertToWords(movie.tolist())
    print(len(politics))
    text.insert(END,str(dataset)+"\n\n")
    text.insert(END,"dataset loaded")
    
def preprocessDataset():
    global dataset
    global count1, count2
    count1  = 0
    count2  = 0
    text.delete('1.0', END)
    trend_hashtag_weight.clear()
    trend_words_weight.clear()
    for i in range(len(dataset)):
        tweets = dataset[i]
        cleanTweet = cleanPost(tweets.lower())
        arr = cleanTweet.split(" ")
        count1 = count1 + len(arr)
        for j in range(len(arr)):
            words = arr[j].strip()
            if words in trend_words_weight:
                count = trend_words_weight.get(words) + 1
                trend_words_weight[words] = count
            else:
                trend_words_weight[words] = 1
            
        arr = tweets.split(" ")
        count2 = count2 + len(arr)
        for j in range(len(arr)):
            words = arr[j].strip()
            words = words.lower()
            if '#' in words:
                if words in trend_hashtag_weight:
                    count = trend_hashtag_weight.get(words) + 1
                    trend_hashtag_weight[words] = count
                else:
                    trend_hashtag_weight[words] = 1
    text.insert(END,"Total tweets found in dataset : "+str(len(dataset))+"\n")                
    text.insert(END,"Total unique words found in tweets dataset : "+str(len(trend_words_weight))+"\n")
    text.insert(END,"Total unique Hashtag found in dataset : "+str(len(trend_hashtag_weight))+"\n\n")
    
def featuresExtraction():
    global dataset
    global count1, count2
    global trend_hashtag_weight
    global trend_words_weight
    text.delete('1.0', END)

    trend_hashtag_weight = sorted(trend_hashtag_weight.items(), key=lambda x: x[1], reverse=True)
    trend_hashtag_weight = {k: v for k, v in trend_hashtag_weight}

    trend_words_weight = sorted(trend_words_weight.items(), key=lambda x: x[1], reverse=True)
    trend_words_weight = {k: v for k, v in trend_words_weight}
    text.insert(END,"Features Extraction Process Completed\n")

            

def trendDetection():
    global count1, count2
    global trend_hashtag_weight
    global trend_words_weight

    text.delete('1.0', END)
    text.insert(END,"Top 100 Trending Hashtags\n\n")
    i = 0
    for k,v in trend_hashtag_weight.items():
        text.insert(END,k+ " : "+str(v/len(dataset))+"\n")
        i = i + 1
        if i > 100:
            break

    text.insert(END,"\nTop 100 High Weight/Frequency occurences\n\n")
    i = 0
    for k,v in trend_words_weight.items():
        text.insert(END,k+ " : "+str(v/len(dataset))+"\n")
        i = i + 1
        if i > 100:
            break        
    

def graph():
    data = []
    hashtag = []
    for k,v in trend_hashtag_weight.items():
        hashtag.append(k)
        data.append(v)
        if len(data) > 10:
            break
    plt.pie(data,labels=hashtag,autopct='%1.1f%%')
    plt.title('Top 10 Trending Hashtags')
    plt.axis('equal')
    plt.show()
                    

def moodPrediction():
    text.delete('1.0', END)
    for i in range(len(dataset)):
        sentiment_dict = sid.polarity_scores(dataset[i].strip().lower())
        compound = sentiment_dict['compound']
        result = ''
        if compound >= 0.05 : 
            result = 'Positive' 
  
        elif compound <= - 0.05 : 
            result = 'Negative' 
  
        else : 
            result = 'Neutral'
        text.insert(END,"Tweets Text : "+dataset[i]+"\n")
        text.insert(END,"Mood Detection : "+result+"\n\n")
         

font = ('times', 15, 'bold')
title = Label(main, text='Twitter Trend Mining')
title.config(bg='mint cream', fg='royal blue')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 14, 'bold')
ff = ('times', 12, 'bold')

l1 = Label(main, text='Dataset Location')
l1.config(font=font1)
l1.place(x=50,y=100)

tf1 = Entry(main,width=40)
tf1.config(font=font1)
tf1.place(x=230,y=100)

uploadButton = Button(main, text="Upload Tweets Dataset", command=uploadDataset)
uploadButton.place(x=50,y=150)
uploadButton.config(font=ff)

preprocessButton = Button(main, text="Preprocess Dataset", command=preprocessDataset)
preprocessButton.place(x=350,y=150)
preprocessButton.config(font=ff)

feButton = Button(main, text="Features Extraction", command=featuresExtraction)
feButton.place(x=50,y=200)
feButton.config(font=ff)

trendButton = Button(main, text="Trend Detection", command=trendDetection)
trendButton.place(x=350,y=200)
trendButton.config(font=ff)

moodButton = Button(main, text="Mood Prediction", command=moodPrediction)
moodButton.place(x=50,y=250)
moodButton.config(font=ff)

graphButton = Button(main, text="Top Ten Trending Hashtags Graph", command=graph)
graphButton.place(x=350,y=250)
graphButton.config(font=ff)


font1 = ('times', 13, 'bold')
text=Text(main,height=18,width=125)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=300)
text.config(font=font1)

main.config(bg='salmon')
main.mainloop()
