import os
from osgeo import gdal

def merge_warp_dems(inFileNames, outFileName, outExtent = None, outEPSG = None, pixelSize=None, doReturnGdalSourceResult = False,
                    resampleAlg = 'cubic', noDataValue = None, format = 'GTiff', compression=None, NumThreads = None):
    """Wrapper for gdal.Warp, an image mosaicing, reprojection and cropping function

    Args:
        inFileNames (list): A list of all the filenames to merge
        outFileName (str): the output path to save the file as
        outExtent (list OR tuple, optional): ([minx, maxx], [miny, maxy]). Defaults to None.
        outEPSG (int, optional): EPSG code for the coordinate system of the specified output extent (also sets the output
            coordinate system). Defaults to None.
        pixelSize (float, optional):  Dimension of the output pixels (x and y direction) in the native units of the
            output coordinate system. Defaults to None.
        doReturnGdalSourceResult (bool, optional): If True returns the gdal source object for the newly created dataset. 
            If False (the default) returns none and closes the connection to the newly created dataset. Defaults to False.
        resampleAlg (str, optional): The resampling algorithm to use in reprojecting and merging the raster. Can be
            any option allowed by GDAL. Prefered options will likely be: 'near', 'bilinear', 'cubic', 'cubicspline',
            'average'. Defaults to 'cubic'.
        noDataValue (float, optional): No data value to use for the input and output data. Defaults to None.
        format (str, optional): File format to save the output dataset as. Defaults to 'GTiff'.
        compression (str, optional): Compression algorithm to use when saving the output dataset. Defaults to None.
        NumThreads (int, optional): Number of threads to use when processing the data. Defaults to None.

    Returns:
        gridSource (None OR gdal.Dataset): If doReturnGdalSource is False, returns None. If doReturnGdalSource is True
            will instead return a gdal.Dataset instance representing the input raster after application of the warp.
    """

    #In some ArcPro created virtual environments the path to the PROJ library (opensource projections) is not always created on startup
    #This will cause a gdal error when trying to transform raster bounding box coordinates to a new CRS.
    #This statement attempts to guess what the path should be, though there is no gurantee this will work w/ all environments
    if not('PROJ_LIB' in os.environ):
        env_path = os.environ['PATH'].split(';')[1] #The second item in the path in arcpro environments is <directory>\\environment\\Libray\\bin
        env_path = os.path.abspath(os.path.join(env_path ,os.pardir)) #Get the path on directory up (to library)
        proj_path = os.path.join(env_path,'share','proj')
        os.environ['PROJ_LIB'] = proj_path

    if not(outExtent is None):
        outExtent = [outExtent[0][0], outExtent[1][0], outExtent[0][1], outExtent[1][1]]


        #If an output coordinate system was specified, format it for gdal
    if not(outEPSG is None):
        outEPSG = 'EPSG:{}'.format(outEPSG)
        #If an output bounding box was specified, format it for gdal. Leave as none if there won't be any clipping


    # Get some creation options for the output file
    creationOptions = ['BIGTIFF=YES', 'TILED=YES']
    # get multithread options
    if NumThreads > 1:
        multithread = True
        NumThreads = int(NumThreads)
        workingmemory = '80%'
        creationOptions.append('NUM_THREADS={}'.format(NumThreads))
    else:
        multithread = False
    # get compression options
    if compression is not None:
        creationOptions.append('COMPRESS={}'.format(compression))
    
    wrpOptions = gdal.WarpOptions(
        outputBounds=outExtent,
        outputBoundsSRS=outEPSG,
        format=format,
        xRes=pixelSize, yRes=pixelSize,
        resampleAlg=resampleAlg,
        dstSRS=outEPSG,
        dstNodata=noDataValue,
        srcNodata=noDataValue,
        multithread=multithread,
        warpMemoryLimit = workingmemory,
        creationOptions = creationOptions
    )
    gridSource = gdal.Warp(outFileName,inFileNames, options=wrpOptions)

   
    if not(doReturnGdalSourceResult):
        gridSource = None

    return gridSource