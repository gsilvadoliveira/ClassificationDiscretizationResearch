#################################################################################################################
#   Author:  Gabriela Silva de Oliveira
#    Email:  gsilvadoliveira@gmail.com
#
#   Program:    ArffReader.py
#   Date:       20/02/2017
#   Purpose:    Read ARFF files and store the data on internal variables
#           
#################################################################################################################

from pyparsing import *
from math import *
from operator import *
from functools import reduce
from pprint import *
from copy import *
from random import *
#Global variables
attr_dict = {}
dap_dict = {}
cap_dict = {}
data = []
counterClassOptions = {}
filename = ''
modelData = {}

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
    
    filename = input('Enter file path: ')
    readArff(filename)
    probability()

    print("\nAttribute(s):")
    pprint(attr_dict)

    print("\nDiscrete probability:")
    pprint(dap_dict)

    print("\nContinuous probablity:")
    pprint(cap_dict)  

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

    attNumber = 0 #Counter for number of attributes
    relation = "" #Relation from ARFF file
    
    comment    = '%' + restOfLine
    identifier = Combine(Word(alphas,exact=1) + Optional(Word(alphanums+'_'+'-'))) #Name of attribute/relation
    relation   = Group((CaselessKeyword('@relation')) + identifier)
    #nominal    = Suppress('{') + Group(delimitedList(identifier))  + Suppress('}')
    nominal    = Suppress('{') + Group(delimitedList(Word(alphanums)))  + Suppress('}')
    domain     = ((CaselessKeyword('numeric')) | nominal)
    attribute  = Group(Suppress(CaselessKeyword('@attribute')) + identifier('name') + domain('domain'))
    example    = Group(delimitedList(Word(alphanums+'.'+'-')))
    arff_fmt   = ( Suppress(relation)
                   + OneOrMore(attribute)('attributes')
                   + (CaselessKeyword('@data'))
                   + OneOrMore(example)('examples') ).ignore(comment)

    
    # Parse input file and obtain result
    with open(filename) as file: text = file.read()
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
        if not(checkIsNumber(attr_dict, w)):
            errorMsg += 'Error in line ' + str(i) + ' of data. The program will ignore the line.\n'
            print('Error in line ' + str(i) + ' of data. The program will ignore the line.')
        else:
            data[i] = tuple( (float(v) if (attr_dict[i][1]=='numeric') else v) for (i,v) in enumerate(w) )

    #print('\nattr =') ; pprint(attr)
    #print('\ndata =') ; pprint(data)
        
    return (attr_dict, data, errorMsg)

#--------------------------------------------------------------------------------------------------------------#
# probability(attr_dict, data):                                                                                #
#       Receives dictionary with attributes and matrix of data                                                 #
#       Calculates probabilities for discrete and continuous attributes                                        #  
#       Receive the dictionaries att and data and create the dicionaries:                                      #
#         - dap (discrete attribute probability) and                                                           #
#         - cap (continuous  attribute probability)                                                            #
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

def probability(flag):
    global counterClassOptions #Count the occurences of each classification possibility
    global attr_dict
    global data
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    global modelData
    
    copyOriginalData = {}
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
    if(flag == 1):
        copyOriginalData = deepcopy(data)
        data = {}
        data = deepcopy(modelData)

    #Going on data dictionary line by line
    for index in data:
        
        #Get the classification value of the current line
        classOption = data[index][-1]
        #Counting the number of each classification possibility occurrances
        counterClassOptions[(classOption,)] = counterClassOptions.get((classOption,),0)+1
        #counterClassOptions = countClassOptions(data)

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
        std[key] = sqrt(squaredDifferences[key]/(counterClassOptions[(key[-1],)] - 1))
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

    #Calculating probability by counting for discrete attributes probability   
    for key in dap_dict:
        if len(key)>2:
            dap_dict[key] /= counterClassOptions[(key[-1],)]
        else:
            dap_dict[key] /= sum(counterClassOptions.values())
            

    if(flag == 1):
        data = {}
        data = deepcopy(copyOriginalData)
    
    return dap_dict, cap_dict

#--------------------------------------------------------------------------------------------------------------#
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def checkIsNumber(attr, line):
    for index, item in enumerate(line):
        if attr[index][-1] == 'numeric':
            numberList = item.split('.')
            if len(numberList) > 2: return False
            else:
                for number in numberList:
                    if not(number.isnumeric()): return False
            
    return True

#--------------------------------------------------------------------------------------------------------------#
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def testClassification():
    global data
    global modelData

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    n = 30
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

        #Dividing data by thirds
        #for i in range(lengthModelDataDict):
        #    modelData[i] = copyData[i]

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
        
        probability(1)
        result = list()
        accuracyCounter = 0
        
        for i in range(len(testData)):
            r = classification(list(testData[i][:-1]))[0]
            result.append(r)

            #Counting right classifications
            if(r == testData[i][-1]):
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
    print('G-measure Mean = ' + str(meanGM))
    print('G-measure Standard Deviation = ' + str(stdGM))
        
    print()
    print('Accuracy Mean = ' + str(mean))
    print('Accuracy Standard Deviation = ' + str(std))
    
    return accuracy



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
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#                                                                                                              #
#--------------------------------------------------------------------------------------------------------------#
def countClassOptions(d):
    counter = {}
    for index in d:        
        #Get the classification value of the current line
        classOption = d[index][-1]
        #Counting the number of each classification possibility occurrances
        counter[(classOption,)] = counter.get((classOption,),0)+1
        
    return counter

def countClassOptions2(d):
    counter = {}
    for index in d:        
        #Get the classification value of the current line
        classOption = d[index][0][-1]
        #Counting the number of each classification possibility occurrances
        counter[(classOption,)] = counter.get((classOption,),0)+1
        
    return counter
#--------------------------------------------------------------------------------------------------------------#
# gauss(x,m,s):                                                                                                #
# Receives value, mean and standard deviation                                                                  #
# Gaussian probability distribution function                                                                   #
#--------------------------------------------------------------------------------------------------------------#
def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((float(x)-float(m))/float(s))**2)


#--------------------------------------------------------------------------------------------------------------#
# Attribute-value-class probability function                                                                   #
# Returns the value of dap_dict or cap_dict at the given position                                              #
#--------------------------------------------------------------------------------------------------------------#
def prob(attribute_column,attribute_value,class_value):
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    global newLaplaceCountingClasses

    #print(counterClassOptions)
    #pprint(cap_dict)
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if type(attribute_domain) == str and attribute_domain.lower() == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict.get((attribute_name,attribute_value,class_value),(1/counterClassOptions[(class_value,)]))


#-------------------------------------------------------------------------------------------------------------#
# Bayesian classification function                                                                            #
# Calculates and returns the probability of the given instance for the                                        #
# clasification                                                                                               #
#-------------------------------------------------------------------------------------------------------------#
def classification(instance):
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
        printProb += 'prob[%s] = %.1f%%\n' % (class_value,probability*100)

    #pprint(dap_dict)
    return max(probs)[1],printProb
    

#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    #main()
    testDiscretization()
