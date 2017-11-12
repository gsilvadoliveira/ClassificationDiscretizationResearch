### File Editor ###

### Discretization tests ###

from pprint import *
import re
import csv
import os

def main():
    original_file= open('ImageSegmentationData.arff','r')# r when we only wanna read file
    revised_file = open('ImageSegmentationNewData.arff','w')# w when u wanna write sth on the file

    for line in original_file:
        line = line.replace(" ","")
        l = re.split(',|\n',line)
        del l[-1]
        l.append(l.pop(0))

        #for i,item in enumerate(l):
        #    if item[0] == '.':
        #        l[i] = "0" + l[i]
                
        newLine = ','.join(l) + '\n'

        revised_file.write(newLine)#for writing your new data

    original_file.close()
    revised_file.close()

        
#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()
