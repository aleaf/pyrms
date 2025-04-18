import os
import numpy as np
from flopy.discretization import StructuredGrid
from pyrms import cascadeParamFile


def test_export_cascades():
    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    
    nrow, ncol = 409, 614
    modelgrid_meters = StructuredGrid(
        delr=np.ones(ncol)*500*.3048,
        delc=np.ones(nrow)*500*.3048,
        xoff=617822.3,
        yoff=5114820.7,
        crs=26715,
    )
    
    cascadesfile = 'tests/data/all_cascades.param'
    cascades = cascadeParamFile.load(cascadesfile, sr=sr)
    cascades.write_cascades_shapefile('tmp/cascades.shp', epsg=26715)
    cascades.write_outlets_shapefile('tmp/cascade_outlets.shp', epsg=26715)
j=2