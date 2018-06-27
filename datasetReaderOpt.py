import os, re
import numpy as np
import operator
import time
from itertools import islice
from lib.Dataset import getDataFromDataset
from lib.WikiCorpus import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem.snowball import SnowballStemmer
from sklearn.naive_bayes import MultinomialNB

def WeightTitle(title,document,wikiCorpus):
    words_list = title.split()
    stuff = []
    count = len(words_list)
    for word in words_list:
        if (word not in document["WeightedWords"]):
            count -= 1
            continue
        stuff.append(document["WeightedWords"][word] / len(wikiCorpus.getTitlesFromWord(word)))
    return (sum(stuff) / len(wikiCorpus.getArticlesFromTitle(title))) * (count / len(words_list))        


#folder = "./corpus/test"
start_time = time.clock()
print("working")
folder = "./corpus/test"
cv = CountVectorizer(stop_words='english')
stemmer = SnowballStemmer("english")
corpus = {}
count = 0

# Corpus
print("Fetching data...")
results = getDataFromDataset("dataset.txt")
print("Creating corpus...")
wikiCorpus = Corpus(results)
print("Corpus created")
title_set = set()

for file in os.listdir(folder):
    count += 1
    print("element : "+str(count))
    #print(file)
    fileId = file
    filepath = os.path.join(folder, file)
    f = open(filepath, 'r')
    data = f.read()
    formattedData = re.sub(r'\\p{L}', ' ', data)
    vector = formattedData.split(" ")
    #Do the stemming on the incoming document
    for z in range(len(vector)):
        vector[z] = stemmer.stem(vector[z])
    #tf only
    transformed_data = cv.fit_transform(vector)
    #Dict of the current document
    tempDict = dict(zip(cv.get_feature_names(), np.ravel(transformed_data.sum(axis=0))))
    #remove words not in wikiCorpus
    for key in tempDict.copy():
        if (key not in wikiCorpus.word_dict):
            tempDict.pop(key)
        else:
            title_set.update(wikiCorpus.getTitlesFromWord(key))
   
    #print(tempDict)
    corpus[fileId] = {}
    corpus[fileId]["WeightedWords"] = tempDict
    corpus[fileId]["Titles"] = []
    corpus[fileId]["Articles"] = {}
    corpus[fileId]["Categories"] = {}
    corpus[fileId]["Words_decay"] = {}
    for word in vector:
        if (word not in corpus[fileId]["Words_decay"]):
            corpus[fileId]["Words_decay"][word] = 1
    
    f.close()
    
# getting titles
print("Begin point 3 & 4 & 5...")
tot = len(title_set)
count = 1
for title in title_set:
    if (count%1000 == 0):
        print(str(count)+"/"+str(tot))
    words_list = title.split(" ")
    for document in corpus:
        count_missing = 0
        supporting_words = {} # for optimization
        for word in words_list:
            if (word not in corpus[document]["WeightedWords"]):
                count_missing += 1
        if (count_missing <= 1):
            weight = WeightTitle(title, corpus[document], wikiCorpus)
            if (weight > 0.2):
                corpus[document]["Titles"].append({"Title": title, "Weight": weight})
                articles = wikiCorpus.getArticlesFromTitle(title)
                for article in articles:
                    if (article not in corpus[document]["Articles"]):
                        corpus[document]["Articles"][article] = 0
                    if (weight > corpus[document]["Articles"][article]):
                        corpus[document]["Articles"][article] = weight
                    categories = wikiCorpus.getCategoriesFromArticle(article)  
                    for category in categories:
                        if (category not in corpus[document]["Categories"]):
                            corpus[document]["Categories"][category] = 0
        for article in corpus[document]["Articles"]:
            categories = wikiCorpus.getCategoriesFromArticle(article)
            for category in categories:
                corpus[document]["Categories"][category] += corpus[document]["Articles"][article]

        #optimization 1
        real_supporting_words = {}
        for category in corpus[document]["Categories"].copy():
            if (corpus[document]["Categories"][category] == 0):
                corpus[document]["Categories"].pop(category)
                continue
            if (category not in real_supporting_words):
                real_supporting_words[category] = set()
            vocabulary = wikiCorpus.category_dict[category]["vocabulary"]
            for word in vocabulary:
                if (word not in supporting_words):
                    supporting_words[word] = set()
                supporting_words[word].add(category)
        for word in supporting_words:
            if (len(supporting_words[word]) == 1):
                real_supporting_words[supporting_words[word].pop()].add(word)
        for category in corpus[document]["Categories"]:
            corpus[document]["Categories"][category] *= (len(real_supporting_words[category])/len(wikiCorpus.category_dict[category]["vocabulary"]))
        
    count += 1

print("DONE")
f = open("outputOpt.txt", "w", encoding="utf-8")
for document in corpus:
    sorted_categories = sorted(corpus[document]["Categories"].items(), key=operator.itemgetter(1))
    sorted_categories.reverse()    
    f.write(document+":\n")
    for elem in sorted_categories:
        if (elem[1] > 0):
            f.write(str(elem)+"\n")
    f.write("\n")
f.close()

#f2 = open("categories_file.txt", "w", encoding="utf-8")
#for category in wikiCorpus.category_dict:
#    if(len(wikiCorpus.category_dict[category]["supporting_words"]) > 0):
#        f2.write(category+":\n"+str(wikiCorpus.category_dict[category]["supporting_words"])+"\n")
#f2.close()
    
            
print(time.clock() - start_time, " seconds")
