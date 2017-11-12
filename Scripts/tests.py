from tkinter import *

root = Tk()

labelframe = LabelFrame(root, text="This is a LabelFrame")
labelframe.pack()
 
left = Label(labelframe, text="Inside the LabelFrame")
left.pack()
 
root.mainloop()
