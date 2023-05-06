import tkinter
from tkinter import *
from tkinter import filedialog
import os

import CrossCheck
import functions
import asyncio

class frame():
    def __init__(self, parentWindow, padx, pady, bg, row, column):
        self.frame = tkinter.Frame(parentWindow, bg=bg, borderwidth=3)
        self.frame.grid(row=row, column=column, padx=padx, pady=pady)

class label():
    def __init__(self, parentWindow, labelText, padx, pady, bg, fg, fontSize):
        self.label = tkinter.Label(parentWindow, text=labelText, foreground=fg,
                                   font=("Robotodo", fontSize), background=bg)
        self.label.pack(padx=padx, pady=pady)

class entry():
    def __init__(self, parentWindow, padx, pady, entryVar):
        self.entry = tkinter.Entry(parentWindow, textvariable=entryVar, width=40,
                                   background="#323232", foreground="#ffffff",
                                   font=("Robotodo", 11), borderwidth=3)
        self.entry.pack(pady=pady, padx=padx)

class button():
    def __init__(self, parentWindow, command, text="", side=None):
        self.button = tkinter.Button(parentWindow, text=text, command=command,
                                     bg="#155eeb", activebackground="#104ab5",
                                     foreground="#ffffff", activeforeground="#e1e2e6",
                                     font=("Robotodo", 11), borderwidth=3
                                     )
        self.button.pack(pady=5, padx=5)

        #Hover change color effect
        self.button.bind("<Leave>", lambda x: self.setNewBg(fg="#ffffff", bg="#155eeb"))
        self.button.bind("<Enter>", lambda x: self.setNewBg(fg="#e1e2e6", bg="#104ab5"))

    def setNewBg(self, fg, bg):
        self.button.config(fg=fg, bg=bg)


class pathSelector():
    def __init__(self, parentWindow, needFrame, filters=[], askFile=True, entryLabelText="", labelText="", nameSelector=False, nameExplorer=False, nameFieldLabel="", scanPath=True, row=None, column=None):
        if needFrame:
            self.frame = frame(parentWindow=parentWindow, pady=15, padx=10, bg="#282828", row=row, column=column)
            self.frame = self.frame.frame
        else:
            self.frame = parentWindow
        if labelText != "":
            self.label = label(parentWindow=self.frame, labelText=labelText, padx=5, pady=7, bg="#282828", fg="#ffffff", fontSize=20)

        if nameSelector:
            self.nameLabel = label(parentWindow=self.frame, labelText=nameFieldLabel, padx=5, pady=7, bg="#282828", fg="#c7c7c7", fontSize=11)
            self.nameSelectorVar = tkinter.StringVar(self.frame, value="")
            self.nameEntry = entry(parentWindow=self.frame, padx=5, pady=7, entryVar=self.nameSelectorVar)
            if nameExplorer:
                self.nameButton = button(parentWindow=self.frame, text="Choose Path",
                                     command=lambda: self.selectPath(filesExt=filters, var=self.nameSelectorVar))

        self.entryLabel = label(parentWindow=self.frame, labelText=entryLabelText, padx=5, pady=7, bg="#282828", fg="#c7c7c7", fontSize=11)
        self.entryVar = tkinter.StringVar(self.frame, value="")
        self.entry = entry(parentWindow=self.frame, padx=5, pady=7, entryVar=self.entryVar)

        if scanPath:
            if askFile:
                self.button = button(parentWindow=self.frame, text="Choose Path", command=lambda: self.selectPath(filesExt=filters, var=self.entryVar))
            else:
                self.button = button(parentWindow=self.frame, text="Choose Path", command=lambda: self.selectDir(var=self.entryVar))

    def selectPath(self, filesExt, var):
        file = filedialog.askopenfilename(filetypes=filesExt)
        if file != "":
            var.set(file)

    def selectDir(self, var):
        dir = filedialog.askdirectory()
        if dir != "":
            var.set(dir)

class gui():
    def __init__(self):
        self.mainWindow = tkinter.Tk()
        self.setupMainWindow()

        self.mainCsvPathSelector = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT CSV FILE PATH",
                                                filters=[("Comma separated values", ".csv")], labelText="MAIN CSV FILE PATH", row=0, column=0)

        self.createCsvWindow = self.defineCreateCsvWindow()
        self.exportHtmlWindow = self.defineExportHtmlWindow()
        self.deleteWindow =self.defineDeleteWindow()
        self.crossCheckWindow = self.definCrossCheckWindow()
        self.updateTableWindow = self.defineUpdateTableWindow()
        self.compareMergeWindow = self.defineCompareMergeWindow()


        self.mainWindow.mainloop()

    def defineDeleteWindow(self):
        deleteRecord = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT ROW ID TO DELETE",
                                    scanPath=False, labelText="DELETE", row=0, column=1)
        deleteRowBtn = button(parentWindow=deleteRecord.frame, text="DELETE ROW",
                              command=lambda: functions.deleteRow(filePath=self.mainCsvPathSelector.entryVar.get(),
                                                                  id=deleteRecord.entryVar.get()))
        deleteTableBtn = button(parentWindow=deleteRecord.frame, text="DELETE CSV FILE",
                                command= lambda: functions.deleteFile(filePath=self.mainCsvPathSelector.entryVar.get()))
        return  deleteRecord

    def defineExportHtmlWindow(self):
        exportHtml = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT CSV FILE PATH",
                                  filters=[("Comma separated values", ".csv")], labelText="EXPORT AS HTML", row=0, column=2)
        exportBtn = button(parentWindow=exportHtml.frame, text="EXPORT AS HTML",
                           command=lambda: functions.exportHtml(filePath=exportHtml.entryVar.get()))
        return exportHtml

    def defineCreateCsvWindow(self):
        createCsv = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT PATH TO SCAN",
                                askFile=False, labelText="CREATE CSV FILE", nameSelector=True,
                                nameFieldLabel="INSERT CSV FILE NAME", row=1, column=0)
        newCsvBtn = button(parentWindow=createCsv.frame, text="GENERATE CSV",
                           command=lambda: functions.scanNewCsv(scanPath=createCsv.entryVar.get(),
                                                        fileName=createCsv.nameSelectorVar.get()))
        return createCsv

    def definCrossCheckWindow(self):
        crossCheck = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT CSV FILE",
                                askFile=True, filters=[("Comma separated values", ".csv")], labelText="CROSS CHECK", row=0, column=3)
        newCsvBtn = button(parentWindow=crossCheck.frame, text="CHECK",
                           command=lambda: asyncio.run(CrossCheck.main(crossCheck.entryVar.get())))
        return crossCheck

    def defineUpdateTableWindow(self):
        updateCsv = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT PATH TO SCAN",
                                 askFile=False, labelText="UPDATE CSV FILE", nameSelector=True, nameExplorer=True,
                                 nameFieldLabel="INSERT CSV FILE NAME", row=1, column=1)
        updateCsvBtn = button(parentWindow=updateCsv.frame, text="UPDATE",
                           command=lambda: functions.update(scanPath=updateCsv.entryVar.get(),
                                                            filePath=updateCsv.nameSelectorVar.get()))
        trimBtn = button(parentWindow=updateCsv.frame, text="TRIM",
                           command=lambda: functions.trim(scanPath=updateCsv.entryVar.get(),
                                                            filePath=updateCsv.nameSelectorVar.get()))

        return updateCsv

    def defineCompareMergeWindow(self):
        csvPathSelector = pathSelector(parentWindow=self.mainWindow, needFrame=True,
                                                entryLabelText="INSERT CSV FILE PATH",
                                                filters=[("Comma separated values", ".csv")],
                                                labelText="COMPARE/MERGE", row=1, column=2)
        csvPathSelector2 = pathSelector(parentWindow=csvPathSelector.frame, needFrame=False,
                                                entryLabelText="INSERT CSV FILE PATH",
                                                filters=[("Comma separated values", ".csv")],
                                                labelText="", row=1, column=2)
        newCsvNameSelector = pathSelector(parentWindow=csvPathSelector.frame, needFrame=False,
                                          entryLabelText="INSERT NEW CSV FILE PATH/NAME",
                                          scanPath=False, row=1, column=2)
        mergeBtn = button(parentWindow=csvPathSelector.frame, text="MERGE",
                           command= lambda: functions.merge(savePath=newCsvNameSelector.entryVar.get(),
                                                            csv1=csvPathSelector.entryVar.get(),
                                                            csv2=csvPathSelector2.entryVar.get()))
        compareBtn = button(parentWindow=csvPathSelector.frame, text="COMPARE",
                          command=lambda: functions.compare(savePath=newCsvNameSelector.entryVar.get(),
                                                          csv1=csvPathSelector.entryVar.get(),
                                                          csv2=csvPathSelector2.entryVar.get()))

    def setupMainWindow(self):
        self.mainWindow.configure(background="#1e1e1e")
        rows= [0, 1]
        columns = [0, 1, 2, 3]
        for row in rows:
            self.mainWindow.rowconfigure(row, weight=1)
        for column in columns:
            self.mainWindow.rowconfigure(column, weight=1)



if __name__ == "__main__":
    gui()