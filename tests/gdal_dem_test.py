import gdal
import os
import time
import shutil


# dst_path = "/internalCompany/PM2019007_nifs/부산대학교/곰소만_NDVI_고도_150m_005_processed/"
# for root, dirs, files in os.walk('/internalCompany/PM2019007_nifs/부산대학교/곰소만_NDVI_고도_150m_005'):
dst_path = "/externalCompany/PM2019007_nifs/곰소만_pnu/NDVI/#1_고도_150m_processed/"
for root, dirs, files in os.walk('/externalCompany/PM2019007_nifs/곰소만_pnu/NDVI/#1_고도_150m'):
    # dem_1970_hs_ds = gdal.DEMProcessing('', ds_list[0], 'hillshade', format='MEM')
    image_start_time = time.time()
    files.sort()
    for file in files:
        start_time = time.time()

        filename = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        file_path = root + '/' + file

        if extension == '.JPG' or extension == '.jpg':
            print('Read the image - ' + file)
            # https://gis.stackexchange.com/questions/257109/gdaldem-alpha-flag-in-python-bindings-is-missing
            gdal.DEMProcessing(dst_path + file, file_path, "color-relief",
                               colorFilename='NDVI_VGYRM-lut.txt', format='JPEG')
            # colored_vrt = gdal.DEMProcessing('', file_path, "color-relief",
            #                                  colorFilename='NDVI_VGYRM-lut.txt', format='MEM')
            # gdal.Translate(dst_path + file, colored_vrt, format='JPEG')
            print("--- %s seconds ---" % (time.time() - start_time))
        elif extension == ".txt":
            print('Read the image - ' + file)
            shutil.copy(file_path, dst_path + file)
            print("--- %s seconds ---" % (time.time() - start_time))

    print('*** Processing time ***')
    print("--- %s seconds ---" % (time.time() - image_start_time))
