#! usr/bin/env python
# -*- coding:utf-8 -*-
# created by zhaoguanhua 2017/10/9
# SurfaceReflectance for Sentinel-2A

import glob
import os
import sys
import tarfile
import re
import numpy
from Py6S import *
from osgeo import gdal
from osgeo import osr
import xml.dom.minidom
import pdb
import shutil
from base import MeanDEM
import argparse

def parse_arguments(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument('--Input_dir',type=str,help='Input dir',default=None)
    parser.add_argument('--Output_dir',type=str,help='Output dir',default=None)

    return parser.parse_args(argv)

def TOAReflectanceToTOARadiance(BandId):
    '''
    灏嗚〃瑙傚弽灏勭巼杞崲涓鸿〃瑙傝緪灏勪寒搴?    '''
    global dom
    #澶槼杈愮収搴?    EsBand = numpy.zeros((14))
    EsBand[1] = 1913.57
    EsBand[2] = 1941.63
    EsBand[3] = 1822.61
    EsBand[4] = 1512.79
    EsBand[5] = 1425.56
    EsBand[6] = 1288.32
    EsBand[7] = 1163.19
    EsBand[8] = 1036.39
    EsBand[9] = 955.19
    EsBand[10]= 813.04 
    EsBand[11]= 367.15
    EsBand[12]= 245.59
    EsBand[13]= 85.25

    #鏃ュ湴鐩稿璺濈锛屽湪1宸﹀彸娉㈠姩锛屾殏鏃剁敤1浠ｆ浛
    #鍏紡锛欴=1+0.0167*sin(2*pi*(days-39.5)/360)  days鏄剴鐣ユ棩
    D = 1
    #澶槼澶╅《瑙?    SunZenith = float(dom.getElementsByTagName('ZENITH_ANGLE')[0].firstChild.data)
    #print('SunZenith=',SunZenith)
    Us = numpy.cos(SunZenith/180*numpy.pi)

    # y = numpy.where(RaCalRaster!=-9999,a * RaCalRaster - b,-9999)
    # Radiance = (ImgRasterData/10000)*Us*EsBand[BandId]/(D*D*numpy.pi)
    Radiance =numpy.where(ImgRasterData!=0,(ImgRasterData/10000)*Us*EsBand[BandId]/(D*D*numpy.pi),-9999)
    return Radiance

# 6s澶ф皵鏍℃
def SurfaceReflectance(BandId):
    '''
    璋冪敤6s妯″瀷锛岀粰鍚勫弬鏁拌祴鍊硷紝寰楀埌澶ф皵鏍℃鍙傛暟
    '''
    global dom,SixsInputParameter
    # 6S妯″瀷
    s = SixS()

    s.geometry = Geometry.User()
    s.geometry.solar_z = SixsInputParameter["SolarZenithAngle"]
    s.geometry.solar_a = SixsInputParameter["SolarAzimuthAngle"]
    s.geometry.view_z = SixsInputParameter["ViewZenithAngle"][BandId]
    s.geometry.view_a = SixsInputParameter["ViewAzimuthAngle"][BandId]

    # 鏃ユ湡:鏈堛€佹棩
    s.geometry.month = SixsInputParameter["ImgMonth"]
    s.geometry.day = SixsInputParameter["ImgDay"]

    #澶ф皵妯″紡绫诲瀷
    s.atmos_profile = AtmosProfile.PredefinedType(SixsInputParameter["AtmosphericProfile"])

    # 姘旀憾鑳剁被鍨嬪ぇ闄?    s.aero_profile = AtmosProfile.PredefinedType(AeroProfile.Continental)

    # 鐩爣鍦扮墿
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.36)

    # 550nm姘旀憾鑳跺厜瀛﹀帤搴?鏍规嵁鏃ユ湡浠嶮ODIS澶勮幏鍙栥€?    #s.visibility=40.0
    s.aot550 = 0.14497

    # 鐮旂┒鍖烘捣鎷斻€佸崼鏄熶紶鎰熷櫒杞ㄩ亾楂樺害
    s.altitudes = Altitudes()
    # s.altitudes.set_target_custom_altitude(0.015)
    s.altitudes.set_target_custom_altitude(SixsInputParameter["meanDEM"])
    s.altitudes.set_sensor_satellite_level()
    #s.altitudes.set_sensor_custom_altitude(-705)

    # 鏍℃娉㈡锛堟牴鎹尝娈靛悕绉帮級
    if BandId == 1:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_01)

    elif BandId == 2:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_02)

    elif BandId == 3:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_03)

    elif BandId == 4:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_04)

    elif BandId == 5:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_05)

    elif BandId == 6:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_06)

    elif BandId == 7:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_07)

    elif BandId == 8:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_08)

    elif BandId == 9:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_09)

    elif BandId == 10:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_10)

    elif BandId == 11:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_11)

    elif BandId == 12:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_12)

    elif BandId == 13:
        s.wavelength = Wavelength(PredefinedWavelengths.S2A_MSI_13)

    # 涓嬪灚闈㈤潪鍧囦竴銆佹湕浼綋
    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)

    # 杩愯6s澶ф皵妯″瀷
    s.run()

    xa = s.outputs.coef_xa
    xb = s.outputs.coef_xb
    xc = s.outputs.coef_xc
    x = s.outputs.values
    # print(x)
    return (xa, xb, xc)

def BasicParameters():
    '''
    鑾峰彇6s澶ф皵鏍℃鎵€闇€鐨勫弬鏁?    '''
    global dom
    SixsParameters = dict()
    #澶槼澶╅《瑙掋€佹柟浣嶈
    SunAngle = dom.getElementsByTagName('Mean_Sun_Angle')
    SixsParameters["SolarZenithAngle"] = float(SunAngle[0].getElementsByTagName('ZENITH_ANGLE')[0].firstChild.data)
    SixsParameters["SolarAzimuthAngle"] = float(SunAngle[0].getElementsByTagName('AZIMUTH_ANGLE')[0].firstChild.data)

    #鍗槦澶╅《瑙掋€佹柟浣嶈
    ViewAngles = dom.getElementsByTagName('Mean_Viewing_Incidence_Angle')
    ViewZeniths = dict()
    ViewAzimuths = dict()

    for angle in ViewAngles:
        ViewAngle = int(angle.getAttribute('bandId'))
        #print(ViewAngle)
        ViewZeniths[ViewAngle+1] = float(angle.getElementsByTagName('ZENITH_ANGLE')[0].firstChild.data)
        ViewAzimuths[ViewAngle+1]= float(angle.getElementsByTagName('AZIMUTH_ANGLE')[0].firstChild.data)

    SixsParameters["ViewZenithAngle"] = ViewZeniths
    SixsParameters["ViewAzimuthAngle"] = ViewAzimuths
    # 鏃ユ湡:鏈堛€佹棩
    Date = dom.getElementsByTagName('SENSING_TIME')[0].firstChild.data.split('T')[0]
    SixsParameters["ImgMonth"] = int(Date.split('-')[1])
    SixsParameters["ImgDay"] = int(Date.split('-')[2])

    #姹傚奖鍍忎腑蹇冪粡绾害
    PointULX = int(dom.getElementsByTagName('ULX')[0].firstChild.data)
    PointULY = int(dom.getElementsByTagName('ULY')[0].firstChild.data)

    Imgsizes = dom.getElementsByTagName('Size')

    for Imgsize in Imgsizes:
        Resolution = Imgsize.getAttribute('resolution')
        if Resolution == '10':
            SixsParameters["Nrows"] = int(Imgsize.getElementsByTagName('NROWS')[0].firstChild.data)
            SixsParameters["Ncols"] = int(Imgsize.getElementsByTagName('NCOLS')[0].firstChild.data)

    PointBRX = PointULX + 10*SixsParameters["Ncols"]
    PointBRY = PointULY - 10*SixsParameters["Nrows"]

    # 灏嗘姇褰卞潗鏍囪浆涓虹粡绾害鍧愭爣锛堝叿浣撶殑鎶曞奖鍧愭爣绯荤敱缁欏畾鏁版嵁纭畾锛?    Proj = dom.getElementsByTagName('HORIZONTAL_CS_CODE')[0].firstChild.data
    ProjCode = int(Proj.split(':')[1])

    source = osr.SpatialReference()
    source.ImportFromEPSG(ProjCode)
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326) 
    ct = osr.CoordinateTransformation(source,target)
    CoordsUL,CoordsBR = ct.TransformPoints([(PointULX,PointULY),(PointBRX,PointBRY)])


    ULLat = CoordsUL[0]
    ULLon = CoordsUL[1]
    BRLat = CoordsBR[0]
    BRLon = CoordsBR[1]

    sLongitude = (ULLon+BRLon) / 2
    sLatitude = (ULLat+BRLat) / 2

    #澶ф皵妯″紡绫诲瀷
    if sLatitude > -15 and sLatitude <= 15:
        SixsParameters["AtmosphericProfile"] = 1                                    #Tropical
    elif sLatitude > 15 and sLatitude <= 45:
        if SixsParameters["ImgMonth"] > 4 and SixsParameters["ImgMonth"] <= 9:
            SixsParameters["AtmosphericProfile"] = 2                                #MidlatitudeSummer
        else:
            SixsParameters["AtmosphericProfile"] = 3                                #MidlatitudeWinter
    elif sLatitude > 45 and sLatitude <= 60:
        if SixsParameters["ImgMonth"] > 4 and SixsParameters["ImgMonth"] <= 9:
            SixsParameters["AtmosphericProfile"] = 4                                #SubarctivWinter
        else:
            SixsParameters["AtmosphericProfile"] = 5                                #SubarcticWinter

    pointUL = dict()
    pointDR = dict()
    pointUL["lat"] = ULLat
    pointUL["lon"] = ULLon
    pointDR["lat"] = BRLat
    pointDR["lon"] = BRLon
    SixsParameters["meanDEM"] = (MeanDEM(pointUL, pointDR)) * 0.001

    return SixsParameters

def AWS_file_bk():
    pass
    # #杈撳叆鏁版嵁璺緞
    # RootInputPath = parse_arguments(sys.argv[1:]).Input_dir
    # #杈撳嚭璺緞
    # RootOutName = parse_arguments(sys.argv[2:]).Output_dir
    #
    # #鍒涘缓鏃ュ織鏂囦欢
    # LogFile = open(os.path.join(RootOutName,'log.txt'),'w')

    # for root,dirs,RSFiles in os.walk(RootInputPath):
    #     #鍒ゆ柇鏄惁杩涘叆鏈€搴曞眰
    #     if len(dirs)==0:
    #         #鏍规嵁杈撳叆杈撳嚭璺緞寤虹珛鐢熸垚鏂版枃浠剁殑璺緞
    #         RootInputPathList = RootInputPath.split(os.path.sep)
    #         RootList = root.split(os.path.sep)
    #         StartList = len(RootInputPathList)
    #         EndList = len(RootList)
    #         outname = RootOutName
    #         for i in range(StartList,EndList):
    #             if os.path.exists(os.path.join(outname,RootList[i]))==False:
    #                 os.makedirs(os.path.join(outname,RootList[i]))
    #                 outname=os.path.join(outname,RootList[i])
    #             else:
    #                 outname=os.path.join(outname,RootList[i])
    #
    #         #鑾峰緱褰卞儚澶存枃浠?    #         MeteData = os.path.join(root,'metadata.xml')
    #         print(MeteData)
    #         shutil.copyfile(MeteData,os.path.join(outname,'metedata.xml'))
    #         dom = xml.dom.minidom.parse(MeteData)
    #         SixsInputParameter = BasicParameters()
    #
    #         #閫夊嚭褰卞儚鎵€鏈夋尝娈?    #         RSbands = glob.glob(os.path.join(root,"B*.tiff"))
    #
    #         for tifFile in RSbands:
    #             print(tifFile)
    #             if os.path.basename(tifFile)=="B8A.tiff":
    #                 BandId = 9
    #             elif int(os.path.basename(tifFile)[1:3])<9:
    #                 BandId = int(os.path.basename(tifFile)[1:3])
    #             else:
    #                 BandId = int(os.path.basename(tifFile)[1:3])+1
    #             print(BandId)
    #             #鎹曟崏鎵撳紑鏁版嵁鍑洪敊寮傚父
    #             try:
    #                 IDataSet = gdal.Open(tifFile)
    #             except Exception as e:
    #                 print("鏂囦欢%S鎵撳紑澶辫触" % tifFile)
    #                 LogFile.write('\n'+tifFile+'鏁版嵁鎵撳紑澶辫触')
    #
    #             if IDataSet == None:
    #                 LogFile.write('\n'+tifFile+'鏁版嵁闆嗚鍙栦负绌?)
    #                 continue
    #             else:
    #                 #鑾峰彇琛屽垪鍙?    #                 cols = IDataSet.RasterXSize
    #                 rows = IDataSet.RasterYSize
    #                 ImgBand = IDataSet.GetRasterBand(1)
    #                 ImgRasterData = ImgBand.ReadAsArray(0, 0, cols, rows)
    #                 # print(ImgRasterData)
    #                 if ImgRasterData is None:
    #                     LogFile.write('\n'+tifFile+'鏍呮牸鏁版嵁涓虹┖')
    #                     continue
    #                 else:
    #                     #璁剧疆杈撳嚭鏂囦欢璺緞
    #                     outFilename=os.path.join(outname,os.path.basename(tifFile)[0:3]+'.tiff')
    #                     # print(outFilename)
    #
    #                     #濡傛灉鏂囦欢瀛樺湪灏辫烦杩囷紝杩涜涓嬩竴娉㈡鎿嶄綔
    #                     if os.path.isfile(outFilename):
    #                         print("%s宸茬粡瀹屾垚" % outFilename)
    #                         continue
    #                     else:
    #                         #琛ㄨ鍙嶅皠鐜囪浆鎹负杈愬皠浜害鍊?    #                         RaCalRaster = TOAReflectanceToTOARadiance(BandId)
    #                         #澶ф皵鏍℃
    #                         a, b, c = SurfaceReflectance(BandId)
    #                         y = numpy.where(RaCalRaster!=-9999,a * RaCalRaster - b,-9999)
    #                         atc = numpy.where(y!=-9999,(y / (1 + y * c))*10000,-9999)
    #
    #                         driver = gdal.GetDriverByName('GTIFF')
    #                         #杈撳嚭鏍呮牸鏁版嵁闆?    #                         outDataset = driver.Create(outFilename, cols, rows, 1, gdal.GDT_Int16)
    #
    #                         # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?    #                         geoTransform = IDataSet.GetGeoTransform()
    #                         outDataset.SetGeoTransform(geoTransform)
    #                         proj = IDataSet.GetProjection()
    #                         outDataset.SetProjection(proj)
    #
    #                         outband = outDataset.GetRasterBand(1)
    #                         outband.SetNoDataValue(-9999)
    #                         outband.WriteArray(atc, 0, 0)

if __name__ == '__main__':

    #鑾峰緱褰卞儚澶存枃浠?    # file_path =r"D:\test\L1C_T51TUE_A004877_20180211T025320"
    #     # output_file=r"D:\test\ac_s2"

    #杈撳叆鏁版嵁璺緞
    file_path = parse_arguments(sys.argv[1:]).Input_dir
    #杈撳嚭璺緞
    output_file = parse_arguments(sys.argv[2:]).Output_dir

    MeteData = os.path.join(file_path, 'MTD_TL.xml')
    #print(MeteData)
    dom = xml.dom.minidom.parse(MeteData)
    SixsInputParameter = BasicParameters()

    # 閫夊嚭褰卞儚鎵€鏈夋尝娈?    RSbands = glob.glob(os.path.join(file_path,"IMG_DATA","*B*.jp2"))

    for imgFile in RSbands:
        img_basename = os.path.basename(imgFile)
        band_id = img_basename[-6:-4]
        if band_id == "8A":
            BandId = 9
        elif int(band_id) < 9:
            BandId = int(band_id)
        else:
            BandId = int(band_id) + 1
        # 鎹曟崏鎵撳紑鏁版嵁鍑洪敊寮傚父
        try:
            IDataSet = gdal.Open(imgFile)
        except Exception as e:
            print("鏂囦欢{file}鎵撳紑澶辫触".format(file=imgFile))

        if IDataSet == None:
            print("{file}鏁版嵁闆嗚鍙栦负绌?.format(file=imgFile))
            continue
        else:
            # 鑾峰彇琛屽垪鍙?            cols = IDataSet.RasterXSize
            rows = IDataSet.RasterYSize
            ImgBand = IDataSet.GetRasterBand(1)
            ImgRasterData = ImgBand.ReadAsArray(0, 0, cols, rows)
            if ImgRasterData is None:
                print("{file}鏍呮牸鏁版嵁涓虹┖".format(file=imgFile))
                continue
            else:
                # 璁剧疆杈撳嚭鏂囦欢璺緞
                outFilename = os.path.join(output_file,img_basename.replace(".jp2",".tiff"))

                # 濡傛灉鏂囦欢瀛樺湪灏辫烦杩囷紝杩涜涓嬩竴娉㈡鎿嶄綔
                if os.path.isfile(outFilename):
                    print("%s宸茬粡瀹屾垚" % outFilename)
                    continue
                else:

                    # 琛ㄨ鍙嶅皠鐜囪浆鎹负杈愬皠浜害鍊?                    RaCalRaster = TOAReflectanceToTOARadiance(BandId)
                    # 澶ф皵鏍℃
                    a, b, c = SurfaceReflectance(BandId)
                    y = numpy.where(RaCalRaster != -9999, a * RaCalRaster - b, -9999)
                    atc = numpy.where(y != -9999, (y / (1 + y * c)) * 10000, -9999)
    #
                    driver = gdal.GetDriverByName('GTIFF')
                    # 杈撳嚭鏍呮牸鏁版嵁闆?                    outDataset = driver.Create(outFilename, cols, rows, 1, gdal.GDT_Int16)

                    # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?                    geoTransform = IDataSet.GetGeoTransform()
                    outDataset.SetGeoTransform(geoTransform)
                    proj = IDataSet.GetProjection()
                    outDataset.SetProjection(proj)

                    outband = outDataset.GetRasterBand(1)
                    outband.SetNoDataValue(-9999)
                    outband.WriteArray(atc, 0, 0)
        print('{file}璁＄畻瀹屾垚'.format(file=img_basename))



