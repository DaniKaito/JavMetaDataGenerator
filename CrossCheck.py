import asyncio
import csv
import enum
from time import sleep, time_ns
import undetected_chromedriver as uc
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import aiohttp
from bs4 import BeautifulSoup
from random import randint

driver = None


LOGGER:logging.Logger=logging.getLogger(__name__)
file_handler = logging.FileHandler('logfile.log')
formatter    = logging.Formatter('%(asctime)s: %(message)s')
file_handler.setFormatter(formatter)
LOGGER.addHandler(file_handler)

class TableKeys(enum.Enum):
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
        FULL_PATH_FILENAME:str='Full_path_filename'



async def controllaID(javid:str):
    urlRicerca="https://www.dmm.co.jp/monthly/premium/-/list/search/=/?searchstr="
    ris=f"{javid}:"
    '''
    Test con id con gli zeri
    
    '''
    print("Cerco su dmm00")
    driver.get(urlRicerca+(javid.replace("-","00")))
    if driver.title =="":
        btns=driver.find_elements(By.CLASS_NAME,"ageCheck__btn")
        btns[1].click()

    films=driver.find_elements(By.CSS_SELECTOR,"ul#list>li")
    numeroRisultati=len(films)
    if numeroRisultati==1: 
        #https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=1sdde00300/?i3_ref=search&i3_ord=1
        link=films[0].find_element(By.CSS_SELECTOR,"div>a").get_attribute('href')
        parts=link.split('/')
        codename=""
        for part in parts:
            if "cid" in part:
                codename=part.split('=')[1]

        
        return ris+link+"\n"
    '''
    Test con id senza niente
    
    '''
    sleep(randint(1, 3))
    print("Cerco su dmmNiente")
    driver.get(urlRicerca+(javid.replace("-","")))    
    films=driver.find_elements(By.CSS_SELECTOR,"ul#list>li")
    numeroRisultati=len(films)
    if numeroRisultati==1: 
        #https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=1sdde00300/?i3_ref=search&i3_ord=1
        link=films[0].find_element(By.CSS_SELECTOR,"div>a").get_attribute('href')
        parts=link.split('/')
        codename=""
        for part in parts:
            if "cid" in part:
                codename=part.split('=')[1]

        
        return ris+link+"\n"
    sleep(randint(1, 3))
    print("Cerco su maxjav")
    urlMaxJav=f"https://maxjav.com/?s={javid}"
    driver.get(urlMaxJav)
    delay = 30 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.post > h2.title')))
        if not "Error 404 - Not Found" in myElem.text:
            print("post presente su maxjav")
            posts=driver.find_elements(By.CSS_SELECTOR,".post.type-post")
            if len(posts)>1:
                return ris+urlMaxJav+"\n"
            linkerino=posts[0].find_element(By.CSS_SELECTOR,"h2.title > a").get_attribute("href")
            # .post.type-post
            return ris+linkerino+"\n"
    except TimeoutException:
        LOGGER.error(f"Page took too much to load, timer was {delay} seconds javid:{javid}")
    except Exception as e:
        LOGGER.error(e)
    
    '''
    qui cerco su javtrailers
    '''
    sleep(randint(1, 3))
    print("Cerco su javtrailers")
    javTrailerSearchURL="https://javtrailers.com/search/"
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(javTrailerSearchURL+javid) as response:
            if response.status==200:
                try:
                    risp=await asyncio.wait_for(response.read(),15)
                    soup=BeautifulSoup(risp,"html.parser")
                    # print("Cerco le card")
                    javCards=soup.select("div.card-container")
                    for card in javCards:
                        link=card.find("a").get('href')
                        # print(javid," ",link)
                        if javid.replace("-","0").lower() in str(link).lower() or javid.replace("-","").lower() in str(link).lower() or javid.replace("-","00").lower() in str(link).lower() :
                            link="https://javtrailers.com"+card.find("a").get('href')
                            async with session.get(link) as response2:
                                if response2.status==200:
                                    try:
                                        risp=await asyncio.wait_for(response2.read(),15)
                                        soup2=BeautifulSoup( risp,"html.parser")
                                        element=soup2.select("div#info-row > div:nth-child(2) > p:nth-child(2)")
                                        #element.pop().text
                                        return ris+link+"\n" 
                                    except TimeoutError:
                                        LOGGER.error(f"Javtrailer2 took too long {javid}")
                                        print(f"Javtrailer2 took too long ")                                    
                                else:
                                    LOGGER.error(f"Request2 to {link} failed, response {response2}")
                except TimeoutError:
                    LOGGER.error(f"Javtrailer1 took too long {javid}")
                    print(f"Javtrailer1 took too long ")

            else:
                LOGGER.error(f"Request to {javTrailerSearchURL+javid} failed, response {response}")
    return ris+"No result"+"\n"

def readCsv(fileName):
    rowsList=[]
    with open(fileName,"r") as file:
        r=csv.reader(file,delimiter=",")    
        i=0
        for row in r:
            tableDict=dict()
            j=0
            for key in TableKeys:
                #print(key,row[j])
                tableDict[key]=row[j]
                j+=1
            rowsList.append(tableDict)           
            i+=1
    return rowsList

"""
Dato il javid da csv togliere i javid presenti in un altro csv e scrivere su un file le coppie(JAVID,URL(dmm o javtrailers))



tu vuoi il codename di quelli con null e quelli che non null DOPO aver fatto la sottrazione

"""

async def main(fileName):
    global driver
    driver = uc.Chrome(use_subprocess=True,headless=True)
    rowList=readCsv(f"{fileName}")
    rowList.pop(0)
    for row in rowList:
        print(row[TableKeys.JAVID])
        inizio=time_ns()
        ris=await controllaID(row[TableKeys.JAVID])
        print(f"Ci ho messo {(time_ns()-inizio)/1000000000} secondi ")
        with open(f"{fileName.split('.')[0]}.txt","a") as file:                   
            file.write(ris)
        sleep(1)
