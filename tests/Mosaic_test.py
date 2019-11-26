import os
import subprocess

working_path1 = '../OTB-7.0.0-Linux64/'
working_path2 = './bin/'
set_env = './otbenv.profile'
mosaic_execution = './otbcli_Mosaic'

dst_path = "/home/innopam-ldm/PycharmProjects/Orthophoto_Maps_Multispectral/tests/"
file_list = [dst_path + "IMG_0200.tif", dst_path + "IMG_0201.tif"]
print(' '.join(file_list))

#change path
os.chdir(working_path1)
# https://stackoverflow.com/questions/13702425/source-command-not-found-in-sh-shell/13702876
subprocess.call(set_env, shell=True)

os.chdir(working_path2)
# subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
#                 ' -comp.feather ' + 'large' + ' -out ' + dst_path + '/mosaic.tif', shell=True)
subprocess.call(mosaic_execution + ' -il ' + ' '.join(file_list) +
                ' -out ' + dst_path + '/mosaic.tif', shell=True)
