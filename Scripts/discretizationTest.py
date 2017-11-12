### Discretization tests ###

import ArffReader as ar
from pprint import *
import re
import csv
import os

def main():

    filesList = [r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\newAbalone.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\bupa.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\pima.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\Ionosphere.arff",
                 #r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\ecoli_replacedName.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\wine_classLast.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\ImageSegmentation_classFirst.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\From Entropy Article\Prontos\glass.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\appendicitis.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\balance.arff",
                 #r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\banana.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\ecoli.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\haberman.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\hayes-roth.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\iris.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\led7digit.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\mammographic.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\page-blocks.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\phoneme.arff",
                 #r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\segment.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\spambase.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\titanic.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\vehicle.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\vowel.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\winequality-white.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\wisconsin.arff",
                 r"C:\Users\gabiiholiveira\Desktop\TCC - AI Research\ARFF\NOVOS\yeast.arff"]
    
                 
    with open("accuracyDiscretizationResults.csv", "w", newline="") as csv_accuracy,open("gmeasureDiscretizationResults.csv", "w", newline="") as csv_gmeasure:
        
        writer_accuracy = csv.writer(csv_accuracy, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer_gmeasure = csv.writer(csv_gmeasure, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        
        header = ["File Name", "No Disc.", "Same Width", "Same Frequency", "Min. Entropy"]
        writer_accuracy.writerow(header)
        writer_gmeasure.writerow(header)
            
        for file in filesList:
            print(file)
            attr, data, errorMsg = ar.readArff(str(file))

            line_accuracy = [os.path.basename(file)]
            line_gmeasure = [os.path.basename(file)]

            
            #No discretization
            attDiscDict = {}
            temp = writeLine(file, attDiscDict, True)
            line_accuracy.append(temp[0])
            line_gmeasure.append(temp[2])

            
            #Same width discretization
            attDiscDict = {}
            for att in attr:
                if(attr[att][-1] == 'numeric' or attr[att][-1] == 'NUMERIC'):
                    attDiscDict[att] = [1,3]

            temp = writeLine(file, attDiscDict, False)
            line_accuracy.append(temp[0])
            line_gmeasure.append(temp[2])


            #Same Frequency discretization
            attDiscDict = {}
            for att in attr:
                if(attr[att][-1] == 'numeric' or attr[att][-1] == 'NUMERIC'):
                    attDiscDict[att] = [2,3]

            temp = writeLine(file, attDiscDict, False)
            line_accuracy.append(temp[0])
            line_gmeasure.append(temp[2])


            #Min Entropy discretization
            attDiscDict = {}
            for att in attr:
                if(attr[att][-1] == 'numeric' or attr[att][-1] == 'NUMERIC'):
                    attDiscDict[att] = [3,3]

            temp = writeLine(file, attDiscDict, False)
            line_accuracy.append(temp[0])
            line_gmeasure.append(temp[2])


            writer_accuracy.writerow(line_accuracy)
            writer_gmeasure.writerow(line_gmeasure)
        
    csv_accuracy.close()
    csv_gmeasure.close()
    return None

def writeLine(file, attDiscDict, regular):

    if not regular:
        ar.startDiscretization(attDiscDict)
        
    result = ar.testClassification()
    result = re.split("\s|\n",result)
    #result[3] result[8] result[13] result[18])

    return [str(result[3]),str(result[8]),str(result[13]),str(result[18])]
#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
