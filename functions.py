import JavMetadataGenerator
import asyncio
import os
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

fm = JavMetadataGenerator.FileManager()
cm = JavMetadataGenerator.CsvManager()

async def scanJavlibraryURL(javLibraryURL, newCsvFilePath, compareCsvFilePath, excludeCsvFilePath):
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
        excludeIds = cm.loadCsvFile(filePath=excludeCsvFilePath)['JAVID'].values.tolist()
    else:
        excludeIds = []
    for javID in javidList:
        if javID not in excludeIds:
            if javID in compareIds:
                videoData = cm.getRow(rowID=javID, dataFrame=compareDf)
            else:
                videoData = fm.standardInfoDict
                videoData[JavMetadataGenerator.indexColumnName] = javID
            cm.appendRow(filePath=newCsvFilePath, info=videoData)

async def scanNewCsv(scanPath, fileName, subFolders=False):
    if subFolders:
        print(f"SUB-FOLDERS SCAN OPTION FOUND")
    if ".csv" not in fileName:
        fileName += ".csv"
    cm.createEmptyCsvFile(filePath=fileName)
    fm.files = []
    for file in fm.getFileList(scanPath=scanPath, subFolders=subFolders):
        file = os.path.join(scanPath, file)
        fileInfo = fm.getVideoData(file=file)
        cm.appendRow(filePath=fileName, info=fileInfo)
        await asyncio.sleep(0.001)
    print(f"NEW CSV FILE CREATED WITH SUCCESS")

async def exportHtml(filePath):
    cm.saveAsHtml(filePath=filePath)

async def deleteRow(filePath, id):
    cm.removeRow(filePath=filePath, rowID=id)

#same as update, but removes the files that aren't in the path anymore from the csv file
async def trim(filePath, scanPath, subFolders):
    if subFolders:
        print(f"SUB-FOLDERS SCAN OPTION FOUND")
    if ".csv" not in filePath:
        filePath += ".csv"
    df = cm.loadCsvFile(filePath=filePath)
    ids = df["JAVID"].values.tolist()
    fm.files = []
    files = fm.getFileList(scanPath=scanPath)
    files = [file.split("\\")[-1].split(".")[0] for file in files]
    count = 0
    for id in ids:
        if id not in files:
            print(f"No file found for the following id: {id}. It will be removed")
            cm.removeRow(filePath=filePath, rowID=id)
            count += 1
    print(f"TRIM SUCCESSFUL: A total of {count} rows had been eliminated")
    update(filePath=filePath, scanPath=scanPath)

#analyzes files video file in a path if their last modification date has been modified from the one stored inside the csv file
async def update(filePath, scanPath, subFolders):
    if subFolders:
        print(f"SUB-FOLDERS SCAN OPTION FOUND")
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
                print(f"Found the following file in the csv: {file}")
                found = True
                lastModificationDate = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime("%d-%m-%Y %H:%M:%S")
                if lastModificationDate != item[1]:
                    print("Last modification date is different, it will be analyzed")
                    fileInfo = fm.getVideoData(file=file)
                    cm.appendRow(filePath=filePath, info=fileInfo)
                else:
                    print(f"Last modification date is the same, it will be skipped")
                break
        if not found:
            print(f"No row found for the following file in the csv: {file}\nIt will be now analyzed")
            fileInfo = fm.getVideoData(file=file)
            cm.appendRow(filePath=filePath, info=fileInfo)
        print("\n\n")
        await asyncio.sleep(0.001)
    print(f"UPDATE SUCCESSFUL")

async def merge(savePath, csv1, csv2):
    if ".csv" not in savePath:
        savePath += ".csv"
    cm.concatDataFrames(savePath=savePath, filePath1=csv1, filePath2=csv2)
    print(f"MERGE SUCCESSFUL")

async def compare(savePath, csv1, csv2):
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
    print(f"COMPARE SUCCESSFUL")