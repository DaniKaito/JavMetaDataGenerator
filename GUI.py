import tkinter
from tkinter import *
from tkinter import filedialog
import threading
import CrossCheck
import functions
import asyncio





class checkBox():
    def __init__(self, parentWindow, text, padx, pady, bg, fg, var, command=None):
        checkBtn = tkinter.Checkbutton(master=parentWindow, text=text,
                            variable=var, background=bg, activeforeground=fg,
                            foreground=fg, selectcolor=bg, activebackground=bg,
                            command=command
                            )
        checkBtn.pack(pady=pady, padx=padx)


        

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
class minSizeInput():
    def __init__(self, parentWindow):
        self.label = label(parentWindow=parentWindow, labelText="INSERT MIN FILE SIZE (IN MB), LEAVE BLANK IF NONE",
                           padx=5, pady=5, bg="#282828", fg="#c7c7c7", fontSize=8)
        self.entryVar = tkinter.StringVar(parentWindow)
        self.entry = entry(parentWindow=parentWindow, padx=5, pady=0, entryVar=self.entryVar)


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
                self.nameButton = button(parentWindow=self.frame, text="Choose File",
                                     command=lambda: self.selectPath(filesExt=filters, var=self.nameSelectorVar))

        self.entryLabel = label(parentWindow=self.frame, labelText=entryLabelText, padx=5, pady=7, bg="#282828", fg="#c7c7c7", fontSize=11)
        self.entryVar = tkinter.StringVar(self.frame, value="")
        self.entry = entry(parentWindow=self.frame, padx=5, pady=7, entryVar=self.entryVar)

        if scanPath:
            if askFile:
                self.button = button(parentWindow=self.frame, text="Choose File", command=lambda: self.selectPath(filesExt=filters, var=self.entryVar))
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
    async def setup(self):
        self.mainWindow = tkinter.Tk()
        self.setupMainWindow()

        self.createCsvWindow = await self.defineCreateCsvWindow()
        self.exportHtmlWindow = await self.defineExportHtmlWindow()
        self.deleteWindow = await self.defineDeleteWindow()
        self.crossCheckWindow = await self.definCrossCheckWindow()
        self.updateTableWindow = await self.defineUpdateTableWindow()
        self.compareMergeWindow = await self.defineCompareMergeWindow()
        self.javLibraryWindow = await self.defineJavLibraryWindow()
        self.sortWindow = await self.defineSortWindow()
        functions.setupConsole(parent=self.mainWindow)

        self.mainWindow.mainloop()

    def runAsync(self, functionTarget):
        self.buttonDisable(parentWindow=self.mainWindow)
        thread = threading.Thread(target=lambda loop: loop.run_until_complete(functionTarget),
                        args=(asyncio.new_event_loop(),))
        thread.start()
        threading.Thread(target=lambda loop: loop.run_until_complete(self.buttonAble(parentWindow=self.mainWindow, thread=thread)),
                        args=(asyncio.new_event_loop(),)).start()
    
    async def buttonAble(self, parentWindow, thread):
        thread.join()
        for child in parentWindow.winfo_children():
            if isinstance(child, tkinter.Button):
                child.configure(state='normal')
            else:
                await self.buttonAble(parentWindow=child, thread=thread)

    def buttonDisable(self, parentWindow):
        for child in parentWindow.winfo_children():
            if isinstance(child, tkinter.Button):
                child.configure(state='disabled')
            else:
                self.buttonDisable(parentWindow=child)
        

    async def defineDeleteWindow(self):
        deleteRecord = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT ID OF THE ROW TO DELETE",
                                    scanPath=False, labelText="DELETE", row=1, column=0, filters=[("Comma separated values", ".csv")],
                                    nameSelector=True, nameExplorer=True, nameFieldLabel="INSERT CSV FILE PATH")

        deleteRowBtn = button(parentWindow=deleteRecord.frame, text="DELETE ROW",
                              command=lambda: self.runAsync(functionTarget=functions.deleteRow(filePath=deleteRecord.nameSelectorVar.get(),
                                                                                                id=deleteRecord.entryVar.get())))
        return  deleteRecord

    async def defineExportHtmlWindow(self):
        exportHtml = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT CSV FILE PATH",
                                  filters=[("Comma separated values", ".csv")], labelText="EXPORT AS HTML", row=1, column=1)

        exportBtn = button(parentWindow=exportHtml.frame, text="EXPORT AS HTML",
                           command=lambda: self.runAsync(functionTarget=functions.exportHtml(filePath=exportHtml.entryVar.get())))
        return exportHtml

    async def defineCreateCsvWindow(self):
        createCsv = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT PATH TO SCAN",
                                askFile=False, labelText="CREATE CSV FILE", nameSelector=True,
                                nameFieldLabel="INSERT CSV FILE NAME", row=0, column=0)
        checkBoxVar = tkinter.BooleanVar(createCsv.frame)
        subFolderSearchBtn = checkBox(parentWindow=createCsv.frame, text="SEARCH IN SUB-FOLDERS",
                                      var=checkBoxVar, bg="#282828", fg="#c7c7c7", padx=5, pady=5)
        
        minSizeBtn = minSizeInput(parentWindow=createCsv.frame)

        newCsvBtn = button(parentWindow=createCsv.frame, text="GENERATE CSV",
                           command=lambda: self.runAsync(functionTarget=functions.scanNewCsv(scanPath=createCsv.entryVar.get(),
                                                                                            fileName=createCsv.nameSelectorVar.get(),
                                                                                            subFolders=checkBoxVar.get(),
                                                                                            minSize=minSizeBtn.entryVar.get())))
        return createCsv

    async def definCrossCheckWindow(self):
        crossCheck = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT CSV FILE PATH",
                                askFile=True, filters=[("Comma separated values", ".csv")], labelText="CROSS CHECK", row=1, column=2)

        newCsvBtn = button(parentWindow=crossCheck.frame, text="CHECK",
                           command=lambda: self.runAsync(functionTarget=functions.crossCheck(filePath=crossCheck.entryVar.get())))
        return crossCheck

    async def defineUpdateTableWindow(self):
        updateCsv = pathSelector(parentWindow=self.mainWindow, needFrame=True, entryLabelText="INSERT PATH TO SCAN",
                                 askFile=False, labelText="UPDATE CSV FILE", nameSelector=True, nameExplorer=True,
                                 nameFieldLabel="INSERT CSV FILE PATH", row=0, column=1)

        checkBoxVar = tkinter.BooleanVar(updateCsv.frame)
        subFolderSearchBtn = checkBox(parentWindow=updateCsv.frame, text="SEARCH IN SUB-FOLDERS",
                                      var=checkBoxVar, bg="#282828", fg="#c7c7c7", padx=5, pady=5)

        minSizeBtn = minSizeInput(parentWindow=updateCsv.frame)

        updateCsvBtn = button(parentWindow=updateCsv.frame, text="UPDATE",
                           command=lambda: self.runAsync(functionTarget=functions.update(scanPath=updateCsv.entryVar.get(),
                                                                                        filePath=updateCsv.nameSelectorVar.get(),
                                                                                        subFolders=checkBoxVar.get(),
                                                                                        minSize=minSizeBtn.entryVar.get())))
        trimBtn = button(parentWindow=updateCsv.frame, text="TRIM",
                           command=lambda: self.runAsync(functionTarget=functions.trim(scanPath=updateCsv.entryVar.get(),
                                                                                        filePath=updateCsv.nameSelectorVar.get(),
                                                                                        subFolders=checkBoxVar.get(),
                                                                                        minSize=minSizeBtn.entryVar.get())))
        return updateCsv

    async def defineCompareMergeWindow(self):
        csvPathSelector = pathSelector(parentWindow=self.mainWindow, needFrame=True,
                                                entryLabelText="INSERT MAIN CSV FILE PATH",
                                                filters=[("Comma separated values", ".csv")],
                                                labelText="COMPARE/MERGE", row=0, column=2)
        csvPathSelector2 = pathSelector(parentWindow=csvPathSelector.frame, needFrame=False,
                                                entryLabelText="INSERT SECONDARY CSV FILE PATH",
                                                filters=[("Comma separated values", ".csv")],
                                                labelText="", row=0, column=2)
        newCsvNameSelector = pathSelector(parentWindow=csvPathSelector.frame, needFrame=False,
                                          entryLabelText="INSERT NEW CSV FILE NAME",
                                          scanPath=False, row=0, column=2)

        mergeBtn = button(parentWindow=csvPathSelector.frame, text="MERGE",
                           command=lambda: self.runAsync(functionTarget=functions.merge(savePath=newCsvNameSelector.entryVar.get(),
                                                                                        csv1=csvPathSelector.entryVar.get(),
                                                                                        csv2=csvPathSelector2.entryVar.get())))
        compareBtn = button(parentWindow=csvPathSelector.frame, text="COMPARE",
                          command=lambda: self.runAsync(functionTarget=functions.compare(savePath=newCsvNameSelector.entryVar.get(),
                                                                                        csv1=csvPathSelector.entryVar.get(),
                                                                                        csv2=csvPathSelector2.entryVar.get())))

    async def defineJavLibraryWindow(self):
        javLib = pathSelector(parentWindow=self.mainWindow, needFrame=True, scanPath=False,
                              entryLabelText="INSERT NEW CSV FILE NAME",
                              labelText="JAVLIBRARY", nameSelector=True,
                              nameFieldLabel="INSERT JAVLIBRARY URL",
                              row=0, column=3)
        csvPathSelector = pathSelector(parentWindow=javLib.frame, needFrame=False,
                                       entryLabelText="INSERT CSV FILE PATH TO BE EXCLUDED",
                                       nameSelector=True, nameFieldLabel="INSERT CSV FILE PATH TO BE COMPARED",
                                       askFile=True, nameExplorer=True, filters=[("Comma separated values", ".csv")])
        startBtn = button(parentWindow=javLib.frame, text="START",
                          command=lambda: self.runAsync(functionTarget=functions.scanJavlibraryURL(javLibraryURL=javLib.nameSelectorVar.get(),
                                                                                           newCsvFilePath=javLib.entryVar.get(),
                                                                                           compareCsvFilePath=csvPathSelector.nameSelectorVar.get(),
                                                                                           excludeCsvFilePath=csvPathSelector.entryVar.get())))
        return javLib

    async def defineSortWindow(self):
        sort = frame(parentWindow=self.mainWindow, padx=5, pady=5, bg="#282828",
                     row=1, column=3)
        sortLabel = label(parentWindow=sort.frame, labelText="SORTING METHOD",
                          padx=5, pady=5, bg="#282828", fg="#ffffff", fontSize=20)
        instructionlabel = label(parentWindow=sort.frame, labelText="CHOOSE ONE OF THE FOLLOWING",
                          padx=5, pady=5, bg="#282828", fg="#c7c7c7", fontSize=11)
        options = {"JavID":"JAVID", "Size Mb":"MB", "Duration":"RUNTIME", "Average Bit Rate":"AVERAGE_BIT_RATE", "Video Bit Rate":"VIDEO_BIT_RATE"}
        sortVar = tkinter.StringVar(sort.frame)
        radioList = []
        for key in list(options.keys()):
            radioBtn = tkinter.Radiobutton(master=sort.frame, text=key,
                                           value=options[key], variable=sortVar,
                                           bg="#282828", fg="#ffffff", activebackground="#282828",
                                           activeforeground="#ffffff", selectcolor="#282828",
                                           command= lambda: self.runAsync(functions.setSort(sortColumn=sortVar.get()))
                                           )
            radioBtn.pack(padx=5, pady=5, anchor=tkinter.W)
            radioList.append(radioBtn)
        self.runAsync(functions.setSort(sortColumn="JAVID"))
        radioList[0].select()

        sortSelector = pathSelector(parentWindow=sort.frame, needFrame=False, filters=[("Comma separated values", ".csv")],
                                    askFile=True, entryLabelText="INSERT CSV FILE PATH", nameSelector=False,
                                    scanPath=True)
        sortBtn = button(parentWindow=sort.frame, text="SORT",
                         command=lambda: self.runAsync(functionTarget=functions.sort(filePath=sortSelector.entryVar.get())))


    def setupMainWindow(self):
        self.mainWindow.configure(background="#1e1e1e")
        rows= [0, 1, 2]
        columns = [0, 1, 2]
        for row in rows:
            self.mainWindow.rowconfigure(row, weight=1)
        for column in columns:
            self.mainWindow.columnconfigure(column, weight=1)
        self.mainWindow.title("JavMetadataGenerator")

async def main():
    GUI = gui()
    await GUI.setup()


asyncio.run(main())