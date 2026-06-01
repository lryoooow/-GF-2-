#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : zhaoguanhua
@Email   :
@Time    : 2021/4/2 16:01
@File    : SurfaceReflectance_multiprocess.py
@Software: PyCharm
"""
from multiprocessing import Pool
import os,time,random
import glob
import json
import gdal
from SurfaceReflectance_GF import untar,Block

def long_time_task(name):
    print('run task {} {} ...'.format(name,os.getpid()))
    start=time.time()
    time.sleep(random.random()*3)
    end = time.time()
    print('Task {} runs {} seconds'.format(name,(end-start)))

def atmospheric_correction(file_path,input_dir,output_dir,config):
    print('run task {} {} ...'.format(file_path, os.getpid()))

    file_name = os.path.basename(file_path)
    fileType = file_name[0:2]
    filename_split = file_name.split("_")

    GFType = filename_split[1][:3]     #浼犳劅鍣?    untar_dirname = file_name[:-7]                 #瑙ｅ帇鍚庡奖鍍忔枃浠跺す鍚?    untar_dir = os.path.join(input_dir, untar_dirname)#瑙ｅ帇鍚庡奖鍍忔枃浠跺す璺緞

    print("鏂囦欢" + file_path + "寮€濮嬭В鍘嬬缉")

    try:
        untar(file_path, untar_dir)
    except Exception as e:
        pass

    if GFType == 'WFV':
        tiffFile = glob.glob(os.path.join(untar_dir, "*.tiff"))[0]
        metedata = glob.glob(os.path.join(untar_dir, "*.xml"))[0]

    elif GFType == 'PMS':
        tiffFile = glob.glob(os.path.join(untar_dir, "*MSS*.tiff"))[0]
        metedata = glob.glob(os.path.join(untar_dir, "*MSS*.xml"))[0]

    atcfile_dir = os.path.join(output_dir,untar_dirname) #澶ф皵鏍℃缁撴灉鏂囦欢澶?
    try:
        os.mkdir(atcfile_dir)
    except Exception as e:
        pass
    # print(filename + "瑙ｅ帇缂╁畬鎴?)

    try:
        IDataSet = gdal.Open(tiffFile)
        # print(IDataSet)
    except Exception as e:
        print("鏂囦欢%S鎵撳紑澶辫触" % tiffFile)

    # Block(IDataSet)
    ImageType = os.path.basename(tiffFile)[-9:-6]

    Block(IDataSet, filename_split, atcfile_dir, ImageType, config, metedata,untar_dirname)


if __name__ == '__main__':
    print('Parent process {}'.format(os.getpid()))
    a=time.time()
    script_path = os.path.split(os.path.realpath(__file__))[0]
    #璇诲彇杈愬皠鏍℃鍜屽ぇ姘旀牎姝ｆ墍闇€鍙傛暟:澧炵泭銆佸亸绉诲拰鍏夎氨鍝嶅簲鍑芥暟
    config_file = os.path.join(script_path,"RadiometricCorrectionParameter.json")
    config = json.load(open(config_file))

    input_dir=r"D:\test_data"
    output_dir=r"D:\temp"

    #鑾峰彇褰卞儚鍒楄〃
    GF_files= glob.glob(os.path.join(input_dir,"*.tar.gz"))
    # print(GF_files)

    #杩涚▼姹?    p=Pool(3)
    for gf_file_path in GF_files:
        p.apply_async(atmospheric_correction,args=(gf_file_path,input_dir,output_dir,config,))


    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print("All subprocesses done")
    b=time.time()
    print("鎬绘椂闂?",b-a)
