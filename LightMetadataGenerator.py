import sqlite3
from enum import Enum
from sqlitedict import SqliteDict
import os
import sys
import ffmpeg
from pprint import pprint
from math import floor
import traceback
import time
from time import sleep
from datetime import datetime
import csv
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


LOGGER:logging.Logger=logging.getLogger(__name__)
file_handler = logging.FileHandler('logfile.log')
formatter    = logging.Formatter('%(asctime)s: %(message)s')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)
DB: str = 'jav'
MAXDEPTH: int = 3
extensions = ['mp4', 'avi', 'flv', 'wmv',
              'mkv', 'asf', 'm4v', 'mpg', 'rmvb', 'mov']

PROGRESS = 0
MAXPROGRESS = 0

#sqlite3 connection
conn = sqlite3.connect(".".join([DB, "sqlite3"]))
cursor = conn.cursor()

#to be modified
class TableKeys(Enum):
        JAVID:str='JAVID'
        EXTENSION:str='Extension'
        FRAME_RATE:str='Frame_Rate'
        BIT_RATE:str='Bit_Rate'
        CODEC:str='Codec'
        RESOLUTION:str='Resolution'
        MB:str='MB'
        GB:str='GB'
        RUNTIME:str='Runtime'
        DURATION:str='Duration'
        ADDED:str='Added'
        LAST_MODIFIED:str='Last_Modified'
        DAMAGED:str='Damaged'
        FULL_PATH_FILENAME:str="Full_path_filename"

#to be modified
class MetadataKeys(Enum):
    STREAMS:str="streams"
    HEIGHT:str="height"
    WIDTH:str="width"
    EXT:str="ext"
    NAME:str="name"
    SIZEMB:str="sizeMB"
    SIZEGB:str="sizeGB"
    DURATIONSECS:str="durationSecs"
    BITRATE:str="bit_rate"
    DURATIONMINTOTAL:str="durationMinTotal"
    DURATIONHH:str="durationHH"
    DURATIONMM:str="durationMM"
    DURATIONSS:str="durationSS"
    FRAMERATE:str="framerate"
    CODECNAME:str="codec_name"
    AVGFRAMERATE:str="avg_frame_rate"
    RFRAMERATE:str="r_frame_rate"
    FORMAT:str="format"
    DURATION:str="duration"
    RESOLUTION:str="resolution"

#to be modified
class Record:
    def __init__(self, JAVID: str, extension: str, frame_rate: int, bit_rate: int, codec: str, resolution: str, MB: int, GB: float, runtime: int, hh: str,mm:str,ss:str, added: str, last_modified: str, damaged: int,full_path_filename:str):
        self.JAVID = JAVID
        self.extension = extension
        self.frame_rate = frame_rate
        self.bit_rate = bit_rate
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
        

#need to be modified
def exportToCsv(tableName=None, path=None, **kwargs):
    if tableName == None:
        return
    table=load(tablename=tableName,cache_name=DB)
    with open(os.path.join(path,f'{DB}-{tableName}.csv'), 'w', newline='') as csvfile:
            fieldnames=[key._value_ for key in TableKeys]
            # fieldnames = ['JAVID', 'Extension','Frame_Rate','Bit_Rate','Codec','Resolution','MB','GB','Runtime','Duration','Added','Last_Modified','Damaged']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=',')
            writer.writeheader()
            keys=list(table.keys())
            keys.sort()
            #for key,value in table.items():
            for key in keys:
                value=table[key]
                if "criteria" in kwargs:
                    if not kwargs['criteria'](value):
                        continue

                writer.writerow({
                    TableKeys.JAVID._value_: value.JAVID,                     
                    TableKeys.EXTENSION._value_:value.extension,
                    TableKeys.FRAME_RATE._value_:value.frame_rate,
                    TableKeys.BIT_RATE._value_:value.bit_rate,
                    TableKeys.CODEC._value_:value.codec,
                    TableKeys.RESOLUTION._value_:value.resolution,
                    TableKeys.MB._value_:value.MB,
                    TableKeys.GB._value_:value.GB,
                    TableKeys.RUNTIME._value_:value.runtime,
                    TableKeys.DURATION._value_:value.duration,
                    TableKeys.ADDED._value_:value.added,
                    TableKeys.LAST_MODIFIED._value_:value.last_modified,
                    TableKeys.DAMAGED._value_:value.damaged,
                    TableKeys.FULL_PATH_FILENAME._value_:value.full_path_filename                    
                    })
    print(f"Table exported into {os.path.join(path,f'{DB}-{tableName}.csv')}")

            

def save(key, value, tablename, cache_name="cache"):
    cache_file = str(cache_name)+".sqlite3"
    try:
        with SqliteDict(cache_file, tablename=tablename) as mydict:
            #print("i'm saving ", key, " ", type(key), " ", str(value)[:15], " ", type(value), "in table:", tablename)
            if value == None:
                raise ValueError("value was None")
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()
    except Exception as ex:
        traceback.print_exc()
        print("Error during storing data (Possibly unsupported):", ex)


def load(tablename, cache_name="cache"):
    cache_file = str(cache_name)+".sqlite3"
    try:
        with SqliteDict(cache_file, tablename=tablename) as mydict:
            ris = dict(mydict)
        return ris
    except Exception as ex:
        print("Error during loading data:", ex)
        return None


def saveTable(table: dict, tablename='cache', cache_name="cache",printMessages=True):
    cache_file = str(cache_name)+".sqlite3"
    try:
        with SqliteDict(cache_file, tablename=tablename) as mydict:
            if printMessages:
                print("i'm overwriting :", tablename)
            mydict.clear()
            if printMessages:
                print("I'm saving the new table ", end="")
            for key, value in table.items():
                mydict[key] = value
                if printMessages:
                    print(".", end="")
            mydict.commit()
            if printMessages:
                print()
    except Exception as ex:
        LOGGER.error(traceback.format_exc())
        traceback.print_exc()

def getTableNames(dbname):
    filename=dbname+".sqlite3"
    tableNames=SqliteDict.get_tablenames(filename)
    resultList=[]
    for table in tableNames:
        with SqliteDict(filename,tablename=table) as tab:
            if len(dict(tab))>0:
                resultList.append(table)
    return resultList

#Added for the GUI
def getTables(dbname):
    filename = dbname + ".sqlite3"
    tableNames = SqliteDict.get_tablenames(filename)
    return tableNames


def isMedia(file):
    for ext in extensions:
        if ext in file:
            return True
    return False


def getNameFileList(path,depth=0,fileNameList:list=[]):
    if depth>MAXDEPTH:
        return fileNameList
    for item in os.listdir(path):
        if '.' in str(item) and str(item).find('.')!=0:
            if os.path.isdir(os.path.join(path, item)):
                ris=getNameFileList(os.path.join(path, item),depth+1,[])
                for item in ris:
                    fileNameList.append(item)
            else:
                
                parts=str(item).split(".")
                if len(parts)==2:
                    fileName = parts[0] 
                else:
                    fileName=""
                    for i in range(len(parts)):
                        if i<(len(parts)-1):
                            fileName+=parts[i]
                fileNameList.append(fileName)
    
    return fileNameList

#TO MODIFY FOR NEW COLUMNS
def analyzeFiles(mPath,tableName,mode='w' ,depth=0, metadata=list(), filesAnalyzed=dict()):
    """
    This function analyze the files in the given path and ,depending on the mode, it will save them on the table given
    """
    if tableName == "DEFAULT":
        tableName = ""

    global PROGRESS

    if depth > MAXDEPTH:
        return
    if os.path.exists(mPath):
        for item in os.listdir(mPath):

            if os.path.isdir(os.path.join(mPath, item)):
                analyzeFiles(os.path.join(mPath, item),tableName,depth=depth+1, metadata=metadata,filesAnalyzed=filesAnalyzed)
            else:
                PROGRESS += 1
                fileName = str(item).split(".")[0]
                if fileName in filesAnalyzed:
                    lastModificationDateDb=filesAnalyzed[fileName].last_modified
                else:
                    lastModificationDateDb=None
                p = os.path.join(mPath, item)
                lastModificationTime = os.path.getmtime(p)
                lastModificationDate = datetime.fromtimestamp(lastModificationTime).strftime('%Y-%m-%d %H:%M:%S')
                if fileName not in filesAnalyzed or lastModificationDateDb != lastModificationDate:
                    if isMedia(item.split(".")[-1]):
                        print(item)
                        print(p)
                        try:
                            meta_dict = ffmpeg.probe(p)
                        except Exception as e:
                            print(e)
                            print("Failed to extract metadata, the JAV will be marked as damaged.")
                            if " " not in str(item):
                                tmp = str(item).split(".")
                            else:
                                tmp = []
                                tmp.append(str(item).split(" ")[0])
                                tmp.append(str(item).split(".")[-1])

                            ts = time.time()
                            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            save(tmp[0],Record(tmp[0],tmp[1],0,0,'0','0',0,0,0,'00','00','00',timestamp,lastModificationDate,1,str(p)),tableName,DB)
                            continue
                        ris = None
                        if MetadataKeys.STREAMS._value_ in meta_dict:
                            if MetadataKeys.HEIGHT._value_ in meta_dict[MetadataKeys.STREAMS._value_][0]:
                                ris = getMetadata(meta_dict[MetadataKeys.STREAMS._value_][0])
                            else:
                                for item in meta_dict[MetadataKeys.STREAMS._value_]:
                                    if MetadataKeys.HEIGHT._value_ in item:
                                        ris = getMetadata(item)
                            if ris != None and ris != {}:
                                ris[MetadataKeys.EXT._value_] = [x for x in extensions if x in os.path.basename(p)][0]
                                if " " not in os.path.basename(p):
                                    ris[MetadataKeys.NAME._value_] = os.path.basename(p).split(".")[0]
                                else:
                                    ris[MetadataKeys.NAME._value_] = os.path.basename(p).split(" ")[0]
                                ris[MetadataKeys.SIZEMB._value_] = round(os.path.getsize(p)/1048576)
                                ris[MetadataKeys.SIZEGB._value_] = round(ris[MetadataKeys.SIZEMB._value_]/1024, 2)

                                if MetadataKeys.DURATIONSECS._value_ not in ris:
                                    ris[MetadataKeys.DURATIONSECS._value_] = meta_dict[MetadataKeys.FORMAT._value_][MetadataKeys.DURATION._value_]
                                '''
                                if 'bit_rate' not in ris:
                                    ris['bit_rate']=int(int(meta_dict[MetadataKeys.FORMAT._value_]['bit_rate'])/1000)
                                '''
                                # nuova riga , per rimuovere questa modifica cancellare la riga sotto e
                                # togliere commento alla parte sopra e dentro la funzione getMetadata
                                ris[MetadataKeys.BITRATE._value_] = int(int(meta_dict[MetadataKeys.FORMAT._value_][MetadataKeys.BITRATE._value_])/1000)

                                ris[MetadataKeys.DURATIONMINTOTAL._value_] = int(float(ris[MetadataKeys.DURATIONSECS._value_])/60)
                                ris[MetadataKeys.DURATIONHH._value_] = floor(ris[MetadataKeys.DURATIONMINTOTAL._value_]/60)
                                ris[MetadataKeys.DURATIONMM._value_] = ris[MetadataKeys.DURATIONMINTOTAL._value_] % 60
                                ris[MetadataKeys.DURATIONSS._value_] = int(float(ris[MetadataKeys.DURATIONSECS._value_]) % 60)
                                if MetadataKeys.FRAMERATE._value_ not in ris:
                                    ris[MetadataKeys.FRAMERATE._value_] = 0
                                ts = time.time()
                                timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                                if "w" in mode:
                                    save(ris[MetadataKeys.NAME._value_],Record(ris[MetadataKeys.NAME._value_],ris[MetadataKeys.EXT._value_],ris[MetadataKeys.FRAMERATE._value_],ris[MetadataKeys.BITRATE._value_],ris[MetadataKeys.CODECNAME._value_],ris[MetadataKeys.RESOLUTION._value_],ris[MetadataKeys.SIZEMB._value_],ris[MetadataKeys.SIZEGB._value_],ris[MetadataKeys.DURATIONMINTOTAL._value_],ris[MetadataKeys.DURATIONHH._value_], ris[MetadataKeys.DURATIONMM._value_],ris[MetadataKeys.DURATIONSS._value_], timestamp, lastModificationDate,0,str(p)),tableName,DB)


                                #insert="insert into " + tableName + " values('{}','{}',{},{},'{}','{}',{},{},{},'{}:{}:{}','{}','{}',0)".format(ris[MetadataKeys.NAME._value_],ris['ext'],ris['framerate'],ris[MetadataKeys.BITRATE._value_],ris['codec_name'],str(ris['resolution']),ris['sizeMB'],ris['sizeGB'],ris[MetadataKeys.DURATIONMINTOTAL._value_],ris[MetadataKeys.DURATIONHH._value_],ris[MetadataKeys.DURATIONMM._value_],ris[MetadataKeys.DURATIONSS._value_], timestamp, lastModficationDate)

                                metadata.append(ris)
    return None




metadataNeeded = ['avg_frame_rate', 'bit_rate',
                  'codec_name', 'height', 'width', 'duration']


def getMetadata(metaDict: dict):
    ris = dict()
    if MetadataKeys.AVGFRAMERATE._value_ in metaDict:
        if metaDict[MetadataKeys.AVGFRAMERATE._value_] == '0/0':
            if MetadataKeys.RFRAMERATE._value_ in metaDict:
                tmp = metaDict[MetadataKeys.RFRAMERATE._value_].split("/")
                tmp[1] = int(tmp[1])
                if tmp[1] != 0:
                    tmp = round(int(tmp[0])/tmp[1])
                    ris[MetadataKeys.FRAMERATE._value_] = tmp
        else:
            tmp = metaDict[MetadataKeys.AVGFRAMERATE._value_].split("/")
            tmp[1] = int(tmp[1])
            if tmp[1] != 0:
                tmp = round(int(tmp[0])/tmp[1])
                ris[MetadataKeys.FRAMERATE._value_] = tmp
    
    if MetadataKeys.CODECNAME._value_ in metaDict:
        ris[MetadataKeys.CODECNAME._value_] = metaDict[MetadataKeys.CODECNAME._value_]
    if MetadataKeys.HEIGHT._value_ in metaDict and MetadataKeys.WIDTH._value_ in metaDict:
        ris['resolution'] = str(
            str(metaDict[MetadataKeys.WIDTH._value_])+'x'+str(metaDict[MetadataKeys.HEIGHT._value_]))
    if MetadataKeys.DURATION._value_ in metaDict:
        ris[MetadataKeys.DURATIONSECS._value_] = metaDict[MetadataKeys.DURATION._value_]
    return ris


def getLastModificationDate(javid:str,filesAnalyzed:set):
    try:
        for file in filesAnalyzed:
            if file!= None and file.JAVID.lower()==javid.lower():
                return file.last_modified
    except:
        return


def createTable(tableName=None):
    print(tableName)
    try:
        tableNames=getTables(DB)
    except OSError:
        tableNames=None
        pass
    if tableNames != None:
        if tableName in tableNames:
            return
    # if not os.path.exists(DB+".sqlite3"):
    #     open(DB+".sqlite3","w")
                        
    saveTable({},tableName,DB,False)
    return tableName

def scanNewTable(tableName=None, path=".\\testPath"):
    tableName=createTable(tableName=tableName)
    while True:
        if os.path.exists(path):
            break
        else:
            return
    analyzeFiles(path,tableName)
    return


def trim(tableName, filesAnalyzed, path, execute=True):
    if tableName == "DEFAULT":
        tableName = ""

    if not execute:
        return
    try:
        print("TRIM")
        fileInThePath=getNameFileList(path)
        fileInThePath=set(fileInThePath)
        newTableValue=dict()
        for name,value in filesAnalyzed.items():
            if name in fileInThePath:
                newTableValue[name]=value
        saveTable(newTableValue,tableName,DB)
        analyzeFiles(path,tableName,"w",filesAnalyzed=newTableValue)
    except FileNotFoundError:
       pass


def export1080p(tableName=None, path=None):
    if tableName == None:
        return
    exportToCsv(tableName=tableName, path=path, criteria=lambda value:"1080" in value.resolution.split('x')[1] and (value.bit_rate<5900 or value.bit_rate>6100))

def deleteTable(tableName):
    query = "DROP TABLE " + tableName
    cursor.execute(query)
    print("table dropped: " + tableName)
    conn.commit()
    return
    #saveTable({},tableName,DB,False)
    #print(f"Table {tableName} deleted")
    
def scanJavlibraryURL(javLibraryURL):
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
        LOGGER.error(traceback.format_exc())
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
                LOGGER.error(traceback.format_exc())
                break
            for link in links:
                javidList.append(link.get_attribute("title").split(" ")[0])
        time.sleep(3)
    return javidList

#TO MODIFY NewTABLEDICT VALUES FOR NEW COLUMNS
def compareTableFromURL(tableName, javLibraryURL):

    javidsFromURL=scanJavlibraryURL(javLibraryURL)
    newTableName = tableName
    newTableName=createTable(newTableName)
    newTableDict=dict()
    table=load(tableName,DB)
    for javid in javidsFromURL:
        if javid in table:
            newTableDict[javid]=table[javid]
        else:
            newTableDict[javid]=Record(javid,"0",0,0,"0","0",0,0,0,"0","0","0","0","0",0,"0")
    saveTable(newTableDict,newTableName,DB)

def merge(table1, table2):
    newTableName = "MERGE".join([table1, table2])
    query = " ".join(["CREATE TABLE", newTableName, "AS SELECT * FROM", table1, "UNION ALL SELECT * FROM", table2])
    print(query)
    cursor.execute(query)
    conn.commit()
    return

def deleteRecord(tableName, JAVID):
    table=load(tableName,DB)
    if JAVID in table:
        table.pop(JAVID)
        saveTable(table,tableName,DB,False)
        print(f"The record with JAVID {JAVID} was removed")



def readCsv(path):
    """
    Read a given csv only if the format is right, 
    returns the rowlist [dict(Tablekeys:value)] if it succeed ,None otherwise.
    Raises FileNotFoundError if the given path doesn't exists
    """
    rowsList=[]
    if not os.path.exists(path):
        raise FileNotFoundError()
    with open(path,"r") as file:
        r=csv.reader(file,delimiter=",")    
        i=0       
        #keys=[key._value_ for key in TableKeys]
        for row in r:
            tableDict=dict()
            if i==0:
                if not row==[key._value_ for key in TableKeys]:
                    print(row)
                    print("Not equal to")
                    print([key._value_ for key in TableKeys])
                    message=f"{path} table doesn't have the correct format,actual format : {row} expected format {[key._value_ for key in TableKeys]}"
                    LOGGER.info(message)
                    print(message)                    
                    return None
                else:
                    i+=1
                    continue
            j=0
            for key in TableKeys:
                #print(key,row[j])
                tableDict[key]=row[j]
                j+=1
            rowsList.append(tableDict)           
            i+=1
    return rowsList

#TO MODIFY FOR NEW COLUMNS
def importCSV(path=None, tableName=None):
    rowList=[]
    try:
        rowList=readCsv(path)
        if rowList == None:
            raise ValueError("AN ERROR OCCURED WHILE LOADING THE CSV")
        if len(rowList)==0:
            raise ValueError("EMPTY CSV")
    except FileNotFoundError :
        LOGGER.error(traceback.format_exc())
        print("The given path to the csv doesn't exist, try again")
    #rowlist [dict(Tablekeys:value)]
    createTable(tableName=tableName)
    tableDict=dict()#key JAVID, value Record
    for row in rowList:
        if len(row)>0:
            parts=row[TableKeys.DURATION].split(":")
            hh=parts[0]
            mm=parts[1]
            ss=parts[2]
            tableDict[row[TableKeys.JAVID]]=Record(row[TableKeys.JAVID],
            row[TableKeys.EXTENSION],
            row[TableKeys.FRAME_RATE],
            row[TableKeys.BIT_RATE],
            row[TableKeys.CODEC],
            row[TableKeys.RESOLUTION],
            row[TableKeys.MB],
            row[TableKeys.GB],
            row[TableKeys.RUNTIME],
            hh,
            mm,
            ss,
            row[TableKeys.ADDED],
            row[TableKeys.LAST_MODIFIED],
            row[TableKeys.DAMAGED],
            row[TableKeys.FULL_PATH_FILENAME]
            )
    saveTable(tableDict,tableName,DB)


def compareTables(firstTableName=None, secondTableName=None):
    print(firstTableName)
    firstTable=load(firstTableName,DB)
    secondTable=load(secondTableName,DB)
    #JAVID,Record
    firstResultDict=dict()
    secondResultDict=dict()

    for JAVID,value in firstTable.items():
        if JAVID not in secondTable:
            firstResultDict[JAVID]=value

    for JAVID,value in firstTable.items():
        if JAVID in secondTable:
            secondResultDict[JAVID]=value

    t1Name = "MINUS".join([firstTableName, secondTableName])
    t2Name = "INTERSECT".join([firstTableName, secondTableName])
    print("Table for the first result(1-2):")
    newTable1=createTable(tableName=t1Name)
    print("Table for the second result(1interesect2):")
    newTable2=createTable(tableName=t2Name)
    saveTable(firstResultDict,newTable1,DB)
    saveTable(secondResultDict,newTable2,DB)