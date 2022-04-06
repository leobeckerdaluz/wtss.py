#
# This file is part of Python Client Library for WTSS.
# Copyright (C) 2022 INPE.
#
# Python Client Library for WTSS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""This example shows how to use a shapely geometry for the request."""

import os

import shapely.geometry

from wtss import *

BDC_AUTH_CLIENT_SECRET = os.getenv("BDC_AUTH_CLIENT_SECRET", None)
WTSS_SERVER_URL = os.getenv("WTSS_SERVER_URL", None)

service = WTSS(url=WTSS_SERVER_URL, access_token=BDC_AUTH_CLIENT_SECRET)

coverage = service['MOD13Q1-6']

"""
geometry can be a GeoJSON, a GeoJSON string or a shapely object. Also,
you can use latitude and longitude parameters instead of geom.

In this example, the geometry is a shapely object that is created based
on a GeoJSON, but it could be an shapely object based on a shapefile.
"""

geom_shapely = shapely.geometry.shape({"type":"Polygon","coordinates":[[[-54,-12],[-53.99,-12],[-53.99,-11.99],[-54,-11.99],[-54,-12]]]})


timeseries = coverage.ts(attributes = ['NDVI','EVI'],
                        geom = geom_shapely,
                        start_datetime = '2017-01-01',
                        end_datetime = '2017-02-01T00:00:00Z')

print('\nTIMESERIES:')
print('number of pixels:', timeseries.number_of_pixels)
print('NDVI:', timeseries.NDVI)
print('timeline:', timeseries.timeline)


summarize = coverage.summarize( attributes = ['NDVI','EVI'],
                                geom = geom_shapely,
                                start_datetime = '2017-01-01', 
                                end_datetime = '2017-02-01', 
                                applyAttributeScale = False)

print('\nSUMMARIZE:')
print('NDVI mean:', summarize.NDVI.mean)
print('timeline:', summarize.timeline)