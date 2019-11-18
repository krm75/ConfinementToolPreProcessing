# -*- coding: utf-8 -*-
"""
Confinement Pre-processing Code
AdvGIS Final Project, Fall 2019

Kim Myers
krm75@duke.edu
"""

#'HALP NOT OVERWRITING OUTPUT CORRECTLY'
#'ALSO CANNOT PULL GEOMORPHONS FROM WEBSITE'

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

### get the file (this can take a few minutes...)
huc4Url = huc4Folder + "/" + huc4File
if os.path.exists(huc4File):
    print("{} already downloaded, proceeding to unzip folder".format(HUC))
else:
    print("Downloading {}".format(HUC))
    urllib.request.urlretrieve(huc4Url, huc4File)

    
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


arcpy.env.workspace = "..\scratch"
# define HUC8 boundary as NHD WBD layer
HUCboundary = 'NHDPLUS_H_{}_HU4_GDB.gdb\\WBDHU8'.format(HUC[:-4])
plusFlow = 'NHDPLUS_H_{}_HU4_GDB.gdb'.format(HUC[:-4]) + "\\" + "NHDFlowline"
clipOutput = "NHDPlus_{}_Flowline".format(HUC)
# clip NHD Plus line to HUC8 boundary
arcpy.Clip_analysis(plusFlow, HUCboundary, clipOutput)

# filter NHD Plus streams (FCODE 460 = StreamRivers), add option for stream orders
orderLimit = input("What is the lowest stream order you want to include?: ")
#orderLimit = GetParameterAsText(0)
orderLimit = int(orderLimit)


#selectInput = "..\data" + "\\" + clipOutput + ".shp"
plusGDB = 'NHDPLUS_H_{}_HU4_GDB.gdb'.format(HUC[:-4])
vaaTable = plusGDB + "\\" + "NHDPlusFlowlineVAA"
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


arcpy.AddField_management(selectOutput, 'Buff_dist', 'DOUBLE')
calcBuffer = '((6.04*(!TotDASqKm!*0.621371)**0.441))*0.3048+13.716' #calculate channel width in meters
arcpy.CalculateField_management(selectOutput, 'Buff_dist', calcBuffer)

bufferInput = selectOutput
bufferOutput = "NHDPlus_{}_channelMargins.shp".format(HUC)
arcpy.Buffer_analysis(bufferInput, bufferOutput, 'Buff_dist','','','ALL')

# match stream margin spatial reference with geomorphons
outCS = arcpy.SpatialReference(102719)
SMprojectOutput = "{}".format(bufferOutput[:-4]) + "_StatePlane.shp"


# extract GEOMORPHONS raster by HUC boundary mask
# match HUC8 boundary spatial reference with geomorphons
HBprojectOutput = "WBDHU8_StatePlane.shp"

arcpy.Project_management(HUCboundary, HBprojectOutput, outCS)

outExtractByMask = ExtractByMask("..\data\\Geomorphons_of_NC_30ft.tif", HUCboundary)
outExtractByMask.save("Geomorphons_{}_StatePlane.tif".format(HUC))

# filter GEOMORPHONS to valley bottom
# filter types 6, 7, 8, 9, 10
geomorph = "Geomorphons_{}_StatePlane.tif".format(HUC)
outSetNull = SetNull(geomorph, 1, "Value < 6")
outSetNull.save("Geomorphons_{}_ValleyBottom.tif".format(HUC))
valley = "Geomorphons_{}_ValleyBottom.tif".format(HUC)

#'UNABLE TO CREATE MULTIPART POLYGONS BECAUSE ONLY 4 ARGUMENTS ALLOWED AND CAN"T MANAGE ENVIRONMENTS'
# convert clipped GEOMORPHONS raster to polygon
polyOutput = "Geomorphons_{}_ValleyBottom_polygon.shp".format(HUC)
arcpy.RasterToPolygon_conversion(valley, polyOutput)
arcpy.Dissolve_management(polyOutput, "Geomorphons_{}_ValleyBottom_dissolve.shp".format(HUC))


