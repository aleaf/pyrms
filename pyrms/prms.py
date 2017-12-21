import os
import numpy as np
import pandas as pd
from .cascades import cascadeParamFile
from .control import controlFile
from .param import paramFile

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

        self.xy_points = xy_points # placeholder for non-structured ref
        self.sr = sr
        self.structured = structured
        self.nrow = nrow
        self.ncol = ncol

    @property
    def dimensions(self):
        dims = self._dimensions
        if dims is None:
            dims = {}
        for k, v in self.files.items():
            if len(v.dimensions) > 0:
                dims.update(v.dimensions)
                self.dimensions_file = k
        return dims

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
                                              verbose=verbose)
            else:
                m.files[pf] = cascadeParamFile.load(pf,
                                                     xy_points=xy_points, sr=sr,
                                                     nrow=nrow, ncol=ncol,
                                                     verbose=verbose)
        # dimensions must be listed first
        if m.dimensions_file is not None and m.files[0] != m.dimensions_file:
            m.files.remove(m.dimensions_file)
            m.file.insert(0, m.dimensions_file)
        m.check()
        return m

    def write_dimensions(self, f=None):
        if f is None:
            filename = self.dimensions_file
        if filename is None:
            filename = 'dimensions.params'

        if filename in self.files and self.files[0] != filename:
            self.files.remove(self.dimensions_file)
            self.file.insert(0, self.dimensions_file)
        df = paramFile(filename, dimensions=self.dimensions)
        df.write()


