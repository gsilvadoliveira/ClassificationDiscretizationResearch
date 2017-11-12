#Discretization tests
from pprint import *
from math import *
att = {}
data = {}

def main():
    global att
    global data

    #values = setOfValues(att, data)

    #Set of data
    att = {0:('outlook',('sunny', 'overcast', 'rainy')), 1:('temperature', 'numeric'), 2:('humidity','numeric'), 3: ('windy',('true', 'false')), 4: ('play',('yes', 'no'))}
    data = {0:('sunny',85.0, 85.0,'false','no'),1:('sunny',80.0,90.0,'true','no'),2:('overcast',83.0,86.0,'false','yes'),3:('rainy',70.0, 96.0,'false','yes'),4:('rainy',68.0,80.0,'false', 'yes'),5: ('rainy',    65.0, 70.0, 'true',  'no' ),6: ('overcast', 64.0, 65.0, 'true',  'yes'),7: ('sunny',    72.0, 95.0, 'false', 'no'),8:('sunny',69.0,70.0,'false','yes'),9:('rainy',75.0,80.0,'false','yes'),10:('sunny',75.0,70.0,'true','yes'),11:('overcast',72.0,90.0,'true','yes'),12:('overcast',81.0,75.0,'false','yes'),13:('rainy',71.0,91.0,'true','no')}

    #pprint(discEqualWidth(att, data, 3))
    print()
    #pprint(discEqualFrequency(att, data, 3))
    #discEntropy(att, data, 1)
    test(att, data)
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
def discEntropy(att, data, setsQtd):
    count=0
   
    values  = setOfValues(att, data, True)
    #for attNumber in values:
    #    values[attNumber] = sorted(values[attNumber])
        
    entS = {}
    
    #Entropy for the entire set
    numberOfInstances = len(data)


    for attNumber in values:
        instancesPerClass = {}
        classes = []
        
    
        for item in values[attNumber]:
            classes.append(item[1])

        #pprint(classes)
        #print()

        classes = list(set(classes))
        numberOfClasses = len(classes)
        
        for item in values[attNumber]:
            for i, c in enumerate(classes):
                if(item[-1] == c):
                    instancesPerClass[c] = instancesPerClass.get(c,0) + 1

        #for c in classes:
        entS[attNumber] = -1*(sum((instancesPerClass[c]/numberOfInstances)*log((instancesPerClass[c]/numberOfInstances),2) for i in range(numberOfClasses)))

    pprint(entS)
        
    
def test(att, data):
    
    n = len(data)

    c = att[len(att)-1][1]
    m = len(c)

   
    print(n)
    print(m)

    s = m*[0]

    for i in range(m):
        s[i] = sum(1 for r in data.values() if r[-1] == c[i])

    p = m*[0]

    for i in range(m):
        p[i] = s[i]/n

    e = -sum(p[i] * log(p[i],2) for i in range(m))
    
    print(e)
    
    #Dividing sets in half
    #numberOfInstances = len(data)/2
    #for attNumber in values:

    #    for i,item in enumerate(values[attNumber]):

            #if(i < len(values[attNumber])/2):
           #     instancesPerClass = {}
           #     classes = []
                
            
           #     for item in values[attNumber]:
           #         classes.append(item[1])

           #     #pprint(classes)
           #     #print()

            #    classes = list(set(classes))
            #    numberOfClasses = len(classes)
                
            #    for item in values[attNumber]:
            #        for i, c in enumerate(classes):
            #            if(item[-1] == c):
            #                instancesPerClass[c] = instancesPerClass.get(c,0) + 1

             #   for c in classes:
             #       entS1[attNumber] = -1*(sum((instancesPerClass[c]/numberOfInstances)*log((instancesPerClass[c]/numberOfInstances),2) for i in range(numberOfClasses)))

                #pprint(values[attNumber][i])
                #pprint(instancesPerClass)
                #pprint(numberOfInstances)
                #pprint(numberOfClasses)
                

       #     else:
       #         instancesPerClass = {}
       #         classes = []
                
            
       #         for item in values[attNumber]:
       #             classes.append(item[1])

                #pprint(classes)
                #print()

       #         classes = list(set(classes))
       #         numberOfClasses = len(classes)
                
       #         for item in values[attNumber]:
       #             for i, c in enumerate(classes):
       #                 if(item[-1] == c):
       #                     instancesPerClass[c] = instancesPerClass.get(c,0) + 1

       #         for c in classes:
       #             entS2[attNumber] = -1*(sum((instancesPerClass[c]/numberOfInstances)*log((instancesPerClass[c]/numberOfInstances),2) for i in range(numberOfClasses)))

                #pprint(classes)
                #pprint(values[attNumber])
                #pprint(instancesPerClass)
                #pprint(numberOfInstances)
                #pprint(numberOfClasses)
                
    #pprint(entS1)
    #print()
    #pprint(entS2)



    
if __name__ == "__main__":
    main()
    #testDiscretization()
