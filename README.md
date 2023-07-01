# JavMetaDataGenerator

Easy to use GUI to generate metadata for Japanese Adult Videos in a csv format, that allows cross-check, compare with other csv, merge between csv, export to html, and more features!

![alt text]([https://github.com/DaniKaito/JavItManager/blob/main/preview.png](https://github.com/DaniKaito/JavMetaDataGenerator/blob/main/preview.png)?raw=true)

## Description

JavMetaDataGenerator allows to create a csv file with metadata from video files, allowing a better search of all the JAV by ID, so you won't need to use windows search to quickly search files, and also you can use that csv file to cross-check on various websites (DMM,MaxJAV,JavTrailers) to search for videos if you need to upgrade the quality of them, or get missing ones from actress/studios/tags after you generate a csv for them using the JavLibrary feature.
You can also update/trim the csv files without having to re-scan all the videos, all the features support multiparts videos, the name must end with _X or -ptX (X = part number)

## Download
If you don't want to install the script with all the python dependancies, you can go to the releases and download the latest compiled version, but you will need to follow step 3 to 5 (MediaInfo download + add to enviroment windows path).

## Installation for the script
1. Install the latest python version from: 
https://www.python.org/downloads/ (tick add to PATH option)
2. Install the python depencies, by running this command on CMD: 
    pip install -r requirements.txt
3. Download latest CLI version of MediaInfo from here: 
https://mediaarea.net/it/MediaInfo/Download/Windows
4. Exctract the folder to C:\mediainfo (create the folder)
5. Add MediaInfo to Windows PATH Enviroment Variables, if you don't know how to do it follow this guide: 
https://www.educative.io/answers/how-to-add-an-application-path-to-system-environment-variables
6. Run the script using: 
    python GUI.py

## Functions:
- `CREATE CSV FILE`: you need to insert first the file name/path of the new CSV file, insert the PATH where the video files are located, enable the Search in subfolders if you have multiple folders to scan in the path, if you have some small files that you want to skip (for example trailers) insert the minimum file size that will be scanned.

- `UPDATE CSV FILE`: insert the CSV file path that you want to update, insert the path where the videos are located, enable the Search in subfolders if you have multiple folders to scan in the path, if you have some small files that you want to skip (for example trailers) insert the minimum file size that will be scanned, the UPDATE button will add videos from the new path, if they are not already present or if their last modification date is different from the one in the csv file, TRIM will remove videos that are not in the new scanned path, and proceed to do the same thing as the UPDATE button.

- `COMPARE/MERGE CSV FILE`: insert the main csv file/path as input, insert the secondary csv file/path, and the name of the new merged file, with the MERGE button it will MERGE both CSV with priority to the main CSV (when it comes to duplicate JAVIDs), COMPARE will generates 2 CSV files inside a folder, the first CSV file will have duplicate values found by comparing JAVIDs, while the other will have only unique values (based on main csv).

- `JAVLIBRARY SEARCH FEATURE`: you will need to input first the JAVlibrary URL (it can be from an actress/studio/tag etc) it can have one or more pages of pagination, then you will need to insert the new CSV file name/path and the CSV file that will be excluded from the creation of the new one (JAVIDs to exclude, for example collection, you will need to generate it first), after the crawling is completed you will obtain a new csv file containing all the JAVIDs from the JAVLIBRARY URL, with the values from the first CSV (if you actually have those JAVIDs) filled, if not they will be empty + the excluded ones will not be inserted at all.

- `DELETE`: will let you choose first the csv file/path and the JAVID of the row you want to delete from the CSV.

- `EXPORT AS HTML`: you need to insert the csv file/path and it will export it as an HTML table, to read it better.

- `CROSS CHECK`: you will need to insert the csv file/path and it will generate a txt file with all the URLs from DMM/MaxJAV/Javtrailers of the IDS in that CSV.

- `SORTING METHOD`: by default it's selected JAVID, it will be used from all the below functions (create, update, compare/merge) and you can select other sorting methods like Size by MB, Duration, Average Bit Rate and Video Bit Rate, you can also insert the csv file/path to sort it.

### License
    GNU GPLv3
