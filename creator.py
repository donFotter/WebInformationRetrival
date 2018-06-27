import time
import sys
import traceback
from lib.Dataset import *
from lib.WikiCorpus import *

N_ARTICLES = 100000

def main():
    print("Creating dataset...")
    t0 = time.time()
    try:
        createDataset("dataset2.txt", N_ARTICLES, True)
    except Exception:
        print(traceback.format_exc())
        input("\npress a key to stop the execution...")
        return
    print("Dataset created: "+str(time.time() - t0)+" seconds")

    print("Getting from dataset...")
    t0 = time.time()
    results = getDataFromDataset("dataset.txt")
    print("Data Fetched: "+str(time.time() - t0)+" seconds")

    print("Generating Corpus...")
    t0 = time.time()
    corpus = Corpus(results)
    print("Corpus created: "+str(time.time() - t0)+" seconds")

    print("NUMBERS =============")
    print("Number of tuples: "+str(len(results)))
    print("Number of terms: "+str(len(corpus.getWords())))
    print("Number of articles: "+str(len(corpus.article_dict)))
    print("Number of categories: "+str(len(corpus.category_dict)))
    print("=====================")


main()
