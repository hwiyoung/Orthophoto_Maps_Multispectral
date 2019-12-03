import gdal

# dem_1970_hs_ds = gdal.DEMProcessing('', ds_list[0], 'hillshade', format='MEM')

colored_vrt = gdal.DEMProcessing('', 'IMG_0323.jpg', "color-relief", colorFilename='NDVI_VGYRM-lut.txt', format='MEM')
gdal.Translate("colored_dem.tif", colored_vrt)
