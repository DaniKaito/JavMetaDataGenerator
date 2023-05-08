import pandas as pd
import os
import asyncio
import subprocess
from datetime import datetime
import time

indexColumnName = "JAVID"
columnNames = [indexColumnName, "EXTENSION", "FRAME_RATE", "AVERAGE_BIT_RATE", "VIDEO_BIT_RATE", "AUDIO_BIT_RATE", "CODEC", "RESOLUTION", "MB", "GB",
               "RUNTIME", "DURATION", "ADDED", "LAST_MODIFIED", "DAMAGED", "FULL_PATH"]

class CsvManager():
    def __init__(self):
        pass

    #CREATES PANDAS DATAFRAME FROM CSV FILE GIVEN ITS PATH
    def loadCsvFile(self, filePath):
        df = pd.read_csv(filePath)
        return df

    #SAVE A CSV FILE GIVEN ITS PATH AND NEW DATAFRAME
    def saveCsv(self, filePath, dataFrame):
        try:
            dataFrame = dataFrame.sort_values(indexColumnName)
            dataFrame.reset_index(drop=True)
            dataFrame.to_csv(filePath, encoding="utf-8", index=False)
            print(f"Saved the following file: {filePath}")
        except PermissionError as e:
            print("A permission error occurred while saving the file, close it before performing any action on it")

    #CONVERTS A CSV INTO HTML TABLE FOR BETTER VISUALIZATION
    def saveAsHtml(self, filePath):
        fileName = filePath.split("\\")[-1].split(".")[0]
        df = self.loadCsvFile(filePath=filePath)
        df.to_html(fileName + ".html")
        print(f"Converted the following file into html table: {filePath}")

    #CREATES A CSV FILE WITH ONLY COLUMNS
    def createEmptyCsvFile(self, filePath):
        print(f"Creating an empty dataframe")
        df = pd.DataFrame(columns=columnNames)
        self.saveCsv(filePath=filePath, dataFrame=df)

    #ADDS A ROW AT THE END OF A CSV FILE
    def appendRow(self, filePath, info):
        print(f"Adding a new row in the following file: {filePath}")
        info = pd.DataFrame.from_dict(info)
        df = self.loadCsvFile(filePath=filePath)
        df = pd.concat([df, info]).reset_index(drop=True)
        self.saveCsv(filePath=filePath, dataFrame=df)

    #DELETE A ROW INSIDE A CSV FILE GIVEN ITS ID
    def removeRow(self, filePath, rowID, dataFrame=None):
        if dataFrame == None:
            dataFrame = self.loadCsvFile(filePath)
        print(f"The following ID has been removed: {rowID}")
        dataFrame = dataFrame[dataFrame[indexColumnName] != rowID]
        self.saveCsv(filePath, dataFrame)

    #MERGES TO DATAFRAMES AND SAVES THEM IN A NEW CSV FILE
    def concatDataFrames(self, savePath, filePath1, filePath2):
        df1 = self.loadCsvFile(filePath1)
        df2 = self.loadCsvFile(filePath2)
        df = pd.concat([df1, df2]).reset_index(drop=True)
        df = df.drop_duplicates(subset=indexColumnName, keep="first")
        print(f"Merge successful")
        self.saveCsv(savePath, df)

    #WRITES TWO CSV FILES, ONE WITH UNIQUE VALUES AND THE OTHER WITH DUPLICATE VALUES
    def compareDataFrames(self, savePath, filePath1, filePath2):
        print(savePath)
        print(filePath1)
        fileName = filePath1.split("/")[-1]
        print(fileName)
        df1 = self.loadCsvFile(filePath1)
        df2 = self.loadCsvFile(filePath2)
        df1Ids = df1[indexColumnName].tolist()
        df2Ids = df2[indexColumnName].tolist()
        different = []
        equal = []
        for id in df1Ids:
            if id in df2Ids:
                equal.append(id)
            else:
                different.append(id)
        noDupDf = df1[df1[indexColumnName].isin(different)]
        dupDf = df1[df1[indexColumnName].isin(equal)]
        print(f"Compare successful")
        noDupDfPath = os.path.join(savePath, "Different_values-" + fileName)
        print(noDupDfPath)
        dupDfPath = os.path.join(savePath, "equal_values-" + fileName)
        self.saveCsv(filePath=noDupDfPath, dataFrame=noDupDf)
        self.saveCsv(filePath=dupDfPath, dataFrame=dupDf)

    def getRow(self, rowID, dataFrame):
        row = dataFrame.loc[dataFrame[indexColumnName] == rowID].to_dict(orient="list")
        return row

class FileManager():
    def __init__(self):
        self.extensions = ['mp4', 'avi', 'flv', 'wmv', 'mkv', 'asf', 'm4v', 'mpg', 'rmvb', 'mov']
        self.mediaInfoPath = "mediainfo"
        self.logFilePath = ".\\logs"
        self.standardInfoDict = {indexColumnName: [""],
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
        self.files = []

    #CREATES LOG FILES
    def resetLogs(self):
        with open(self.logFilePath, "w") as f:
            print(f"Created the following log file: {self.logFilePath}\n\n")

    #WRITES A RECORD IN THE LOGS
    def writeInLog(self, text, err=None):
        with open(self.logFilePath, "a") as f:
            f.write(text)
            if err != None:
                f.write("\n")
                f.write(err)
            f.write("\n\n")

    #RETURNS TRUE IF A FILE IS A VIDEO
    def isVideo(self, filePath):
        fileExtension = filePath.split(".")[-1]
        if fileExtension in self.extensions:
            return True
        else:
            return  False

    #GET ALL VIDEOS IN A DIR
    def getFileList(self, scanPath, subFolders):
        for file in os.listdir(scanPath):
            filePath = os.path.join(scanPath, file)
            if self.isVideo(filePath=filePath):
                self.files.append(filePath)
            elif os.path.isdir(filePath) and subFolders:
                self.getFileList(scanPath=filePath, subFolders=True)
        return self.files

    #RUNS A MEDIA INFO CLI COMMAND GIVEN THE SOURCE AND PARAMETER TO SEARCH AND THE FILE TO SEARCH IN
    def runMediaInfo(self, stream, outputParameter, filePath):
        result = subprocess.run([self.mediaInfoPath, '--Output=' + stream + ";" + outputParameter, filePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode("utf-8").strip()
        if result.returncode == 0:
            if output == "":
                return "N/A"
            else:
                return output
        else:
            print(f"An error occurred while analyzing the following file: {filePath}\nIt will be logged")
            self.writeInLog(text=filePath, err=output)
            return "err"


    #GET VIDEO METADATA
    def getVideoData(self, file):
        print(f"\n\nNow analyzing the following file: {file}")
        info = self.standardInfoDict
        info["JAVID"] = [file.split("\\")[-1].split(".")[0]]
        info["EXTENSION"] = [file.split(".")[-1]]
        try:
            info["FRAME_RATE"] = [round(float(self.runMediaInfo(stream="Video", outputParameter="%FrameRate%", filePath=file)))]
        except:
            info["FRAME_RATE"] = "N/A"
        info["AVERAGE_BIT_RATE"] = [self.runMediaInfo(stream="General", outputParameter="%OverallBitRate/String%", filePath=file)]
        info["VIDEO_BIT_RATE"] = [self.runMediaInfo(stream="Video", outputParameter="%BitRate/String%", filePath=file)]
        info["AUDIO_BIT_RATE"] = [self.runMediaInfo(stream="Audio", outputParameter="%BitRate/String%", filePath=file)]
        info["CODEC"] = [self.runMediaInfo(stream="Video", outputParameter="%CodecID%", filePath=file)]
        info["RESOLUTION"] = ["x".join([self.runMediaInfo(stream="Video", outputParameter="%Width%", filePath=file),
                                        self.runMediaInfo(stream="Video", outputParameter="%Height%", filePath=file)])]
        info["MB"] = [os.path.getsize(file) // 1048576]
        info["GB"] = [round(info["MB"][0] / 1024, 2)]
        info["DURATION"] = [float(self.runMediaInfo(stream="Video", outputParameter="%Duration%", filePath=file)) // 1000]
        info["RUNTIME"] = [info["DURATION"][0] // 60]
        info["DURATION"] = [time.strftime("%H:%M:%S", time.gmtime(info["DURATION"][0]))]
        info["ADDED"] = [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]
        info["LAST_MODIFIED"] = [datetime.fromtimestamp(os.path.getmtime(file)).strftime("%d-%m-%Y %H:%M:%S")]
        info["FULL_PATH"] = [file]
        print(f"Found the following data:")
        #IF FAILED TO GET A METADATA IT MARKS THE FILE AS DAMAGED
        for key in list(info.keys()):
            print(f"{key} : {info[key]}")
            if info[key] == "err":
                info["DAMAGED"] = "1"
        print("\n")
        return info