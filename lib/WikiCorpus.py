from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

# Initialize nltk
stop_words = set(stopwords.words('english'))
stemmer = SnowballStemmer("english")
# ==============================

class Corpus:
    category_dict = {} # Contains all categories. Values are a list of useful properties (not yet implemented)
    article_dict = {} # Contains the link between articles and categories
    title_dict = {} # Contains the link between titles and articles
    word_dict = {} # Contains the link between words and titles
    
    def __init__(self, results):
        size = len(results)
        analyzed=0
        for result in results:
            if (analyzed%1000 == 0):
                print("Analyzed: "+str(analyzed)+"/"+str(size))

            stemmed_titles = [__createStemmedTitle__(result["article"])]
            for redirection in result["redirections"]:
                stemmed_titles.append(__createStemmedTitle__(redirection))
            
            #link articles with category
            if (result["article"] not in self.article_dict):
                self.article_dict[result["article"]] = result["categories"]
                for category in result["categories"]: # add categories in dict and increase the number of articles for each category
                    if (category not in self.category_dict):
                        self.category_dict[category] = {"number_of_articles": 0, "vocabulary": set()}
                    for title in stemmed_titles:
                        for word in title.split():
                            self.category_dict[category]["vocabulary"].add(word)
                    self.category_dict[category]["number_of_articles"] += 1
                
            # link (stemmed) titles with article
            for title in stemmed_titles:
                if (title not in self.title_dict):
                    self.title_dict[title] = [result["article"]]
                else:
                    if (result["article"] not in self.title_dict[title]):
                        self.title_dict[title].append(result["article"])

            # link words with stemmed titles
            for title in stemmed_titles:
                for word in title.split():
                    if (word not in self.word_dict):
                        self.word_dict[word] = [title]
                    else:
                        if (title not in self.word_dict[word]):
                            self.word_dict[word].append(title)
            analyzed+=1
        # discard categories from category_dict
        for category in self.category_dict.copy():
            if (self.category_dict[category]["number_of_articles"] > 187):
                self.category_dict.pop(category)

        # discard categories not in category_dict
        for article in self.article_dict:
            for category in self.article_dict[article].copy():
                if (category not in self.category_dict):
                    self.article_dict[article].pop(self.article_dict[article].index(category))

    def __str__(self):
        ret = "--------------\n"
        ret += "Dictionary of Categories: (links categories with their properties)\n"
        for key in self.category_dict:
            ret += (key+": "+str(self.category_dict[key]))+"\n"
        ret += "--------------\n"
        ret += "Dictionary of article names: (links articles with their categories)\n"
        for key in self.article_dict:
            ret += (key+":")+"\n"
            for elem in self.article_dict[key]:
                ret += ("    "+str(elem))+"\n"
        ret += "--------------\n"
        ret += "Dictionary of stemmed titles: (links stemmed titles with their articles)\n"
        for key in self.title_dict:
            ret += (key+":")+"\n"
            for elem in self.title_dict[key]:
                ret += ("    "+elem)+"\n"
        ret += "--------------\n"
        ret += "Inverted index: (links words with stemmed titles)\n"
        for key in self.word_dict:
            ret += (key+":")+"\n"
            for elem in self.word_dict[key]:
                ret += ("    "+elem)+"\n"
        return ret

    # ============ GETTERS:
    def getArticleText(self, title):
        return __getAbstract__(title)

    def getPropertiesFromCategory(self, categoryName):
        return self.category_dict[categoryName]

    def getCategoriesFromArticle(self, title):
        return self.article_dict[title]

    def getArticlesFromTitle(self, title):
        return self.title_dict[title]
    
    def getTitlesFromWord(self, word):
        return self.word_dict[word]

    def getWords(self):
        return self.word_dict.keys()
        
def __createStemmedTitle__(word):
    word_tokens = word_tokenize(word.replace(",", "").replace(".", "").replace("(", "").replace(")", ""))
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    stemmed_word = ""
    for w in filtered_sentence:
        stemmed_word += stemmer.stem(w)+" "
    return stemmed_word.strip()

