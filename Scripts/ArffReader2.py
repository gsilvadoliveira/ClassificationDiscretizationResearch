##########################################################################
#   Author:  Gabriela Silva de Oliveira
#    Email:  gsilvadoliveira@gmail.com
#
#   Program:  ArffReader2.py
#
#   Purpose:  Read ARFF files and store the data on internal variables
#           
##########################################################################

from pyparsing import *

def main():
    filename = input('Enter file path: ')
    result = openArff(filename)
    

def openArff(filename):
    keyAtt = 1
    keyData = 1
    relation = ''
    attributes = {}
    data = {}


    infoRule = ZeroOrMore(Word("@" + alphas)) + ZeroOrMore(Word(alphas)) + ZeroOrMore(Word("{" + alphanums + "}"))
    #PROBLEMAS pyparsing:
    #   - ZeroOrMore funciona apenas uma vez
    #   - alphanum nao lendo array de classes
    #   - regex teria que ser criado para todas as variaveis possiveis
        
    #DÚVIDA: attibute data type, tratar como string?
    
    with open(filename, 'r') as arffFile:

        #Reading file
        for line in arffFile:
            
            #Skip blank lines and comments
            if len(line.split()) > 0 and line.split()[0] != "%":

                currentLine = infoRule.parseString(line)
                if(currentLine[0] == '@RELATION' or currentLine[0] == '@relation'):
                    relation = currentLine[1]

                elif(currentLine[0] == '@ATTRIBUTE' or currentLine[0] == '@attribute'):
                    temp = []
                    temp.append(currentLine[1])
                    temp.append(currentLine[2])
                    attributes[keyAtt] = temp
                    keyAtt += 1

                #Data
                elif(currentLine[0] == '@DATA' or currentLine[0] == '@data'):                 
                    for line in arffFile:
                        currentLine = commaSeparatedList.parseString(line)
                        temp = []
                        
                        for value in currentLine:
                            temp.append(value)
                        data[keyData] = temp
                        keyData += 1
                        
        print("Relation: " + relation)

        print("\n" + "Atributtes:")
        for i in range(1, keyAtt):
            print(attributes[i])

        print("\n" + "Data:")
        for j in range(1, keyData):
            print(data[j])

        print()

    return relation, attributes, data


#--------------------------------------------------------------------------#
# Calling main() function if initialized as a script
#--------------------------------------------------------------------------#
if __name__ == "__main__":
    main()



                
