import asyncio
import csv
import enum
from time import sleep, time_ns
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import aiohttp
from bs4 import BeautifulSoup
from random import randint

driver = None

class TableKeys(enum.Enum):
        JAVID:str='JAVID'
        EXTENSION:str='EXTENSION'
        FRAME_RATE:str='FRAME_RATE'
        AVERAGE_BIT_RATE:str='AVERAGE_BIT_RATE'
        VIDEO_BIT_RATE:str='VIDEO_BIT_RATE'
        AUDIO_BIT_RATE:str='AUDIO_BIT_RATE'
        CODEC:str='CODEC'
        RESOLUTION:str='RESOLUTION'
        MB:str='MB'
        GB:str='GB'
        RUNTIME:str='RUNTIME'
        DURATION:str='DURATION'
        ADDED:str='ADDED'
        LAST_MODIFIED:str='LAST_MODIFIED'
        DAMAGED:str='DAMAGED'
        FULL_PATH:str='FULL_PATH'

async def checkID(javid:str):
    dmmSearchURL="https://www.dmm.co.jp/monthly/premium/-/list/search/=/?searchstr="
    ris=f"{javid}:"
    '''
    DMM Search ID with double zero
    '''
    print("Searching on DMM with double zero..")
    driver.get(dmmSearchURL+(javid.replace("-","00")))
    if driver.title =="":
        btns=driver.find_elements(By.CLASS_NAME,"ageCheck__btn")
        btns[1].click()

    films=driver.find_elements(By.CSS_SELECTOR,"ul#list>li")
    results=len(films)
    if results==1: 
        link=films[0].find_element(By.CSS_SELECTOR,"div>a").get_attribute('href')
        parts=link.split('/')
        codename=""
        for part in parts:
            if "cid" in part:
                codename=part.split('=')[1]
        return ris+link+"\n"
    '''
    DMM Search ID without zero
    '''
    sleep(randint(1, 3))
    print("Searching on DMM without zero..")
    driver.get(dmmSearchURL+(javid.replace("-","")))    
    films=driver.find_elements(By.CSS_SELECTOR,"ul#list>li")
    results=len(films)
    if results==1: 
        link=films[0].find_element(By.CSS_SELECTOR,"div>a").get_attribute('href')
        parts=link.split('/')
        codename=""
        for part in parts:
            if "cid" in part:
                codename=part.split('=')[1]
        return ris+link+"\n"
    '''
    Search on MaxJAV
    '''
    sleep(randint(1, 3))
    print("Searching on MaxJAV..")
    urlMaxJav=f"https://maxjav.com/?s={javid}"
    driver.get(urlMaxJav)
    delay = 30
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.post > h2.title')))
        if not "Error 404 - Not Found" in myElem.text:
            print("JAV found on MaxJAV.")
            posts=driver.find_elements(By.CSS_SELECTOR,".post.type-post")
            if len(posts)>1:
                return ris+urlMaxJav+"\n"
            link=posts[0].find_element(By.CSS_SELECTOR,"h2.title > a").get_attribute("href")
            return ris+link+"\n"
    except TimeoutException:
        print(f"Page took too much to load, timer was {delay} seconds javid:{javid}")
    except Exception as e:
        print(e)
    '''
    Search on JavTrailers
    '''
    sleep(randint(1, 3))
    print("Searching on JavTrailers..")
    javTrailerSearchURL="https://javtrailers.com/search/"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(javTrailerSearchURL+javid) as response:
            if response.status==200:
                try:
                    resp=await asyncio.wait_for(response.read(),15)
                    soup=BeautifulSoup(resp,"html.parser")
                    javCards=soup.select("div.card-container")
                    for card in javCards:
                        link=card.find("a").get('href')
                        if javid.replace("-","0").lower() in str(link).lower() or javid.replace("-","").lower() in str(link).lower() or javid.replace("-","00").lower() in str(link).lower() :
                            link="https://javtrailers.com"+card.find("a").get('href')
                            async with session.get(link) as response2:
                                if response2.status==200:
                                    try:
                                        resp=await asyncio.wait_for(response2.read(),15)
                                        soup2=BeautifulSoup( resp,"html.parser")
                                        element=soup2.select("div#info-row > div:nth-child(2) > p:nth-child(2)")
                                        return ris+link+"\n" 
                                    except TimeoutError:
                                        print(f"JavTrailer took too long.")                                    
                                else:
                                    print(f"Request to {link} failed, response {response2}")
                except TimeoutError:
                    print(f"JavTrailer took too long.")

            else:
                print(f"Request to {javTrailerSearchURL+javid} failed, response {response}")
    return ris+"No results"+"\n"

def readCsv(fileName):
    rowsList=[]
    with open(fileName,"r") as file:
        r=csv.reader(file,delimiter=",")    
        i=0
        for row in r:
            tableDict=dict()
            j=0
            for key in TableKeys:
                tableDict[key]=row[j]
                j+=1
            rowsList.append(tableDict)           
            i+=1
    return rowsList

async def main(fileName):
    global driver
    driver = uc.Chrome()
    rowList=readCsv(f"{fileName}")
    rowList.pop(0)
    for row in rowList:
        print(row[TableKeys.JAVID])
        beggining=time_ns()
        ris=await checkID(row[TableKeys.JAVID])
        print(f"{(time_ns()-beggining)//1000000000} seconds to complete the search.")
        with open(f"{fileName.split('.')[0]}.txt","a") as file:                   
            file.write(ris)
        sleep(1)
