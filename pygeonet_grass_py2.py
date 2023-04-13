import os
import sys
import shutil
import subprocess
from time import clock
import ConfigParser
#from pygeonet_rasterio import *
import grass.script as g
import grass.script.setup as gsetup

def grass(demFileName, geonetResultsDir, pmGrassGISfileName):
    grass7bin = 'grass76'
    if sys.platform.startswith('win'):
        # MS Windows
        grass7bin = r'C:\Program Files\GRASS GIS 7.6\grass76.bat'
        # uncomment when using standalone WinGRASS installer
        # grass7bin = r'C:\software\GRASS GIS 7.6\grass76.bat'
        # this can be avoided if GRASS executable is added to PATH
    elif sys.platform == 'darwin':
        # Mac OS X
        # TODO: this have to be checked, maybe unix way is good enough
        grass7bin = r'C:\software\GRASS_GIS_7.6\grass76.bat'
    startcmd = [grass7bin, '--config', 'path']
    p = subprocess.Popen(startcmd, shell=False,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 " \
              "start script (%s)" % startcmd
        sys.exit(-1)
    gisbase = out.strip('\n\r')
    gisdb = os.path.join(os.path.expanduser("~"), "grassdata")
    mswin = sys.platform.startswith('win')
    if mswin:
        gisdbdir = os.path.join(os.path.expanduser("~"), "Personal\grassdata")
    else:
        gisdbdir = os.path.join(os.path.expanduser("~"), "grassdata")
    gisdbdir = r"C:\Users\\alecc\Documents\grassdata1"
    geotiff = pmGrassGISfileName
    locationGeonet = 'geonet'
    grassGISlocation = os.path.join(gisdbdir, locationGeonet)
    if os.path.exists(grassGISlocation):
        print "Cleaning existing Grass location"
        shutil.rmtree(grassGISlocation)
    gsetup.init(gisbase, gisdbdir, locationGeonet, 'PERMANENT')
    mapsetGeonet = 'geonetuser'
    print 'Making the geonet location'
    g.run_command('g.proj', georef=geotiff, location = locationGeonet)
    location = locationGeonet  
    mapset = mapsetGeonet
    print 'Existing Mapsets after making locations:'
    g.read_command('g.mapsets', flags = 'l')
    print 'Setting GRASSGIS environ'
    gsetup.init(gisbase, gisdbdir, locationGeonet, 'PERMANENT')
    ##    g.gisenv()
    print 'Making mapset now'
    g.run_command('g.mapset', flags = 'c', mapset = mapsetGeonet,\
                  location = locationGeonet, dbase = gisdbdir)
    # gsetup initialization 
    gsetup.init(gisbase, gisdbdir, locationGeonet, mapsetGeonet)
    # Read the filtered DEM
    print 'Import filtered DEM into GRASSGIS and '\
          'name the new layer with the DEM name'
    tmpfile = demFileName 
    geotiffmapraster = tmpfile.split('.')[0]
    print 'GRASSGIS layer name: ',geotiffmapraster
    g.run_command('r.in.gdal', input=geotiff, \
                  output=geotiffmapraster,overwrite=True)
    #Flow computation for massive grids (float version)
    print "Calling the r.watershed command from GRASS GIS"
    subbasinThreshold = 1500
    print ('using swap memory option for large size DEM')
    g.run_command('r.watershed',flags ='am',overwrite=True,\
                  elevation=geotiffmapraster, \
                  threshold=subbasinThreshold, \
                  drainage = 'dra1v23')
    g.run_command('r.watershed',flags ='am',overwrite=True,\
                  elevation=geotiffmapraster, \
                  threshold=subbasinThreshold, \
                  accumulation='acc1v23')
    print 'Identify outlets by negative flow direction'
    g.run_command('r.mapcalc',overwrite=True,\
                  expression='outletmap = if(dra1v23 >= 0,null(),1)')
    print 'Convert outlet raster to vector'
    g.run_command('r.to.vect',overwrite=True,\
                  input = 'outletmap', output = 'outletsmapvec',\
                  type='point')
    print 'Delineate basins according to outlets'
    g.run_command('r.stream.basins',overwrite=True,\
                  direction='dra1v23',points='outletsmapvec',\
                  basins = 'outletbasins')
    # Save the outputs as TIFs
    outlet_filename = geotiffmapraster + '_outlets.tif'
    g.run_command('r.out.gdal',overwrite=True,\
                  input='outletmap', type='Float32',\
                  output=os.path.join(geonetResultsDir,
                                      outlet_filename),\
                  format='GTiff')
    outputFAC_filename = geotiffmapraster + '_fac.tif'
    g.run_command('r.out.gdal',overwrite=True,\
                  input='acc1v23', type='Float64',\
                  output=os.path.join(geonetResultsDir,
                                      outputFAC_filename),\
                  format='GTiff')
    outputFDR_filename = geotiffmapraster + '_fdr.tif'
    g.run_command('r.out.gdal',overwrite=True,\
                  input = "dra1v23", type='Int32',\
                  output=os.path.join(geonetResultsDir,
                                      outputFDR_filename),\
                  format='GTiff')
    outputBAS_filename = geotiffmapraster + '_basins.tif'
    g.run_command('r.out.gdal',overwrite=True,\
                  input = "outletbasins", type='Int16',\
                  output=os.path.join(geonetResultsDir,
                                      outputBAS_filename),\
                  format='GTiff')
# def path_finder():
#    config = ConfigParser.RawConfigParser()
#    cfg =[]
#    for dirpath, subdirs, files in os.walk(os.getcwd()):
#    	for y in subdirs:
# 		if y.endswith
#    	for x in files:
#        	if x.endswith("_blah.cfg"):
#            		cfg.append(os.path.join(dirpath, x))
#    print(cfg)
#    config.read('GeoFlood.cfg')
#    demFileName=config.get('Section','dem_name')
#    geoNetHomeDir = config.get('Section', 'geofloodhomedir')
#    geonetResultsDir = os.path.join(geoNetHomeDir,"Outputs","GIS")
#    pmGrassGISfileName = os.path.join(geonetResultsDir, "PM_filtered_grassgis.tif")

#    return demFileName, geonetResultsDir, pmGrassGISfileName 

def main():
    abspath=os.path.abspath(__file__)
    geonet_dir = os.path.dirname(os.path.dirname(abspath))
    #geonet_dir = os.path.dirname(abspath)
    config = ConfigParser.RawConfigParser()
    #config.read(os.path.join(geonet_dir,"GeoFlood.cfg"))
    config.read(os.path.join(geonet_dir,"GeoNet_my_project.cfg"))
    projectname=config.get('Section','projectname')
    dem_name=config.get('Section','dem_name')
    demFileName=dem_name+'.tif'
    # geonetResultsDir=os.path.join(geonet_dir,"Outputs","GIS",projectname)
    geonetResultsDir=os.path.join(geonet_dir,"GeoOutputs","GIS",projectname)
    pmGrassGISfileName = os.path.join(geonetResultsDir, "PM_filtered_grassgis.tif")
    #pmGrassGISfileName = "PM_filtered_grassgis.tif"
    print(demFileName,geonetResultsDir,pmGrassGISfileName)
    grass(demFileName, geonetResultsDir, pmGrassGISfileName)

if __name__ == '__main__':
    #demFileName, geonetResultsDir, pmGrassGISfileName=path_finder()
    t0 = clock()
    main()
    t1 = clock()
    print "time taken to complete flow accumulation:", t1-t0, " seconds"
