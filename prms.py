import numpy as np
import pandas as pd

prmsdtypes = {int: 1, float: 2, str: 4}
dtypes = {v:k for k, v in prmsdtypes.items()}
fmt = {1: '%d', 2: '%.16f', 4: '%s'}

class param:

    def __init__(self, name, values, ndim=1, dim_names=['one'],
                 dtype=None, nrow=None, ncol=None, verbose=False):

        if not isinstance(values, list) and not isinstance(values, np.ndarray):
            values = [values]
        if dtype is None:
            for prmsdtype, pydtype in dtypes.items():
                if isinstance(values[0], pydtype):
                    self.dtype = prmsdtype
        else:
            self.dtype = dtype
            pydtype = dtypes[dtype]
            # enforce submitted dtypes
            values = list(map(pydtype, values))

        self.name = name
        self.ndim = ndim
        self.dim_names = dim_names
        self.nvalues = len(values)
        self.array = np.array(values, dtype=dtypes[self.dtype])
        if nrow is not None and ncol is not None:
            if self.nvalues == nrow * ncol:
                self.array = np.reshape(values, (nrow, ncol))
        self.verbose = verbose

    def write(self, f):

        # update the array length in case it has been changed
        a = self.array.ravel()
        self.nvalues = len(a)
        f.write('####\n')
        f.write('{}\n{:d}\n'.format(self.name, self.ndim))
        for n in self.dim_names:
            f.write('{}\n'.format(n))
        f.write('{:d}\n{:d}\n'.format(self.nvalues, self.dtype))
        df = pd.DataFrame(a)
        df.to_csv(f, index=False, header=False)
        if self.verbose:
            print(self.name)

class paramFile(object):

    def __init__(self, filename='stuff.param', dimensions={}, params={},
                 nrow=None, ncol=None,
                 verbose=False):

        self.filename = filename
        self.dimensions = dimensions
        self.params = params
        self.nrow = nrow
        self.ncol = ncol
        self.verbose = verbose
        self.param_order = []
        return

    @property
    def df(self):
        return self.get_dataframe()

    def get_dataframe(self):
        plist = []
        for k, v in self.params.items():
            plist.append([v.name, v.nvalues, v.array.min(), v.array.mean(), v.array.max()])
        return pd.DataFrame(plist, columns=['name', 'nvalues', 'min', 'mean', 'max'])

    def read_comments(self, f):
        comments = ''
        while True:
            line = next(f)
            if '####' in line or '**' in line:
                break
            else:
                comments += line.strip() + '\n'
        self.comments = comments
        return line

    def read_dimension(self, f):
        dim_name = next(f).strip()
        dim_len = int(next(f).strip())
        self.dimensions[dim_name] = dim_len
        if self.verbose:
            print(dim_name)

    @staticmethod
    def _read_stuff(f, line, addtoo):
        # in case index is already at delimiter
        if '####' in line:
            addtoo(f)
        for line in f:
            if '####' in line:
                addtoo(f)
            else:
                return line

    def read_param(self, f):
        name = next(f).strip()
        ndim = int(next(f).strip())
        dim_names = []
        for d in range(ndim):
            dim_names.append(next(f).strip())
        nvalues = int(next(f).strip())
        dtype = int(next(f).strip())
        convert_dtype = dtypes[dtype]
        values = [convert_dtype(next(f).strip()) for i in range(nvalues)]
        self.params[name] = param(name, values, ndim=ndim,
                                  dim_names=dim_names,
                                  dtype=dtype,
                                  nrow=self.nrow, ncol=self.ncol)
        self.param_order.append(name)
        if self.verbose:
            print(name)

    @staticmethod
    def load(filename, model=None, nrow=None, ncol=None, verbose=False):

        pf = paramFile(filename=filename, nrow=nrow, ncol=ncol, verbose=verbose)
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

        if model is not None:
            model.dimensions.update(pf.dimensions)
            model.params.update(pf.params)
            model.param_files[filename] = pf
            model.paramdf.append(pf.df)
        else:
            return pf

    def write(self, filename=None):

        # determine an order for writing parameters
        # (alphabetically if none specified)
        if len(self.param_order) != len(self.params):
            self.param_order = sorted(list(self.params.keys()))

        with open(filename, 'w') as output:
            output.write(self.comments)
            if len(self.dimensions) > 0:
                if self.verbose:
                    print('\nwriting parameter dimension info...')
                output.write('** Dimensions **\n')
                for k, v in self.dimensions.items():
                    output.write('####\n{}\n{:d}\n'.format(k, v))
            if len(self.params) > 0:
                if self.verbose:
                    print('\nwriting parameters...')
                if len(self.dimensions) > 0:
                    output.write('** Parameters **\n')
            for k in self.param_order:
                self.params[k].write(output)

