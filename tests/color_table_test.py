import gdal

# specify GeoTIFF file name, open it using GDAL and get the first band
fn = 'IMG_0323.jpg'
ds = gdal.Open(fn)
band = ds.GetRasterBand(1)

# create color table
colors = gdal.ColorTable()

# set color for each value
colors.SetColorEntry(0, (255, 255, 255))
colors.SetColorEntry(1, (250, 250, 250))
colors.SetColorEntry(2, (246, 246, 246))
colors.SetColorEntry(3, (242, 242, 242))
colors.SetColorEntry(4, (238, 238, 238))
colors.SetColorEntry(5, (233, 233, 233))
colors.SetColorEntry(6, (229, 229, 229))
colors.SetColorEntry(7, (225, 225, 225))
colors.SetColorEntry(8, (221, 221, 221))
colors.SetColorEntry(9, (216, 216, 216))

# set color table and color interpretation
band.SetRasterColorTable(colors)
band.SetRasterColorInterpretation(gdal.GCI_PaletteIndex)

# close and save file
del band, ds