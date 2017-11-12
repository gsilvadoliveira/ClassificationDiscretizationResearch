#Discretization tests
from pprint import *
from math import *
att = {}
data = {}
entropyS = 0.0
lengthS = 0
#intervalList = []
def main():
    global attr_dict
    global data
    global entropyS
    global lengthS
    #values = setOfValues(att, data)

    #Set of data
    attr_dict = {0:('outlook',('sunny', 'overcast', 'rainy')), 1:('temperature', 'numeric'), 2:('humidity','numeric'), 3: ('windy',('true', 'false')), 4: ('play',('yes', 'no'))}
    data = {0:('sunny',85.0, 85.0,'false','no'),1:('sunny',80.0,90.0,'true','no'),2:('overcast',83.0,86.0,'false','yes'),3:('rainy',70.0, 96.0,'false','yes'),4:('rainy',68.0,80.0,'false', 'yes'),5: ('rainy',    65.0, 70.0, 'true',  'no' ),6: ('overcast', 64.0, 65.0, 'true',  'yes'),7: ('sunny',    72.0, 95.0, 'false', 'no'),8:('sunny',69.0,70.0,'false','yes'),9:('rainy',75.0,80.0,'false','yes'),10:('sunny',75.0,70.0,'true','yes'),11:('overcast',72.0,90.0,'true','yes'),12:('overcast',81.0,75.0,'false','yes')}

    pprint(discEqualWidth(data, 3))
    print()
    pprint(discEqualFrequency(data, 3))
    #discEntropy(att, data)
    #sets = {}
    #sets['s'] = data
    entropyS = calcEntropy(data)
    lengthS = len(data)
    print(minimumEntropy(data,1,list()))
    #recursiveEntropy(list(), data, 1)
    return None
    

#------------------------------------------------------------------------------------------------------------#
#
#
#
#   Discretization functions
#
#
#
#------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------#
# Create a dictionary with the continuous values from the data
# The index of the dictionary is the same index of the continuous attribute
#------------------------------------------------------------------------------------------------------------#
def setOfValues(data, flagEntropy):
    global attr_dict
    values = {}
    for j in attr_dict:
        temp=[]
        for i in data:
            if(attr_dict[j][1] == 'numeric' or attr_dict[j][1] == 'NUMERIC'):
                if(flagEntropy):
                    temp.append((data[i][j], data[i][-1]))
                else:
                    temp.append(data[i][j])
        if(len(temp)>0):
            values[j] = temp
    #print(values)
    return values



#------------------------------------------------------------------------------------------------------------#
# Separate continuous values into intervals (bins) with discretization by equal width
#------------------------------------------------------------------------------------------------------------#
def discEqualWidth(data, numberOfBins):
    global attr_dict

    #Gets all the values of the continuous attributes
    values  = setOfValues(data, False)

    limits = {}
    intervals = {}

    #creating intervals dictionary
    for attNumber in values:
        intervals[attNumber] = {}
        limits[attNumber] = []
        for i in range(numberOfBins):
            intervals[attNumber][i] = []

    #For each continuous attribute
    for attNumber in values:
        minValue = min(values[attNumber])
        maxValue = max(values[attNumber])
        width = (maxValue - minValue)/numberOfBins

        #Divide attributes in intervals
        for value in values[attNumber]:
            for n in range(numberOfBins):
                if(n == numberOfBins-1):
                    if(value >= minValue + width*n and value <= minValue + width*(n+1)):
                        intervals[attNumber][n].append(value)
                else:
                    if(value >= minValue + width*n and value < minValue + width*(n+1)):
                        intervals[attNumber][n].append(value)

    #print(values)

    #Getting limits from intervals
    for i in intervals:
        for j in intervals[i]:
            if j == 0:
                limits[i].append(max(intervals[i][j]))
            elif j == len(intervals[i])-1:
                limits[i].append(min(intervals[i][j]))
            else:
                limits[i].append((min(intervals[i][j]),max(intervals[i][j])))
                
    return limits       
                
    

#------------------------------------------------------------------------------------------------------------#
# Separate continuous values into intervals (bins) with discretization by equal frequency
#------------------------------------------------------------------------------------------------------------#
#Same of the book
def discEqualFrequency(data, numberOfBins):
    global attr_dict
    values  = setOfValues(data, False)
    intervals = {}
    limits = {}

    #creating intervals dictionary
    for attNumber in values:
        values[attNumber] = set(values[attNumber])
        values[attNumber] = sorted(values[attNumber])
        
        intervals[attNumber] = {}
        limits[attNumber] = []
        for i in range(numberOfBins):
            intervals[attNumber][i] = []

    #For each continuous attribute
    for attNumber in values:
        frequency = len(values[attNumber])/numberOfBins
        #Round frequency up
        frequency = int(ceil(frequency))
        
        #Divinding data in intervals
        for i in range(numberOfBins):
            if(i != numberOfBins-1):
                for j in range(frequency*i, (i+1)*frequency):
                    intervals[attNumber][i].append(values[attNumber][j])
            else:
                for j in range(frequency*i, len(values[attNumber])):
                    intervals[attNumber][i].append(values[attNumber][j])
                    
    #Getting limits of each interval
    for i in intervals:
        for j in intervals[i]:
            if j == 0:
                limits[i].append(max(intervals[i][j]))
            elif j == len(intervals[i])-1:
                limits[i].append(min(intervals[i][j]))
            else:
                limits[i].append((min(intervals[i][j]),max(intervals[i][j])))

    return limits

#------------------------------------------------------------------------------------------------------------#
# Calculate entropy on a set
#------------------------------------------------------------------------------------------------------------#    
def calcEntropy(data):
    global attr_dict
    entropy = 0.0
    lenData = len(data)
    classes = attr_dict[len(attr_dict)-1][1]
    numberOfClasses = len(classes)

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

#------------------------------------------------------------------------------------------------------------#
# Check minimum entropy recursively
#------------------------------------------------------------------------------------------------------------#
def minimumEntropy(data, entropy, intervalList):
    global attr_dict
    #global data
    #global intervalList
    
    if len(data) < 4 or entropy == 0:
        #print(intervalList, entropy)
        print(intervalList, entropy)
        return intervalList
        
    dataLength = len(data)
    int1 = int(dataLength/4)
    int2 = int(dataLength/2)
    int3 = 3 * int(dataLength/4)

    entropy1 = finalEntropyTwoSets(int1, data)
    entropy2 = finalEntropyTwoSets(int2, data)
    entropy3 = finalEntropyTwoSets(int3, data)

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
    
    
#------------------------------------------------------------------------------------------------------------#
# Calculate final entropy between two sets
#------------------------------------------------------------------------------------------------------------#
def finalEntropyTwoSets(interval, data):
    global attr_dict
    global entropyS
    global lengthS

    dict1 = {}
    dict2 = {}

    for i in range(interval):
        dict1[i] = data[i]

    for i in range(interval, len(data)):
        dict2[i] = data[i]

    entropyS1 = calcEntropy(dict1)
    entropyS2 = calcEntropy(dict2)

    finalEntropy = ((len(dict1)/lengthS) * entropyS1) + ((len(dict2)/lengthS) * entropyS2)
    
    return finalEntropy

    
if __name__ == "__main__":
    main()
    #testDiscretization()
