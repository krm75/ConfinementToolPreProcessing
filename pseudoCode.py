# -*- coding: utf-8 -*-
"""
PSEUDO CODE

Confinement Pre-processing Code
AdvGIS Final Project, Fall 2019

Kim Myers
krm75@duke.edu
"""

# import NHD Plus file for NC HUC of choice from USGS server

# import GEOMORPHONS layer from USGS server

# import HUC boundary form USGS server

# extract GEOMORPHONS raster by HUC boundary mask

# convert clipped GEOMORPHONS raster to polygon

# filter NHD Plus streams

# segment stream networks 

# buffer polylines, with distance weighted by drainage area, to create channel margins

# buffer channel margins to account for digitization error (based on DEM resolution)

# run confinement tool

