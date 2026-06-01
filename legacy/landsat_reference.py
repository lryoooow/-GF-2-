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

# 瑙ｅ帇缂╁師濮嬫枃浠?def untar(fname, dirs):
    try:
        t = tarfile.open(fname)
    except Exception as e:
        print("鏂囦欢%s鎵撳紑澶辫触" % fname)
    t.extractall(path=dirs)

# 閫愭尝娈佃緪灏勫畾鏍?def RadiometricCalibration(BandId):
    # LandSat8 TM杈愬皠瀹氭爣鍙傛暟
    global data2,ImgRasterData
    parameter_OLI = numpy.zeros((11,2))

    #璁＄畻杈愬皠浜害鍙傛暟
    # parameter_OLI[0,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_1.+',data2)).split("=")[1])
    parameter_OLI[1,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_9.+',data2)).split("=")[1])
    parameter_OLI[9,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_10.+',data2)).split("=")[1])
    parameter_OLI[10,0] = float(''.join(re.findall('RADIANCE_MULT_BAND_11.+',data2)).split("=")[1])


    # parameter_OLI[0,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_1.+',data2)).split("=")[1])
    parameter_OLI[1,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_9.+',data2)).split("=")[1])
    parameter_OLI[9,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_10.+',data2)).split("=")[1])
    parameter_OLI[10,1] = float(''.join(re.findall('RADIANCE_ADD_BAND_11.+',data2)).split("=")[1])

    if len(BandId) ==8:
        n = int(BandId[2])
    else:
        n = int(BandId[1:3])
    Gain = parameter_OLI[n - 1,0]
    Bias = parameter_OLI[n - 1,1]

    RaCal = numpy.where(ImgRasterData>0 ,Gain * ImgRasterData + Bias,-9999)
    return (RaCal)

#璁＄畻琛ㄨ鍙嶅皠鐜?def TOAReflectance(BandId):
    # LandSat8 TM杈愬皠瀹氭爣鍙傛暟
    global data2,ImgRasterData
    parameter_OLI = numpy.zeros((9,2))

    #璁＄畻琛ㄨ鍙嶅皠鐜囧弬鏁?    parameter_OLI[0,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_1.+',data2)).split("=")[1])
    parameter_OLI[1,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,0] = float(''.join(re.findall('REFLECTANCE_MULT_BAND_9.+',data2)).split("=")[1])

    parameter_OLI[0,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_1.+',data2)).split("=")[1])
    parameter_OLI[1,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_2.+',data2)).split("=")[1])
    parameter_OLI[2,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_3.+',data2)).split("=")[1])
    parameter_OLI[3,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_4.+',data2)).split("=")[1])
    parameter_OLI[4,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_5.+',data2)).split("=")[1])
    parameter_OLI[5,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_6.+',data2)).split("=")[1])
    parameter_OLI[6,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_7.+',data2)).split("=")[1])
    parameter_OLI[7,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_8.+',data2)).split("=")[1])
    parameter_OLI[8,1] = float(''.join(re.findall('REFLECTANCE_ADD_BAND_9.+',data2)).split("=")[1])

    n = int(BandId[1])
    Gain = parameter_OLI[n - 1,0]
    Bias = parameter_OLI[n - 1,1]


    SunElevationFactor = numpy.sin(float(''.join(re.findall('SUN_ELEVATION.+',data2)).split("=")[1])/180*numpy.pi)

    TOARef = numpy.where(ImgRasterData>0,(Gain * ImgRasterData + Bias)/SunElevationFactor,-9999)

    return (TOARef)

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
    if BandId == 'B1.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B1)

    elif BandId == 'B2.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B2)

    elif BandId == 'B03.tiff':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B3)

    elif BandId == 'B04.tiff':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B4)

    elif BandId == 'B05.tiff':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B5)

    elif BandId == 'B6.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B6)

    elif BandId == 'B7.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B7)

    elif BandId == 'B8.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B8)

    elif BandId == 'B9.TIF':
        s.wavelength = Wavelength(PredefinedWavelengths.LANDSAT_OLI_B9)

    # 涓嬪灚闈㈤潪鍧囦竴銆佹湕浼綋
    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)

    # 杩愯6s澶ф皵妯″瀷
    s.run()

    xa = s.outputs.coef_xa
    xb = s.outputs.coef_xb
    xc = s.outputs.coef_xc
    x = s.outputs.values
    print(x)
    return (xa, xb, xc)

def MeanDEM(pointUL, pointDR):
    # 鎵撳紑DEM鏁版嵁
    try:
        DEMIDataSet = gdal.Open("GMTED2km.tif")
    except Exception as e:
        pass

    DEMBand = DEMIDataSet.GetRasterBand(1)
    cols = DEMIDataSet.RasterXSize
    rows = DEMIDataSet.RasterYSize

    geotransform = DEMIDataSet.GetGeoTransform()
    # DEM鍒嗚鲸鐜?    pixelWidth = geotransform[1]
    pixelHight = geotransform[5]

    # DEM璧峰鐐癸細宸︿笂瑙掞紝X锛氱粡搴︼紝Y锛氱含搴?    originX = geotransform[0]
    originY = geotransform[3]

    # 鐮旂┒鍖哄乏涓婅鍦ㄧ煩闃典腑鐨勪綅缃?    yoffset1 = int((originY - pointUL['lat']) / pixelWidth)
    xoffset1 = int((pointUL['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖哄彸涓嬭鍦ㄧ煩闃典腑鐨勪綅缃?    yoffset2 = int((originY - pointDR['lat']) / pixelWidth)
    xoffset2 = int((pointDR['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖虹煩闃佃鍒楁暟
    xx = xoffset2 - xoffset1
    yy = yoffset2 - yoffset1


    # 璇诲彇鐮旂┒鍖哄唴鐨勬暟鎹紝骞惰绠楅珮绋?    DEMRasterData = DEMBand.ReadAsArray(xoffset1, yoffset1, xx, yy)

    MeanAltitude = numpy.mean(DEMRasterData)
    return MeanAltitude

def CloudMaskScore():

    mask = BrightTemp == -9999

    #寰楀垎1锛欱lue
    BluePart = numpy.ma.array((TOARefRasterBlue-0.1)/0.2,mask=mask)
    BluePart.fill_value=-9999
    ScorePart1 = numpy.where(BluePart.filled()>1,1,BluePart.filled())

    #寰楀垎2锛歊ed銆丅lue銆丟reen
    RGBPart = numpy.ma.array((TOARefRasterBlue+TOARefRasterGreen+TOARefRasterRed-0.2)/0.6,mask=mask)
    RGBPart.fill_value=-9999
    ScorePart2 = numpy.where(RGBPart.filled()>ScorePart1,ScorePart1,RGBPart.filled())

    #寰楀垎3锛歂ir銆丼wir1銆丼wir2
    NSSPart = numpy.ma.array((TOARefRasterNir+TOARefRasterSwir1+TOARefRasterSwir2-0.3)/0.5,mask=mask)
    NSSPart.fill_value=-9999
    ScorePart3 = numpy.where(NSSPart.filled()>ScorePart2,ScorePart2,NSSPart.filled())

    #寰楀垎4:temperature
    TempPart = numpy.ma.array((BrightTemp-300)/(-10),mask=mask)
    TempPart.fill_value=-9999
    ScorePart4 = numpy.where(TempPart.filled()>ScorePart3,ScorePart3,TempPart.filled())

    #寰楀垎5NDSI锛欸reen銆乀OARefRasterSwir1
    NDSIPart1 = numpy.ma.array((TOARefRasterGreen- TOARefRasterSwir1)/(TOARefRasterGreen+TOARefRasterSwir1),mask=mask)
    NDSIPart2 = numpy.ma.array((NDSIPart1-0.8)/(-0.2),mask=mask)
    NDSIPart2.fill_value=-9999
    ScorePart5 = numpy.where(NDSIPart2.filled()>ScorePart4,ScorePart4,NDSIPart2.filled())

    ScoreCloud = numpy.where(ScorePart5!=-9999,1- ScorePart5,-9999)
    return ScoreCloud

if __name__ == '__main__':

    #杈撳叆鏁版嵁璺緞
    RootOutName = sys.argv[2]
    RootInputPath = sys.argv[1]

    Contronal=0
    #鍒涘缓鏃ュ織鏂囦欢
    LogFile = open(os.path.join(RootOutName,'log.text'),'w')

    for root,dirs,RSFiles in os.walk(RootInputPath):

        #鍒ゆ柇鏄惁杩涘叆鏈€搴曞眰
        if len(dirs)==0:
            #鏍规嵁杈撳叆杈撳嚭璺緞寤虹珛鐢熸垚鏂版枃浠剁殑璺緞
            RootInputPathList = RootInputPath.split('/')
            RootList = root.split('/')
            StartList = len(RootInputPathList)
            EndList = len(RootList)
            outname = RootOutName
            for i in range(StartList,EndList):
                if os.path.exists(os.path.join(outname,RootList[i]))==False:
                    os.makedirs(os.path.join(outname,RootList[i]))
                    outname=os.path.join(outname,RootList[i])
                else:
                    outname=os.path.join(outname,RootList[i])

            #鍒ゆ柇鏂囦欢鏄惁閮藉瓨鍦?            CloudScoreFile = os.path.join(outname,RootList[-1]+'_CloudScore.TIF')

            if os.path.isfile(CloudScoreFile):
                print(root+'璁＄畻瀹屾垚')
                continue
            else:
                MeteData = os.path.join(root,'MTL.txt')
                f = open(MeteData)
                data = f.readlines()
                data2 =' '.join(data)
                
                shutil.copyfile(MeteData,os.path.join(outname,RootList[-1]+'MTL.txt'))

                for tifFile in RSFiles:
                    # print(tifFile)
                    if tifFile[-5:] == '.tiff':
                        BandId = (os.path.basename(tifFile))
                        # print(BandId)

                        #鎹曟崏鎵撳紑鏁版嵁鍑洪敊寮傚父
                        try:
                            IDataSet = gdal.Open(os.path.join(root,tifFile))
                        except Exception as e:
                            print("鏂囦欢%S鎵撳紑澶辫触" % tifFile)
                            LogFile.write('\n'+os.path.join(root,tifFile)+'鏁版嵁鎵撳紑澶辫触')
                        
                        if IDataSet == None:
                            LogFile.write('\n'+os.path.join(root,tifFile)+'鏁版嵁闆嗚鍙栦负绌?)
                            continue
                        else:
                            #鑾峰彇琛屽垪鍙?                            cols = IDataSet.RasterXSize
                            rows = IDataSet.RasterYSize
                            ImgBand = IDataSet.GetRasterBand(1)
                            ImgRasterData = ImgBand.ReadAsArray(0, 0, cols, rows)

                            if ImgRasterData is None:
                                LogFile.write('\n'+os.path.join(root,tifFile)+'鏍呮牸鏁版嵁涓虹┖')
                                continue
                            else:
                                if BandId =='B02.tiff':
                                    # TOARefRasterBlue = TOAReflectance(BandId)
                                    RaCalRaster = RadiometricCalibration(BandId)
                                    Contronal = Contronal + 1
                                elif BandId =='B03.tiff':
                                    # TOARefRasterGreen = TOAReflectance(BandId)
                                    RaCalRaster = RadiometricCalibration(BandId)
                                    Contronal = Contronal + 1
                                elif BandId =='B04.tiff':
                                    # TOARefRasterRed = TOAReflectance(BandId)
                                    RaCalRaster = RadiometricCalibration(BandId)
                                    Contronal = Contronal + 1
                                elif BandId =='B05.tiff':
                                    # TOARefRasterNir = TOAReflectance(BandId)
                                    RaCalRaster = RadiometricCalibration(BandId)
                                    Contronal = Contronal + 1
                                # elif BandId =='B6.TIF':
                                #     TOARefRasterSwir1 = TOAReflectance(BandId)
                                #     Contronal = Contronal + 1
                                # elif BandId =='B7.TIF':
                                #     TOARefRasterSwir2 = TOAReflectance(BandId)
                                #     Contronal = Contronal + 1
                                # elif tifFile[-7:] =='B10.TIF':
                                #     RaCalRaster = RadiometricCalibration(BandId)
                                #     Contronal = Contronal + 1
                                #     BrightTemp = numpy.where(RaCalRaster!=-9999,1321.08/numpy.log(774.89/RaCalRaster+1),-9999)
                                    # print("浜俯璁＄畻瀹屾垚")

                                if BandId == 'B02.tiff'or BandId == 'B03.tiff'or BandId == 'B04.tiff'or BandId == 'B05.tiff':
                                    #璁剧疆杈撳嚭鏂囦欢璺緞
                                    outFilename=os.path.join(outname,os.path.basename(tifFile))

                                    #濡傛灉鏂囦欢瀛樺湪灏辫烦杩囷紝杩涜涓嬩竴娉㈡鎿嶄綔
                                    if os.path.isfile(outFilename):
                                        print("%s宸茬粡瀹屾垚" % outFilename)
                                        continue
                                    else:
                                        # #杈愬皠鏍℃
                                        # RaCalRaster = RadiometricCalibration(tifFile, BandId)
                                        #澶ф皵鏍℃
                                        a, b, c = SurfaceReflectance(BandId)
                                        y = numpy.where(RaCalRaster!=-9999,a * RaCalRaster - b,-9999)
                                        atc = numpy.where(y!=-9999,(y / (1 + y * c))*10000,-9999)
                                        
                                        driver = IDataSet.GetDriver()
                                        #杈撳嚭鏍呮牸鏁版嵁闆?                                        outDataset = driver.Create(outFilename, cols, rows, 1, gdal.GDT_Int16)

                                        # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?                                        geoTransform = IDataSet.GetGeoTransform()
                                        outDataset.SetGeoTransform(geoTransform)
                                        proj = IDataSet.GetProjection()
                                        outDataset.SetProjection(proj)

                                        outband = outDataset.GetRasterBand(1)
                                        outband.SetNoDataValue(-9999)
                                        outband.WriteArray(atc, 0, 0)
                print(root+'璁＄畻瀹屾垚')

                # if Contronal == 7:
                #     print(Contronal)
                #     #璁剧疆杈撳嚭鏂囦欢璺緞
                #     outFilename=os.path.join(outname,os.path.basename(tifFile)[0:41]+'CloudScore.TIF')
                #     CloudScoreFile = os.path.join(outname,RootList[-1]+'_CloudScore.TIF')

                #     CloudScoreData = CloudMaskScore()
                #     driver = IDataSet.GetDriver()
                #     #杈撳嚭鏍呮牸鏁版嵁闆?                #     CloudDataset = driver.Create(CloudScoreFile, cols, rows, 1, gdal.GDT_Float32)

                #     # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?                #     geoTransform = IDataSet.GetGeoTransform()
                #     proj = IDataSet.GetProjection()
                #     CloudDataset.SetGeoTransform(geoTransform)
                #     CloudDataset.SetProjection(proj)

                #     outband = CloudDataset.GetRasterBand(1)
                #     outband.SetNoDataValue(-9999)
                #     outband.WriteArray(CloudScoreData, 0, 0)
                #     print('褰卞儚'+outFilename + '澶勭悊瀹屾垚')
                #     RasterData = None
                #     Contronal=0
                # else:
                #     Contronal=0

    #鍏抽棴鏃ュ織鏂囦欢
    LogFile.close()



