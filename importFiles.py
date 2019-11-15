# -*- coding: utf-8 -*-
"""
IMPORT FILES FROM USGS

Confinement Pre-processing Code
AdvGIS Final Project, Fall 2019

Kim Myers
krm75@duke.edu
"""
# import modules
import os
import arcpy
import shutil
import urllib
import zipfile #https://pymotw.com/2/zipfile/
#import geopandas as gpd #http://geopandas.org/io.html

##### import NHD Plus (HUC4) and NHD (HUC8) GDBs for NC HUC of choice from USGS 

### define HUC
HUC = input("Which HUC8 would you like to analyze?: ")
#HUC = GetParameterAsText(0)
#HUC = '0303'

### set the URLs
huc4Folder = 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/NHDPlus/HU4/HighResolution/GDB/'
huc4File = 'NHDPLUS_H_{}_HU4_GDB.zip'.format(HUC[:-4])
huc8Folder = 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/NHD/HU8/HighResolution/GDB/'
huc8File = 'NHD_H_{}_HU8_GDB.zip'.format(HUC)

### get the file (this can take a few minutes...)
huc4Url = huc4Folder + "/" + huc4File
huc8Url = huc8Folder + "/" + huc8File
if os.path.exists(huc4File):
    print("{} already downloaded, proceeding to unzip folder".format(huc8File))
else:
    print("Downloading {}".format(huc8File))
    urllib.request.urlretrieve(huc4Url, huc4File)
    urllib.request.urlretrieve(huc8Url, huc8File)
    
arcpy.env.workspace = "..\data"
for file in arcpy.ListFiles("NHD*.zip"):
    ### move NHD Plus zip to desired folder
    currentPath = os.getcwd() + "\\" + file
    #desiredPath = GetParametersAsText(1)
    desiredPath = "..\data" + "\\" + file
    shutil.move(currentPath, desiredPath)
    ### first open the local zip file as a zipFile object
    zipObject = zipfile.ZipFile(desiredPath)
    zipObject.extractall(path="..\data")
    zipObject.close()
    
    
# import GEOMORPHONS layer from USGS 

##answer = input("Is your HUC8 completely within North Carolina? (yes/no): ")
#answer = GetParametersAsText(0)

##if answer == 'yes':
    ##print('The valley bottom layer is being downloaded for you...')
    ##gUrl = 'https://www.sciencebase.gov/catalog/item/5b72ee50e4b0f5d5787c5720'
    ##geoFile = 'Geomorphons_of_NC_30ft.tif'
    ##geoFile, headers = urllib.request.urlretrieve('http://python.org/')
##else: print('You will need to download a valley bottom layer.')


# define HUC8 boundary as NHDPlusCatchment layer
boundaryPath = desiredPath[:-26] + "\\" + huc8File[:-4] + ".gdb"
HUCboundary = boundaryPath + "\\" + "WBDHU8.shp"
