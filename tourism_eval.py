# coding:cp936
# 引入库文件
import arcpy
import numpy as np
import math
from os import path as p

#%% 按照指定距离List，多重缓冲
def MultiRingBuffer(ringDistance, inputLayer, outputLayer):
    buffers = []  
    cursor = arcpy.SearchCursor(inputLayer)  
    for inputFeature in cursor:  
        sourceOid = inputFeature.getValue("FID")  
        currentBuffers = dict()  
        buffers.append(currentBuffers)  
        prevBuffer = None  
  
        for distance in ringDistance:
            bufferedGeom = inputFeature.Shape.buffer(distance)
            if prevBuffer != None:
                bufGeom = bufferedGeom.difference(prevBuffer)
            else:
                bufGeom =  bufferedGeom
            prevBuffer = bufferedGeom
            row = dict()  
            row["FID"] = sourceOid  
            row["distance"] = distance  
            row["SHAPE"] = bufGeom  
            currentBuffers[distance] = row  
    del cursor  
  
    cursor = arcpy.InsertCursor(outputLayer)  
    for ringBuffers in buffers:  
        for feature in ringBuffers.values():  
            row = cursor.newRow()  
            keys = feature.keys()
            keys.remove('FID')
            for k in keys: 
                #print(k)
                if k == "SHAPE":  
                    row.Shape = feature[k]  
                else:  
                    row.setValue(k, feature[k])  
            cursor.insertRow(row)  
    del cursor

#%% 设置全局变量
arcpy.env.overwriteOutput = True
arcpy.env.workspace= "G:/Landsat_CX/data/" # arcgis工作空间
templateLayer = 'G:/Landsat_CX/data/view/template.shp' # 用于生成多值缓冲输出的模板shp面文件
fc = "G:/Landsat_CX/data/view/viewBeauty_all.shp" # 待进行旅游敏感度评价的点文件
resultFile = open('G:/Landsat_CX/RS_Tourism/viewBeauty_all.txt', 'w') # 存储计算结果文件
outws = "G:/Landsat_CX/data/temp_all" # 存放计算过程文件

valList = [] # FID列表
xyList = {}  # 以FID为Key的，视点坐标清单

# 遍历点文件，获取FID及坐标XY
rows = arcpy.da.SearchCursor(fc,['FID', 'SHAPE@XY'])
for row in rows:
    #print(row[0], row[1])
    value = row[0]
    xyList[row[0]] = row[1]
    if value not in valList:
        valList.append(value)

elevRaster = arcpy.sa.Raster(r"G:\Landsat_CX\data\dem\CX_DEM48N.tif") # DEM数据
DemExtent = elevRaster.extent

#valList.remove(21)

#%% Create temp.shp
for val in valList:
    print("Process feature %d."%val)
    query = '"FID" = {0}'.format(val)
    desc = arcpy.Describe(outws)
    viewPt = p.join(outws, '%d.shp'%val)
    if not arcpy.Exists(viewPt):
        # arcpy.Delete_management(viewPt)        
        arcpy.Select_analysis(fc, viewPt, query)
    print '\t%d-1.From feature %d Created "%s"' % (val, val, p.basename(viewPt))

    # Viewshed
    rows = arcpy.da.SearchCursor(viewPt,['SHAPE@XY'])
    cx = 0
    cy = 0
    for row in rows:
        cx = row[0][0]
        cy = row[0][1]
    if cx == 0 and  cy == 0:
        continue
    cx = xyList[val][0]
    cy = xyList[val][1]
    arcpy.env.extent = arcpy.Extent(max(cx-50000, DemExtent.XMin), max(cy-50000, DemExtent.YMin), 
                                    min(cx+50000, DemExtent.XMax), min(cy+50000, DemExtent.YMax)) #根据视点50km范围进行计算
    
    #print(cx, cy,
    #      max(cx-50000, DemExtent.XMin), max(cy-50000, DemExtent.YMin), 
    #      min(cx+50000, DemExtent.XMax), min(cy+50000, DemExtent.YMax))
    
    arcpy.env.snapRaster = r"G:\Landsat_CX\data\image\川西小环线.tif"


    # Set local variables
    inRaster = r"G:\Landsat_CX\data\dem\CX_DEM48N.tif"
    inObserverFeatures = viewPt
    zFactor = 1
    useEarthCurvature = "CURVED_EARTH"
    refractivityCoefficient = 0.15
    
    arcpy.env.overwriteOutput = True
    
    # 计算可视域，同时获取可视域范围，恰巧等于可视域图像均值
    if not arcpy.Exists(p.join(outws, "%d_view.tif"%val)):
        outViewshed = arcpy.sa.Viewshed(inRaster, inObserverFeatures, zFactor, 
                               useEarthCurvature, refractivityCoefficient)
        # height = outViewshed.height
        # width = outViewshed.width
        view_mean = outViewshed.mean
        # view_sum = view_mean*width*height
        # s_view = view_sum/(width*height) = view_mean
        s_view = view_mean                    
        # Save the output 
        outViewshed.save(p.join(outws, "%d_view.tif"%val))
    else:
        # width = arcpy.GetRasterProperties_management(p.join(outws, "%d_view.tif"%val), "COLUMNCOUNT")
        # height = arcpy.GetRasterProperties_management(p.join(outws, "%d_view.tif"%val), "ROWCOUNT")
        view_mean = arcpy.GetRasterProperties_management(p.join(outws, "%d_view.tif"%val), "MEAN")
        # view_sum = view_mean*width*height
        # s_view = view_sum/(width*height) = view_mean
        s_view = view_mean
        
    print('\t%d-2.Feature viewshed Finshed.'%val)
    
    #%% get height
    #height = arcpy.GetCellValue_management(inRaster, "%s %s"%(cx, cy), "1")
    #height = int(height.getOutput(0))
    #print('Height : %s' % height)

    #%% distance map
    # Set local variables
    # inFeatures = viewPt
    # valField = "FID"
    # outRaster = p.join(outws, "temp.tif")
    
    # Execute PointToRaster
    # arcpy.env.overwriteOutput = True
    # arcpy.PointToRaster_conversion(inFeatures, valField, outRaster, cellsize=30)
    
    inFeatures = viewPt
    outFeatureClass = p.join(outws, "%d_buffer.shp"%val)
    #distances = np.arange(1000, 72000, 1000).tolist()
    distances = [1000, 2783, 7743, 21544, 35938, 60000]
                
    bufferUnit = "meters"
     
    # Execute MultipleRingBuffer
    arcpy.env.overwriteOutput = True
    if not arcpy.Exists(outFeatureClass):
        # Set local variables
        geometry_type = "POLYGON"
        has_m = "DISABLED"
        has_z = "DISABLED"

        # Use Describe to get a SpatialReference object
        spatial_reference = arcpy.Describe(inFeatures).spatialReference

        # Execute CreateFeatureclass
        arcpy.env.overwriteOutput = True
        arcpy.CreateFeatureclass_management(p.dirname(outFeatureClass), p.basename(outFeatureClass), 
                                            geometry_type, templateLayer, has_m, has_z, spatial_reference)

        MultiRingBuffer(distances, inFeatures, outFeatureClass) 

        # arcpy.MultipleRingBuffer_analysis(inFeatures, outFeatureClass, distances, bufferUnit, "distance", "ALL")
    
    print('\t%d-3.Feature buffer finished.' % val)
    
    inFeatures = p.join(outws, "%d_buffer.shp"%val)
    valField = "distance"
    outRaster = p.join(outws, "%d_distance.tif"%val)
    
    # Execute PolygonToRaster
    arcpy.env.overwriteOutput = True
    
    if not arcpy.Exists(outRaster):
        arcpy.PolygonToRaster_conversion(inFeatures, valField, outRaster, cellsize=30)
    
    
    # Set local variables
    # tmp = arcpy.sa.Raster(outRaster)
    
    # Execute Plus
    #arcpy.env.overwriteOutput = True
    #outPlus = tmp / 71000
    
    # Save the output 
    #outPlus.save(p.join(outws, "distance_1.tif"))
    print('\t%d-4.Feature distance map finished.' % val)

    '''    
    #%% Cal
    distanceRas = arcpy.sa.Raster(p.join(outws, "%d_distance.tif"%val))
    beautyRas = arcpy.sa.Raster(r"G:\Landsat_CX\data\product\CX_BEAUTY_china30m.tif")
    slopeRas = arcpy.sa.Raster(r"G:\Landsat_CX\data\dem\CX_DEM48N_SLOPE.tif")
    viewRas = arcpy.sa.Raster(p.join(outws, "%d_view.tif"%val))
    #'SetNull("0_view.tif" == 0, 0.33*("0_distance.tif" / 100000.0)+0.33 * "CX_BEAUTY.tif"*0.1+0.33 * Sin(3.1415926*"CX_DEM48N_SLOPE.tif"/180.0))'

    resultRas = arcpy.sa.SetNull(viewRas == 0, 
        0.33*((61000 - distanceRas) / 60000.0)+0.34 * beautyRas+0.33 * arcpy.sa.Sin(math.pi*slopeRas/180.0))
    resultFile.writelines(['%s,%s,%s\n'%(cx, cy, resultRas.mean*float(s_view.getOutput(0)))])
    print('\t%d-5.finished.' % val)
    '''
    
resultFile.close()
