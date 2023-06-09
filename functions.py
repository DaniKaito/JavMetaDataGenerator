import JavMetadataGenerator
import asyncio
import os
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import tkinter
from tkinter import *
import CrossCheck
import time


multiPartIndicators = ["-pt", "_"]

class textBox():
    def __init__(self):
        pass

    def setup(self, parentWindow, bg, fg, row, column, columnspan):
        self.box = tkinter.Text(master=parentWindow, bg=bg, height=4, width=100,
                           foreground=fg, font=("Robotodo", 11))
        self.box.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=5)
    
    def writeInBox(self, text):
        timeStamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        text = timeStamp + "  " + text
        self.box.insert(INSERT, text)
        self.box.see("end")
    
    def deleteAll(self):
        self.box.delete("1.0", END)

fm = JavMetadataGenerator.FileManager()
cm = JavMetadataGenerator.CsvManager()
console = textBox()

def setupConsole(parent):
    console.setup(parentWindow=parent, bg="#282828",
                        fg="#c7c7c7", row=2, column=0, columnspan=8)

async def scanJavlibraryURL(javLibraryURL, newCsvFilePath, compareCsvFilePath, excludeCsvFilePath):
    console.deleteAll()
    if ".csv" not in newCsvFilePath:
        newCsvFilePath += ".csv"
    console.writeInBox(text="Starting to scan javlibrary\n")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.maximize_window()
    # esempio https://www.javlibrary.com/en/vl_star.php?s=ae2sc
    javidList=[]
    driver.get(javLibraryURL)
    try:
        links=driver.find_elements(By.CSS_SELECTOR,"div.videos > div.video>a")
    except Exception:
        return []
    
    #HOME
    for link in links:
        javidList.append(link.get_attribute("title").split(" ")[0])
    
    url = javLibraryURL+ "&page="
    counter = 2
    while True:
        newUrl=url+str(counter)
        print(f"Fetching info from {newUrl}")
        driver.get(newUrl)
        try:
            driver.find_element(By.CSS_SELECTOR, "#rightcolumn > p > em")
            break
        except:
            counter+=1
            try:
                links=driver.find_elements(By.CSS_SELECTOR,"div.videos > div.video>a")
            except Exception:
                break
            for link in links:
                javidList.append(link.get_attribute("title").split(" ")[0])
        await asyncio.sleep(3)
    
    cm.createEmptyCsvFile(filePath=newCsvFilePath)
    compareDf = cm.loadCsvFile(filePath=compareCsvFilePath)
    compareIds = compareDf['JAVID'].values.tolist()
    if excludeCsvFilePath != "":
        console.writeInBox(text="Found excluded ids\n")
        excludeIds = cm.loadCsvFile(filePath=excludeCsvFilePath)['JAVID'].values.tolist()
    else:
        excludeIds = []
    console.writeInBox(text="Finished analyzing javlibary urls - Now compiling the csv file\n")
    for javID in javidList:
        if javID not in excludeIds:
            if javID in compareIds:
                videoData = cm.getRow(rowID=javID, dataFrame=compareDf)
            else:
                videoData = {"JAVID": [javID],
                                 "EXTENSION": [""],
                                 "FRAME_RATE": [""],
                                 "AVERAGE_BIT_RATE": [""],
                                 "VIDEO_BIT_RATE": [""],
                                 "AUDIO_BIT_RATE": [""],
                                 "CODEC": [""],
                                 "RESOLUTION": [""],
                                 "MB": [""],
                                 "GB": [""],
                                 "RUNTIME":[""],
                                 "DURATION": [""],
                                 "ADDED": [""],
                                 "LAST_MODIFIED": [""],
                                 "DAMAGED": ["0"],
                                 "FULL_PATH": [""]}
            cm.appendRow(filePath=newCsvFilePath, info=videoData)
    console.writeInBox(text="Created new csv file successfully")

def checkMinSize(minSize):
    if minSize == "":
        return None
    else:
        return int(minSize)

async def sort(filePath):
    if ".csv" not in filePath:
        filePath += ".csv"
    dataFrame = cm.loadCsvFile(filePath=filePath)
    cm.saveCsv(filePath=filePath, dataFrame=dataFrame)
    console.writeInBox(text=f"Sorting completed.")

async def scanNewCsv(scanPath, fileName, subFolders=False, minSize=None):
    minSize = checkMinSize(minSize=minSize)
    console.deleteAll()
    if subFolders:
        console.writeInBox(text="Sub-folders scan option found\n")
    if ".csv" not in fileName:
        fileName += ".csv"
    cm.createEmptyCsvFile(filePath=fileName)
    fm.files = []
    for file in fm.getFileList(scanPath=scanPath, subFolders=subFolders):
        console.writeInBox(text=f"Now analyzing the following file: {file}\n")
        file = os.path.join(scanPath, file)
        fileInfo = fm.getVideoData(file=file, minSize=minSize)
        if fileInfo != "sizeErr":
            cm.appendRow(filePath=fileName, info=fileInfo)
        await asyncio.sleep(0.001)
    console.writeInBox(text=f"Created new csv file successfully")
    await multiPart(filePath=fileName)

async def exportHtml(filePath):
    console.deleteAll()
    cm.saveAsHtml(filePath=filePath)
    console.writeInBox(text=f"{filePath} successfully exported")

async def deleteRow(filePath, id):
    console.deleteAll()
    cm.removeRow(filePath=filePath, rowID=id)
    console.writeInBox(text=f"{id} successfully deleted from {filePath}")

#analyzes files video file in a path if their last modification date has been modified from the one stored inside the csv file
async def update(filePath, scanPath, subFolders, minSize=""):
    minSize = checkMinSize(minSize=minSize)
    console.deleteAll()
    if subFolders:
        console.writeInBox(text="Sub-folders scan option found\n")
    if ".csv" not in filePath:
        filePath += ".csv"
    df = cm.loadCsvFile(filePath=filePath)
    items = df[["JAVID", "LAST_MODIFIED"]].values.tolist()
    fm.files = []
    for file in fm.getFileList(scanPath=scanPath, subFolders=subFolders):
        found = False
        fileName = file.split("\\")[-1].split(".")[0]
        for item in items:
            if fileName == item[0]:
                console.writeInBox(text=f"Found the following file in the csv: {file}\n")
                found = True
                lastModificationDate = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime("%d-%m-%Y %H:%M:%S")
                if lastModificationDate != item[1]:
                    console.writeInBox(text="Last modification date is different, it will be analyzed\n")
                    fileInfo = fm.getVideoData(file=file, minSize=minSize)
                    if fileInfo != "sizeErr":
                        cm.appendRow(filePath=filePath, info=fileInfo)
                else:
                    print(f"Last modification date is the same, it will be skipped\n")
                break
        if not found:
            console.writeInBox(text=f"No row found for the following file in the csv: {file} - It will be now analyzed\n")
            fileInfo = fm.getVideoData(file=file, minSize=minSize)
            cm.appendRow(filePath=filePath, info=fileInfo)
        print("\n\n")
        await asyncio.sleep(0.001)
    console.writeInBox(text=f"Update Successful")
    await multiPart(filePath=filePath)

#same as update, but removes the files that aren't in the path anymore from the csv file
async def trim(filePath, scanPath, subFolders, minSize=None):
    console.deleteAll()
    console.writeInBox(text="Starting trim\n")
    if ".csv" not in filePath:
        filePath += ".csv"
    df = cm.loadCsvFile(filePath=filePath)
    ids = df["JAVID"].values.tolist()
    fm.files = []
    files = fm.getFileList(scanPath=scanPath, subFolders=subFolders)
    files = [file.split("\\")[-1].split(".")[0] for file in files]
    count = 0
    for id in ids:
        if id not in files:
            cm.removeRow(filePath=filePath, rowID=id)
            count += 1
    print(f"TRIM SUCCESSFUL: A total of {count} rows had been eliminated")
    await update(filePath=filePath, scanPath=scanPath, subFolders=subFolders, minSize=minSize)

async def merge(savePath, csv1, csv2):
    console.deleteAll()
    if ".csv" not in savePath:
        savePath += ".csv"
    cm.concatDataFrames(savePath=savePath, filePath1=csv1, filePath2=csv2)
    console.writeInBox(text=f"Merge Successful")

async def compare(savePath, csv1, csv2):
    console.deleteAll()
    if os.path.isfile(savePath):
        print("The path given for the comparison is a file, saving the files inside the same dir as that file")
        dirs = savePath.split("\\")
        dirs.pop(-1)
        savePath = "\\".join(dirs)
        print(savePath)
    elif not os.path.exists(savePath):
        print(f"The following dir doesn't exist, now creating it")
        os.mkdir(savePath)
    cm.compareDataFrames(savePath=savePath, filePath1=csv1, filePath2=csv2)
    console.writeInBox(text=f"Compare Successful\n\n\n")

async def crossCheck(filePath):
    console.deleteAll()
    console.writeInBox(text=f"Cross Check started\n")
    await CrossCheck.main(filePath)
    console.writeInBox(text="Cross Check finished")

def getSecondsFromTimeStamp(timeStamp, splitValue=":"):
    h, m, s = [int(i) for i in timeStamp.split(splitValue)]
    s += 60 * m + 3600 * h
    return s

async def setSort(sortColumn):
    if cm.sortColumn != sortColumn:
        cm.sortColumn = sortColumn
        print(f"Changed sort column to {cm.sortColumn}")

async def multiPart(filePath):
    df = cm.loadCsvFile(filePath=filePath)
    ids = df[JavMetadataGenerator.indexColumnName]
    console.writeInBox(text="\n\nNow checking for multiparts\n")
    multiPartIds = []
    for partID in ids:
        for indicator in multiPartIndicators:
            if indicator in partID:
                console.writeInBox(text=f"Now processing the following id {partID}\n")
                id = partID.split(indicator)[0]
                if id not in multiPartIds:
                    multiPartIds.append(id)
                    videoInfo = cm.getRow(rowID=partID, dataFrame=cm.loadCsvFile(filePath=filePath))
                    videoInfo[JavMetadataGenerator.indexColumnName] = [id]
                    videoInfo["FULL_PATH"] = ["MULTIPART-GENERATED"]
                else:
                    videoInfo = cm.getRow(rowID=id, dataFrame=cm.loadCsvFile(filePath=filePath))
                    partInfo = cm.getRow(rowID=partID, dataFrame=cm.loadCsvFile(filePath=filePath))
                    videoInfo["MB"] = [int(videoInfo["MB"][0]) + int(partInfo["MB"][0])]
                    videoInfo["GB"] = [float(videoInfo["GB"][0]) + float(partInfo["GB"][0])]
                    videoInfo["RUNTIME"] = [int(videoInfo["RUNTIME"][0]) + int(partInfo["RUNTIME"][0])]
                    videoInfo["DURATION"] = [getSecondsFromTimeStamp(videoInfo["DURATION"][0]) + getSecondsFromTimeStamp(partInfo["DURATION"][0])]
                    videoInfo["DURATION"] = [time.strftime("%H:%M:%S", time.gmtime(videoInfo["DURATION"][0]))]
                cm.removeRow(rowID=id, filePath=filePath)
                cm.appendRow(filePath=filePath, info=videoInfo)
    console.writeInBox(text="Multipart check completed")    
    
    

