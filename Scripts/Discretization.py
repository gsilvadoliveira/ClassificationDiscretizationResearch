#Discretization tests
from pprint import *
from math import *
att = {}
data = {}
entropyS = 0.0
lengthS = 0
#intervalList = []
def main():
    global att
    global data
    global entropyS
    global lengthS
    #values = setOfValues(att, data)

    #Set of data
    att = {0:('outlook',('sunny', 'overcast', 'rainy')), 1:('temperature', 'numeric'), 2:('humidity','numeric'), 3: ('windy',('true', 'false')), 4: ('play',('yes', 'no'))}
    data = {0:('sunny',85.0, 85.0,'false','no'),1:('sunny',80.0,90.0,'true','no'),2:('overcast',83.0,86.0,'false','yes'),3:('rainy',70.0, 96.0,'false','yes'),4:('rainy',68.0,80.0,'false', 'yes'),5: ('rainy',    65.0, 70.0, 'true',  'no' ),6: ('overcast', 64.0, 65.0, 'true',  'yes'),7: ('sunny',    72.0, 95.0, 'false', 'no'),8:('sunny',69.0,70.0,'false','yes'),9:('rainy',75.0,80.0,'false','yes'),10:('sunny',75.0,70.0,'true','yes'),11:('overcast',72.0,90.0,'true','yes'),12:('overcast',81.0,75.0,'false','yes')}

    pprint(discEqualWidth(att, data, 3))
    print()
    pprint(discEqualFrequency(att, data, 3))
    #discEntropy(att, data)
    #sets = {}
    #sets['s'] = data
    entropyS = discEntropy(att, data)
    lengthS = len(data)
    #minimumEntropy(data,1,list())
    #recursiveEntropy(list(), data, 1)
    return None
    
    
def setOfValues(att, data, flagEntropy):
    values = {}
    for j in att:
        temp=[]
        for i in data:
            if(att[j][1] == 'numeric' or att[j][1] == 'NUMERIC'):
                if(flagEntropy):
                    temp.append((data[i][j], data[i][-1]))
                else:
                    temp.append(data[i][j])
        if(len(temp)>0):
            values[j] = temp
    return values



#By equal width
def discEqualWidth(att, data, numberOfBins):

    values  = setOfValues(att, data, False)
    #pprint(values)
    intervals = {}

    for attNumber in values:
        intervals[attNumber] = {}
        for i in range(numberOfBins):
            intervals[attNumber][i] = []

    for attNumber in values:
        minValue = min(values[attNumber])
        maxValue = max(values[attNumber])
        width = (maxValue - minValue)/numberOfBins
        width = int(width)
        
        for attValue in values[attNumber]:
            for factor in range(1,numberOfBins+1):
                if(attValue >= (minValue + width*(factor-1))):
                    if(factor == numberOfBins):
                        if(attValue <= (minValue + width*factor)):
                            intervals[attNumber][factor-1].append(attValue)
                    else:
                        if(attValue < (minValue + width*factor)):
                            intervals[attNumber][factor-1].append(attValue)
                    
    #pprint(intervals)
    return intervals       
                
    

#By equal frequency
#Same of the book
def discEqualFrequency(att, data, numberOfBins):
    values  = setOfValues(att, data, False)
    intervals = {}

    for attNumber in values:
        values[attNumber] = set(values[attNumber])
        values[attNumber] = sorted(values[attNumber])
        
        intervals[attNumber] = {}
        for i in range(numberOfBins):
            intervals[attNumber][i] = []

    for attNumber in values:
        frequency = len(values[attNumber])/numberOfBins
        frequency = int(frequency)

        for i in range(1,numberOfBins+1):
            for j in range(frequency*(i-1),i*frequency):
                intervals[attNumber][i-1].append(values[attNumber][j])

    #pprint(intervals)

    return intervals

#Entropy     
def discEntropy(att, data):
    entropy = 0.0
    lenData = len(data)
    classes = att[len(att)-1][1]
    numberOfClasses = len(classes)

    #print(classes)
    #print(lenData)
    #print(numberOfClasses)

    occurPerClass = numberOfClasses*[0]

    for i in range(numberOfClasses):
        occurPerClass[i] = sum(1 for r in data.values() if r[-1] == classes[i])

    #print(occurPerClass)
    
    p = numberOfClasses*[0]

    for i in range(numberOfClasses):
        p[i] = occurPerClass[i]/lenData

    #pprint(p)
    #entropy = -sum(p[i] * log(p[i],2) for i in range(numberOfClasses))

    #Change for when p[i] == 0
    for i in range(numberOfClasses):
        if(p[i] != 0):
            entropy += (p[i] * log(p[i],2))
        else:
            entropy += 0

    entropy = entropy *(-1)
            
    #print(e)

    return entropy
    
def minimumEntropy(data, entropy, intervalList):
    global att
    #global data
    #global intervalList
    
    if len(data) < 4 or entropy == 0:
        print(intervalList, entropy)
        return intervalList
        
    dataLength = len(data)
    int1 = int(dataLength/4)
    int2 = int(dataLength/2)
    int3 = 3 * int(dataLength/4)

    print(int1)
    print(int2)
    print(int3)

    entropy1 = calcEntropy(int1, data)
    entropy2 = calcEntropy(int2, data)
    entropy3 = calcEntropy(int3, data)

    minEntropy = min(entropy1, entropy2, entropy3)

    if minEntropy == entropy1:
        interval = int1
    elif minEntropy == entropy2:
        interval = int2
    elif minEntropy == entropy3:
        interval = int3

    intervalList.append(interval)
    dict1 = {}
    dict2 = {}

    for i in range(interval):
        dict1[i] = data[i]
    minimumEntropy(dict1, minEntropy, intervalList)

    for i in range(interval, len(data)):
        dict2[i - interval] = data[i]
    minimumEntropy(dict2, minEntropy, intervalList)
    
    

def calcEntropy(interval, data):
    global att
    global entropyS
    global lengthS

    dict1 = {}
    dict2 = {}

#    print()
#    pprint(data)
    for i in range(interval):
        dict1[i] = data[i]

    for i in range(interval, len(data)):
        dict2[i] = data[i]

    #pprint(dict1)
    #pprint(dict2)

    
    entropyS1 = discEntropy(att,dict1)
    entropyS2 = discEntropy(att,dict2)

    finalEntropy = ((len(dict1)/lengthS) * entropyS1) + ((len(dict2)/lengthS) * entropyS2)
    
    return finalEntropy

#def recursiveEntropy(interval, sets, entropy):
#    global att
#    global entropyS
#    global lengthS
#    dict1 = {}
#    dict2 = {}
#    
#    if len(sets) < 4 or entropy == 0:
#        print(interval)
#        return interval

#    pprint(sets)
#    result = minimumEntropy(sets)
    
#    interval.append(result[0])
#    entropy = result[1]

#    lastInterval = interval[len(interval)-1]
#    
#    for i in range(lastInterval):
#        dict1[i] = sets[i]
    
    
#    recursiveEntropy(interval, dict1, entropy)
        
#    for i in range(lastInterval, len(sets)):
#        dict2[i] = sets[i]
        
#    recursiveEntropy(interval, dict2, entropy)

    
if __name__ == "__main__":
    main()
    #testDiscretization()
