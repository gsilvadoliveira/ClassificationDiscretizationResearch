#################################################################################################################
#   Author:  Gabriela Silva de Oliveira
#    Email:  gsilvadoliveira@gmail.com
#
#   Program:    ArffReader.py
#   Date:       20/02/2017
#   Purpose:    Read ARFF files and store the data on internal variables
#           
#################################################################################################################

from pprint import *
from pyparsing import *
from math import *
from operator import *
from functools import reduce
    
from copy import *
from random import *
#Global variables
attr_dict = {}
dap_dict = {}
cap_dict = {}
data = []
counterClassOptions = {}
filename = ''
entropyS = 0.0
lengthS = 0


#--------------------------------------------------------------------------------------------------------------#
# main():                                                                                                      #
# Gets the file from the user,                                                                                 #
# calls the function that reads the files                                                                      #
# and prints the returns on screen                                                                             #
#--------------------------------------------------------------------------------------------------------------#
def main():
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    global data      #Matrix of data from the ARFF file
    global filename  #File chosen by user
    global lengthS
    global entropyS
    filename = input('Enter file path: ')
    readArff(filename)
    probability(data)

    #pprint(data)
    #input()
    
    print("\nAttribute(s):")
    pprint(attr_dict)

    print("\nDiscrete probability:")
    pprint(dap_dict)

    print("\nContinuous probablity:")
    pprint(cap_dict)  

    #Discretization

    print()

    print('Equal width intervals: ')
    pprint(discEqualWidth(data, 3))
    print()

    print('Equal frequency intervals: ')
    pprint(discEqualFrequency(data, 3))
    print()

    #input()
    
    print('Minimum entropy intervals: ')
    entropyS = calcEntropy(data)
    lengthS = len(data)
    #pprint(lengthS)
    #input()
    print(minimumEntropy(data,1,list()))

    print()
    print('End')
    input('Hit ENTER to input an instance. ')
    instance = input("Enter an instance to be tested: ")
    classification(instance.lower().replace(' ','').split(','))    

    
#--------------------------------------------------------------------------------------------------------------#
# readArff():                                                                                                  #
# Read the given ARFF file line by line.                                                                       #
# Creates a matrix with the data from the file                                                                 #
# Creates a dictionary of attributes                                                                           #
# Example of output:                                                                                           #
#                                                                                                              #
# attr = {0: ('outlook',     ('sunny', 'overcast', 'rainy')),                                                  #
#         1: ('temperature', 'numeric'),                                                                       #
#         2: ('humidity',    'numeric'),                                                                       #
#         3: ('windy',       ('true', 'false')),                                                               #
#         4: ('play',        ('yes', 'no'))}                                                                   #
#                                                                                                              #
# data = { 0: ('sunny',    85.0, 85.0, 'false', 'no' ),                                                        #
#          1: ('sunny',    80.0, 90.0, 'true',  'no' ),                                                        #
#          2: ('overcast', 83.0, 86.0, 'false', 'yes'),                                                        #
#          3: ('rainy',    70.0, 96.0, 'false', 'yes'),                                                        #
#          4: ('rainy',    68.0, 80.0, 'false', 'yes'),                                                        #
#          5: ('rainy',    65.0, 70.0, 'true',  'no' ),                                                        #
#          6: ('overcast', 64.0, 65.0, 'true',  'yes'),                                                        #
#          7: ('sunny',    72.0, 95.0, 'false', 'no' ),                                                        #
#          8: ('sunny',    69.0, 70.0, 'false', 'yes'),                                                        #
#          9: ('rainy',    75.0, 80.0, 'false', 'yes'),                                                        #
#         10: ('sunny',    75.0, 70.0, 'true',  'yes'),                                                        #
#         11: ('overcast', 72.0, 90.0, 'true',  'yes'),                                                        #
#         12: ('overcast', 81.0, 75.0, 'false', 'yes'),                                                        #
#         13: ('rainy',    71.0, 91.0, 'true',  'no' )}                                                        #
#--------------------------------------------------------------------------------------------------------------#
def readArff(filename):
    global attr_dict
    global data
    
    attr_dict = {}
    data = {}
    
    attNumber = 0 #Counter for number of attributes
    relation = "" #Relation from ARFF file
    
    comment    = '%' + restOfLine
    identifier = Combine(Word(alphas,exact=1) + Optional(Word(alphanums+'_'+'-'))) #Name of attribute/relation
    relation   = Group((CaselessKeyword('@relation')) + identifier)

    #iris/golf
    nominal    = Suppress('{') + Group(delimitedList(identifier))  + Suppress('}')

    #others
    #nominal    = Suppress('{') + Group(delimitedList(Word(alphanums)))  + Suppress('}')

    domain     = ((CaselessKeyword('numeric')) | nominal)
    attribute  = Group(Suppress(CaselessKeyword('@attribute')) + identifier('name') + domain('domain'))
    example    = Group(delimitedList(Word(alphanums+'.'+'-')))
    arff_fmt   = ( Suppress(relation)
                   + OneOrMore(attribute)('attributes')
                   + (CaselessKeyword('@data'))
                   + OneOrMore(example)('examples') ).ignore(comment)

    
    # Parse input file and obtain result
    with open(filename) as file: text = file.read()
    #text = text.lower()
    result = list(arff_fmt.parseString(text))
    middle = (result.index('@data') if '@data' in result else result.index('@DATA'))
    
      
    # create the attribute dictionary from the first part of the result
    
    #attr = {} # attribute dictionary
    
    for (i,v) in enumerate(result[:middle]):
        attr_dict[i] = (v[0],v[1].lower() if (v[1]=='numeric' or v[1]=='NUMERIC') else tuple(v[1]))

    # create the data dictionary from the second part of the result

    data = {} # data dictionary (must be consisted)
    errorMsg = ""
    
    for (i,w) in enumerate(result[middle+1:]):
        if not(consistData(attr_dict, w)):
            errorMsg += 'Error in line ' + str(i) + ' of data. The program will ignore the line.\n'
            print('Error in line ' + str(i) + ' of data. The program will ignore the line.')
        else:
            data[i] = tuple( (float(v) if (attr_dict[i][1]=='numeric') else v) for (i,v) in enumerate(w) )

    #print('\nattr =') ; pprint(attr)
    #print('\ndata =') ; pprint(data)
        
    return (attr_dict, data, errorMsg)

#--------------------------------------------------------------------------------------------------------------#
# probability(flag):                                                                                           #
#       Receives a flag that indicates if the function is running a accuracy test or a classification of       #
#       a new instance: 0 represents new classification and 1 represents accuracy test.                        #
#       Calculates probabilities for discrete and continuous attributes                                        #  
#       Creates the dicionaries:                                                                               #
#         - dap_dict (discrete attribute probability) and                                                      #
#         - cap_dict (continuous  attribute probability)                                                       #
#                                                                                                              #
# Example of output:                                                                                           #
#                                                                                                              #
# dap = {('outlook', 'overcast', 'yes'): 0.44,                                                                 #
#        ('outlook', 'rainy',    'no' ): 0.40,                                                                 #
#        ('outlook', 'rainy',    'yes'): 0.33,                                                                 #
#        ('outlook', 'sunny',    'no' ): 0.60,                                                                 #
#        ('outlook', 'sunny',    'yes'): 0.22,                                                                 #
#        ('play',                'no' ): 0.36,                                                                 #
#        ('play',                'yes'): 0.64,                                                                 #
#        ('windy',   'false',    'no' ): 0.40,                                                                 #
#        ('windy',   'false',    'yes'): 0.67,                                                                 #
#        ('windy',   'true',     'no' ): 0.60,                                                                 #
#        ('windy',   'true',     'yes'): 0.33}                                                                 #
#                                                                                                              #
# cap = {('humidity',    'no' ): (86.2,  9.7),                                                                 #
#        ('humidity',    'yes'): (79.1, 10.2),                                                                 #
#        ('temperature', 'no' ): (74.6,  7.9),                                                                 #
#        ('temperature', 'yes'): (73.0,  6.2)}                                                                 #
#--------------------------------------------------------------------------------------------------------------#

def probability(data):
    global counterClassOptions #Count the occurences of each classification possibility
    global attr_dict #Dictionary with attributes from the present data set
    #global data      #Data of the present data set
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    #global modelData
    
    #copyOriginalData = {}
    cap_dict = {}
    dap_dict = {}
    idealKeyNumber = 0
    classOption = ()
    counterClassOptions = {}
    #Next three dictionaries used to calculate standard deviation
    mean = {}                
    squaredDifferences = {}  
    std = {} #Standard deviation

    
    #Test Flag
    #if(flag == 1):
    #    copyOriginalData = deepcopy(data)
    #    data = {}
    #    data = deepcopy(modelData)

    #Going on data dictionary line by line
    for index in data:
        
        #Get the classification value of the current line
        classOption = data[index][-1]
        #Counting the number of each classification possibility occurrances
        counterClassOptions[(classOption,)] = counterClassOptions.get((classOption,),0)+1
        #counterClassOptions = countClassOptions(data)
        #pprint(counterClassOptions)
        #Adding probability for classification attribute in dap_dict
        dap_dict[(attr_dict[len(attr_dict)-1][0],classOption)] = dap_dict.get((attr_dict[len(attr_dict)-1][0],classOption),1) + 1

        #For each attribute except the classification one, at the present line
        for j,column in enumerate(data[index][:-1]):
            #If the attribute is numeric 
            if type(attr_dict[j][1]) == str and attr_dict[j][1].lower() == 'numeric':
                #attr_dict[j][0],c = Attribute_name, classification
                cap_dict[(attr_dict[j][0],classOption)] = cap_dict.get((attr_dict[j][0],classOption),0) + column
            else:
                #Getting discrete values by counting
                #Starts with 1 for Laplace fix
                dap_dict[(attr_dict[j][0],column,classOption)] = dap_dict.get((attr_dict[j][0],column,classOption),1) + 1


    #CONTINOUS NORMAL PROBABILITY
    #Calculating mean for continuous attributes probability
    #Average of one type of classification based only on that classification
    for key in cap_dict:
        if len(key)>1:
            mean[key] = cap_dict[key] / counterClassOptions[(key[-1],)]

    #Getting column numbers and names of numeric attributes
    numericAttributesColumns = [(index, attItem[0]) for index, attItem in attr_dict.items() if (type(attItem[1]) == str and attItem[1].lower() == 'numeric')]
    
    #Next two for statements: standard deviation and updating cap_dict
    for index in data:
        #Just for the numeric attributes
        for columnNumber,attName in numericAttributesColumns:
            #Summing squared(value - mean)**2
            squaredDifferences[(attName,data[index][-1])] = squaredDifferences.get((attName,data[index][-1]),0) + pow((data[index][columnNumber]-mean[(attName,data[index][-1])]),2)

    for key in cap_dict:
        #Sum(squaredDifference/(N-1)) (N is the number of data with that classification, different from the total number of registers)
        std[key] = sqrt(squaredDifferences[key]/max(counterClassOptions[(key[-1],)] - 1,1))
        cap_dict[key] = (mean[key],std[key])

    
    #DISCRETE PROBABILITY WITH LAPLACE
    #Counting total possible number of keys for discrete attributes
    for i in range(len(attr_dict) - 1):
        if(type(attr_dict[i][-1]) == tuple):
            idealKeyNumber += (len(attr_dict[i][-1]) * len(counterClassOptions))
            
    #Calculating how many keys should exist for each class option
    idealKeyNumberByClass = idealKeyNumber/len(counterClassOptions)

    
    #Counting number of existent keys
    counter = {}
    if((len(dap_dict)-len(counterClassOptions)) < idealKeyNumber):
        for key in dap_dict:
            for option in counterClassOptions:
                #print(option)
                #print((key[-1],))
                if((key[-1],) == option and len(key) > 2):
                    counter[option] = counter.get(option,0) + 1

        #pprint(newLaplaceCountingClasses)
        #pprint(counter)
        #Updating counterClassOptions dict
        for key in counterClassOptions:
            #print(key)
            if(counter[key] < idealKeyNumberByClass):
                counterClassOptions[key] += (idealKeyNumberByClass - counter[key])

        #Updating classification classes in dap_dict
        for key in dap_dict:
            if(len(key) == 2):
                dap_dict[key] = counterClassOptions[(key[-1],)]

    dap_counting = deepcopy(dap_dict)
    #Calculating probability by counting for discrete attributes probability   
    for key in dap_dict:
        if len(key)>2:
            dap_dict[key] /= counterClassOptions[(key[-1],)]
        else:
            dap_dict[key] /= sum(counterClassOptions.values())

    #if(flag == 1):
    #    data = {}
    #    data = deepcopy(copyOriginalData)

    return dap_dict, dap_counting, cap_dict, counterClassOptions

#--------------------------------------------------------------------------------------------------------------#
# consistData(attr, line):                                                                                   #
#   Receives attributes dictionary and a line of data, and verify if values of data that should be numeric     #
#   are in the right format.                                                                                   #
#   Return True if all the numeric values are in the right format.                                             #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def consistData(attr, line):
    for index, item in enumerate(line):
        if attr[index][-1] == 'numeric':
            numberList = item.split('.')
            if len(numberList) > 2: return False
            else:
                for number in numberList:
                    if not(number.isnumeric()): return False
            
        else:
            if item not in attr[index][1]: return False

    return True

#--------------------------------------------------------------------------------------------------------------#
# testClassification():                                                                                        #
#   Recalculates probabilities using just a part of the data as model.                                         #
#   Then uses the probabilities to classify the other part of the data and calculates the accuracy             #
#   and g-measure of the classifier for a given relation (data set)                                            #                                                                                                              #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def testClassification():
    global data
    #global modelData

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    n = 30
    result = ''
    modelData = {}
    
    copyData = deepcopy(data)
    accuracyList = []
    listGM = []

    print("Calculando...")
    
    while n>0:
        classCounter = 0
        testData = {}
        modelData = {}
        percentage = {}
        numberOfElementByClass = {}
        classes = []

        classCounter = countClassOptions(copyData)
        for key in classCounter:
            classes.append(key)

        shuffle(copyData)

        lengthModelDataDict = int((len(copyData)/3) * 2)

        #Divinding data proportionally
        for key in classCounter:
            percentage[key] = round(classCounter[key]/sum(classCounter.values()),2)

        #for key in percentage:
            numberOfElementByClass[key] = round(percentage[key]*lengthModelDataDict)

        indexM = 0
        usedIndexes = []
        for key in numberOfElementByClass:
            c = 0
            for i in copyData:
                if(c < numberOfElementByClass[key] and key == (copyData[i][-1],)):
                    c += 1
                    modelData[indexM] = copyData[i]
                    indexM += 1
                    usedIndexes.append(i)

        indexT = 0
        for i in copyData:
            if not(i in usedIndexes):
                testData[indexT] = copyData[i]
                indexT += 1
        
        probability(modelData)
        result = list()
        accuracyCounter = 0
        
        for i in range(len(testData)):
            r = classification(list(testData[i][:-1]))[0]
            result.append(r)

            #g-measure for RIGHT classified instances
            if(r == testData[i][-1]):
                accuracyCounter += 1

                #If the instance was classified as positive, TP += 1
                if((r,) == classes[0]):
                    tp += 1

                #If the instance was classified as negative, TN += 1
                else:
                    tn += 1
                    
            #g-measure for WRONG classified instances            
            else:

                #If the instance was classified as positive, FP += 1
                #It was actually negative.
                if((r,) == classes[0]):
                    fp += 1

                #If the instance was classified as negative, FN +=1
                #It was actually positive
                else:
                    fn += 1

        #Calculating g-measure
        tpr = tp/(tp + fn)
        tnr = tn/(fp + tn)

        gm = sqrt(tpr * tnr)
        listGM.append(gm)
            
        #Calculating accuracy 
        accuracy = accuracyCounter/len(testData)
        accuracyList.append(accuracy)
        
        #print('Accuracy = ' + str(round(accuracy*100,2)) + '%')
        n -= 1

    #Accuracy mean and std
    mean = sum(accuracyList)/len(accuracyList)
    std = 0
    for i, value in enumerate(accuracyList):
        std += (mean - value) ** 2

    std /= (len(accuracyList) - 1)
    std = sqrt(std)

    #G-measure mean and std
    meanGM = sum(listGM)/len(listGM)
    stdGM = 0
    for i, value in enumerate(listGM):
        stdGM += (meanGM - value) ** 2

    stdGM /= (len(listGM) - 1)
    stdGM = sqrt(stdGM)
        
    print()
    print('Accuracy Mean = ' + str(mean))
    print('Accuracy Standard Deviation = ' + str(std))

    print()
    print('G-measure Mean = ' + str(meanGM))
    print('G-measure Standard Deviation = ' + str(stdGM))

    result = 'Accuracy Mean = ' + str(mean) + '\nAccuracy Standard Deviation = ' + str(std) + '\n\nG-measure Mean = ' + str(meanGM) + '\nG-measure Standard Deviation = ' + str(stdGM)
                
    return result


#--------------------------------------------------------------------------------------------------------------#
# testDiscretization():                                                                                        #
#   Calculates accuracy and g-measure for the data sets 'golf' and 'ModifiedGolf'                              #                                                                                                              #
#   to determine if files with discrete attributes are better classified than files with continuous attributes #
#--------------------------------------------------------------------------------------------------------------#
def testDiscretization():
    global data
    global attr_dict
    global modelData
    global filename
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    n = 30

    accuracyList1 = []
    listGM1 = []
    accuracyList2 = []
    listGM2 = []
    
    print("Calculando...")

    
    while n>0:
        filename = r'C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\Professor\golf.arff'
        attr_dict, data, error = readArff(filename)
        copyData = deepcopy(data)
    
        classCounter = 0
        testGolf = {}
        testGM = {}
        modelData = {}
        percentage = {}
        numberOfElementByClass = {}
        classes = []

        classCounter = countClassOptions(copyData)
        for key in classCounter:
            classes.append(key)

        for i in copyData:
            copyData[i] = copyData[i],i
            
        shuffle(copyData)
        
        
        lengthModelDataDict = int((len(copyData)/3) * 2)

        #Divinding data proportionally
        for key in classCounter:
            percentage[key] = round(classCounter[key]/sum(classCounter.values()),2)

        #for key in percentage:
            numberOfElementByClass[key] = round(percentage[key]*lengthModelDataDict)


        indexM = 0
        usedIndexes = []
        for key in numberOfElementByClass:
            c = 0
            for i in copyData:
                if(c < numberOfElementByClass[key] and key == (copyData[i][0][-1],)):
                    c += 1
                    modelData[indexM] = copyData[i][0]
                    indexM += 1
                    usedIndexes.append(copyData[i][1])

        
        indexT = 0
        for i in copyData:
            if not(copyData[i][1] in usedIndexes):
                testGolf[indexT] = copyData[i][0]
                indexT += 1
        
        probability(1)
        result = list()
        accuracyCounter = 0

        tp = 0
        tn = 0
        fp = 0
        fn = 0
        for i in range(len(testGolf)):
            r = classification(list(testGolf[i][:-1]))[0]
            result.append(r)

            #Counting right classifications
            if(r == testGolf[i][-1]):
                accuracyCounter += 1
                
                if((r,) == classes[0]):
                    tp += 1
                else:
                    tn += 1
                        
            else:
                if((r,) == classes[0]):
                    fp += 1
                else:
                    fn += 1

        #Calculating g-measure
        tpr = tp/(tp + fn)
        tnr = tn/(fp + tn)

        gm = sqrt(tpr * tnr)
        listGM1.append(gm)
            
        #Calculating accuracy 
        accuracy = accuracyCounter/len(testGolf)
        accuracyList1.append(accuracy)


        #########
        
        filename = r'C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\ModifiedGolf.arff'
        attr_dict, data, error = readArff(filename)
        copyData = deepcopy(data)

        for i in copyData:
            copyData[i] = copyData[i],i
            
        classCounter = 0
        testGolf = {}
        testMG = {}
        modelData = {}
        percentage = {}
        numberOfElementByClass = {}
        classes = []

        classCounter = countClassOptions2(copyData)
        for key in classCounter:
            classes.append(key)

        shuffle(copyData)
                    
        indexT = 0
        indexM = 0
        for i in copyData:
            if not(copyData[i][1] in usedIndexes):
                testGM[indexT] = copyData[i][0]
                indexT += 1
            else:
                modelData[indexM] = copyData[i][0]
                indexM += 1

        
        probability(1)
        result = list()
        accuracyCounter = 0

        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for i in range(len(testGM)):
            r = classification(list(testGM[i][:-1]))[0]
            result.append(r)

            #Counting right classifications
            if(r == testGM[i][-1]):
                accuracyCounter += 1
                
                if((r,) == classes[0]):
                    
                    tp += 1
                else:
                    tn += 1
                        
            else:
                if((r,) == classes[0]):
                    fp += 1
                else:
                    fn += 1

        #Calculating g-measure
        tpr = tp/(tp + fn)
        tnr = tn/(fp + tn)

        gm = sqrt(tpr * tnr)
        listGM2.append(gm)
            
        #Calculating accuracy 
        accuracy = accuracyCounter/len(testGM)
        accuracyList2.append(accuracy)
        
        
        #print('Accuracy = ' + str(round(accuracy*100,2)) + '%')
        n -= 1

    #Accuracy mean and std
    mean1 = sum(accuracyList1)/len(accuracyList1)
    std1 = 0
    for i, value in enumerate(accuracyList1):
        std1 += (mean1 - value) ** 2

    std1 /= (len(accuracyList1) - 1)
    std1 = sqrt(std1)

    #G-measure mean and std
    meanGM1 = sum(listGM1)/len(listGM1)
    stdGM1 = 0
    for i, value in enumerate(listGM1):
        stdGM1 += (meanGM1 - value) ** 2

    stdGM1 /= (len(listGM1) - 1)
    stdGM1 = sqrt(stdGM1)
    print()
    print('golf')
    print('G-measure Mean = ' + str(meanGM1))
    print('G-measure Standard Deviation = ' + str(stdGM1))
        
    print()
    print('Accuracy Mean = ' + str(mean1))
    print('Accuracy Standard Deviation = ' + str(std1))


    ######
    

    #Accuracy mean and std
    mean2 = sum(accuracyList2)/len(accuracyList2)
    std2 = 0
    for i, value in enumerate(accuracyList2):
        std2 += (mean2 - value) ** 2

    std2 /= (len(accuracyList2) - 1)
    std2 = sqrt(std2)

    #G-measure mean and std
    meanGM2 = sum(listGM2)/len(listGM2)
    stdGM2 = 0
    for i, value in enumerate(listGM2):
        stdGM2 += (meanGM2 - value) ** 2

    stdGM2 /= (len(listGM2) - 1)
    stdGM2 = sqrt(stdGM2)
    print()
    print('ModifiedGolf')
    print('G-measure Mean = ' + str(meanGM2))
    print('G-measure Standard Deviation = ' + str(stdGM2))
        
    print()
    print('Accuracy Mean = ' + str(mean2))
    print('Accuracy Standard Deviation = ' + str(std2))
    
    return None

    
#--------------------------------------------------------------------------------------------------------------#
# Count the occurrences of each possible classification among the data                                         #
#--------------------------------------------------------------------------------------------------------------#
def countClassOptions(d):
    counter = {}
    for index in d:        
        #Get the classification value of the current line
        classOption = d[index][-1]
        #Counting the number of each classification possibility occurrences
        counter[(classOption,)] = counter.get((classOption,),0)+1
        
    return counter

#--------------------------------------------------------------------------------------------------------------#
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def countClassOptions2(d):
    counter = {}
    for index in d:        
        #Get the classification value of the current line
        classOption = d[index][0][-1]
        #Counting the number of each classification possibility occurrences
        counter[(classOption,)] = counter.get((classOption,),0)+1
        
    return counter
#--------------------------------------------------------------------------------------------------------------#
# gauss(x,m,s):                                                                                                #
# Receives value, mean and standard deviation                                                                  #
# Gaussian probability distribution function                                                                   #
#--------------------------------------------------------------------------------------------------------------#
def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((float(x)-float(m))/max(float(s),1))**2)


#--------------------------------------------------------------------------------------------------------------#
# Attribute-value-class probability function                                                                   #
# Returns the value of dap_dict or cap_dict at the given position                                              #
#--------------------------------------------------------------------------------------------------------------#
def prob(attribute_column,attribute_value,class_value):
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    #global newLaplaceCountingClasses

    #print(counterClassOptions)
    #pprint(cap_dict)
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if type(attribute_domain) == str and attribute_domain.lower() == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict.get((attribute_name,attribute_value,class_value),(1/max(counterClassOptions[(class_value,)],1)))


#-------------------------------------------------------------------------------------------------------------#
# Bayesian classification function                                                                            #
# Calculates and returns the probability of the given instance for the                                        #
# clasification                                                                                               #
#-------------------------------------------------------------------------------------------------------------#
def classification(instance):
    #global data
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities

    class_attribute_column = len(attr_dict)-1
    class_attribute_name   = attr_dict[class_attribute_column][0]
    class_attribute_domain = attr_dict[class_attribute_column][1]

    likelihoods = [ [prob(i,instance[i],class_value)
                                for i in range(len(instance))]
                    + [dap_dict[(class_attribute_name,class_value)]]
                    for class_value in class_attribute_domain ]
    # the next line is only for debug purpose
    # print(likelihoods)
    likelihoods = [reduce(mul,likelihood,1) for likelihood in likelihoods]
    # the next line is only for debug purpose
    # print(likelihoods)
    denominator = sum(likelihoods)
    probs = list(zip([likelihood/denominator for likelihood in likelihoods],
                     class_attribute_domain))
    # the next two lines are only for debug purpose
    printProb = ''
    for (probability,class_value) in probs:
        #print('prob[%s] = %.1f%%' % (class_value,probability*100))
        printProb += '%s = %.1f%%\n' % (class_value.capitalize(),probability*100)

    #pprint(probs)
    #pprint(dap_dict)
    return max(probs)[1],printProb
    

def displayProbabilities(attr, data):

    discrete = {}
    continuous = {}

    numericAtt = {}
    numericAttMean = {}
    discreteAttCounting = {}
    std = {}

    for index in data:
        for att in attr:
            
            if attr[att][1] == 'numeric' or attr[att][1] == 'NUMERIC':
                numericAtt[att] = numericAtt.get(att,0) + data[index][att]

            else:
                for value in attr[att][1]:
                    #print(value)
                    #print(data[index][att]) 
                    if value == data[index][att]:
                        discreteAttCounting[(att,value)] = discreteAttCounting.get((att,value),0) + 1

    #print(attr)
    #print()
    #print(data)
    #print()
    
    for index in numericAtt: numericAttMean[index] = numericAtt[index]/len(data)

    #STD
    sumSquared = {}
    stdev = {}
    for line in data:
        for attIndex in numericAttMean:
            sumSquared[attIndex] = sumSquared.get(attIndex,0)+((numericAttMean[attIndex] - data[line][attIndex])**2)

    for attIndex in sumSquared: stdev[attIndex] = sqrt(sumSquared[attIndex]/ max(len(data)-1,1))

    
    for index in numericAttMean:
        continuous[index] = (numericAttMean[index], stdev[index])
        
    for index in discreteAttCounting:
        discrete[index] = (discreteAttCounting[index], discreteAttCounting[index]/len(data))

    #print(attr)
    #print()
    #print(data)
    #print()
    #print(discreteAttCounting)
    return discrete, continuous


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

    print(values)
    input()
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


#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
    #testDiscretization()
