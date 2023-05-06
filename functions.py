import JavMetadataGenerator
import asyncio
import os
import datetime

fm = JavMetadataGenerator.FileManager()
cm = JavMetadataGenerator.CsvManager()

def scanNewCsv(scanPath, fileName):
    if ".csv" not in fileName:
        fileName += ".csv"
    cm.createEmptyCsvFile(filePath=fileName)
    for file in fm.getFileList(scanPath=scanPath):
        file = os.path.join(scanPath, file)
        fileInfo = fm.getVideoData(file=file)
        cm.appendRow(filePath=fileName, info=fileInfo)

def exportHtml(filePath):
    cm.saveAsHtml(filePath=filePath)

def deleteFile(filePath):
    os.remove(filePath)
    print(f"Successfully deleted the following file: {filePath}")

def deleteRow(filePath, id):
    cm.removeRow(filePath=filePath, rowID=id)

#same as update, but removes the files that aren't in the path anymore from the csv file
def trim(filePath, scanPath):
    df = cm.loadCsvFile(filePath=filePath)
    ids = df["JAVID"].values.tolist()
    files = fm.getFileList(scanPath=scanPath)
    files = [file.split("\\")[-1].split(".")[0] for file in files]
    count = 0
    for id in ids:
        if id not in files:
            print(f"No file found for the following id: {id}\nIt will be removed")
            cm.removeRow(filePath=filePath, rowID=id)
            count += 1
    print(f"A total of {count} rows had been eliminated")
    update(filePath=filePath, scanPath=scanPath)

#analyzes files video file in a path if their last modification date has been modified from the one stored inside the csv file
def update(filePath, scanPath):
    df = cm.loadCsvFile(filePath=filePath)
    items = df[["JAVID", "LAST_MODIFIED"]].values.tolist()
    for file in fm.getFileList(scanPath=scanPath):
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

def merge(savePath, csv1, csv2):
    if ".csv" not in savePath:
        savePath += ".csv"
    cm.concatDataFrames(savePath=savePath, filePath1=csv1, filePath2=csv2)

def compare(savePath, csv1, csv2):
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


if __name__ == "__main__":
    df = cm.loadCsvFile(filePath=".\\test.csv")
    items = df[["JAVID", "ADDED"]].values.tolist()
    print(items)
    print(items[0])