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
import geopandas as gpd #http://geopandas.org/io.html

# import NHD Plus file for NC HUC of choice from USGS 

### define HUC
HUC = input("Which HUC4 would you like to analyze?: ")
#HUC = GetParameterAsText(0)
#HUC = '0303'

### set the URLs
ftpFolder = 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/NHDPlus/HU4/HighResolution/GDB/'
hucFile = 'NHDPLUS_H_{}_HU4_GDB.zip'.format(HUC)

### get the file (this can take a few minutes...)
sUrl = ftpFolder + "/" + hucFile
if os.path.exists(hucFile):
    print("{} already downloaded".format(hucFile))
else:
    print("Downloading {}".format(hucFile))
    data = urllib.request.urlretrieve(sUrl, hucFile)

### move NHD Plus zip to desired folder
currentPath = os.getcwd() + "\\" + hucFile
#desiredPath = GetParametersAsText(1)
desiredPath = "..\data" + "\\" + hucFile
shutil.move(currentPath, desiredPath)

### first open the local zip file as a zipFile object
zipObject = zipfile.ZipFile(desiredPath)
zipObject.extractall(path=desiredPath[:-26])
zipObject.close()


'CHECK WITH JOHN IF THIS DATASET IS DOWNLOADABLE'
# import GEOMORPHONS layer from USGS 

answer = input("Is your HUC4 completely within North Carolina? (yes/no): ")
#answer = GetParametersAsText(0)

if answer == 'yes':
    print('The valley bottom layer is being downloaded for you...')
    gUrl = 'https://www.sciencebase.gov/catalog/item/5b72ee50e4b0f5d5787c5720'
    geoFile = 'Geomorphons_of_NC_30ft.tif'
    geoFile, headers = urllib.request.urlretrieve('http://python.org/')
else: print('You will need to download a valley bottom layer.')


# define HUC4 boundary as NHDPlusCatchment layer
boundaryPath = desiredPath[:-26] + "\\" + hucFile[:-4] + ".gdb"
HUCboundary = boundaryPath + "\\" + "NHDPlusCatchment.shp"

'CHECK SLASHES LATER'
