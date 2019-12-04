from __future__ import print_function
import argparse
import os
import numpy as np
import cv2
import time
from EoData import read_eo, convertCoordinateSystem, Rot3D
from Boundary import boundary
from BackprojectionResample import projectedCoord, backProjection, resample, createGeoTiff
from system_calibration import calibrate
import subprocess
from progress import Broadcaster
import socket


PROGRESS_BROADCAST_PORT = 6367 #ODMR
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except:
    print("Cannot create UDP socket, progress reporting will be disabled.")
    sock = None
progressbc = Broadcaster(PROGRESS_BROADCAST_PORT)

def main():
    parser = argparse.ArgumentParser(description='This code is written for practice about argparse')
    parser.add_argument('--project-path', type=str, help='The project path')
    parser.add_argument('project_name', type=str, help='The project name')
    args = parser.parse_args()

    project_path = args.project_path
    project_name = args.project_name

    ########## Settings for showing progress ##########
    progressbc.set_project_name(project_name)

    ########## Run the processing function ##########
    rectify(project_path, project_name)


def rectify(path, name):
    print(path, name)

    ground_height = 0               # unit: m
    height_threshold = 100          # unit: m
    focal_length = 5 / 1000         # unit: m
    pixel_size = 0.00375 / 1000     # unit: m/px

    # 190911
    R_CB = np.array(
        [[0.990635238726878, 0.135295782209043, 0.0183541578119133],
         [-0.135993334134149, 0.989711806459606, 0.0444561944563446],
         [-0.0121505910810649, -0.0465359159242159, 0.998842716179817]], dtype=float)

    dst_path = path + "/" + name + '/odm_orthophoto/'
    if not (os.path.isdir(dst_path)):
        os.mkdir(dst_path)

    dst_path2 = path + "/" + name + '/odm_individual_orthophoto/'
    if not (os.path.isdir(dst_path2)):
        os.mkdir(dst_path2)

    file_list = []
    for root, dirs, files in os.walk(path + "/" + name + '/images'):
        files.sort()
        count = 0
        len_files = len(files)
        for file in files:
            filename = os.path.splitext(file)[0]
            extension = os.path.splitext(file)[1]
            file_path = root + '/' + file

            if extension == '.JPG' or extension == '.jpg':
                print('Read the image - ' + file)
                image = cv2.imread(file_path, -1)

            elif extension == '.txt':
                print('Read EOP - ' + file)
                eo = read_eo(file_path, 3)
                eo = convertCoordinateSystem(eo)

                if eo[2] - ground_height <= height_threshold:
                    print("The height of the image is too low: ", eo[2] - ground_height, " m")
                    return "The height of the image is too low"

                # System Calibration
                OPK = calibrate(eo[3], eo[4], eo[5], R_CB)
                eo[3:] = OPK
                print(eo)

                if abs(OPK[0]) > 30*(np.pi/180) or abs(OPK[1]) > 30*(np.pi/180):
                    print('Too much omega/phi will kill you')
                    return

                R = Rot3D(eo)

                # 4. Extract a projected boundary of the image
                bbox = boundary(image, eo, R, ground_height, pixel_size, focal_length)

                # 5. Compute GSD & Boundary size
                # GSD
                gsd = (pixel_size * (eo[2] - ground_height)) / focal_length  # unit: m/px
                print("GSD: ", gsd)
                # Boundary size
                boundary_cols = int((bbox[1, 0] - bbox[0, 0]) / gsd)
                boundary_rows = int((bbox[3, 0] - bbox[2, 0]) / gsd)
                print(boundary_rows, boundary_cols)

                # 6. Compute coordinates of the projected boundary
                proj_coords = projectedCoord(bbox, boundary_rows, boundary_cols, gsd, eo, ground_height)

                # Image size
                image_size = np.reshape(image.shape[0:2], (2, 1))

                # 6. Back-projection into camera coordinate system
                backProj_coords = backProjection(proj_coords, R, focal_length, pixel_size, image_size)

                # 7. Resample the pixels
                b, g, r, a = resample(backProj_coords, boundary_rows, boundary_cols, image)

                # 8. Create GeoTiff
                dst = dst_path2 + filename
                createGeoTiff(b, g, r, a, bbox, gsd, boundary_rows, boundary_cols, dst)

                # file_list.append("../../" + dst + '.tif')   # in relative path
                file_list.append(dst + '.tif')   # in absolute path

                count += 1
                progressbc.send_update(count / len_files * 100 * 0.9)



    # 10. Mosaic individual orthophotos for each band
    working_path1 = './OTB-7.0.0-Linux64/'
    working_path2 = './bin/'
    set_env = './otbenv.profile'
    mosaic_execution = './otbcli_Mosaic'

    start_time = time.time()
    os.chdir(working_path1)  # change path
    # https://stackoverflow.com/questions/13702425/source-command-not-found-in-sh-shell/13702876
    subprocess.call(set_env, shell=True)

    os.chdir(working_path2)
    # subprocess.call("ls", shell=True)
    print(file_list)
    # subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
    #                 ' -comp.feather ' + 'large' +
    #                 ' -out ' + dst_path + 'IMG_RGB.tif', shell=True)
    # subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
    #                 ' -out ' + "../../" + dst_path + 'odm_orthophoto.tif', shell=True)  # in relative path
    subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
                    ' -out ' + dst_path + 'odm_orthophoto.tif', shell=True)  # in absolute path
    print("--- %s seconds ---" % (time.time() - start_time))

    progressbc.send_update(100)
    print("Sent!")


if __name__ == "__main__":
    main()
