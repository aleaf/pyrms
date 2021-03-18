import os
import numpy as np
import pandas as pd
from pyrms.cascades import cascadeParamFile
from pyrms.control import controlFile
from pyrms.param import paramFile

class model:

    def __init__(self, control_file, model_ws=None,
                 xy_points=None, sr=None,
                 structured=True, nrow=None, ncol=None,
                 verbose=False):


        self.verbose = verbose
        self.model_ws, self.control_file = os.path.split(control_file)
        if model_ws is not None:
            self.model_ws = model_ws
        self.files = {}
        self.control_file = control_file
        self.dimensions_file = None
        self._dimensions = None
        self.param_files = []

        self.xy_points = xy_points # placeholder for non-structured ref
        self.sr = sr
        self.structured = structured
        self.nrow = nrow
        self.ncol = ncol

    def __setattr__(self, key, value):
        if key == "dimensions":
            super(model, self). \
                __setattr__("_dimensions", np.atleast_1d(np.array(value)))
        elif key == "params":
            super(model, self). \
                __setattr__("_params", np.atleast_1d(np.array(value)))
        else:
            super(model, self).__setattr__(key, value)

    @property
    def dimensions(self):
        dims = self._dimensions
        if dims is None:
            dims = {}
            for k, v in self.files.items():
                if len(v.dimensions) > 0:
                    dims.update(v.dimensions)
                    self.dimensions_file = k
            self._dimensions = dims
        return dims

    @property
    def hru_type(self):
        hru_type = self.params.get('hru_type', None)
        if hru_type is not None:
            return hru_type.array
        return np.ones(self.nhru)

    @property
    def nhru(self):
        for p in self.params:
            if p.dim_names[0] == 'nhru':
                return p.dim_names[0]
        return 0

    @property
    def params(self):
        params = {}
        for k, v in self.files.items():
            for n, p in v.params.items():
                params[n] = p
        return params

    @property
    def summary(self):
        return pd.concat([v.summary for k, v in self.files.items()])

    def check(self):

        # check for duplicate parameter values
        isduplicate = self.summary.duplicated(subset='name', keep=False)
        df = self.summary.loc[isduplicate]
        if len(df) > 0:
            print('Warning: Duplicate parameter entries found! See duplicate_params.csv')
            df.to_csv('duplicate_params.csv')

    @staticmethod
    def load(control_file, m=None,
             load_only=None,
             xy_points=None, sr=None, nrow=None, ncol=None,
             skip=None,
             verbose=False, check=True):

        if load_only is not None:
            load_only = [os.path.split(f)[1].split('.')[0]
                         for f in load_only]

        if m is None:
            m = model(control_file=control_file,
                      xy_points=xy_points, sr=sr,
                      nrow=nrow, ncol=ncol, verbose=verbose)

        if skip is None:
            skip = []
        elif isinstance(skip, str):
            skip = [skip]
        print('loading model...\n{}'.format(control_file))
        m.ctrl = controlFile.load(control_file, verbose=verbose)
        for pf in m.ctrl.param_file.values:
            basename = os.path.split(pf)[1].split('.')[0]
            if load_only is not None and basename not in load_only:
                print('\tskipping {}'.format(pf))
                continue
            if basename in skip:
                print('\tskipping {}'.format(pf))
                continue
            print(pf)
            pf = os.path.join(m.model_ws, pf)
            if 'cascade' not in pf:
                m.files[pf] = paramFile.load(pf, nrow=nrow, ncol=ncol,
                                              model=m,
                                              verbose=verbose)
            else:
                m.files[pf] = cascadeParamFile.load(pf,
                                                     xy_points=xy_points, sr=sr,
                                                     nrow=nrow, ncol=ncol,
                                                     model=m,
                                                     verbose=verbose)
        m.check()
        return m

    def write_dimensions(self, f=None):
        if f is None:
            filename = self.dimensions_file
        if filename is None:
            filename = 'dimensions.params'

        df = paramFile(filename, dimensions=self.dimensions)
        df.write()


