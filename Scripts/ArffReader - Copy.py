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
    relation, attr_dict, data = readArff(filename)
    
    print("\nAttribute(s):")
    printing(attributes)

    print("\nData:")
    printing(data)

    
    #dap_dict = probabilityDisc(attr_dict, data, frequencyDisc(attr_dict, data))
    #cap_dict = probabilityCont(attr_dict, data)

    instance = input('\nEnter instance to be tested: ')
    classification(instance.split(','))
    
def readArff(filename):
    #
    # Read the given ARFF file line by line.
    # return: dictionaries with the content of the ARFF file
    #
    
    #Variables
    attNumber = 0
    keyData = 0
    keyCount = 0
    keyDict = 0
    relation = ""
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
        
        #Read lines of DATA
        for line in arffFile:
            line = line.replace('\n','')
            if(len(line) > 0):
                #Break the line by commas
                currentLine = line.split(',')
                
                #for j in range(len(currentLine) - 1):
                    #print(j)
                    #print((attributes[j][0], currentLine[j], currentLine[len(currentLine)-1]))
                    #((j != len(attributes)-1) and 
                #    if(attributes[j][len(attributes[j])-1].upper()) == 'NUMERIC':
                        #print((attributes[j][len(attributes[j])-1]))
                #        cap_dict[keyCount] = (attributes[j][0], currentLine[j], currentLine[len(currentLine)-1])
                #        keyCount += 1
                #    else:
                        #print((attributes[j][len(attributes[j])-1]))
                #        dap_dict[keyDict] = (attributes[j][0], currentLine[j], currentLine[len(currentLine)-1])
                #        keyDict += 1
                   
                    
                #Building data dictionary
                temp = []
                for word in currentLine:
                    temp.append(word.strip())
                data[keyData] = temp
                keyData += 1

    #for f in cap_dict:
    #    print('cap_dict[' + str(f) + '] = ' + str(cap_dict[f]))

    #print()
    #for f in dap_dict:
    #    print('dap_dict[' + str(f) + '] = ' + str(dap_dict[f]))
                
    #dap_dict = probabilityDisc(attributes, dap_dict, frequencyDisc(attributes, dap_dict))
    #cap_dict = probabilityCont(attributes, cap_dict)
    
    
    
    #print(dap_dict)
    #print(cap_dict)
    #
    #
    
    #Returns information from the file
    return relation, attributes, data
    #return relation, attributes, dap_dict, cap_dict



def frequencyDisc(att, data):
    frequency = {}
    
    #Building frequency dictionary
    for choice in classPossibilities:
        key = (att[len(att) - 1][0], choice)
        frequency[key] = 0
        
    for i in range(0, len(att) - 1):
        possibilities = att[i][1]
        print(possibilities)
        for item in possibilities:
            for choice in classPossibilities:
                key = (att[i][0],item,choice)
                frequency[key] = 0

    #print(frequency)
    #Counting frequencies
    #print()
    #print(data)
    for k in range(len(data)):
        for j in range(len(att)):
            print((k,j))
            if(j == len(att)-1):
                key = (att[j][0],data[k][len(data[k]) - 1])
            else:
                print(data[k])
                key = (att[j][0], data[k][j], data[k][len(data[k]) - 1])
            if(key in frequency):
                frequency[key] += 1
            
            
            
    #Printing frequencies
    #for f in frequency:
    #    print('frequency[' + str(f) + '] = ' + str(frequency[f]))

    return frequency



def probabilityDisc(att, data, frequency):
    #print(data)
    #key model: attName, attValue, class
    probability = {}
    
    #classification = att[len(att)][1].replace('{','').replace('}','').replace(' ','').split(',')

    #Building probability dictionary
    for key in frequency:
        probability[key] = 0

    #Probabilities
    for pKey in probability:
        part = 0
        total = 0
        part = frequency[pKey]
        for i in range(len(data)):
            if(pKey[-1] == data[i][len(data[i])-1]):
                total += 1

        probability[pKey] = round(part/total,2)

    #Probability of the classification attributes
    for j in range(len(classPossibilities)):
        cKey = (att[len(att) - 1][0],classPossibilities[j])
        if cKey in probability:
            probability[cKey] = round(frequency[cKey]/len(data),2)

        
    #Printing frequencies
    for p in probability:
        print('probability[' + str(p) + '] = ' + str(probability[p]))

    return probability



def probabilityCont(att, data):
    #print(data)
    #print(att)
    mean = {}
    std = {}
    cap_dict = {}
    for i in range(0, len(att)):
        for choice in classPossibilities:
            key = (att[i][0],choice)
            mean[key] = 0
            std[key] = 0

    print(classPossibilities)
    for choice in classPossibilities:
        for j in range(len(att)):
            counter = 0
            for k in range(len(data)):
                if(data[k][len(data[k])-1] == choice):
                    counter += 1
                    if(j == len(att)-1):
                        mean[att[j][0],choice] +=1
                    else:
                        mean[att[j][0],choice] += float(data[k][j])
            if(j == len(att)-1):
                mean[att[j][0],choice] = round((mean[att[j][0],choice]/len(data)),2)
            else:
                mean[att[j][0],choice] = round((mean[att[j][0],choice]/counter),2)

    for choice in classPossibilities:       
        for j in range(len(att) - 1):
            counter = 0
            for k in range(len(data)):
                if(data[k][len(data[k])-1] == choice):
                    counter += 1
                    std[att[j][0],choice] += pow((float(data[k][j]) - mean[att[j][0],choice]),2)

            std[att[j][0],choice] = std[att[j][0],choice]/counter
            std[att[j][0],choice] = round(sqrt(std[att[j][0],choice]),5)
            
    for key in mean:
        #print((mean[key],std[key]))
        cap_dict[key] = (mean[key],std[key])
        print(str(key) + ": " + str(cap_dict[key]))
        
    return cap_dict


    
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
