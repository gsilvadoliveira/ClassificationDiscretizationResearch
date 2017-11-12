##########################################################################
#   Author:  Gabriela Silva de Oliveira
#    Email:  gsilvadoliveira@gmail.com
#
#   Program:    ArffReader.py
#   Date:       20/02/2017
#   Purpose:    Read ARFF files and store the data on internal variables
#           
##########################################################################

from math import *
from pprint import pprint
from operator import *
from functools import reduce


#--------------------------------------------------------------------------#
# main():                                                                  #
# Gets the file from the user,                                             #
# calls the function that reads the files                                  #
# and prints the returns on screen                                         #
#--------------------------------------------------------------------------#
def main():
    global attr_dict #Dictionary for attributes
    global dap_dict  #Dictionary for discrete attributes probabilities
    global cap_dict  #Dictionary for continuous attributes probabilities
    global data      #Matrix of data from the ARFF file

    attr_dict = {}
    dap_dict = {}
    cap_dict = {}
    data = []
    
    filename = input('Enter file path: ')
    relation, attr_dict, data = readArff(filename)
    dap_dict, cap_dict = probability(attr_dict, data)

    print("\nAttribute(s):")
    pprint(attr_dict)

    print("\nDiscrete data:")
    pprint(dap_dict)

    print("\nContinuous data:")
    pprint(cap_dict)
    
    instance = input('\nEnter instance to be tested: ')
    classification(instance.replace(' ','').split(','))


#--------------------------------------------------------------------------#
# readArff():                                                              #
# Read the given ARFF file line by line.                                   #
# Creates a matrix with the data from the file                             #
# Creates a dictionary of attributes                                       #
#--------------------------------------------------------------------------#
def readArff(filename):

    global classAtt  #Name of classification attribute
    global classPossibilities #Possible classifications
    classAtt = ""
    classPossibilities = ()
    
    attNumber = 0 #Counter for number of attributes
    relation = "" #Relation from ARFF file
    
    #Opening ARFF file
    with open(filename, 'r') as arffFile:
        
        #Reading file
        for line in arffFile:
            line = line.replace('\n','')

            if line.find('{') > 0:
                bracketIndex = line.index('{')
                line = line[:bracketIndex] + line[bracketIndex:].replace(' ','')
                
            #Split current line by blank spaces
            line = line.split()
                        
            #Skip blank lines
            if(len(line) > 0):

                #Stop reading if reach Data, goes to next for
                if(line[0].upper() == '@DATA'):
                    break
                
                #Reading Relation
                elif(line[0].upper() == '@RELATION'):
                    relation = line[1]


                #Reading Attributes
                elif(line[0].upper() == '@ATTRIBUTE'):
                    #Remove lable of the line
                    line.pop(0)
                    
                    #Making a list if the attributes are discrete
                    if line[1].find('{') > -1:
                        line[1] = line[1].replace('{','').replace('}','').replace(' ','').split(',')

                    attr_dict[attNumber] = (line[0], line[1])
                    attNumber += 1
                    
        classAtt = attr_dict[len(attr_dict) - 1][0]
        classPossibilities = attr_dict[len(attr_dict) - 1][1]
        
        #Read lines of DATA
        for line in arffFile:
            line = line.replace('\n','')
            if(len(line) > 0):
                #Break the line by commas
                currentLine = line.split(',')
                
                #Building data dictionary
                temp = []
                for i,word in enumerate(currentLine):
                    if(type(attr_dict[i][-1]) == str and attr_dict[i][-1].upper() == 'NUMERIC'):
                        temp.append(float(word.strip()))
                    else:
                        temp.append(word.strip())
                data.append(temp)


    #Returns information from the file
    return relation, attr_dict, data


#--------------------------------------------------------------------------#
# probability(attr_dict, data):                                            #
# Receives dictionary with attributes and matrix of data                   #
# Calculates probabilities for discrete and continuous attributes          #
#--------------------------------------------------------------------------#
def probability(attr_dict, data):
    
    counterClassOptions = {} #Count the occurences of each classification possibility
    #Next two dictionaries used to calculate standard deviation
    mean = {}                
    squaredDifferences = {}  

    std = {} #Standard deviation

    #Going on data dictionary line by line
    for i, line in enumerate(data):
        #Get the classification value of the current line
        classOption = line[-1]
        
        #Counting the number of each classification possibility occurrances
        counterClassOptions[(classOption,)] = counterClassOptions.get((classOption,),0)+1

        #Adding porability for classification attribute in dap_dict
        dap_dict[(attr_dict[len(attr_dict)-1][0],classOption)] = dap_dict.get((attr_dict[len(attr_dict)-1][0],classOption),0) + 1

        #For each attribute except the classification one, at the present line
        for j,column in enumerate(line[:-1]):
            #If the attribute is numeric 
            if type(attr_dict[j][1]) == str and attr_dict[j][1].lower() == 'numeric':
                #attr_dict[j][0],c = Attribute_name, classification
                cap_dict[(attr_dict[j][0],classOption)] = cap_dict.get((attr_dict[j][0],classOption),0) + column
            else:
                #Getting discrete values by counting
                #Starts with 1 for Laplace fix
                dap_dict[(attr_dict[j][0],column,classOption)] = dap_dict.get((attr_dict[j][0],column,classOption),1) + 1
      
    #Calculating probability by counting for discrete attributes probability   
    for key in dap_dict:
        if len(key)>2:
            dap_dict[key] /= counterClassOptions[(key[-1],)]
        else:
            dap_dict[key] /= len(data)

    #Calculating mean for continuous attributes probability
    #Average of one type of classification based only on that classification
    for key in cap_dict:
        if len(key)>1:
            mean[key] = cap_dict[key] / counterClassOptions[(key[-1],)]

    #Getting column numbers and names of numeric attributes
    numericAttributesColumns = [(i, attItem[0]) for i, attItem in attr_dict.items() if (type(attItem[1]) == str and attItem[1].lower() == 'numeric')]

    #Next two for statements: standard deviation and updating cap_dict
    for line in data:
        #Just for the numeric attributes
        for columnNumber,attName in numericAttributesColumns:
            #Summing squared(value - mean)**2
            squaredDifferences[(attName,line[-1])] = squaredDifferences.get((attName,line[-1]),0) + pow((line[columnNumber]-mean[(attName,line[-1])]),2)

    for key in cap_dict:
        #Sum(squaredDifference/(N-1)) (N is the number of data with that classification, different from the total number of registers)
        std[key] = sqrt(squaredDifferences[key]/(counterClassOptions[(key[-1],)] - 1))
        cap_dict[key] = (mean[key],std[key])
        
    
    return dap_dict, cap_dict

    
#--------------------------------------------------------------------------#
# gauss(x,m,s):                                                            #
# Receives value, mean and standard deviation                              #
# Gaussian probability distribution function                               #
#--------------------------------------------------------------------------#
def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((float(x)-float(m))/float(s))**2)


#--------------------------------------------------------------------------#
# Attribute-value-class probability function                               #
# Returns the value of dap_dict or cap_dict at the given position          #
#--------------------------------------------------------------------------#
def prob(attribute_column,attribute_value,class_value):
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if type(attribute_domain) == str and attribute_domain.lower() == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict.get((attribute_name,attribute_value,class_value),1)


#--------------------------------------------------------------------------#
# Bayesian classification function                                         #
# Calculates and returns the probability of the given instance for the     #
# clasification                                                            #
#--------------------------------------------------------------------------#
def classification(instance):
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
    for (probability,class_value) in probs:
        print('prob[%s] = %.1f%%' % (class_value,probability*100))
    return max(probs)[1]


#--------------------------------------------------------------------------#
# Calling main() function if initialized as a script
#--------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
