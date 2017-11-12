#################################################################################################################
#   Authors:  Gabriela Silva de Oliveira, Silvio do Lago Pereira
#   Emails:  gsilvadoliveira@gmail.com, slago@fatecsp.br
#
#   Program:    ArffReader.py
#   Date:       20/02/2017
#   Purpose:    Bayesian classifier  
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
backUpData = []
backupAttr = {}
limits=[]
discAttributesDict = {}

#--------------------------------------------------------------
# main():
# Gets the file from the user,
# calls the function that reads the files
# and prints the returns on screen
# Used when the classifier runs without the user interface
#--------------------------------------------------------------
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

    
    print('Minimum entropy intervals: ')
    entropyS = calcEntropy(data)
    lengthS = len(data)

    print(minimumEntropy(data,1,list()))

    print()
    print('End')
    input('Hit ENTER to input an instance. ')
    instance = input("Enter an instance to be tested: ")
    classification(instance.lower().replace(' ','').split(','))    

    
#--------------------------------------------------------------------------------------------------------------#
# readArff(filename):                                                                                          #
# Read the given ARFF file line by line using pyparsing                                                        #
# Creates a dictionary of attributes and a dictionary of data                                                  #
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
    global backUpData
    global backupAttr
    attr_dict = {}
    data = {}
    
    attNumber = 0 #Counter for number of attributes
    relation = "" #Relation from ARFF file
    
    comment    = '%' + restOfLine
    identifier = Combine(Word(alphas,exact=1) + Optional(Word(alphanums+'_'+'-'))) #Name of attribute/relation
    relation   = Group((CaselessKeyword('@relation')) + identifier)

    #iris/golf
    #nominal    = Suppress('{') + Group(delimitedList(identifier))  + Suppress('}')

    #pima
    #nominal    = Suppress('{') + Group(delimitedList(Word(alphanums)))  + Suppress('}')
    
    nominal    = Suppress('{') + Group(delimitedList(Word(alphanums+'_'+'-'+'.')))  + Suppress('}')
    
    domain     = ((CaselessKeyword('numeric')) | nominal)
    attribute  = Group(Suppress(CaselessKeyword('@attribute')) + identifier('name') + domain('domain'))
    example    = Group(delimitedList(Word(alphanums+'.'+'-'+'?')))
    arff_fmt   = ( Suppress(relation)
                   + OneOrMore(attribute)('attributes')
                   + (CaselessKeyword('@data'))
                   + OneOrMore(example)('examples') ).ignore(comment)

    
    # Parse input file and obtain result
    with open(filename) as file: text = file.read()

    result = list(arff_fmt.parseString(text))
    middle = (result.index('@data') if '@data' in result else result.index('@DATA'))
    
    # create the attribute dictionary from the first part of the result
    for (i,v) in enumerate(result[:middle]):
        attr_dict[i] = (v[0],v[1].lower() if (v[1]=='numeric' or v[1]=='NUMERIC') else tuple(v[1]))

    # create the data dictionary from the second part of the result
    data = {} # data dictionary (must be consisted)
    errorMsg = ""

    for (i,w) in enumerate(result[middle+1:]):
        if not(consistData(attr_dict, w)):
            if ('?' in list(w)):
                errorMsg += 'Line ' + str(i) + ': ignored for missing attribute values.\n'
            else:    
                #errorMsg += 'Error in line ' + str(i) + ' of data. The program will ignore the line.\n'
                errorMsg += 'Line ' + str(i) + ': ignored for error on the data format.\n'

        #Missing Attributes
        elif (len(attr_dict) != len(w)):
            errorMsg += 'Line ' + str(i) + ': ignored for missing attribute values.\n'

        else:
            data[i] = tuple( (float(v) if (attr_dict[i][1]=='numeric') else v) for (i,v) in enumerate(w) )

    backUpData = deepcopy(data)
    backupAttr = deepcopy(attr_dict)

    #pprint(data)
    return (attr_dict, data, errorMsg)


#-------------------------------------------------------------------------------------------------------------
# consistData(attr, line):
#   Receives attributes dictionary and a line of data, and verify if values of data that should be numeric
#   are in the right format.
#   Return True if all the numeric values are in the right format.
#-------------------------------------------------------------------------------------------------------------
def consistData(attr, line):        
    for index, item in enumerate(line):
    
        #Numeric attributes
        if attr[index][-1] == 'numeric':
            if not(testNumeric(item)): return False
        
        #Discrete Attributes
        else:
            if item not in attr[index][1]: return False
    
    return True


#-------------------------------------------------------------------------------------
# testNumeric(value):
#   Checks if the given value is a number
#-------------------------------------------------------------------------------------
def testNumeric(value):

    #strValue = deepcopy(value)
    if value == '': return False
    if value[0] in ['+','-']:
        value = value[1:]

    numberList = value.split('.')

    if all(x == '' for x in numberList): return False
    
    if len(numberList) > 2: return False
    else:
        for number in numberList:
            if number != '' and not(number.isnumeric()): return False
    return True


#--------------------------------------------------------------------------------------------------------------#
# probability(data):                                                                                           #
#       Calculates probabilities for discrete and continuous attributes on the given data                      #  
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
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    
    cap_dict = {}
    dap_dict = {}
    idealKeyNumber = 0
    classOption = ()
    counterClassOptions = {}
    
    #Next three dictionaries used to calculate standard deviation
    mean = {}                
    squaredDifferences = {}  
    std = {} #Standard deviation

    for index in data:
        
        #Get the classification value of the current line
        classOption = data[index][-1]
        #Counting the number of each classification possibility occurrances
        counterClassOptions[(classOption,)] = counterClassOptions.get((classOption,),0)+1

        #Adding probability for classification attribute in dap_dict
        dap_dict[(attr_dict[len(attr_dict)-1][0],classOption)] = dap_dict.get((attr_dict[len(attr_dict)-1][0],classOption),1) + 1

        #For each attribute except the classification one, at the present line
        for j,column in enumerate(data[index][:-1]):
            #If the attribute is numeric 
            if type(attr_dict[j][1]) == str and attr_dict[j][1].lower() == 'numeric':
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
                if((key[-1],) == option and len(key) > 2):
                    counter[option] = counter.get(option,0) + 1

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

    return dap_dict, dap_counting, cap_dict, counterClassOptions



#----------------------------------------------------------------------------------------------------------
# testClassification():
#   Recalculates probabilities using just a part of the data as model.
#   Then uses the probabilities to classify the other part of the data and calculates the accuracy
#   and g-measure of the classifier for a given relation (data set)
#----------------------------------------------------------------------------------------------------------
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


    
#--------------------------------------------------------------------------------------
# Count the occurrences of each possible classification among the data
#--------------------------------------------------------------------------------------
def countClassOptions(d):
    counter = {}
    for index in d:        
        #Get the classification value of the current line
        classOption = d[index][-1]
        #Counting the number of each classification possibility occurrences
        counter[(classOption,)] = counter.get((classOption,),0)+1
        
    return counter



#--------------------------------------------------------------------------------------------------
# gauss(x,m,s): 
# Receives value, mean and standard deviation
# returns the Gaussian probability distribution function
#--------------------------------------------------------------------------------------------------
def gauss(x,m,s):
    #Return 1 or average?
    if s == 0: return 1
    return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((float(x)-float(m))/max(float(s),1))**2)


#----------------------------------------------------------------------------
# Attribute-value-class probability function
# Returns the value of dap_dict or cap_dict at the given position 
#----------------------------------------------------------------------------
def prob(attribute_column,attribute_value,class_value):
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities

    if (class_value,) not in counterClassOptions: return 0
    
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if type(attribute_domain) == str and attribute_domain.lower() == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict.get((attribute_name,attribute_value,class_value),(1/max(counterClassOptions[(class_value,)],1)))


#--------------------------------------------------------------------------------------
# Bayesian classification function
# Calculates and returns the probability of the given instance for the clasification
#--------------------------------------------------------------------------------------
def classification(instance):
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities

    class_attribute_column = len(attr_dict)-1
    class_attribute_name   = attr_dict[class_attribute_column][0]
    class_attribute_domain = attr_dict[class_attribute_column][1]

    likelihoods = [ [prob(i,instance[i],class_value)
                                for i in range(len(instance))]
                    + [dap_dict.get((class_attribute_name,class_value),0)]
                    for class_value in class_attribute_domain ]

    # the next line is only for debug purpose

    likelihoods = [reduce(mul,likelihood,1) for likelihood in likelihoods]
    # the next line is only for debug purpose
    #print(likelihoods)
    
    denominator = sum(likelihoods)

    probs = list(zip([likelihood/max(denominator,1.0e-323) for likelihood in likelihoods],
                     class_attribute_domain))
    
    printProb = ''
    for (probability,class_value) in probs:
        # the next line is only for debug purpose
        #print('prob[%s] = %.1f%%' % (class_value,probability*100))
        printProb += '%s = %.1f%%\n' % (class_value.capitalize(),probability*100)

    return max(probs)[1],printProb
    

#-------------------------------------------------------------------------------------
#  Load attributes information on the main screen of the user interface
#-------------------------------------------------------------------------------------
def displayProbabilities(attr, data):
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict
    
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
                    if value == str(data[index][att]):
                        discreteAttCounting[(att,value)] = discreteAttCounting.get((att,value),0) + 1
    
    for index in numericAtt: numericAttMean[index] = numericAtt[index]/len(data)

    #Standard Deviation
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

#-------------------------------------------------------------
# Discretize instance entered by the user
#-------------------------------------------------------------
def discreteInstance(instance, discMethod):
    global discAttributesDict
    global attr_dict

    
    instance = instance.replace(' ','').split(',')

    print(instance)
    if discMethod != 0 and len(discAttributesDict)>0:
        
        for att in discAttributesDict:

            #and instance[att] not in attr_dict[att][-1]:
            if testNumeric(instance[att]):
                print(discAttributesDict[att])
                for i,limit in enumerate(discAttributesDict[att]):

                    #Same Width
                    if discMethod == 1:
                        if(float(instance[att]) < limit):
                            instance[att] = str(i)
                            break

                    #Same Frequency
                    elif discMethod == 2:
                        if(float(instance[att]) <= limit):
                            instance[att] = str(i)
                            break

    print(instance)
    return instance
    
#-----------------------------------------------------
# Get discretization parameters from interface
#-----------------------------------------------------
def cleanData(attribute):
    global data
    global backUpData
    global attr_dict
    global backupAttr
    global limits
    global discAttributesDict

    limits = []
    discAttributesDict.pop(attribute, None)

    for d in data:
        temp = []
        for i,item in enumerate(data[d]):
            if i == attribute:
                temp.append(backUpData[d][i])
            else:
                temp.append(data[d][i])

        data[d] = tuple(temp)

            
    #data = deepcopy(backUpData)
    attr_dict[attribute] = deepcopy(backupAttr[attribute])

   
    return data, attr_dict

#-----------------------------------------------------
# Discretize attributes
#-----------------------------------------------------
def startDiscretization(attListDisc):
    global data
    global attr_dict
    global limits
    global discAttributesDict
    #global backUpData
    
    limits=[]

    for attIndex in attListDisc:

        typeDisc = attListDisc[attIndex][0]

        if(typeDisc != 3):
            numerOfIntervals = int(attListDisc[attIndex][-1])

        cleanData(attIndex)
        
        if(attr_dict[attIndex][-1] == "numeric" or attr_dict[attIndex][-1] == "NUMERIC"):

            #Same width discretization
            if typeDisc == 1:
                discEqualWidth(data, int(attIndex), numerOfIntervals)
            elif typeDisc == 2:
                discEqualFrequency(data, int(attIndex), numerOfIntervals)
            elif typeDisc == 3:
                discMinimumEntropy(data, int(attIndex))

            list.sort(limits)    
            limits[-1] = float('inf')
            
            newAttValuesStr = []
            for index, value in enumerate(limits):
                newAttValuesStr.append(str(index))
                
            attr_dict[attIndex] = (attr_dict[attIndex][0], newAttValuesStr)

            discAttributesDict[attIndex] = limits


            
        for d in data:
            for i, v in enumerate(limits):
                #Same width or Minimum Entropy
                if(typeDisc == 1 or typeDisc == 3):
                    if type(v) == tuple:
                        if (data[d][attIndex] < v[0]):
                            data[d] = data[d][:attIndex] + (i,) + data[d][attIndex+1:]
                            break

                    else:
                        if (data[d][attIndex] < v):
                            data[d] = data[d][:attIndex] + (i,) + data[d][attIndex+1:]
                            break

                #Same frequency
                elif(typeDisc == 2):
                    if (data[d][attIndex] <= v):
                        data[d] = data[d][:attIndex] + (i,) + data[d][attIndex+1:]
                        break

    return data, attr_dict

#------------------------------------------------------------------------------------------------------------
# Separate continuous values into intervals (bins) with discretization by equal width
#------------------------------------------------------------------------------------------------------------
def discEqualWidth(data, attIndex, numberOfBins):
    global attr_dict
    global limits
    
    #Gets all the values of the continuous attributes
    width=0.0
    values = setOfValues(data, attIndex, False)

    intervals = {}

    #Calculate width
    minValue = min(values)
    maxValue = max(values)
    width = (maxValue - minValue)/numberOfBins

    #Get limits for discretization
    for n in range(numberOfBins):
        limits.append(minValue + width*(n+1))

    return None       
                
    
#------------------------------------------------------------------------------------------------------------#
# Separate continuous values into intervals (bins) with discretization by equal frequency
#------------------------------------------------------------------------------------------------------------#
#Same of the book
def discEqualFrequency(data, attIndex, numberOfBins):
    global attr_dict
    global limits
    
    values  = setOfValues(data, attIndex, False)

    values = set(values)
    values = sorted(values)

    frequency = len(values)/numberOfBins
    frequency = int(ceil(frequency))

    for i in range(numberOfBins):
        if ((frequency - 1) + (frequency * i)) < len(values):
            limits.append(values[(frequency - 1) + (frequency * i)])
        else:
            limits.append(max(values))

    return None


#------------------------------------------------------------------------------------------------------------#
# Enttropy
#------------------------------------------------------------------------------------------------------------#
def discMinimumEntropy(data, attIndex):
    global attr_dict
    global limits
    entropyU = 0

    limits = []
    
    values  = setOfValues(data, attIndex, True)

    #Entropy on the Universe
    entropyU = calcEntropy(values)

    #Recursive entropy
    recursiveMinEntropy(values, log(len(set(values)),2))

    #print(limits)
    return None


#-------------------------------------------------------
# Calculates entropy on the given set
#-------------------------------------------------------
def calcEntropy(setValues):
    global counterClassOptions
    cont = {}
    entropy = 0

    #print(len(counterClassOptions))
    #input()

    setValues = sorted(setValues)
    #print(setValues)
    #print()
    #input()

    n = len(setValues)

    for key in counterClassOptions:
        count = 0
        
        for value in setValues:
            #print(value)
            if value[1] == key[0]:
                count += 1

        p = count/n
        if p != 0:
            entropy += (p * log(p,2))
    
    #print(setValues)
    
    #for v in setValues:
            #cont[v] = cont.get(v,0) + 1
            
    #for i in cont:
    #    p = cont[i]/n
    #    entropy += (p * log(p,2))
    
    entropy = (-1) * entropy

    
    return entropy


#-----------------------------------------------------------------------------
# Calculate information entropy
#-----------------------------------------------------------------------------
def informationEntropy(s, s1, s2):
    return (len(s1)/len(s) * calcEntropy(s1)) + (len(s2)/len(s) * calcEntropy(s2))


#----------------------------------------------------------------------------
# Verify minimum entropy by recursivity and save the intervals
#----------------------------------------------------------------------------
def recursiveMinEntropy(s, entropy):
    global attr_dict
    global data
    global limits

    if len(s) < 4 or entropy <= 0:
        return
    
    s = sorted(s)

    for i in range(1,len(s)):
        if(i < len(s)) and (s[i][0] == s[i-1][0]):
            del s[i]

    setLength = len(s)
    #int1 = int(setLength/4)
    #int2 = int(setLength/2)
    #int3 = 3 * int(setLength/4)
    
    #entropy1 = informationEntropy(s, s[:int1], s[int1:])
    #entropy2 = informationEntropy(s, s[:int2], s[int2:])
    #entropy3 = informationEntropy(s, s[:int3], s[int3:])

    #minEntropy = min((entropy1,int1), (entropy2,int2), (entropy3,int3))

    #limits.append(s[minEntropy[1]])
    
    minEntropy = (float('Inf'), 0)

    for i in range(setLength-1):
        cutPoint = 0.00
        cutPoint = (s[i][0] + s[i+1][0])/2
        
        s1 = []
        s2 = []
        for value in s:
            #print(value[0])
            if value[0] <= cutPoint:
                s1.append(value)
            else:
                s2.append(value)

        e = informationEntropy(s, s1, s2)

        if (e < minEntropy[0]):
            minEntropy = (e, cutPoint)

    limits.append(minEntropy[1])

    s1minEnt = []
    s2minEnt = []
    for value in s:
        if value[0] <= minEntropy[1]:
            s1minEnt.append(value)
        else:
            s2minEnt.append(value)

            
    #minEntropy = min(entropyList)
    
    
    recursiveMinEntropy(s1minEnt, minEntropy[0])
    recursiveMinEntropy(s2minEnt, minEntropy[0])

#------------------------------------------------------------------------------------------------------------#
# Create a list with the continuous values from the data
# The index of the dictionary is the same index of the continuous attribute
#------------------------------------------------------------------------------------------------------------#
def setOfValues(data, attIndex, entFlag):
    global attr_dict
    
    values = []

    if entFlag:
        for i in data:
            values.append((data[i][attIndex],data[i][-1]))

    else:
        for i in data:
            values.append(data[i][attIndex])

    return values


#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
    #testDiscretization()
