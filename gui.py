import asyncio
import time
import customtkinter
import tkinter as tk
import tkinter.filedialog
import LightMetadataGenerator
import threading
import os
import CrossCheck

class topLevel():
    def __init__(self):
        self.progressLabel, self.window, self.progressDesc = self.createProgressWindow()

    def createProgressWindow(self):
        topLevel = tk.Toplevel(background="#2b2b2b")
        progressLabel = customtkinter.CTkLabel(master=topLevel,
                                               text="",
                                               font=("Robotodo", 28),
                                               width=175)
        progressLabel.pack(padx=10, pady=15)
        progressDesc = customtkinter.CTkLabel(master=topLevel,
                                               text="Don't close anything, you can check the progress on the CMD",
                                               font=("Robotodo", 11),
                                               width=175, text_color="#e00d2d")
        progressDesc.pack(padx=10, pady=15)
        return progressLabel, topLevel, progressDesc

class Record:
    def __init__(self, JAVID: str, extension: str, frame_rate: int, average_bit_rate: int, video_bit_rate:int, audio_bit_rate:int, codec: str, resolution: str, MB: int, GB: float, runtime: int, hh: str,mm:str,ss:str, added: str, last_modified: str, damaged: int,full_path_filename:str):
        self.JAVID = JAVID
        self.extension = extension
        self.frame_rate = frame_rate
        self.average_bit_rate = average_bit_rate
        self.video_bit_rate = video_bit_rate
        self.audio_bit_rate = audio_bit_rate
        self.codec = codec
        self.resolution = resolution
        self.MB = MB
        self.GB = GB
        self.runtime = runtime
        self.duration =f'{hh}:{mm}:{ss}'
        self.added = added
        self.last_modified = last_modified
        self.damaged = damaged
        self.full_path_filename=full_path_filename
        pass


    def __str__(self) -> str:

        return str(self.JAVID)+" "+str(self.extension)+" "+" "+str(self.frame_rate)+" "+" "+str(self.bit_rate)+" "+" "+str(self.codec)+" "+" "+str(self.resolution)

#WIDGET CONTAINING ONE BUTTON PER COMMNAND
class buttonWindow():
    def __init__(self, master=None, row=0, column=0, header="", commandList=[], textList=[], startButtonRow=1, needFrame=True, skipRow=1):
        #raise an error if the lengths aren't equal
        self.skipCounter = skipRow
        if len(commandList) != len(textList):
            raise IndexError("command and text list length must be equal when creating a button window")
        self.frame = master
        if needFrame:
            self.frame = self.defineBtnFrame(master, row, column, header)
        self.rowCount = startButtonRow
        self.btnCount = 0
        self.btnList = []
        for command in commandList:
            btn = self.packNewButton(command, textList[self.btnCount])
            self.btnCount += 1
            self.btnList.append(btn)

    #define the widget frame
    def defineBtnFrame(self, master, row, column, header):
        frame = customtkinter.CTkFrame(master=master, height=500)
        frame.grid(row=row, column=column, padx=25, pady=25)

        header = customtkinter.CTkLabel(master=frame, text=header,
                                        font=("Robotodo", 21), )
        header.grid(row=0, column=0, padx=15, pady=15)
        return frame

    #create a new button with sequential row
    def packNewButton(self, command, text):
        newButton = customtkinter.CTkButton(master=self.frame,
                                            text=text,
                                            command=command)
        newButton.grid(row=self.rowCount, column=0, padx=10, pady=10)
        self.rowCount += self.skipCounter
        return newButton

    def createProcessThread(self, command):
        return threading.Thread(target=command)

#WIDGET CONTAINING 2 ENTRIES (one optional) AND AN EXPLORER
class ScanPathWindow():
    def __init__(self, master=None, row=0, column=0, header="", newTable=True, needFrame=True, needExplorer=True, askFile=False, placeHolder="Insert path to scan", useCustomPlaceHolder=False, tableEntryRow=1):
        self.actionBtn = customtkinter.CTkButton(master=master)
        self.tableEntryRow = tableEntryRow
        self.customPlaceHolder = useCustomPlaceHolder
        self.askFile = askFile
        self.needExplorer = needExplorer
        self.placeHolder = placeHolder
        self.scanPathWindow, self.tableEntry, self.scanPathEntry = self.defineScanPathWindow(master, row, column, header, newTable, needFrame)

    def openExplorerDir(self, var, entry):
        dir = tkinter.filedialog.askdirectory()
        var.set(dir)
        entry.insert(1, "")
        entry.configure(textvariable=var)
        self.checkEntry([entry])
        return dir

    def openExplorerFile(self, var, entry):
        file = tkinter.filedialog.askopenfilename()
        var.set(file)
        entry.insert(1, "")
        entry.configure(textvariable=var)
        self.checkEntry([entry])
        return file

    def checkEntry(self, entry):
        try:
            for e in entry:
                if len(e.get()) > 0:
                    for btn in self.actionBtn:
                        btn.configure(state="normal")
                else:
                    for btn in self.actionBtn:
                        btn.configure(state="disabled")
                    return
        except:
            pass

    def defineScanPathWindow(self, master, row, column, header, newTable, needFrame):
        frame = None
        tableNameEntry = None
        scanPathEntry = None

        if needFrame:
            frame = customtkinter.CTkFrame(master=master, width=200, height=500)
            frame.grid(row=row, column=column, padx=20, pady=15)
            master = frame

        header = customtkinter.CTkLabel(master=master,
                                                   text=header, font=("Robotodo", 21))
        header.grid(row=0, column=0, padx=15, pady=15)

        newTablePlaceHolder = "Insert table name"
        if newTable:

            # define the table name entry
            if self.customPlaceHolder:
                newTablePlaceHolder = self.placeHolder

            tableNameEntry = customtkinter.CTkEntry(master=master,
                                                    placeholder_text=newTablePlaceHolder)
            tableNameEntry.grid(row=self.tableEntryRow, column=0, padx=15, pady=10)
            tableNameEntry.bind("<KeyRelease>", lambda event: self.checkEntry(entry=[tableNameEntry]))

        if self.needExplorer:
            # define the path to scan entry or explorer, when a folder is selected in the explorer the entry is filled
            scanPathEntry = customtkinter.CTkEntry(master=master,
                                                   placeholder_text=self.placeHolder)
            scanPathEntry.grid(row=3, column=0, padx=15, pady=3)

            scanVar = tk.StringVar(master)
            command = lambda x=None: self.openExplorerDir(var=scanVar, entry=scanPathEntry)
            if self.askFile:
                command = lambda X=None: self.openExplorerFile(var=scanVar, entry=scanPathEntry)
            scanPathBtn = customtkinter.CTkButton(master=master, text=self.placeHolder,
                                                  command=command)
            scanPathBtn.grid(row=4, column=0, padx=15, pady=10)
            scanPathEntry.bind("<KeyRelease>", lambda event: self.checkEntry(entry=[scanPathEntry]))
        if self.needExplorer and newTable:
            scanPathEntry.unbind()
            tableNameEntry.unbind()
            scanPathEntry.bind("<KeyRelease>", lambda event: self.checkEntry(entry=[scanPathEntry, tableNameEntry]))
            tableNameEntry.bind("<KeyRelease>", lambda event: self.checkEntry(entry=[scanPathEntry, tableNameEntry]))

        return frame, tableNameEntry, scanPathEntry




class GUI():
    def __init__(self):
        self.configureMainAppearance()

        #define general appearance for the window
        self.windowTitle = "LightMetadataGenerator"
        self.startWindowSize = "1280x720"
        self.mainWindow = self.defineMainWindow()

        #DEFINE WIDGETS COSTANTS
        self.currentTable = tk.StringVar(self.mainWindow)
        #for compare window
        self.currentTable1 = tk.StringVar(self.mainWindow)
        self.currentTable2 = tk.StringVar(self.mainWindow)

        #DEFINE WIDGETS
        self.tableBox = self.defineTableBox()
        self.cdFrame = customtkinter.CTkFrame(master=self.mainWindow, width=400)
        self.cdFrame.grid(row=1, column=0, padx=15, pady=15)
        self.createTableWindow = self.defineCreateTable()
        self.updateTableWindow = self.defineUpdateTable()
        self.ieFrame = customtkinter.CTkFrame(master=self.mainWindow, width=400)
        self.ieFrame.grid(row=1, column=1, padx=15, pady=15)
        self.defineExportTable()
        self.deleteTableBtn = self.defineDeleteTable()
        self.compareFrame = customtkinter.CTkFrame(master=self.mainWindow, width=400)
        self.compareFrame.grid(row=1, column=2, padx=15, pady=15)
        self.table1Box, self.tableBox2, self.mergeBtn, self.compareBtn = self.defineCompareTable()
        self.defineImportTable()
        """self.currentTable1.trace("w",lambda x=None: self.checkValue([self.currentTable1.get(), self.currentTable2.get()],
                                                      [self.compareBtn, self.mergeBtn]))
        self.currentTable2.trace("w", lambda x=None: self.checkValue([self.currentTable1.get(), self.currentTable2.get()],
                                                      [self.compareBtn, self.mergeBtn]))"""
        self.defineCrossCheckTable()

        #Start the GUI
        self.refreshAll()
        self.mainWindow.mainloop()

    def configureMainAppearance(self):
        #Light or Dark mode depends on the system settings
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

    def defineMainWindow(self):
        root = customtkinter.CTk()
        #root.geometry(self.startWindowSize)
        root.title(self.windowTitle)
        root.grid_columnconfigure((0,1,2), weight=1)
        root.grid_rowconfigure((0,1,2,3), weight=1)
        return root

    def updateBtn(self, value, btn):
        if len(value.get()) > 1 :
            btn.config(state="normal")
        else:
            btn.config(state="disabled")

    #Option menu containig all names of the tables
    def defineTableBox(self):
        tableBoxFrame = customtkinter.CTkFrame(master=self.mainWindow, width=800)
        tableBoxFrame.grid(row=0, column=1, padx=20, pady=15)

        tableBoxHeader = customtkinter.CTkLabel(master=tableBoxFrame, text="SELECT TABLE",
                                             font=("Robotodo", 21))
        tableBoxHeader.grid(row=0, column=0, padx=15, pady=7)

        tableBox = customtkinter.CTkOptionMenu(master=tableBoxFrame,
                                               variable=self.currentTable)
        tableBox.grid(row=1, column=0, padx=15, pady=15)
        return tableBox

    #Modifies an option menu with new values and set the first value as default
    def refreshOptionMenu(self, optionMenu, optionMenuVar, options):
        try:
            if "" in options:
                for i in range(len(options)):
                    if options[i] == "":
                        options[i] = "DEFAULT"
            optionMenu.configure(values=options)
            optionMenuVar.set(options[0])
            return
        except:
            pass


    #Window that when used makes the user create a new table in the db
    def defineCreateTable(self):
        createTableWindow = ScanPathWindow(master=self.cdFrame, row=0, column=0, header="CREATE TABLE", newTable=True)
        #define the button that activates the create table function
        createTableBtn = customtkinter.CTkButton(master=createTableWindow.scanPathWindow,
                                                 text="CREATE TABLE",
                                                 command=lambda x=None:threading.Thread(target=self.startProgress(scanPath=createTableWindow.scanPathEntry.get(),
                                                                                          command="create")).start(),
                                                 state="disabled")
        createTableBtn.grid(row=5, column=0, padx=15, pady=15)
        createTableWindow.actionBtn = [createTableBtn]
        return createTableWindow

    #Creates the update table window with the add and trim option
    def defineUpdateTable(self):
        updateTableWindow = ScanPathWindow(master=self.cdFrame, row=2, column=0, header="UPDATE TABLE", newTable=False)
        addBtn = customtkinter.CTkButton(master=updateTableWindow.scanPathWindow,
                                         text="ADD/UPDATE",
                                         command=lambda x=None: threading.Thread(target=self.startProgress(scanPath=updateTableWindow.scanPathEntry.get(),
                                                                                   command="add")).start(),
                                         state="disabled")
        addBtn.grid(row=5, column=0, padx=15, pady=5)

        trimBtn = customtkinter.CTkButton(master=updateTableWindow.scanPathWindow,
                                         text="TRIM/UPDATE",
                                         command=lambda x=None: threading.Thread(target=self.startProgress(scanPath=updateTableWindow.scanPathEntry.get(), command="trim")).start(),
                                          state="disabled")
        trimBtn.grid(row=6, column=0, padx=15, pady=5)
        updateTableWindow.actionBtn = [addBtn, trimBtn]
        return updateTableWindow

    def defineExportTable(self):
        exportScanFrame = ScanPathWindow(master=self.ieFrame, row=0, column=0, header="EXPORT",
                                         newTable=False, needFrame=True, placeHolder="Insert output path")
        exportBtnFrame = buttonWindow(master=exportScanFrame.scanPathWindow, row=0, column=1, header="EXPORT",
                                      commandList=[lambda x=None:LightMetadataGenerator.exportToCsv(tableName=self.currentTable.get(), path=exportScanFrame.scanPathEntry.get())],
                                      textList=["Export"],
                                      startButtonRow=5, needFrame=False)

    def defineDeleteTable(self):
        deleteTableFrame = ScanPathWindow(master=self.cdFrame, row=1, column=0, header="DELETE",
                                          newTable=True, needFrame=True, needExplorer=False,
                                          placeHolder="Insert jav ID", useCustomPlaceHolder=True, tableEntryRow=3)
        deleteTableBtn = buttonWindow(master=deleteTableFrame.scanPathWindow, row=0, column=1, header="DELETE",
                                      commandList=[lambda x=None: self.deleteTable(),
                                                   lambda x=None: self.deleteRecord(deleteTableFrame)],
                                      textList=["Delete Table", "Delete Record"],
                                      startButtonRow=2, needFrame=False, skipRow=2)
        deleteTableBtn.btnList[-1].configure(state="disabled")
        deleteTableFrame.actionBtn = [deleteTableBtn.btnList[-1]]
        return deleteTableBtn

    def deleteTable(self):
        LightMetadataGenerator.deleteTable(tableName=self.currentTable.get())
        self.refreshAll()

    def deleteRecord(self, deleteTableFrame):
        LightMetadataGenerator.deleteRecord(tableName=self.currentTable.get(), JAVID=deleteTableFrame.tableEntry.get())

    def defineCompareTable(self):
        compareTableFrame = customtkinter.CTkFrame(master=self.compareFrame, width=200)
        compareTableFrame.grid(row=0, column=0, padx=25, pady=25)

        header = customtkinter.CTkLabel(master=compareTableFrame, text="COMPARE/MERGE",
                                        font=("Robotodo", 21))
        header.grid(row=0, column=0, padx=10, pady=10)

        tableBoxHeader1 = customtkinter.CTkLabel(master=compareTableFrame, text="SELECT TABLE 1",
                                                font=("Robotodo", 14))
        tableBoxHeader1.grid(row=1, column=0, padx=15, pady=3)


        tableBox1 = customtkinter.CTkOptionMenu(master=compareTableFrame,
                                               variable=self.currentTable1)
        tableBox1.grid(row=2, column=0, padx=15, pady=10)

        tableBoxHeader2 = customtkinter.CTkLabel(master=compareTableFrame, text="SELECT TABLE 2",
                                                 font=("Robotodo", 14))
        tableBoxHeader2.grid(row=3, column=0, padx=15, pady=3)

        tableBox2 = customtkinter.CTkOptionMenu(master=compareTableFrame,
                                                variable=self.currentTable2)
        tableBox2.grid(row=4, column=0, padx=15, pady=10)

        compareBtn = customtkinter.CTkButton(master=compareTableFrame, text="Compare",
                                             command=lambda x=None: self.compare(tableBox1, tableBox2),
                                             state="normal")
        compareBtn.grid(row=5, column=0, padx=15, pady=12)


        urlFrame = customtkinter.CTkFrame(master=self.compareFrame, width=200)
        urlFrame.grid(row=1, column=0, padx=25, pady=25)
        compareUrlLabel = customtkinter.CTkLabel(master=urlFrame, text="JAV-LIBRARY",
                                        font=("Robotodo", 21))
        compareUrlLabel.grid(row=0, column=0, padx=10, pady=10)
        tableUrlEntry = customtkinter.CTkEntry(master=urlFrame,
                                               placeholder_text="Insert Table Name")
        tableUrlEntry.grid(row=6, column=0, padx=15, pady=12)
        tableUrlEntry.bind("<KeyRelease>", lambda event: self.checkValue([compareUrlEntry.get(), tableUrlEntry.get()], [compareUrlBtn]))
        compareUrlEntry = customtkinter.CTkEntry(master=urlFrame,
                                                 placeholder_text="Insert JavLibrary url")
        compareUrlEntry.grid(row=7, column=0, padx=15, pady=12)

        compareUrlBtn = customtkinter.CTkButton(master=urlFrame, text="Compare Url",
                                                command=lambda x=None: self.compareUrl(tableName=tableUrlEntry.get(),
                                                                                       url=compareUrlEntry.get()),
                                                state="disabled")
        compareUrlBtn.grid(row=8, column=0, padx=15, pady=10)
        compareUrlEntry.bind("<KeyRelease>", lambda event: self.checkValue([compareUrlEntry.get(), tableUrlEntry.get()], [compareUrlBtn]))


        mergeBtn = customtkinter.CTkButton(master=compareTableFrame, text="Merge",
                                           command= lambda x=None: self.mergeTable(self.currentTable1.get(),
                                                                                   self.currentTable2.get()),
                                           state="normal")
        mergeBtn.grid(row=8, column=0, padx=15, pady=10)
        return tableBox1, tableBox2, compareBtn, mergeBtn

    def checkValue(self, values, btn):
        for value in values:
            if len(value) < 1:
                for b in btn:
                    b.configure(state="disabled")
                    return
            else:
                for b in btn:
                    b.configure(state="normal")

    def mergeTable(self, table1, table2):
        progressWindow = topLevel()
        progressWindow.progressLabel.pack(padx=35, pady=25)
        progressWindow.progressLabel.configure(text="IN PROGRESS")
        progressWindow.window.update()
        progressWindow.window.wm_deiconify()
        LightMetadataGenerator.merge(table1, table2)
        self.refreshAll()
        progressWindow.progressLabel.configure(text="COMPLETED")
        progressWindow.progressDesc.configure(text="You can now close this pop-up")

    def compareUrl(self, tableName, url):
        progressWindow = topLevel()
        progressWindow.progressLabel.pack(padx=35, pady=25)
        progressWindow.progressLabel.configure(text="IN PROGRESS")
        progressWindow.window.update()
        progressWindow.window.wm_deiconify()
        if tableName in LightMetadataGenerator.getTables("jav"):
            progressWindow.progressLabel.configure(text="TABLE ALREADY EXISTS", font=("Robotodo", 14))
            progressWindow.progressDesc.configure(text="")
            return
        LightMetadataGenerator.compareTableFromURL(
            tableName=tableName,
            javLibraryURL=url)
        self.refreshAll()
        progressWindow.progressLabel.configure(text="COMPLETED")
        progressWindow.progressDesc.configure(text="You can now close this pop-up")

    def compare(self, table1, table2):
        progressWindow = topLevel()
        progressWindow.progressLabel.pack(padx=35, pady=25)
        progressWindow.progressLabel.configure(text="IN PROGRESS")
        progressWindow.window.update()
        progressWindow.window.wm_deiconify()
        LightMetadataGenerator.compareTables(firstTableName=self.currentTable1.get(), secondTableName=self.currentTable2.get())
        self.refreshAll()
        progressWindow.progressLabel.configure(text="COMPLETED")
        progressWindow.progressDesc.configure(text="You can now close this pop-up")


    def defineImportTable(self):
        importFrame = ScanPathWindow(master=self.ieFrame, row=1, column=0, header="IMPORT",
                                     placeHolder="Insert Csv File Path", askFile=True)
        importBtn = customtkinter.CTkButton(master=importFrame.scanPathWindow, text="Import",
                                            command=lambda x=None: self.importTable(importFrame.scanPathEntry.get(),
                                                                            importFrame.tableEntry.get()),
                                            state="disabled")
        importFrame.actionBtn = [importBtn]
        importBtn.grid(row=5, column=0, padx=15, pady=15)

    def importTable(self, path, tableName):
        LightMetadataGenerator.importCSV(path=path,
                                         tableName=tableName)
        self.refreshAll()

    def defineCrossCheckTable(self):
        crossCheckFrame = ScanPathWindow(master=self.ieFrame, row=3, column=0, askFile=True, needFrame=True, placeHolder='Insert CSV path', header='CROSS-CHECK', newTable=False)
        crossCheckBtn = customtkinter.CTkButton(master=crossCheckFrame.scanPathWindow, text='Cross-Check',
            command=lambda x=None: asyncio.run(CrossCheck.main(crossCheckFrame.scanPathEntry.get())),
            state='disabled')
        crossCheckFrame.actionBtn = [crossCheckBtn]
        crossCheckBtn.grid(row=5, column=0, padx=15, pady=15)

    def refreshAll(self):

        options = LightMetadataGenerator.getTables("jav")
        self.refreshOptionMenu(optionMenu=self.tableBox, optionMenuVar=self.currentTable, options=options)
        self.refreshOptionMenu(optionMenu=self.table1Box, optionMenuVar=self.currentTable, options=options)
        self.refreshOptionMenu(optionMenu=self.tableBox2, optionMenuVar=self.currentTable, options=options)

    def startProgress(self, scanPath, command):
        progressWindow = topLevel()
        progressWindow.progressLabel.pack(padx=35, pady=25)
        progressWindow.progressLabel.configure(text="IN PROGRESS")
        progressWindow.window.update()
        progressWindow.window.wm_deiconify()
        if command == "create":
            if self.createTableWindow.tableEntry.get() not in LightMetadataGenerator.getTables("jav"):
                LightMetadataGenerator.scanNewTable(tableName=self.createTableWindow.tableEntry.get(), path=self.createTableWindow.scanPathEntry.get())
            else:
                progressWindow.progressLabel.configure(text="TABLE ALREADY EXISTS", font=("Robotodo", 14))
                progressWindow.progressDesc.configure(text="")
                return
        elif command == "add":
            LightMetadataGenerator.analyzeFiles(mPath=self.updateTableWindow.scanPathEntry.get(),
                                                         tableName=self.currentTable.get())
        elif command == "trim":
            LightMetadataGenerator.trim(tableName=self.currentTable.get(),
                                                  filesAnalyzed=LightMetadataGenerator.load(self.currentTable.get(),LightMetadataGenerator.DB),
                                                   path=self.updateTableWindow.scanPathEntry.get())
        progressWindow.progressLabel.configure(text="COMPLETED")
        progressWindow.progressDesc.configure(text="You can now close this pop-up")
        self.refreshAll()



if __name__ == "__main__":
    gui = GUI()


