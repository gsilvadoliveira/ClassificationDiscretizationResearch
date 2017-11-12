################################################################################################################
#   Authors:  Gabriela Silva de Oliveira, Silvio do Lago Pereira
#   Emails:  gsilvadoliveira@gmail.com, slago@fatecsp.br
#
#   Program:    ClassifierGUI.py
#   Date:       29/03/2017
#   Purpose:    Interface for the Bayesian Classifyer
#           
#################################################################################################################

from tkinter import *
from tkinter.filedialog  import *
from tkinter.messagebox import *
from tkinter.ttk import *
from tktable import *
import ArffReader as ar
from pprint import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab


#Global variables
attr = {}
data = {}
dap_dict = {}
dap_counting = {}
cap_dict = {}
counterClassOptions = {}
master1 = Tk()
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
resultLabel = Label()
meanLabel = Label()
stdLabel = Label()
tree = Treeview()
discAttList = {}
intervalOpsList = []
classificationMethodsList = []
currentSelection = -1
instanceButton = Button()
testButton = Button()
graphButton = Button()
discretizeButton = Button()
    
#----------------------------------------------------------
# Initiate the program
# Call function that creates screens and the main menu
# ---------------------------------------------------------
def main():
    screenCreation()
    mainMenu()

#----------------------------------------------------------
# Creates all the screens used on the program
# ---------------------------------------------------------
def screenCreation():
    global filename
    global master1
    global master2
    global labelFileName
    global attr
    global attrListBox
    global attrTree
    global discButton
    global discButtonState
    global labelErrors
    global labelAttName
    global labelAttType
    global master4
    global userInstance
    global attrListBox
    global meanLabel
    global stdLabel
    global labelAttMean
    global labelAttStd
    global resultLabel
    global tree
    global nIntervals
    global nIntervalsLabel
    global intervalOpsList
    global currentIntervalValue
    global intialValueFilter
    global filterOption
    global classificationMethodsList
    global instanceButton
    global testButton
    global graphButton
    global discretizeButton
    
    style = Style()
    
    #Master 1
    master1.title('NAIVE-BAYES CLASSIFIER')
    
    back = Frame(master=master1, width=700, height=500)

    #CHOOSING FILE
    #Frame
    labelFrameChosenFile = LabelFrame(master=master1, text='File:', width=600, height=60)
    labelFrameChosenFile.pack(fill="both")
    #Button
    openFileButton = Button(master=master1, text='Choose File', command=getFileName)
    openFileButton.place(relx=0.072, rely=0.065, anchor=CENTER)
    #File name
    labelFileName = Label(master=master1, anchor=W, width=90)
    labelFileName.place(relx=0.16, rely=0.065, anchor=W)


    #ATTRIBUTES BOX
    #Frame
    labelFrameAttributes = LabelFrame(master=master1, text='Attributes:', width=270, height=220)
    labelFrameAttributes.place(relx=0.0, rely=0.5, anchor=SW)
    #ListBox
    attrListBox = Listbox(master=master1, width=30, height=10, borderwidth=0, highlightthickness=0)
    attrListBox.place(relx=0.15, rely=0.16, anchor=N)

    attrListBox.bind('<<ListboxSelect>>', fillLabels)

    attScrollbar = Scrollbar(master1, orient="vertical", command=attrListBox.yview)
    attScrollbar.place(relx=0.255, rely=0.4491, anchor=SW, height=162)
    attrListBox.configure(yscrollcommand=attScrollbar.set)
   
    
    #SELECTED ATTRIBUTE BOX
    #Frame
    labelFrameSelectedAttribute = LabelFrame(master=master1, text="Selected Attribute:", width=430, height=220)
    labelFrameSelectedAttribute.place(relx=0.35, rely=0.5, anchor=SW)
    
    #TABLE
    tree = Treeview(master1, height=7, columns=("Type", "Class","Count","Prob"))
    tree['show']='headings'
    tree.heading('#1', text='', anchor=CENTER)
    tree.column('#1', width=90, anchor=CENTER)
    tree.heading('#2', text='', anchor=CENTER)
    tree.column('#2', width=90, anchor=CENTER)
    tree.heading('#3', text='', anchor=CENTER)
    tree.column('#3', width=90, anchor=CENTER)
    tree.heading('#4', text='', anchor=CENTER)
    tree.column('#4', width=90, anchor=CENTER)
    
    tree.place(relx=0.4, rely=0.45, anchor=SW)

    treeScrollbar = Scrollbar(master1, orient="vertical", command=tree.yview)
    treeScrollbar.place(relx=0.89, rely=0.4491, anchor=SW, height=163)
    
    tree.configure(yscrollcommand=treeScrollbar.set)
    style.layout("Treeview",[('Treeview.treearea', {'sticky':'nswe'})])

    #CHOOSING CLASSIFICATION METHOD
    #Frame
    labelFrameFilter = LabelFrame(master=master1, text='Classification Method for this Attribute:', width=700, height=60)
    labelFrameFilter.pack(fill="both")
    labelFrameFilter.place(relx=0.0, rely=0.56, anchor=W)
    
    #Option menu
    intialValueFilter = StringVar()
    classificationMethodsList = ["Regular Naive-Bayes", "Naive-Bayes with Discretization by Same Width", "Naive-Bayes with Discretization by Same Frequency", "Naive-Bayes with Discretization by Minimum Entropy"]
    filterOption = OptionMenu(master1, intialValueFilter, "Regular Naive-Bayes", *classificationMethodsList, command=discOptionUp)
    filterOption.place(relx=0.0, rely=0.56, anchor=W)
    filterOption.configure(state="disabled")
    
    #DISCRETIZATION
    #Number of intervals
    nIntervalsLabel = Label(master=master1, width=90, text="Enter number of intervals: ")
    nIntervalsLabel.place(relx=0.5, rely=0.545)
    nIntervalsLabel.configure(state='disabled')

    intervalOpsList = []
    currentIntervalValue = StringVar()
    nIntervals = OptionMenu(master1, currentIntervalValue, "", *intervalOpsList, command=getNumberOfIntervals)
    nIntervals.place(relx=0.72, rely=0.545)
    nIntervals.configure(state='disabled')

    #Discretize button
    discretizeButton = Button(master=master1, text='Discretize', command=discretize)
    discretizeButton.place(relx=0.8, rely=0.545)
    
    #ERROR BOX
    #Frame
    labelFrameErrors = LabelFrame(master=master1, text="Errors on file", width=700, height=150)
    labelFrameErrors.place(relx=0.0, rely=0.90, anchor=SW)
    #Label
    labelErrors = Label(master=master1, anchor=NW, width=70)
    labelErrors.place(relx=0.33, rely=0.67, anchor=N)
    
    #BOTTOM BUTTONS
    #New Instance
    instanceButton = Button(master=master1, text='Enter new instance', command=calculateInstance)
    instanceButton.place(relx=0.30, rely=0.95, anchor=CENTER)

    #Graphs
    graphButton = Button(master=master1, text='Generate Data Graphs', command=generateGraphics)
    graphButton.place(relx=0.475, rely=0.95, anchor=CENTER)

    #Tester
    testButton = Button(master=master1, text='Classification Model Test', command=test)
    testButton.place(relx=0.11, rely=0.95, anchor=CENTER)

    #Exit
    exitButton = Button(master=master1, text='Exit', command=exitGUI)
    exitButton.place(relx=0.9, rely=0.95, anchor=CENTER)
  
    master1.protocol('WM_DELETE_WINDOW', exitGUI)

    discretizeButton.configure(state="disabled")
    instanceButton.configure(state="disabled")
    testButton.configure(state="disabled")
    graphButton.configure(state="disabled")
    
    back.pack()

    #Master 2---------------------------------------------------------------------------------------------------------------------------------------
    master2.title('Accuracy and G-Measure Test')
    back = Frame(master=master2, width=470, height=150)

    #Result
    #Frame
    labelFrameAccuracyTest = LabelFrame(master=master2, text="Result", width=420, height=130)
    labelFrameAccuracyTest.place(relx=0.05, rely=0.05)
    #Label
    resultLabel = Label(master=master2, text='Calculating.....')
    resultLabel.place(relx=0.07, rely=0.2)

    master2.protocol('WM_DELETE_WINDOW', master2.withdraw)
    back.pack()
    
    #Master 3---------------------------------------------------------------------------------------------------------------------------------------


    #Master 4---------------------------------------------------------------------------------------------------------------------------------------    
    master4.title('New Classification')

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
    
    master4.protocol('WM_DELETE_WINDOW', master4.withdraw)
    master4.bind('<Return>', getUserInstance)

    back.pack()

    #Hiding all screens
    master1.withdraw()
    master2.withdraw()
    master3.withdraw()
    master4.withdraw()

    return None
#----------------------------------------------------------
# Shows the main screen
# ---------------------------------------------------------
def mainMenu():
    global master1
    global master2
    global master3
    global master4
    
    master1.deiconify()
    master2.withdraw()
    master3.withdraw()
    master4.withdraw()

    return None
#----------------------------------------------------------
# Gets the data file entered by the user, reads it, shows
# discretization options and calculate its probabilities
# ---------------------------------------------------------
def getFileName():
    global filename
    global labelFileName
    global attr
    global data
    global attrListBox
    global tree
    global labelErrors
    global attrListBox
    global dap_dict
    global dap_counting
    global cap_dict
    global counterClassOptions
    global intervalOpsList
    global nIntervals
    global discAttList
    global currentIntervalValue
    global intialValueFilter
    global instanceButton
    global testButton
    global graphButton

    
    maxIntervals = 11
    dap_dict = {}
    dap_counting = {}
    cap_dict = {}
    counterClassOptions = {}
    attr = {}
    data = {}
    tree.delete(*tree.get_children())
    filename = ""
    accuracy = 0
    
    attrListBox.delete(0,END)
    filename = askopenfilename()
    
    if(len(filename) > 0):
        labelFileName.config(text=filename)
        attr, data, errorMsg = ar.readArff(filename)
        
        if(len(errorMsg) > 0):
            labelErrors.config(text=errorMsg)
        else:
            labelErrors.config(text="No errors on this file.")
        
        for i in attr:
            attrListBox.insert(END, attr[i][0])

        intervalOpsList = range(1,maxIntervals)
        
        nIntervals.set_menu("",*intervalOpsList)
        currentIntervalValue.set("")
        discAttList = {}
        intialValueFilter.set("Regular Naive-Bayes")

        dap_dict, dap_counting, cap_dict, counterClassOptions = ar.probability(data)

    instanceButton.configure(state="enable")
    testButton.configure(state="enable")
    graphButton.configure(state="enable")
    
    return None

#----------------------------------------------------------
# Fill the properties of the attributes on the main screen
# ---------------------------------------------------------
def fillLabels(e):
    global data
    global attrListBox
    global labelAttName
    global labelAttType
    global meanLabel
    global stdLabel
    global attr
    global labelAttMean
    global labelAttStd
    global counterClassOptions
    global tree
    global discButtion
    global discButtonState
    global discAttList
    global currentSelection
    global intervalOpsList
    global currentIntervalValue
    global nIntervals
    global nIntervalsLabel
    global intialValueFilter
    global classificationMethodsList

    
    disc, cont = ar.displayProbabilities(attr,data)
    
    if(len(attrListBox.curselection()) > 0):
        labelAttName.config(text=attrListBox.get(attrListBox.curselection()))
        currentSelection = (attrListBox.curselection()[0])
        mean = 0
        std = 0

        tree.delete(*tree.get_children())
        tree.heading('#1', text='Type')

        #Numeric attributes
        if(attr[currentSelection][len(attr[currentSelection])-1] == 'numeric'):
            filterOption.configure(state='enable')
            tree.column('#1', width=90, anchor=CENTER)
            tree.heading('#2', text='Mean')
            tree.heading('#3', text='Std. Dev.')
            tree.heading('#4', text='')
            
            tree.insert('', 'end', values=('Numeric',round(cont[currentSelection][0],2),round(cont[currentSelection][1],2)))
    
            if currentSelection in discAttList:
                intialValueFilter.set(classificationMethodsList[discAttList[currentSelection][0]])
                currentIntervalValue.set(discAttList[currentSelection][-1])
            else:
                intialValueFilter.set(classificationMethodsList[0])
                currentIntervalValue.set("")
                
            
        #Discrete attributes    
        else:
            if (currentSelection in discAttList):
                discretizeButton.configure(state="enable")
                filterOption.configure(state='enable')
                currentIntervalValue.set(discAttList[currentSelection][-1])
                intialValueFilter.set(classificationMethodsList[discAttList[currentSelection][0]])
            else:
                discretizeButton.configure(state="disabled")
                currentIntervalValue.set("")
                intialValueFilter.set(classificationMethodsList[0])
                filterOption.configure(state='disabled')
            
            tree.heading('#2', text='Domain')
            tree.heading('#3', text='Count.')
            tree.heading('#4', text='Prob.')
            
            for item in disc:
                if(item[0] == currentSelection):
                    count = disc[item][0]
                    prob = disc[item][1]
                    if not(tree.get_children()):
                        if (currentSelection in discAttList):
                            tree.column('#1', width=110, anchor=CENTER)
                            tree.column('#2', width=80, anchor=CENTER)
                            tree.column('#3', width=80, anchor=CENTER)
                            tree.column('#4', width=80, anchor=CENTER)

                            method = ""
                            #print(intialValueFilter.get())
                            
                            if(intialValueFilter.get() == classificationMethodsList[1]):
                                method = "Same Width"
                            elif(intialValueFilter.get() == classificationMethodsList[2]):
                                method = "Same Frequency"
                            elif(intialValueFilter.get() == classificationMethodsList[3]):
                                method = "Min. Entropy"
                            else:
                                method = "Naive-Bayes"
                                
                            tree.insert('', 'end', values=(method,item[1],count,round(prob,2)))
                        else:
                            tree.column('#1', width=90, anchor=CENTER)
                            tree.insert('', 'end', values=('Discrete',item[1],count,round(prob,2)))
                    else:
                        tree.insert('', 'end', values=('',item[1],count,round(prob,2)))


        if(intialValueFilter.get() == classificationMethodsList[0] or intialValueFilter.get() == classificationMethodsList[3]):
            nIntervals.configure(state='disabled')
            nIntervalsLabel.configure(state='disabled')
        else:
            nIntervals.configure(state='enable')
            nIntervalsLabel.configure(state='enable')
            
        master1.update()

    return None

#------------------------------------------------------
# Gets the discretization method chosen by the user
#------------------------------------------------------
def discOptionUp(e):
    global master1
    global intialValueFilter
    global nIntervals
    global nIntervalsLabel
    #global discButton
    global discButtonState
    global currentSelection
    global attr
    global data
    global currentIntervalValue
    global discAttList
    global discretizeButton

    data, attr = ar.cleanData(currentSelection)
    currentIntervalValue.set("")
    
    if(len(attr) > 0 and len(data) > 0):
        
        if(intialValueFilter.get() == "Regular Naive-Bayes"):
            if currentSelection in discAttList:
                discAttList.pop(currentSelection, None)
            discretizeButton.configure(state="disabled")
            nIntervals.configure(state='disabled')
            nIntervalsLabel.configure(state='disabled')
            
            fillLabels(None)
            
        else:
            if(currentSelection > -1 and (attr[currentSelection][len(attr[currentSelection])-1] == 'numeric' or currentSelection in discAttList)):                
                if(intialValueFilter.get() == "Naive-Bayes with Discretization by Minimum Entropy"):
                    currentIntervalValue.set("-")
                    nIntervals.configure(state='disabled')
                    discretizeButton.configure(state="enable")
                    #getNumberOfIntervals(None)
                else:
                    nIntervals.configure(state='enable')
                    nIntervalsLabel.configure(state='enable')
                    currentIntervalValue.set("")
    
    master1.update()

    return None


#------------------------------------------------------
# Gets the number of intervals chosen by the user and
# calls the discretization function
#------------------------------------------------------
def getNumberOfIntervals(e):
    discretizeButton.configure(state="enable")

    return None

def discretize():
    global intialValueFilter
    global classificationMethodsList
    global nIntervals
    global nIntervalsLabel
    global currentSelection
    global attr
    global data
    global currentIntervalValue
    global discretizeButton
    discAttList[currentSelection] = [classificationMethodsList.index(intialValueFilter.get()), currentIntervalValue.get()]

    data, attr = ar.startDiscretization(discAttList)
    
    if(len(attr) > 0 and len(data) > 0):
        fillLabels(None)

    return None


#------------------------------------------------------
# Checks if there's an open file before calculating
# a new instance
#------------------------------------------------------
def calculateInstance():
    global master4
    global attrListBox
    global userInstance
    
    if(attrListBox.size() == 0):
        messagebox.showwarning("Warning!", "Open a file before calculate a new instance.")       
    else:
        master4.deiconify()
        messagebox.showinfo("Warning!", "Enter the values separated by commas (,).", parent=userInstance)

    return None

#------------------------------------------------------
# Checks consistence of entered instance, calculate
# probabilities and classify the new instance
#------------------------------------------------------
def getUserInstance(*e):
    global userInstance
    global master4
    global attr
    global data
    global intialValueFilter
    global classificationMethodsList
    global intialValueFilter
    
    ar.probability(data)
    result=''
    message=''
    instance=''
    
    if(len(userInstance.get()) == 0):
        messagebox.showwarning("Warning!", "Please, enter values before clicking 'OK'.", parent=master4)

    else:    
        instance = userInstance.get()
        userInstance.delete(0, END)

        instance = ar.discreteInstance(instance, classificationMethodsList.index(intialValueFilter.get()))
        
        if ar.consistData(attr,instance):
            result = ar.classification(instance)
            message = 'Classification: ' + result[0] + '\n\nProbability: \n' + result[1]
            messagebox.showinfo('Result', message, parent=master4)
        else:
            messagebox.showerror("Error!", "Please enter valid values.", parent=master4)

    return None

#----------------------------------------------
# Calls the classification test function
#----------------------------------------------
def test():
    global resultLabel
    global master2
    
    accuracy = ''
    
    if(attrListBox.size() == 0):
        messagebox.showwarning("Warning!", "Open a file before making an Accuracy Test.")       
    else:
        master2.deiconify()   
        resultLabel.config(text='Calculating results... Please wait.')
        master2.update()
        accuracy = ar.testClassification()         
        resultLabel.config(text=accuracy)
        master2.update()


#------------------------------------------------------
# Generate graphics with information about the data
#------------------------------------------------------
def generateGraphics():
    global attr
    global data
    global counterClassOptions

    #Classes Within the Data Chart
    classData = []
    classLabels = []
    total = 0
    
    for i in counterClassOptions:
        classData.append(counterClassOptions[i])
        total += counterClassOptions[i]
        classLabels.append(i[0])

    plt.figure()
    plt.axis('equal')
    plt.pie(classData, autopct=lambda p: '{:.0f}'.format(p * total / 100))
    plt.legend(classLabels)
    plt.title("Classes Within the Data")


    #Discrete x Continuous Attributes Chart
    attCont = 0
    attDisc = 0

    for n in attr:
        if attr[n][len(attr[n])-1] == 'numeric' or attr[n][len(attr[n])-1] == 'NUMERIC':
            attCont += 1
        else:
            attDisc += 1

    plt.figure()
    attData = [attCont, attDisc]
    plt.axis('equal') 
    plt.pie(attData, colors=["#CB4335", "#45B39D"], autopct=lambda p: '{:.0f}'.format(p * sum(attData) / 100) if p > 0 else '')
    plt.title("Discrete x Continuous Attributes")
    plt.legend(['Continuous','Discrete'])


    #Attributes charts
    for i in attr:
        if attr[i][len(attr[i])-1] == 'numeric' or attr[n][len(attr[n])-1] == 'NUMERIC':
            attValues = []
            for d in data:
                attValues.append(data[d][i])
            
            plt.figure()
            
            plt.bar(range(len(data)), attValues)
    
    plt.show()

    return None

#--------------------------------------------------
# Closes the program
#--------------------------------------------------
def exitGUI():
    global master1
    global master2
    global master3
    global master4
    
    master2.destroy()
    master3.destroy()
    master4.destroy()
    master1.destroy()
    exit()

    return None

#------------------------------------------------------------------------------------------------------------#
# Calling main() function if initialized as a script                                                         #
#------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    main()



    
