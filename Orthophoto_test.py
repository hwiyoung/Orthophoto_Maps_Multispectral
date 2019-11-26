import os
import numpy as np
import cv2
import time
from ExifData import getMetadataExiv2
from EoData import readEOfromMetadata, convertCoordinateSystem, Rot3D
from Boundary import boundary
from BackprojectionResample import projectedCoord, backProjection, resample, createGeoTiff
from system_calibration import calibrate
import subprocess
import gdal2tiles

if __name__ == '__main__':
    ground_height = 45  # unit: m, Chungju

    # 190911
    R_CB = np.array(
        [[0.990635238726878, 0.135295782209043, 0.0183541578119133],
         [-0.135993334134149, 0.989711806459606, 0.0444561944563446],
         [-0.0121505910810649, -0.0465359159242159, 0.998842716179817]], dtype=float)

    # # 191126
    # R_CB = np.array(
    #     [[0.999048294872098, -0.0225558651674755, 0.0373327933551652],
    #      [0.00684675563259514, 0.926395499861564, 0.376489707393907],
    #      [-0.0430769828384060, -0.375875791695593, 0.925668279010764]], dtype=float)

    # # 191126_2
    # R_CB = np.array(
    #     [[0.998890698610195, -0.00497321615644135, 0.0468256270764031],
    #      [-0.0130299574357571, 0.926387629906560, 0.376345824163534],
    #      [-0.0452503308193368, -0.376538479145450, 0.925295186026369]], dtype=float)

    dst_path = '/internalCompany/PM2019007_nifs/DKC/chungju/cj_000_thumbnails_orthophotos/'
    # dst_path = '/internalCompany/PM2019007_nifs/DKC/gomso_1024_1025/orthophoto2/'
    file_list = []

    for root, dirs, files in os.walk('/internalCompany/PM2019007_nifs/DKC/chungju/cj_000_thumbnails'):
    # for root, dirs, files in os.walk('/internalCompany/PM2019007_nifs/DKC/gomso_1024_1025/gomso_1024_300_001_002_thumbnails'):
        files.sort()
        for file in files:
            image_start_time = time.time()
            start_time = time.time()

            filename = os.path.splitext(file)[0]
            extension = os.path.splitext(file)[1]
            file_path = root + '/' + file

            if extension == '.JPG' or extension == '.jpg':
                print('Read the image - ' + file)
                image = cv2.imread(file_path, -1)

                # 1. Extract metadata from the image
                focal_length, sensor_width = getMetadataExiv2(file_path)  # unit: m, mm
                # pixel_size = sensor_width / image_cols  # unit: mm/px
                pixel_size = 0.00375  # unit: mm/px
                pixel_size = pixel_size / 1000  # unit: m/px

                image_rows = image.shape[0]
                image_cols = image.shape[1]

                end_time = time.time()
                print("--- %s seconds ---" % (time.time() - start_time))

                read_time = end_time - start_time

                print('Read EOP - ' + file)
                # eo = read_eo_2(file_path)
                eo = readEOfromMetadata(file_path)
                # eo[-1] = eo[-1] - 15*np.pi/180
                eo = convertCoordinateSystem(eo)
                print(eo)

                # System Calibration
                OPK = calibrate(eo[3], eo[4], eo[5], R_CB)
                eo[3:] = OPK

                # if abs(OPK[0]) > 30*(np.pi/180) or abs(OPK[1]) > 30*(np.pi/180):
                #     print('Too much omega/phi will kill you')
                #     continue

                print('Easting | Northing | Altitude | Omega | Phi | Kappa')
                print(eo)
                R = Rot3D(eo)

                # 4. Extract a projected boundary of the image
                bbox = boundary(image, eo, R, ground_height, pixel_size, focal_length)
                print("--- %s seconds ---" % (time.time() - start_time))

                # 5. Compute GSD & Boundary size
                # GSD
                gsd = (pixel_size * (eo[2] - ground_height)) / focal_length  # unit: m/px
                # Boundary size
                boundary_cols = int((bbox[1, 0] - bbox[0, 0]) / gsd)
                boundary_rows = int((bbox[3, 0] - bbox[2, 0]) / gsd)

                # 6. Compute coordinates of the projected boundary
                print('projectedCoord')
                start_time = time.time()
                proj_coords = projectedCoord(bbox, boundary_rows, boundary_cols, gsd, eo, ground_height)
                print("--- %s seconds ---" % (time.time() - start_time))

                # Image size
                image_size = np.reshape(image.shape[0:2], (2, 1))

                # 6. Back-projection into camera coordinate system
                print('backProjection')
                start_time = time.time()
                backProj_coords = backProjection(proj_coords, R, focal_length, pixel_size, image_size)
                print("--- %s seconds ---" % (time.time() - start_time))

                # 7. Resample the pixels
                print('resample')
                start_time = time.time()
                b, g, r, a = resample(backProj_coords, boundary_rows, boundary_cols, image)
                print("--- %s seconds ---" % (time.time() - start_time))

                # 8. Create GeoTiff
                print('Save the image in GeoTiff')
                start_time = time.time()
                dst = dst_path + filename
                createGeoTiff(b, g, r, a, bbox, gsd, boundary_rows, boundary_cols, dst)
                print("--- %s seconds ---" % (time.time() - start_time))

                file_list.append(dst + '.tif')

                print('*** Processing time per each image')
                print("--- %s seconds ---" % (time.time() - image_start_time + read_time))

    # 10. Mosaic individual orthophotos for each band
    working_path1 = './OTB-7.0.0-Linux64/'
    working_path2 = './bin/'
    set_env = './otbenv.profile'
    mosaic_execution = './otbcli_Mosaic'

    start_time = time.time()
    os.chdir(working_path1)     # change path
    # https://stackoverflow.com/questions/13702425/source-command-not-found-in-sh-shell/13702876
    subprocess.call(set_env, shell=True)

    os.chdir(working_path2)
    # subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
    #                 ' -comp.feather ' + 'large' +
    #                 ' -out ' + dst_path + 'IMG_RGB.tif', shell=True)
    subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
                    ' -out ' + dst_path + 'IMG_RGB.tif', shell=True)
    print("--- %s seconds ---" % (time.time() - start_time))

    # 12. Generate tiles
    options = {'zoom': (14, 21)}
    gdal2tiles.generate_tiles(dst_path + 'IMG_RGB.tif', dst_path + '/tiles/', **options)

