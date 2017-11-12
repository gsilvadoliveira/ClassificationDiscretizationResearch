#################################################################################################################
#   Author:  Gabriela Silva de Oliveira
#    Email:  gsilvadoliveira@gmail.com
#
#   Program:    ClassifierGUI.py
#   Date:       29/03/2017
#   Purpose:    GUI for the ArffReader program
#           
#################################################################################################################

from tkinter import *
from tkinter.filedialog  import *
from tkinter.messagebox import *
from tkinter.ttk import *
import ArffReader as ar
#import ClassifierTester as ct
from pprint import *

#Global variables
attr = {}
data = {}
master1 = Tk() #Choose file
master2 = Tk()
master3 = Tk()
master4 = Tk()
filename = ""
accuracy = 0
userInstance = Entry()
attrListBox = Listbox()
labelErrors = Label()
labelAttName = Label()
labelAttType = Label()
labelAttMean = Label()
labelAttStd = Label()
#userInstance = Entry(master, width=30)
#chooseFileButton = Button(master=master)

def main():
    screenCreation()
    mainMenu()


def screenCreation():
    global filename
    global master1
    global labelFileName
    global attr
    global data
    global attrListBox
    global attrTree
    global labelErrors
    global labelAttName
    global labelAttType
    global master4
    global userInstance
    global attrListBox
    global labelAttMean
    global labelAttStd
    
    #Master 1
    master1.title('NAIVE-BAYES CLASSIFIER')
    
    back = Frame(master=master1, width=700, height=500)

    #CHOOSING FILE
    #Frame
    labelFrameChosenFile = LabelFrame(master=master1, text='File:', width=600, height=60)
    labelFrameChosenFile.pack(fill="both")
    #Button
    openFileButton = Button(master=master1, text='Choose File', command=getFileName)
    openFileButton.place(relx=0.1, rely=0.065, anchor=CENTER)
    #File name
    labelFileName = Label(master=master1, anchor=W, width=90)
    labelFileName.place(relx=0.16, rely=0.065, anchor=W)


    #CHOOSING CLASSIFICATION METHOD
    #Frame
    labelFrameFilter = LabelFrame(master=master1, text='Classification Method:', width=600, height=60)
    labelFrameFilter.pack(fill="both")
    #Option menu
    intialValueFilter = StringVar()
    filterOption = Combobox(master=master1, textvariable=intialValueFilter, width=70)
    filterOption['values'] = ("Regular Nayve-Bayes", "Nayve-Bayes with Discretization")
    filterOption.place(relx=0.046, rely=0.15, anchor=W)


    #ATTRIBUTES BOX
    #Frame
    labelFrameAttributes = LabelFrame(master=master1, text='Attributes:', width=250, height=250)
    labelFrameAttributes.place(relx=0.0, rely=0.6, anchor=SW)
    #ListBox
    attrListBox = Listbox(master=master1, height=10)
    attrListBox.place(relx=0.13, rely=0.25, anchor=N)

    attrListBox.bind('<<ListboxSelect>>', fillLabels)
    
    #SELECTED ATTRIBUTE BOX
    #Frame
    labelFrameSelectedAttribute = LabelFrame(master=master1, text="Selected Attribute", width=420, height=250)
    labelFrameSelectedAttribute.place(relx=0.4, rely=0.6, anchor=SW)
    #Labels
    nameLabel = Label(master=master1, text="Name: ", anchor=W)
    nameLabel.place(relx=0.43, rely=0.28, anchor=SW)
    typeLabel = Label(master=master1, text="Type: ", anchor=W)
    typeLabel.place(relx=0.43, rely=0.33, anchor=SW)
    meanLabel = Label(master=master1, text="Mean: ", anchor=W)
    meanLabel.place(relx=0.43, rely=0.38, anchor=SW)
    stdLabel = Label(master=master1, text="Standard Deviation: ", anchor=W)
    stdLabel.place(relx=0.43, rely=0.43, anchor=SW)
    #Content
    labelAttName = Label(master=master1, text="", anchor=W)
    labelAttName.place(relx=0.5, rely=0.28, anchor=SW)
    labelAttType = Label(master=master1, text="", anchor=W)
    labelAttType.place(relx=0.5, rely=0.33, anchor=SW)
    labelAttMean = Label(master=master1, text="", anchor=W)
    labelAttMean.place(relx=0.5, rely=0.38, anchor=SW)
    labelAttStd = Label(master=master1, text="", anchor=W)
    labelAttStd.place(relx=0.6, rely=0.43, anchor=SW)
    
    #ERROR BOX
    #Frame
    labelFrameErrors = LabelFrame(master=master1, text="Errors on file", width=700, height=150)
    labelFrameErrors.place(relx=0.0, rely=0.85, anchor=SW)
    #Label
    labelErrors = Label(master=master1, anchor=NW, width=70)
    labelErrors.place(relx=0.33, rely=0.65, anchor=N)
    
    #BOTTOM BUTTONS
    #New Instance
    instanceButton = Button(master=master1, text='Enter new instance', command=calculateInstance)
    instanceButton.place(relx=0.30, rely=0.9, anchor=CENTER)

    #Graphs
    #instanceButton = Button(master=master1, text='Generate classification graphs')
    #instanceButton.place(relx=0.35, rely=0.9, anchor=CENTER)

    #Tester
    testButton = Button(master=master1, text='Classification Model Test', command=test)
    testButton.place(relx=0.11, rely=0.9, anchor=CENTER)

    #Exit
    exitButton = Button(master=master1, text='Exit', command=exitGUI)
    exitButton.place(relx=0.9, rely=0.9, anchor=CENTER)
    
    back.pack()

    #Master 2---------------------------------------------------------------------------------------------------------------------------------------


    #Master 3---------------------------------------------------------------------------------------------------------------------------------------


    #Master 4---------------------------------------------------------------------------------------------------------------------------------------    
    master4.title('NAIVE-BAYES CLASSIFIER')

    back = Frame(master=master4, width=470, height=100)

    labelMenu = Label(master=master4, text='NAIVE-BAYES CLASSIFIER', font="DefaultFont 9 underline")
    labelMenu.place(relx=0.5, rely=0.2, anchor=CENTER)
    
    labelMenu = Label(master=master4, text='2. Enter instance to be tested: ')
    labelMenu.place(relx=0.2, rely=0.5, anchor=CENTER)

    userInstance = Entry(master=master4, width=30)
    userInstance.place(relx=0.57, rely=0.5, anchor=CENTER)
    
    okButton = Button(master=master4, text='OK', command=getUserInstance)
    okButton.place(relx=0.87, rely=0.5, anchor=CENTER)

    exitButton = Button(master=master4, text='EXIT', command=master4.withdraw)
    exitButton.place(relx=0.87, rely=0.8, anchor=CENTER)
    
    back.pack()
    master4.deiconify()

    #Hiding all screens
    master1.withdraw()
    master2.withdraw()
    master3.withdraw()
    master4.withdraw()

    
def mainMenu():
    global master1
    global master2
    global master3
    global master4
    
    master1.deiconify()
    master2.withdraw()
    master3.withdraw()
    master4.withdraw()
    
    
def calculateInstance():
    global master4
    global userInstance
    global attrListBox
    
    if(attrListBox.size() == 0):
        messagebox.showwarning("Warning!", "Open a file before calculate a new instance.")       
    else:
        master4.deiconify()
    
def fillLabels(e):
    global attrListBox
    global labelAttName
    global labelAttType
    global attr
    global labelAttMean
    global labelAttStd
    #global ar.cap_dict

    #probability(0)
    labelAttName.config(text=attrListBox.get(attrListBox.curselection()))
    currentSelection = (attrListBox.curselection()[0])

    if(attr[currentSelection][len(attr[currentSelection])-1] == 'numeric'):
        labelAttType.config(text='Numeric')
        labelAttMean.config(text='')
        labelAttStd.config(text='')
    else:
        labelAttType.config(text="Discrete")
        labelAttMean.config(text='-')
        labelAttStd.config(text='-')
        
def backMainMenu():
    global master1
    global master2
    global master3
    global master4

    master2.withdraw()
    master3.withdraw()
    master4.withdraw()
    master1.deiconify()
    
def getFileName():
    global filename
    global master1
    global labelFileName
    global attr
    global data
    global attrListBox
    global attrTree
    global labelErrors
    global labelAttName
    global labelAttType
    global master4
    #global userInstance
    global attrListBox
    global labelAttMean
    global labelAttStd
    
    attr = {}
    data = {}
    filename = ""
    accuracy = 0
    #userInstance = Entry()

    filename = askopenfilename()

    attrListBox.delete(0,END)
    labelFileName.config(text=filename)
    attr, data, errorMsg = ar.readArff(filename)
    

    if(len(errorMsg) > 0):
        labelErrors.config(text=errorMsg)
    else:
        labelErrors.config(text="No errors on this file.")
    for i in attr:
        attrListBox.insert(END, attr[i][0].title())
        
def getUserInstance():
    global userInstance
    global master4
    ar.probability(0)
    
    if(len(userInstance.get()) == 0):
        messagebox.showwarning("Warning!", "Please, enter an instance before click 'OK'.")
        master4.deiconify()
    else:    
        instance = userInstance.get()
        userInstance.delete(0, END)
        result = ar.classification(instance.lower().replace(' ','').split(','))
        messagebox.showinfo('Result: ', result[1], parent=master4)
    
def test():
    global accuracy
    accuracy = ar.testClassification()
    
def exitGUI():
    global master1
    global master2
    global master3
    global master4
    
    master2.destroy()
    master3.destroy()
    master4.destroy()
    master1.destroy()
    sys.exit()


#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()



    
