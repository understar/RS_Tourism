# coding:cp936

import arcpy
from arcpy import env
from arcpy.sa import *

env.workspace = "G:/Landsat_CX/data/product"
env.snapRaster = "G:/Landsat_CX/data/image/川西小环线.tif"
elevRaster = arcpy.sa.Raster(r"G:\Landsat_CX\data\dem\CX_DEM48N.tif")
env.extent = elevRaster.extent

# 输入遥感分类栅格
# inRaster = "CX_GLC.tif" # 欧空局分类图
inRaster = "china30m_clip.tif" # 中国30m全球分类图

''' 欧空局分类结果重映射
myRemapVal = arcpy.sa.RemapValue([
	[0,0],
	[10,3], # cropland 农田、旱地
	[11,5], # herbaceous 草地
	[12,3], # Tree or shrub cover 乔木或灌木
	[20,9], # Cropland, irrigated or post-flooding 农田、灌溉或洪水后
	[30,4], # Mosaic cropland or natural vegetation (tree, shrub, herbaceous cover)  农田或自然植被（乔木、灌木、草本覆盖） 
	[40,4],
	[50,5],
	[60,4],
	[61,4],
	[62,6],
	[70,5],
	[71,4],
	[72,4],
	[80,6],
	[81,6],
	[82,6],
	[90,8],
	[100,5],
	[110,3],
	[120,2],
	[121,1],
	[122,2],
	[130,7],
	[140,5],
	[150,3],
	[151,2],
	[152,1],
	[153,2],
	[160,8],
	[170,7],
	[180,7],
	[190,2],
	[200,2],
	[201,1],
	[202,1],
	[210,8],
	[220,10]])
''' 
#中国30m全球分类结果重映射
myRemapVal = arcpy.sa.RemapValue([
	[0,0],  # 未分类
	[10,6], # 10 Cultivated land 耕地
	[20,7], # 20 Forest 林地
	[30,9], # 30 Grassland 草地
	[40,3], # 40 Shrubland 灌木地
	[50,8], # 50 Wetland 湿地
	[60,9], # 60 Water bodies 水体
	[70,5], # 70 Tundra 苔原（一般出现在极地）
	[80,2], # 80 Artificial Surface 人工地表
	[90,1], # 90 Bareland 裸地
	[100,10]# 100 Permanent snow and ice 永久冰雪
	])

# 执行重分类
outReclassRV = Reclassify(inRaster, "VALUE", myRemapVal, "")

# 保存分类结果
outReclassRV.save("CX_BEAUTY_china30m.tif")