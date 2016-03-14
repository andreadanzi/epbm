# -*- coding: utf-8 -*-
import logging
import logging.handlers
import ConfigParser, os
from datetime import datetime
from pymongo import MongoClient
from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from building import Building
from domain import Domain
from bson.objectid import ObjectId
import glob,io
import csv, re
import sys, getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.tri as tri
from mpl_toolkits.mplot3d.axes3d import *
from scipy.interpolate import griddata
from collections import defaultdict
from shapely.geometry import LineString
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import osgeo.ogr as ogr
import osgeo.osr as osr
import osgeo.gdal as gdal
# danzi.tn@20160310 plot secondo distanze dinamiche
# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('plto_data.log',maxBytes=5000000, backupCount=5)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# reading config file
sCFGName = 'smt.cfg'
smtConfig = ConfigParser.RawConfigParser()
smtConfig.read(sCFGName)
# setup DB parameter
host = smtConfig.get('MONGODB','host')
database = smtConfig.get('MONGODB','database')
source_database = smtConfig.get('MONGODB','source_database')
username = smtConfig.get('MONGODB','username')
password = smtConfig.get('MONGODB','password')
# Colori da associare alle aree degli strati di riferimento
main_colors = {
                'MC':'#1f77b4',
                'MCA':'#ff7f0e', 
                'SO2':'#2ca02c',
                'MFL5':'#d62728',  
                'CG':'#9467bd',
                'MIG':'#8c564b',  
                'SB':'#e377c2', 
                'MA':'#7f7f7f',
                'SO4':'#bcbd22', 
                'MFL4':'#dbdb8d', 
                'SO':'#17becf', 
                'MFL3':'#9edae5',
                'R':'#7f7f7f',
                'AA':'#bcbd22',}

def mid_point(p1,p2):
    x = (p1[0] + p2[0])/2.
    y = (p1[1] + p2[1])/2.
    return x,y



def asse2p_p1(p1,p2,x):
    if p2[0]==p1[0]:
        return p1[1]
    if p2[1]==p1[1]:
        return None
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    m_asse = -1/m
    return m_asse*(x-p1[0]) + p1[1]
    

def pfromdistance_p1(p1,p2,d):
    if abs(p2[0]-p1[0])<=0.1:
        return (p1[0] - d,p1[1]) , (p1[0]+d,p1[1])
    if abs(p2[1]-p1[1])<=0.1:
        return (p1[0],p1[1]+d) , (p1[0],p1[1] - d)
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    mx = p1[0]
    a = 1.
    b = -2.*mx
    c = mx**2-d**2*m**2/(m**2+1)
    coeff = [a, b, c]
    res_x = np.roots(coeff)
    if isinstance(res_x[0], complex):
        print '%s=x is complex for %s %s %f' % (str(res_x[0]),p1,p2,d)
        print "p2[0]-p1[0] = %f" % (p2[0]-p1[0])
        print "p2[1]-p1[1] = %f" % (p2[1]-p1[1])
    res_y0 = asse2p_p1(p1,p2,res_x[0])
    res_y1 = asse2p_p1(p1,p2,res_x[1])
    return (res_x[0],res_y0),(res_x[1],res_y1)
                
                
def asse2p(p1,p2,x):
    mid = mid_point(p1,p2)
    if abs(p2[0]-p1[0])<=0.1:
        return mid[1]
    if abs(p2[1]-p1[1])<=0.1:
        return None
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    m_asse = -1/m
    return m_asse*(x-mid[0]) + mid[1]

def pfromdistance(p1,p2,d):
    mid = mid_point(p1,p2)
    if abs(p2[0]-p1[0])<=0.1:
        return (p1[0] - d,mid[1]) , (p1[0]+d,mid[1])
    if abs(p2[1]-p1[1])<=0.1:
        return (mid[0],p1[1]+d) , (mid[0],p1[1] - d)
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    mx = mid[0]
    a = 1.
    b = -2.*mx
    c = mx**2-d**2*m**2/(m**2+1)
    coeff = [a, b, c]
    res_x = np.roots(coeff)
    if isinstance(res_x[0], complex):
        print '%s=x is complex for %s %s %f' % (str(res_x[0]),p1,p2,d)
        print "p2[0]-p1[0] = %f" % (p2[0]-p1[0])
        print "p2[1]-p1[1] = %f" % (p2[1]-p1[1])
    res_y0 = asse2p(p1,p2,res_x[0])
    res_y1 = asse2p(p1,p2,res_x[1])
    return (res_x[0],res_y0),(res_x[1],res_y1)
        
                
def plot_line( ob, color="green"):
    parts = hasattr(ob, 'geoms') and ob or [ob]
    for part in parts:
        x, y = part.xy
        plt.plot(x, y,'o', color=color, zorder=1) 
        #plt.plot(x, y, color=color, linewidth=2, solid_capstyle='round', zorder=1)    


def plot_coords( x, y, color='#999999', zorder=1):
    plt.plot(x, y, 'o', color=color, zorder=zorder)


def outputFigure(sDiagramsFolderPath, sFilename, format="svg"):
    imagefname=os.path.join(sDiagramsFolderPath,sFilename)
    if os.path.exists(imagefname):
        os.remove(imagefname)
    plt.savefig(imagefname,format=format, bbox_inches='tight', pad_inches=0)

def processSettlements(a_list):
    distanceIndex = defaultdict(list)
    for i, a_item in enumerate(a_list):
        for item in a_item["SETTLEMENTS"]:
            #if item["code"] > 0:
            distanceIndex[item["code"]].append(item["value"])
    distanceKeys = distanceIndex.keys()
    distanceKeys.sort()
    return distanceKeys, distanceIndex
    
def fillBetweenStrata(a_list):
    currentStrata = None
    x=[]
    y1=[]
    y2=[]
    facecolors=['orange','yellow']
    for i, a_item in enumerate(a_list):
        z_base = a_item['REFERENCE_STRATA']['POINTS']['base']['coordinates'][2]
        z_top = a_item['REFERENCE_STRATA']['POINTS']['top']['coordinates'][2]  
        code = a_item['REFERENCE_STRATA']['CODE']
        if not currentStrata:
            currentStrata = code        
        elif currentStrata == code:
            pass
        else:
            plt.fill_between(x, y1, y2,facecolor=main_colors[currentStrata], interpolate=True,label=currentStrata)
            x=[]
            y1=[]
            y2=[]
            currentStrata = code
        x.append(a_item['PK'])
        y1.append(z_base)
        y2.append(z_top)        

def plot_data(bAuthenticate, sPath):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    ##################################################### GIS SETUP
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # create the spatial reference, EPSG3949 RGF93 / CC49 - http://spatialreference.org/ref/epsg/3949/
    # xMin,yMin 1653513.80,8175914.21 : xMax,yMax 1659996.62,8177877.58
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3949)
    
    
    # DB authentication if required
    if bAuthenticate:
        bLoggedIn = db.authenticate(username,password,source=source_database)
    else:
        bLoggedIn = True
    if bLoggedIn:
        logger.info("Logged in")
        pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
        if pd:
            logger.info("Project %s found" % pd["project_name"])
            p = Project(db, pd)
            p.load()
            found_domains = Domain.find(db, {"project_id": p._id})
            for dom in found_domains:
                d = Domain(db,dom)
                d.load()
                # Example of query
                # asets = db.AlignmentSet.find({"$and":[{"domain_id": d._id},{"code": "main_01"}]})
                asets = db.AlignmentSet.find({"$and":[{"domain_id": d._id}]})
                for aset in asets:
                    a_set = AlignmentSet(db,aset)
                    a_set.load()
                    sCode = a_set.item["code"]
                    
                    # GIS create the data source
                    shpfname=os.path.join(sPath,"smt_%s.shp" % sCode)
                    if os.path.exists(shpfname):
                        os.remove(shpfname)
                    data_source = driver.CreateDataSource(shpfname)
                    layer = data_source.CreateLayer("subsidence", srs, ogr.wkbPoint)     
                    # Add the GIS fields we're interested in
                    field_name = ogr.FieldDefn("Name", ogr.OFTString)
                    field_name.SetWidth(24)
                    layer.CreateField(field_name)
                    field_type = ogr.FieldDefn("Type", ogr.OFTString)
                    field_type.SetWidth(24)
                    layer.CreateField(field_type)
                    field_align = ogr.FieldDefn("Alignment", ogr.OFTString)
                    field_align.SetWidth(24)
                    layer.CreateField(field_align)
                    layer.CreateField(ogr.FieldDefn("PK", ogr.OFTInteger))
                    layer.CreateField(ogr.FieldDefn("Distance", ogr.OFTInteger))
                    layer.CreateField(ogr.FieldDefn("Latitude", ogr.OFTReal))
                    layer.CreateField(ogr.FieldDefn("Longitude", ogr.OFTReal))
                    layer.CreateField(ogr.FieldDefn("Elevation", ogr.OFTInteger))
                    layer.CreateField(ogr.FieldDefn("COB", ogr.OFTReal))
                    layer.CreateField(ogr.FieldDefn("BLOWUP", ogr.OFTReal))
                    layer.CreateField(ogr.FieldDefn("SETTLEMENT", ogr.OFTReal))
                    # GIS end 
                    
                    
                    #als = db.Alignment.find({"$and":[{"alignment_set_id":a_set._id},{"PK":{"$gt":2128568}},{"PK":{"$lt":2129768}}]},{"PK":True,"COB":True,"BLOWUP":True, "PH":True, "DEM":True,"SETTLEMENT_MAX":True, "VOLUME_LOSS":True, "REFERENCE_STRATA":True, "SETTLEMENTS":True}).sort("PK", 1)
                    als = db.Alignment.find({"alignment_set_id":a_set._id},{"PK":True,"COB":True,"BLOWUP":True, "PH":True, "DEM":True,"SETTLEMENT_MAX":True, "VOLUME_LOSS":True, "REFERENCE_STRATA":True, "SETTLEMENTS":True}).sort("PK", 1)
                    a_list = list(als)
                    pks =[d['PK'] for d in a_list]
                    # scalo di fattore 100
                    cobs =[d['COB']/100 for d in a_list]
                    # scalo di fattore 100
                    blowups =[d['BLOWUP']/100 for d in a_list]
                    # amplifico di fattore 100
                    max_settlements =[d['SETTLEMENT_MAX']*100 for d in a_list]
                    phs =[d['PH']['coordinates'][2] for d in a_list]
                    dems =[d['DEM']['coordinates'][2] for d in a_list]
                    pkys =[d['PH']['coordinates'][1] for d in a_list]
                    pkxs =[d['PH']['coordinates'][0] for d in a_list]   
                    # punti medi
                    pmidx = []
                    pmidy = []
                    # punti a distanza 20 e 40
                    keys, dictValues = processSettlements(a_list)
                    pkxs_d_1 = defaultdict(list)
                    pkys_d_1 = defaultdict(list)
                    pkzs_d_1 = defaultdict(list)
                    pkxs_d_2 = defaultdict(list)
                    pkys_d_2 = defaultdict(list)
                    pkzs_d_2 = defaultdict(list)
                    mypoints = np.zeros((0,2))
                    myvalues = np.zeros(0,'f')
                    pcalc_x = []
                    pcalc_y = []
                    pcalc_z = []
                   
                    for i,x in enumerate(pkxs):

                        if i==0:
                            pass
                        else:
                            p1 = (pkxs[i-1],pkys[i-1])
                            p2 = (pkxs[i],pkys[i])
                            pm = mid_point(p1,p2)
                            pmidx.append(pm[0])
                            pmidy.append(pm[1])
                            for key in keys:
                                val = dictValues[key][i-1]
                                if key == 0.0:
                                
                                    mypoints = np.append(mypoints,[[pkxs[i-1],pkys[i-1]]],axis=0)
                                    myvalues = np.append(myvalues,[val],axis=0)
                                    # GIS 1.1
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    feature.SetField("Name", "PK %f %d" % (pks[i-1],0))
                                    feature.SetField("Type", "Central")
                                    feature.SetField("Alignment", str(sCode))
                                    feature.SetField("Distance",0)
                                    feature.SetField("PK", int(pks[i-1]))
                                    feature.SetField("Latitude", pkys[i-1])
                                    feature.SetField("Longitude", pkxs[i-1])
                                    feature.SetField("Elevation", phs[i-1])
                                    feature.SetField("COB", cobs[i-1])
                                    feature.SetField("SETTLEMENT", val)
                                    feature.SetField("BLOWUP", blowups[i-1])
                                    wkt = "POINT(%f %f)" %  (float(pkxs[i-1]) , float(pkys[i-1]))
                                    
                                    # Create the point from the Well Known Txt
                                    point = ogr.CreateGeometryFromWkt(wkt)

                                    # Set the feature geometry using the point
                                    feature.SetGeometry(point)
                                    # Create the feature in the layer (shapefile)
                                    layer.CreateFeature(feature)
                                    # Destroy the feature to free resources
                                    feature.Destroy()
                                    # GIS 1.1 end
                                else:    
                                    ret_d = pfromdistance_p1(p1,p2,key)
                                    x1 = ret_d[0][0]
                                    x2 = ret_d[1][0]
                                    y1 = ret_d[0][1]
                                    y2 = ret_d[1][1]
                                    pkxs_d_1[key].append(x1)
                                    pkxs_d_2[key].append(x2)
                                    pkys_d_1[key].append(y1)
                                    pkys_d_2[key].append(y2) 
                                    mypoints = np.append(mypoints,[[x1,y1]],axis=0)
                                    pcalc_x.append(x1)
                                    pcalc_y.append(y1)
                                    pcalc_z.append(val)
                                    myvalues = np.append(myvalues,[val],axis=0)
                                    mypoints = np.append(mypoints,[[x2,y2]],axis=0)
                                    pcalc_x.append(x2)
                                    pcalc_y.append(y2)
                                    pcalc_z.append(val)
                                    myvalues = np.append(myvalues,[val],axis=0)
                                    
                                    # GIS 1.1
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    feature.SetField("Name", "PK %f +%d" % (pks[i-1],int(key)))
                                    feature.SetField("Type", "Distance")
                                    feature.SetField("Alignment", str(sCode))
                                    feature.SetField("Distance",int(key))
                                    feature.SetField("PK", int(pks[i-1]))
                                    feature.SetField("Latitude", y1)
                                    feature.SetField("Longitude", x1)
                                    feature.SetField("Elevation", phs[i])
                                    feature.SetField("COB", cobs[i])
                                    feature.SetField("SETTLEMENT", val)
                                    feature.SetField("BLOWUP", blowups[i])
                                    wkt = "POINT(%f %f)" %  (float(x1) , float(y1))
                                    
                                    # Create the point from the Well Known Txt
                                    point = ogr.CreateGeometryFromWkt(wkt)

                                    # Set the feature geometry using the point
                                    feature.SetGeometry(point)
                                    # Create the feature in the layer (shapefile)
                                    layer.CreateFeature(feature)
                                    # Destroy the feature to free resources
                                    feature.Destroy()
                                    
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    feature.SetField("Name", "PK %f -%d" % (pks[i],int(key)))
                                    feature.SetField("Type", "Distance")           
                                    feature.SetField("Alignment", str(sCode))
                                    feature.SetField("Distance",int(key))
                                    feature.SetField("PK", int(pks[i]))
                                    feature.SetField("Latitude", y2)
                                    feature.SetField("Longitude", x2)
                                    feature.SetField("Elevation", dems[i])
                                    feature.SetField("COB", cobs[i])
                                    feature.SetField("SETTLEMENT", val)
                                    feature.SetField("BLOWUP", blowups[i])
                                    wkt = "POINT(%f %f)" %  (float(x2) , float(y2))
                                    
                                    # Create the point from the Well Known Txt
                                    point = ogr.CreateGeometryFromWkt(wkt)

                                    # Set the feature geometry using the point
                                    feature.SetGeometry(point)
                                    # Create the feature in the layer (shapefile)
                                    layer.CreateFeature(feature)
                                    # Destroy the feature to free resources
                                    feature.Destroy()
                                    
                                    # GIS 1.1 end
                    
                    x_min, x_max, y_min, y_max = layer.GetExtent()
                    
                    data_source.Destroy()
                    ############### END GIS
                    min_x = min(pcalc_x)
                    min_y = min(pcalc_y)
                    max_x = max(pcalc_x)
                    max_y = max(pcalc_y)
                    # Interpolazione ...forse non è la cosa giusta da fare
                    logger.info("x range %d" % (max_x - min_x) )
                    logger.info("y range %d" % (max_y - min_y) )
                    gx, gy =  np.mgrid[min_x:max_x:1500j,min_y:max_y:1500j]
                    m_interp_cubic = griddata(mypoints, myvalues, (gx, gy),method='cubic')
                    # plot
                    fig = plt.figure()
                    plt.title("Profilo %s" % sCode)
                    ### visualizza gli strati di riferimento
                    # fillBetweenStrata(a_list)
                    
                    ################################################
                    plt.plot(pks,phs, linewidth=2,label='Tracciato')
                    plt.plot(pks,dems,  linewidth=2,label='DEM' )
                    plt.plot(pks,cobs, label='COB / 100')
                    plt.plot(pks,blowups, label='BLOWUP / 100')
                    plt.plot(pks,max_settlements, label='SETTLEMENT_MAX * 100')
                    plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                    plt.legend()
                    outputFigure(sPath, "profilo_%s.svg" % a_set.item["code"])            
                    logger.info("profilo_%s.png plotted in %s" % (a_set.item["code"], sPath))
                    plt.close(fig)
                    fig = plt.figure()
                    # stampa planimetria
                    plt.title("Planimetria") 

                    # filtro a zero tutto qeullo che sta sotto
                    # m_interp_cubic[ m_interp_cubic < 0.0] = 0.0
                        
                    
                    cp = plt.contour(gx, gy, m_interp_cubic,linewidths=0.5,colors='k')
                    cmap = LinearSegmentedColormap.from_list(name="Custom CMap", colors =["white", "blue", "red"], N=11)
                    contours = plt.contourf(gx, gy, m_interp_cubic,cmap = cmap)
                    
                    
                    # GIS create the data source
                    attr_name = "SETTLEMENT"
                    shpfname=os.path.join(sPath,"contour_%s.shp" % sCode)
                    if os.path.exists(shpfname):
                        os.remove(shpfname)
                    dst_ds = driver.CreateDataSource(shpfname)
                    dst_layer = dst_ds.CreateLayer("contour_subsidence", srs, ogr.wkbPolygon)     
                    # Add the GIS fields we're interested in
                    dst_layer.CreateField(ogr.FieldDefn(attr_name, ogr.OFTReal))
                    field_align = ogr.FieldDefn("Alignment", ogr.OFTString)
                    field_align.SetWidth(24)
                    dst_layer.CreateField(field_align)
                    field_level = ogr.FieldDefn("LevelID", ogr.OFTString)
                    field_level.SetWidth(24)
                    dst_layer.CreateField(field_level)
                    # GIS end 
                    
                    for level in range(len(contours.collections)): 
                        paths = contours.collections[level].get_paths()  
                        for path in paths:  

                            feat_out = ogr.Feature( dst_layer.GetLayerDefn())  
                            feat_out.SetField( attr_name, contours.levels[level] )  
                            feat_out.SetField("Alignment", str(sCode))
                            feat_out.SetField("LevelID", str(level))
                            pol = ogr.Geometry(ogr.wkbPolygon)  


                            ring = None              
                              
                            for i in range(len(path.vertices)):  
                                point = path.vertices[i]  
                                if path.codes[i] == 1:  
                                    if ring != None:  
                                        pol.AddGeometry(ring)  
                                    ring = ogr.Geometry(ogr.wkbLinearRing)  
                                      
                                ring.AddPoint_2D(point[0], point[1])  
                              

                            pol.AddGeometry(ring)  
                              
                            feat_out.SetGeometry(pol)  
                            if dst_layer.CreateFeature(feat_out) != 0:  
                                print "Failed to create feature in shapefile.\n"  
                                exit( 1 )  

                              
                            feat_out.Destroy()  


                    """
                    # Create the destination tiff data source
                    raster_fn=os.path.join(sPath,"smt_%s.tif" % sCode)
                    if os.path.exists(raster_fn):
                        os.remove(raster_fn)
                    
                    # Define pixel_size and NoData value of new raster

                    pixel_size = 1
                    NoData_value = -9999
                    x_res = int((max_x - min_x) / pixel_size)
                    y_res = int((max_y - min_y) / pixel_size)
                    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
                    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
                    band = target_ds.GetRasterBand(1)
                    band.WriteArray(m_interp_cubic)
                    outRasterSRS = osr.SpatialReference()
                    outRasterSRS.ImportFromEPSG(3949)
                    outRaster.SetProjection(outRasterSRS.ExportToWkt())
                    outband.FlushCache()
                    """
                    
                    
                    
                    plt.colorbar()
                    plt.plot(pkxs,pkys, "g-",label='Tracciato %s' % a_set.item["code"])
                    plt.plot(pkxs,pkys, "g.")

                    # Punti medi
                    plt.plot(pmidx,pmidy, "gx")
                    
                    for key in keys:
                        pkzs_d_1[key] = dictValues[key]
                        pkzs_d_2[key] = dictValues[key]
                        plt.plot(pkxs_d_1[key],pkys_d_1[key], "w.", ms=1)
                        plt.plot(pkxs_d_2[key],pkys_d_2[key], "w.", ms=1)
                    
                    array_x = np.asarray(pcalc_x)
                    array_y = np.asarray(pcalc_y)
                    array_z = np.asarray(pcalc_z)
                    plt.axis("equal")
                    outputFigure(sPath, "tracciato_%s.svg" % a_set.item["code"], format="svg")
                    logger.info("tracciato_%s.png plotted in %s" % (a_set.item["code"], sPath))
                    #plt.show()
                    plt.close(fig)
                    logger.info("plot_data terminated!")
    else:
        logger.error("Authentication failed")
        
                
def main(argv):
    sPath = None
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) +" -p <output folder path> [-a for autentication -h for help]"
    try:
        opts, args = getopt.getopt(argv,"hap:",["path="])
    except getopt.GetoptError:
        print sSyntax
        sys.exit(1)
    if len(opts) < 1:
        print sSyntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sSyntax
            sys.exit()
        elif opt == '-a':
            bAuthenticate = True
        elif opt in ("-p", "--path"):
            sPath = arg
            if not os.path.isdir(sPath):
                print sSyntax
                print "Directory %s does not exists!" % sPath
                sPath = None
                sys.exit(3)
    if sPath:
        plot_data(bAuthenticate, sPath)
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
