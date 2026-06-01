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
    Us = numpy.cos(SunZenith/180*numpy.pi)

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
    s.altitudes.set_target_custom_altitude(SixsInputParameter["meanDEM"])
    s.altitudes.set_sensor_satellite_level()

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
    return (xa, xb, xc)

def MeanDEM(pointUL, pointDR):
    '''
    璁＄畻褰卞儚鎵€鍦ㄥ尯鍩熺殑骞冲潎楂樼▼.
    '''
    try:
        DEMIDataSet = gdal.Open("GMTED2km.tif")
    except Exception as e:
        pass

    DEMBand = DEMIDataSet.GetRasterBand(1)
    geotransform = DEMIDataSet.GetGeoTransform()
    # DEM鍒嗚鲸鐜?    pixelWidth = geotransform[1]
    pixelHight = geotransform[5]

    # DEM璧峰鐐癸細宸︿笂瑙掞紝X锛氱粡搴︼紝Y锛氱含搴?    originX = geotransform[0]
    originY = geotransform[3]

    # 鐮旂┒鍖哄乏涓婅鍦―EM鐭╅樀涓殑浣嶇疆
    yoffset1 = int((originY - pointUL['lat']) / pixelWidth)
    xoffset1 = int((pointUL['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖哄彸涓嬭鍦―EM鐭╅樀涓殑浣嶇疆
    yoffset2 = int((originY - pointDR['lat']) / pixelWidth)
    xoffset2 = int((pointDR['lon'] - originX) / (-pixelHight))

    # 鐮旂┒鍖虹煩闃佃鍒楁暟
    xx = xoffset2 - xoffset1
    yy = yoffset2 - yoffset1

    # 璇诲彇鐮旂┒鍖哄唴鐨勬暟鎹紝骞惰绠楅珮绋?    DEMRasterData = DEMBand.ReadAsArray(xoffset1, yoffset1, xx, yy)

    MeanAltitude = numpy.mean(DEMRasterData)
    return MeanAltitude

def BasicParameters():
    '''
    鏁寸悊6s澶ф皵鏍℃鎵€闇€鐨勫弬鏁?    '''
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

    ULLon = CoordsUL[0]
    ULLat = CoordsUL[1]
    BRLon = CoordsBR[0]
    BRLat = CoordsBR[1]

    sLongitude = (ULLon+BRLon) / 2
    sLatitude = (ULLat+ULLat) / 2

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

if __name__ == '__main__':

    #杈撳叆鏁版嵁璺緞
    RootOutName = sys.argv[2]
    RootInputPath = sys.argv[1]

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


            #鑾峰緱褰卞儚澶存枃浠?
            MeteData = os.path.join(root,'metadata.xml')
            shutil.copyfile(MeteData,os.path.join(outname,'metedata.xml'))
            dom = xml.dom.minidom.parse(MeteData)
            SixsInputParameter = BasicParameters()

            #閫夊嚭褰卞儚鎵€鏈夋尝娈?            RSbands = glob.glob(os.path.join(root,"B*.tiff"))

            for tifFile in RSbands:
                print(tifFile)
                if os.path.basename(tifFile)=="B8A.tiff":
                    BandId = 9
                elif int(os.path.basename(tifFile)[1:3])<9:
                    BandId = int(os.path.basename(tifFile)[1:3])
                else:
                    BandId = int(os.path.basename(tifFile)[1:3])+1
                print(BandId)
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
                        outFilename=os.path.join(outname,os.path.basename(tifFile)[0:3]+'.tiff')

                        #濡傛灉鏂囦欢瀛樺湪灏辫烦杩囷紝杩涜涓嬩竴娉㈡鎿嶄綔
                        if os.path.isfile(outFilename):
                            print("%s宸茬粡瀹屾垚" % outFilename)
                            continue
                        else:
                            #琛ㄨ鍙嶅皠鐜囪浆鎹负杈愬皠浜害鍊?                            RaCalRaster = TOAReflectanceToTOARadiance(BandId)
                            #澶ф皵鏍℃
                            a, b, c = SurfaceReflectance(BandId)
                            y = numpy.where(RaCalRaster!=-9999,a * RaCalRaster - b,-9999)
                            atc = numpy.where(y!=-9999,(y / (1 + y * c))*10000,-9999)
                            
                            driver = gdal.GetDriverByName('GTIFF')
                            #杈撳嚭鏍呮牸鏁版嵁闆?                            outDataset = driver.Create(outFilename, cols, rows, 1, gdal.GDT_Int16)

                            # 璁剧疆鎶曞奖淇℃伅锛屼笌鍘熸暟鎹竴鏍?                            geoTransform = IDataSet.GetGeoTransform()
                            outDataset.SetGeoTransform(geoTransform)
                            proj = IDataSet.GetProjection()
                            outDataset.SetProjection(proj)

                            outband = outDataset.GetRasterBand(1)
                            outband.SetNoDataValue(-9999)
                            outband.WriteArray(atc, 0, 0)

    #鍏抽棴鏃ュ織鏂囦欢
    LogFile.close()



