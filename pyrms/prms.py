import os
import numpy as np
import pandas as pd
from .cascades import cascadeParamFile
from .control import controlFile
from .param import paramFile

class model:

    def __init__(self, control_file, model_ws=None,
                 structured=True, nrow=None, ncol=None,
                 verbose=False):

        self.verbose = verbose
        self.model_ws, self.control_file = os.path.split(control_file)
        if model_ws is not None:
            self.model_ws = model_ws
        self.files = {}

        self.structured = structured
        self.nrow = nrow
        self.ncol = ncol

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

    @staticmethod
    def load(control_file, m=None,
             xy_points=None, sr=None, nrow=None, ncol=None,
             skip=None,
             verbose=False):

        if m is None:
            m = model(control_file=control_file, verbose=verbose)

        if skip is None:
            skip = []
        elif isinstance(skip, str):
            skip = [skip]
        print('loading model...\n{}'.format(control_file))
        m.ctrl = controlFile.load(control_file, verbose=verbose)
        for pf in m.ctrl.param_file.values:
            if os.path.split(pf)[1].split('.')[0] in skip:
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
        return m

