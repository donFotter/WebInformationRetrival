from SPARQLWrapper import SPARQLWrapper, JSON # requires installation with pip
import requests # requires intallation with pip
from urllib.request import unquote
import ast

def createDataset(filename, size, append=False):
    article_names = set()
    if (append):
        partial = getDataFromDataset(filename)
        for result in partial:
            article_names = result["article"]
        print("Already created: "+str(len(partial)))
        size = size - len(partial)
        file = open(filename, "a", encoding="utf-8")
    else:
        file = open(filename, "w", encoding="utf-8")
        cmd = input("ATTENTION: previously created dataset will be deleted. Are you sure you want to continue?")
        if (cmd.strip().lower() != "yes"):
            return None
    total = size
    invalid_char = ["\\", "/", ":", "*", "?", '"', ">", "<"]
    print("created: "+str(total-size)+"/"+str(total))
    while(size > 0):
        res = requests.get('https://en.wikipedia.org/wiki/Special:Random')
        name = unquote(res.url.split('/')[-1])
        invalid = False
        for char in invalid_char:
            if char in name:
                invalid = True
        if (invalid):
            continue
        if (name in article_names):
            continue
        try:
            result = __getRandomData__(name)
        except:
            continue
        if (result):
            file.write(str(result)+"\n")
            size = size-1
        print("created: "+str(total-size)+"/"+str(total))
    file.close()

def getDataFromDataset(filename):
    file = open(filename, "r", encoding="utf-8")
    lines = file.readlines()
    ret = []
    for line in lines:
        ret.append(ast.literal_eval(line.strip()))
    file.close()
    return ret

def __getRandomData__(name): # PRIVATE
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>
    PREFIX dbres: <http://dbpedia.org/resource/>
    PREFIX dbterms: <http://purl.org/dc/terms/>
    
    SELECT distinct ?categoryName, ?redirectName WHERE {{{{
     <http://dbpedia.org/resource/{}> dbterms:subject ?category.
     ?category rdfs:label ?categoryName
    }}
    UNION
    {{
     ?redirect dbpedia-owl:wikiPageRedirects <http://dbpedia.org/resource/{}>.
     ?redirect rdfs:label ?redirectName.
    }}}}""".format(name, name))
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    bindings = results["results"]["bindings"]
    if bindings:
        ret = {"article": name.replace("_", " "), "categories": [], "redirections": []}
        for elem in bindings:
            keys = elem.keys()
            if ("categoryName" in keys):
                ret["categories"].append(elem["categoryName"]["value"])
            elif ("redirectName" in keys):
                ret["redirections"].append(elem["redirectName"]["value"])
        return ret
    else:
        return None

def printData(data):
    print("Title:")
    print("    "+data["article"])
    print("Categories:")
    if (len(data["categories"]) == 0):
        print("    None")
    else:
        for elem in data["categories"]:
            print("    "+elem)
    print("Redirections:")
    if (len(data["redirections"]) == 0):
        print("    None")
    else:
        for elem in data["redirections"]:
            print("    "+elem)
    
