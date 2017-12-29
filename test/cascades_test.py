import sys
import os
import glob
sys.path += glob.glob('/Users/aleaf/Documents/GitHub/*')
import numpy as np
from flopy.utils.reference import SpatialReference
from pyrms import cascadeParamFile

if not os.path.exists('tmp'):
    os.mkdir('tmp')

# spatial reference info
nrow, ncol = 409, 614
dxdy_m = 76.2*2
xll, yll = 617822.3, 5114820.7
yul = yll + dxdy_m * nrow
epsg = 26715
sr = SpatialReference(delr=np.ones(ncol)*dxdy_m, delc=np.ones(nrow)*dxdy_m,
                      xll=xll, yll=yll, epsg=26715)

cascadesfile = '/Users/aleaf/Documents/BR/gsflow/data500/params/all_cascades.param'
cascades = cascadeParamFile.load(cascadesfile, sr=sr)
cascades.write_cascades_shapefile('tmp/cascades.shp', epsg=26715)
cascades.write_outlets_shapefile('tmp/cascade_outlets.shp', epsg=26715)
j=2