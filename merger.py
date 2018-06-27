from lib.Dataset import *

results1 = getDataFromDataset("dataset.txt")
results2 = getDataFromDataset("dataset2.txt")
file = open("dataset2.txt", "a", encoding="utf-8")
size = len(results2)
copied=0
print("start")
for result in results1:
    if (result not in results2):
        file.write(str(result)+"\n")
        copied+=1
        print("copied: "+str(copied))
        if (copied+size == 100000):
            break
file.close()


    
