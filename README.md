# Orthophoto_Maps_Multispectral
Orthophoto_Maps is a mapping software that generate individual maps(orthophotos) from multispectral images(especially drone). Only with images and sensor data, you can generate orthophotos of area of interests.

## Getting Started
* Run OrthophotoMultiSpectral.py with **<u>Data</u>** folder
  * The **<u>Data</u>** folder will be updated
* Data folder is constructed with aligned multi-band images

## Input & Output
* Input - ./Data
  * Images to rectify
* Output
  * Individual orthophotos - .tif(GeoTIFF)

## Flow of functions in this module
1. Extract metadata(focal length, sensor width) from the image
2. Extract an array from each band
3. Extract EOP from metadata of each band
    1. Convert coordinate to planar coordinate system
    2. System calibration
4. Extract a projected boundary of the image
5. Compute GSD & Boundary size
6. Compute coordinates of the projected boundary
7. Back-projection into camera coordinate system
8. Resample the pixels
9. createGeoTiff
10. Mosaic individual orthophotos for each band
11. Merge 3-band to one image
12. Generate tiles