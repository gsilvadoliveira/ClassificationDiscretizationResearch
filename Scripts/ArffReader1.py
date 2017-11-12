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
from operator import *
from functools import reduce
import sys

def main():
    #
    # Gets the file from the user,
    # calls the function that reads the files
    # and prints the returns on screen
    #

    global attr_dict
    global dap_dict
    global cap_dict

    dap_dict = {}
    attr_dict = {}
    cap_dict = {}
    filename = input('Enter file path: ')
    attr_dict, cap_dict, dap_dict = readArff(filename)
    
    print("\nAttribute(s):")
    for key in attr_dict:
        print('attr_dict[' + str(key) + '] = ' + str(attr_dict[key]))
    print()
    for key in dap_dict:
        print('dap_dict[' + str(key) + '] = ' + str(dap_dict[key]))

    print()
    for key in cap_dict:
        print('cap_dict[' + str(key) + '] = ' + str(cap_dict[key]))
        
    instance = ['sunny',66,90,'true']

    print('\nPrediction: %s = "%s"'
          % (attr_dict[len(attr_dict)-1][0], classification(instance)))

def readArff(filename):
    #
    # Read the given ARFF file line by line.
    # return: dictionaries with the content of the ARFF file
    #
    
    #Variables
    global classAtt
    global attributes
    global data    
    global classPossibilities
    global dap_dict
    global cap_dict
    
    dap_dict = {}
    cap_dict = {}
    classAtt = ""
    classPossibilities = ()
    attributes = {}
    data = {}

    attNumber = 0
    keyCount = 0
    keyDict = 0
    relation = ""
    
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

                    attributes[attNumber] = (line[0], line[1])
                    attNumber += 1
                    
        classAtt = attributes[len(attributes) - 1][0]
        classPossibilities = attributes[len(attributes) - 1][1]

        #Checking if class attributes are strings
        for option in classPossibilities:
            try:
                float(option)
                sys.exit('Classifications attributes are not strings')
            except ValueError:
                continue
        
        #Read lines of DATA
        for line in arffFile:
            line = line.replace('\n','')
            if(len(line) > 0):
                #Break the line by commas
                currentLine = line.split(',')
                
                for j in range(len(currentLine)):
                    if type(attributes[j][len(attributes[j])-1]) != list and (attributes[j][len(attributes[j])-1].upper()) == 'NUMERIC':
                        cap_dict[keyCount] = (attributes[j][0].strip(), float(currentLine[j]), currentLine[len(currentLine)-1].strip())
                        keyCount += 1
                        
                    else:
                        if(currentLine[j] == currentLine[len(currentLine)-1]):
                            dap_dict[keyDict] = (attributes[j][0], currentLine[j].strip())
                        else:
                            dap_dict[keyDict] = (attributes[j][0], currentLine[j].strip(), currentLine[len(currentLine)-1].strip())
                        keyDict += 1
    
    cap_dict = probabilityCont(attributes, cap_dict)
    dap_dict = probabilityDisc(attributes, dap_dict)
    
    #Creating keys for missing values
#for option in classPossibilities:
#    for i in range(len(attr_dict)):

#        #If it is not a classification attribute
#        if(i != len(attr_dict)-1):

#            #Discrete attributes
#            if(type(attr_dict[i][-1]) == list):                                      
#                for j in range(len(attr_dict[i][-1])):
#                    #key = (att_name, att_value, classification)
#                    key = (attr_dict[i][0], attr_dict[i][-1][j], option)
#                    #Starts with 1 for Laplace fix
#                    dap_dict[key] = dap_dict.get((key),1)

#            #Numeric attributes
#            elif(type(attr_dict[i][-1]) == str and attr_dict[i][-1].lower() == 'numeric'):
#                #key = (att_name, classification)
#                key = (attr_dict[i][0], option)
#                cap_dict[key] = cap_dict.get((key),0)

		#Adding classfication attributes to dap_dict        
#        else:
#            key = (attr_dict[i][0], option)
#            dap_dict[key] = dap_dict.get((key),0)

    return attributes, cap_dict, dap_dict



def probabilityCont(att, data):

    mean = {}
    std = {}
    cap_dict = {}
    counter = {}
    
    for choice in classPossibilities:
        for z in range(len(data)):
            key = (data[z][0],choice)
            mean[key] = 0
            std[key] = 0
            counter[key] = 0

    for possibility in classPossibilities:
        for j in range(len(att)-1):
            for k in range(len(data)):
                if(data[k][0] == att[j][0] and data[k][2] == possibility):
                    counter[(data[k][0],possibility)] += 1
                    mean[(data[k][0],possibility)] += float(data[k][1])
                
    for key in mean:
        mean[key] = mean[key]/counter[key]

    for possibility in classPossibilities:
        for j in range(len(att)-1):
            for k in range(len(data)):
                if(data[k][0] == att[j][0] and data[k][2] == possibility):
                    std[(data[k][0],possibility)] += pow(mean[(data[k][0],possibility)] - float(data[k][1]),2)

    for key in std:
        std[key] = sqrt(std[key]/(counter[key]-1))

    for key in mean:
        mean[key] = round(mean[key],4)
        std[key] = round(std[key],4)
        cap_dict[key] = (mean[key],std[key])
        
    return cap_dict



def probabilityDisc(att, data):
    frequency = {}
    counter = {}
    probability = {}

    #print(data)
    for choice in classPossibilities:
        key = (att[len(att) - 1][0], choice)
        frequency[key] = 0

        
    for i in range(0, len(att) - 1):
        if not (type(att[i][1]) == str and att[i][1].upper() == 'NUMERIC'):
            possibilities = att[i][1]
            #print(possibilities)
            for item in possibilities:
                for choice in classPossibilities:
                    key = (att[i][0],item,choice)
                    frequency[key] = 0
                    
    #attribute name
    for j in range(len(att)):
        #data dictionary
        for k in range(len(data)):
            if(data[k][0] == att[j][0]):
                #attribute possible values
                for l in range(len(att[j][1])):
                    for possibility in classPossibilities:
                        if(len(data[k])>2 and data[k][1] == att[j][1][l] and data[k][2] == possibility):
                            frequency[data[k][0],data[k][1],data[k][2]] += 1

    for possibility in classPossibilities:
        for z in range(len(data)):
            if(len(data[k]) == 2 and data[z][0] == att[len(att)-1][0] and data[z][len(data[z])-1] == possibility):
                frequency[att[len(att)-1][0],possibility] += 1

    
    
    for key in frequency:
        for possibility in classPossibilities:
            if(len(key) > 2 and key[len(key)-1] == possibility):
                probability[key] = frequency[key]/frequency[(att[len(att)-1][0],possibility)]
    total = 0
        
    for possibility in classPossibilities:
        total += frequency[(att[len(att)-1][0],possibility)]
    
    for possibility in classPossibilities:
        probability[(att[len(att)-1][0],possibility)] = frequency[(att[len(att)-1][0],possibility)]/total

    for key in probability:
        probability[key] = probability[key]
    
    return probability


    

############################################################################
# Gaussian probability distribution function                               #
############################################################################

def gauss(x,m,s): return 1/(s * sqrt(2*pi)) * exp(-1/2 * ((x-m)/s)**2)


############################################################################
# Attribute-value-class probability function                               #
############################################################################

def prob(attribute_column,attribute_value,class_value):
    (attribute_name, attribute_domain) = attr_dict[attribute_column]
    if attribute_domain == 'numeric':
        (mean, standard_deviation) = cap_dict[(attribute_name,class_value)]
        return gauss(attribute_value,mean,standard_deviation)
    else:
        return dap_dict[(attribute_name,attribute_value,class_value)]


############################################################################
# Bayesian classification function                                         #
############################################################################

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

def printing(d):
    #
    # Prints a dictionary on the screen
    #
    for i in range(0, len(d)):
        print(str(i) + ': ' + str(d[i]))

    print()

    return None


#--------------------------------------------------------------------------#
# Calling main() function if initialized as a script
#--------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
