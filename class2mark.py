# coding:cp936

import arcpy
from arcpy import env
from arcpy.sa import *

env.workspace = "G:/Landsat_CX/data/product"

# ����ң�з���դ��
inRaster = "CX_GLC.tif" # ŷ�վַ���ͼ
# inRaster = "china30m.tif" # �й�30mȫ�����ͼ

# ŷ�վַ�������ӳ��
myRemapVal = arcpy.sa.RemapValue([
	[0,0],
	[10,3], # cropland ũ�����
	[11,5], # herbaceous �ݵ�
	[12,3], # Tree or shrub cover ��ľ���ľ
	[20,9], # Cropland, irrigated or post-flooding ũ���Ȼ��ˮ��
	[30,4], # Mosaic cropland or natural vegetation (tree, shrub, herbaceous cover)  ũ�����Ȼֲ������ľ����ľ���ݱ����ǣ� 
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
	
''' �й�30mȫ���������ӳ��
myRemapVal = arcpy.sa.RemapValue([
	[0,0],  # δ����
	[10,6], # 10 Cultivated land ����
	[20,7], # 20 Forest �ֵ�
	[30,9], # 30 Grassland �ݵ�
	[40,3], # 40 Shrubland ��ľ��
	[50,8], # 50 Wetland ʪ��
	[60,9], # 60 Water bodies ˮ��
	[70,5], # 70 Tundra ̦ԭ��һ������ڼ��أ�
	[80,2], # 80 Artificial Surface �˹��ر�
	[90,1], # 90 Bareland ���
	[100,10]# 100 Permanent snow and ice ���ñ�ѩ
	])
'''

# ִ���ط���
outReclassRV = Reclassify(inRaster, "VALUE", myRemapVal, "")

# ���������
outReclassRV.save("CX_BEAUTY.tif")