#! usr/bin/env python
# -*- coding:utf-8 -*-
# created by zhaoguanhua 2017/9/25
# SurfaceReflectance for Landsat8

import glob
import os
import sys
import tarfile
import re
import gdal
import numpy
from Py6S import *
from osgeo import gdal
import pdb
import shutil
import argparse
from .base import MeanDEM

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--Input_dir',type=str,help='Input dir',default=None)
    parser.add_argument('--Output_dir',type=str,help='Output dir',default=None)

    return parser.parse_args(argv)

# 閫愭尝娈佃緪灏勫畾鏍?def RadiometricCalibration(BandId):
    # LandSat8 TM杈愬皠瀹氭爣鍙傛暟
    global data2,ImgRasterData
    parameter_OLI = numpy.zeros((9,2))

    #璁＄畻杈愬皠浜害鍙傛暟
    parameter_OLI[0,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_1.+',data2)[0]).split("=")[1])
    parameter_OLI[1,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_9.+',data2)).split("=")[1])

    parameter_OLI[0,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_1.+',data2)[0]).split("=")[1])
    parameter_OLI[1,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_9.+',data2)).split("=")[1])

    Gain = parameter_OLI[int(BandId) - 1,0]
    Bias = parameter_OLI[int(BandId) - 1,1]

    RaCal = numpy.where(ImgRasterData>0 ,Gain * ImgRasterData + Bias,-9999)
    return (RaCal)

# 6s澶ф皵鏍℃
def SurfaceReflectance(BandId):
    global data
    # 6S妯″瀷
    s = SixS()

    s.geometry = Geometry.User()
    s.geometry.solar_z = 90-float(''.join(re.findall('SUN_ELEVATION.+',data2)).split("=")[1])
    s.geometry.solar_a = float(''.join(re.findall('SUN_AZIMUTH.+',data2)).split("=")[1])
    s.geometry.view_z = 0
    s.geometry.view_a = 0


    # 鏃ユ湡
    Dateparm = ''.join(re.findall('DATE_ACQUIRED.+',data2)).split("=")
    Date = Dateparm[1].split('-')

    s.geometry.month = int(Date[1])
    s.geometry.day = int(Date[2])

    # 涓績缁忕含搴?    point1lat = float(''.join(re.findall('CORNER_UL_LAT_PRODUCT.+',data2)).split("=")[1])
    point1lon = float(''.join(re.findall('CORNER_UL_LON_PRODUCT.+',data2)).split("=")[1])
    point2lat = float(''.join(re.findall('CORNER_UR_LAT_PRODUCT.+',data2)).split("=")[1])
    point2lon = float(''.join(re.findall('CORNER_UR_LON_PRODUCT.+',data2)).split("=")[1])
    point3lat = float(''.join(re.findall('CORNER_LL_LAT_PRODUCT.+',data2)).split("=")[1])
    point3lon = float(''.join(re.findall('CORNER_LL_LON_PRODUCT.+',data2)).split("=")[1])
    point4lat = float(''.join(re.findall('CORNER_LR_LAT_PRODUCT.+',data2)).split("=")[1])
    point4lon = float(''.join(re.findall('CORNER_LR_LON_PRODUCT.+',data2)).split("=")[1])

    sLongitude = (point1lon + point2lon + point3lon + point4lon) / 4
    sLatitude = (point1lat + point2lat + point3lat + point4lat) / 4

    # 澶ф皵妯″紡绫诲瀷
    if sLatitude > -15 and sLatitude <= 15:
        s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)

    if sLatitude > 15 and sLatitude <= 45:
        if s.geometry.month > 4 and s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeWinter)

    if sLatitude > 45 and sLatitude <= 60:
        if s.geometry.month > 4 and s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticWinter)

    # 姘旀憾鑳剁被鍨嬪ぇ闄?    s.aero_profile = AtmosProfile.PredefinedType(AeroProfile.Continental)

    # 鐩爣鍦扮墿锛燂紵锛燂紵锛燂紵
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.36)

    # 550nm姘旀憾鑳跺厜瀛﹀帤搴?鏍规嵁鏃ユ湡浠嶮ODIS澶勮幏鍙栥€?    #s.visibility=40.0
    s.aot550 = 0.14497

    # 閫氳繃鐮旂┒鍘诲尯鐨勮寖鍥村幓姹侱EM楂樺害銆?    pointUL = dict()
    pointDR = dict()
    pointUL["lat"] = point1lat
    pointUL["lon"] = point1lon
    pointDR["lat"] = point4lat
    pointDR["lon"] = point2lon
    meanDEM = (MeanDEM(pointUL, pointDR)) * 0.001

    # 鐮旂┒鍖烘捣鎷斻€佸崼鏄熶紶鎰熷櫒杞ㄩ亾楂樺害
    s.altitudes = Altitudes()
    s.altitudes.set_target_custom_altitude(meanDEM)
    s.altitudes.set_sensor_satellite_level()

    # 鏍℃娉㈡锛堟牴鎹尝娈靛悕绉帮級
    if BandId == '1':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B1)

    elif BandId == '2':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B2)

    elif BandId == '3':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B3)

    elif BandId == '4':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B4)

    elif BandId == '5':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B5)

    elif BandId == '6':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B6)

    elif BandId == '7':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B7)

    elif BandId == '8':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B8)

    elif BandId == '9':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B9)

    # 涓嬪灚闈㈤潪鍧囦竴銆佹湕浼綋
    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)

    # 杩愯6s澶ф皵妯″瀷
    s.run()

    xa = s.outputs.coef_xa
    xb = s.outputs.coef_xb
    xc = s.outputs.coef_xc
    x = s.outputs.values
    return (xa, xb, xc)

if __name__ == '__main__':

    #杈撳叆鏁版嵁璺緞
    RootInputPath = parse_arguments(sys.argv[1:]).Input_dir
    RootOutName = parse_arguments(sys.argv[2:]).Output_dir

    #鍒涘缓鏃ュ織鏂囦欢
    LogFile = open(os.path.join(RootOutName,'log.txt'),'w')

    for root,dirs,RSFiles in os.walk(RootInputPath):

        #鍒ゆ柇鏄惁杩涘叆鏈€搴曞眰
        if len(dirs)==0:
            #鏍规嵁杈撳叆杈撳嚭璺緞寤虹珛鐢熸垚鏂版枃浠剁殑璺緞
            RootInputPathList = RootInputPath.split(os.path.sep)
            RootList = root.split(os.path.sep)
            StartList = len(RootInputPathList)
            EndList = len(RootList)
            outname = RootOutName
            for i in range(StartList,EndList):
                if os.path.exists(os.path.join(outname,RootList[i]))==False:
                    os.makedirs(os.path.join(outname,RootList[i]))
                    outname=os.path.join(outname,RootList[i])
                else:
                    outname=os.path.join(outname,RootList[i])

            MeteDatas = glob.glob(os.path.join(root,'*MTL.txt'))

            for MeteData in MeteDatas:
                pass

            f = open(MeteData)
            data = f.readlines()
            data2 =' '.join(data)
            
            shutil.copyfile(MeteData,os.path.join(outname,os.path.basename(MeteData)))

            if len(os.path.basename(MeteData))<10:

                RSbands = glob.glob(os.path.join(root,"B0[1-8].tiff"))
            else:
                RSbands = glob.glob(os.path.join(root,"*B[1-8].TIF"))
            print('褰卞儚'+root+'寮€濮嬪ぇ姘旀牎姝?)
            print(RSbands)
            for tifFile in RSbands:

                BandId = (os.path.basename(tifFile).split('.')[0])[-1]

                #鎹曟崏鎵撳紑鏁版嵁鍑洪敊寮傚父
                try:
                    IDataSet = gdal.Open(tifFile)
                except Exception as e:
                    print("鏂囦欢%S鎵撳紑澶辫触" % tifFile)
                    LogFile.write('\n'+tifFile+'鏁版嵁鎵撳紑澶辫触')

                if IDataSet == None:
                    LogFile.write('\n'+tifFile+'鏁版嵁闆嗚鍙栦负绌?)
                    continue
                else:
                    #鑾峰彇琛屽垪鍙?                    cols = IDataSet.RasterXSize
                    rows = IDataSet.RasterYSize
                    ImgBand = IDataSet.GetRasterBand(1)
                    ImgRasterData = ImgBand.ReadAsArray(0, 0, cols, rows)

                    if ImgRasterData is None:
                        LogFile.write('\n'+tifFile+'鏍呮牸鏁版嵁涓虹┖')
                        continue
                    else:
                        #璁剧疆杈撳嚭鏂囦欢璺緞
                        outFilename=os.path.join(outname,os.path.basename(tifFile))

                        #濡傛灉鏂囦欢瀛樺湪灏辫烦杩囷紝杩涜涓嬩竴娉㈡鎿嶄綔
                        if os.path.isfile(outFilename):
                            print("%s宸茬粡瀹屾垚" % outFilename)
                            continue
                        else:
                            # #杈愬皠鏍℃
                            RaCalRaster = RadiometricCalibration(BandId)
                            #澶ф皵鏍℃
                            a, b, c = SurfaceReflectance(BandId)
                            y = numpy.where(RaCalRaster!=-9999,a * RaCalRaster - b,-9999)
                            atc = numpy.where(y!=-9999,(y / (1 + y * c))*10000,-9999)
                            
                            driver = IDataSet.GetDriver()
                            #杈撳嚭鏍呮牸鏁版嵁闆?                            outDataset = driver.Create(outFilename, cols, rows, 1, gdal.GDT_Int16)

                            # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?                            geoTransform = IDataSet.GetGeoTransform()
                            outDataset.SetGeoTransform(geoTransform)
                            proj = IDataSet.GetProjection()
                            outDataset.SetProjection(proj)

                            outband = outDataset.GetRasterBand(1)
                            outband.SetNoDataValue(-9999)
                            outband.WriteArray(atc, 0, 0)
                print('绗?s娉㈡璁＄畻瀹屾垚'%BandId)
            # print(root+'璁＄畻瀹屾垚')
            print('\n')
    #鍏抽棴鏃ュ織鏂囦欢
    LogFile.close()

