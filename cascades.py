import sys
sys.path.append('D:/ATLData/Documents/GitHub/pyrms/')
sys.path.append('D:/ATLData/Documents/GitHub/flopy/')
from prms import paramFile
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point
from prms import paramFile
import matplotlib.pyplot as plt
from flopy.utils.reference import SpatialReference
from GISio import df2shp, arc_ascii



class cascadeParamFile(paramFile):

    def __init__(self, filename='stuff.param', dimensions={}, params={},
                 nrow=None, ncol=None, xy_points=None, sr=None, gw=False,
                 verbose=False):

        paramFile.__init__(self, filename=filename, dimensions=dimensions, params=params,
                           nrow=nrow, ncol=ncol,
                           verbose=False)

        self._set_names(gw)
        self.gw = gw # groundwater or hru cascades

        self.xy_points = xy_points
        if sr is not None:
            self.xy_points = np.array(list(zip(sr.xcentergrid.ravel(),
                                               sr.ycentergrid.ravel())))
            nrow, ncol = sr.nrow, sr.ncol
            if sr.epsg is not None:
                self.epsg = sr.epsg
        return


    def _set_names(self, gw=False):
        self.didname = 'hru_down_id' if not gw else 'gw_down_id'
        self.uidname = 'hru_up_id' if not gw else 'gw_up_id'

    @property
    def df(self):
        assert self.didname in self.params.keys() and self.uidname in self.params.keys()
        did = self.params[self.didname].array
        uid = self.params[self.uidname].array
        lines = [self.make_arrow(d, u) for d, u in zip(did, uid) if d != 0]
        return pd.DataFrame({self.didname: did[did != 0], self.uidname: uid[did != 0], 'geometry': lines})

    @property
    def outlets(self):
        assert self.didname in self.params.keys() and self.uidname in self.params.keys()
        did = self.params[self.didname].array
        uid = self.params[self.uidname].array
        outlets = uid[did == 0]
        outletxys = self.xy_points[outlets - 1]
        outletpoints = [Point(*p) for p in outletxys]
        return pd.DataFrame({self.uidname: outlets, 'geometry': outletpoints})

    @staticmethod
    def load(filename, model=None, nrow=None, ncol=None,
             xy_points=None, sr=None, gw=False, verbose=False):

        pf = cascadeParamFile(filename=filename, nrow=nrow, ncol=ncol,
                              xy_points=None, sr=sr, gw=gw,
                              verbose=verbose)

        with open(filename) as input:

            line = pf.read_comments(input)
            if 'Dimensions' in line:
                if verbose:
                    print('reading dimensions...')
                line = paramFile._read_stuff(input, line, pf.read_dimension)
            if 'Parameters' in line or '####' in line:
                if verbose:
                    print('reading parameters...')
                line = paramFile._read_stuff(input, line, pf.read_param)

        cascadetype = set([k.split('_')[0] for k in pf.params.keys()])
        print(cascadetype)
        if len(cascadetype) == 1 and 'gw' in cascadetype:
            pf.gw = True

        if model is not None:
            model.dimensions.update(pf.dimensions)
            model.params.update(pf.params)
            model.param_files[filename] = pf
            model.paramdf.append(pf.df)
        return pf

    @staticmethod
    def write_gwcascade_from_hrucascade(hrucascadefile, gwcascadefile=None):
        if gwcascadefile is None:
            gwcascadefile = hrucascadefile.replace('.param', 'gw.param')
        with open(hrucascadefile) as input:
            txt = input.read()
            txt = txt.replace('hru_', 'gw_').replace('ncascade', 'ncascdgw')
            with open(gwcascadefile, 'w') as output:
                output.write(txt)

    def make_arrow(self, dn_hru, up_hru):
        u, d = dn_hru, up_hru

        # get the coordinates of the up and down hrus; make a line
        dn_xy = self.xy_points[d - 1]
        up_xy = self.xy_points[u - 1]
        ls = LineString([dn_xy, up_xy])

        # trim the line so it only covers half distance between nodes
        p1 = ls.interpolate(ls.length * .25)
        p2 = ls.interpolate(ls.length * .75)
        ls = LineString([p1, p2])
        return ls

    def write_cascades_shapefile(self, filename, gw=False, epsg=None):
        epsg = self.epsg if epsg is None else epsg
        df2shp(self.df, filename, epsg=epsg)

    def write_outlets_shapefile(self, filename, gw=False, epsg=None):
        epsg = self.epsg if epsg is None else epsg
        df2shp(self.outlets, filename, epsg=epsg)