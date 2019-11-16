# -*- coding: utf-8 -*-
"""
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
arcpy.overwriteoutput = True

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

'CAN USE LAYER IN HUC4 GDB'
# define HUC8 boundary as NHD WBD layer
HUCboundary = 'NHD_H_03030002_HU8_GDB.gdb\\WBDHU8'
plusFlow = 'NHDPLUS_H_{}_HU4_GDB.gdb'.format(HUC[:-4]) + "\\" + "NHDFlowline"
clipOutput = "NHDPlus_{}_Flowline".format(HUC)
# clip NHD Plus line to HUC8 boundary
arcpy.Clip_analysis(plusFlow, HUCboundary, clipOutput)

# filter NHD Plus streams (FCODE 460 = StreamRivers), add option for stream orders
orderLimit = input("What is the lowest stream order you want to include?: ")
#orderLimit = GetParameterAsText(0)
orderLimit = int(orderLimit)

'HALP NOT OVERWRITING OUTPUT CORRECTLY'
#selectInput = "..\data" + "\\" + clipOutput + ".shp"
plusGDB = 'NHDPLUS_H_{}_HU4_GDB.gdb'.format(HUC[:-4])
vaaTable = "..\data" + "\\" + plusGDB + "\\" + "NHDPlusFlowlineVAA"
#arcpy.JoinField_management(selectInput, 'ReachCode', vaaTable, 'ReachCode', ['StreamOrde','TotDASqKm'])

if orderLimit == 1:  
    selectOutput = "NHDPlus_{}_Streams.shp".format(HUC)
    whereClause = '"FType" = 460 OR "FType" = 558'
    arcpy.Select_analysis(selectInput, selectOutput, whereClause)
else: 
    selectOutput = "NHDPlus_{}_Streams_{}Order.shp".format(HUC, orderLimit)
    whereClause = '("FType" = 460 OR "FType" = 558) AND "StreamOrde" >= {}'.format(orderLimit)
    arcpy.Select_analysis(selectInput, selectOutput, whereClause)
    
# buffer polylines, with distance weighted by drainage area, to create channel margins
# buffer channel margins to account for digitization error (based on DEM resolution)
### 60 in field calculationg expression account for digitzation error

'ASK DANICA AND JULIE BEST EQUATION TO CONVERT DRAINAGE AREA TO STREAM WIDTH'
arcpy.AddField_management(selectOutput, 'Buff_dist', 'DOUBLE')
calcBuffer = '((6.04*(!TotDASqKm!*0.621371)**0.441))*0.3048+13.716' #calculate channel width in meters
arcpy.CalculateField_management(selectOutput, 'Buff_dist', calcBuffer)

bufferInput = selectOutput
bufferOutput = "..\data\\NHDPlus_{}_channelMargins.shp".format(HUC)
arcpy.Buffer_analysis(bufferInput, bufferOutput, 'Buff_dist','','','ALL')




