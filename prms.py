import numpy as np
import pandas as pd

prmsdtypes = {int: 1, float: 2, str: 4,
              np.int32: 1, np.int64: 1}
dtypes = {v:k for k, v in prmsdtypes.items()}
fmt = {1: '%d', 2: '%.16f', 4: '%s'}

class param:

    def __init__(self, name, values, ndim=1, dim_names=['one'],
                 dtype=None, nrow=None, ncol=None, verbose=False):

        if not isinstance(values, list) and not isinstance(values, np.ndarray):
            values = [values]
        if dtype is None:
            self.dtype = 1 # default to int
            if isinstance(values[0], float):
                self.dtype = 2
            elif isinstance(values[0], str):
                self.dtype = 4
            #for prmsdtype, pydtype in dtypes.items():
            #    if isinstance(values[0], pydtype):
            #        self.dtype = prmsdtype
        else:
            self.dtype = dtype
            pydtype = dtypes[dtype]
            # enforce submitted dtypes
            values = list(map(pydtype, values))

        self.name = name
        if isinstance(dim_names, str):
            self.dim_names = [dim_names]
        else:
            self.dim_names = dim_names
        self.array = np.array(values, dtype=dtypes[self.dtype])
        if nrow is not None and ncol is not None:
            if self.nvalues == nrow * ncol:
                self.array = np.reshape(values, (nrow, ncol))
        self.verbose = verbose

    @property
    def ndim(self):
        return len(self.dim_names)

    @property
    def nvalues(self):
        return len(self.array)

    def write(self, f):

        # update the array length in case it has been changed
        a = self.array.ravel()
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
                 nrow=None, ncol=None, comments=None,
                 verbose=False):

        if comments is None:
            self.comments = 'paramfile created by pyrms\n'
        else:
            self.comments = comments.strip() + '\n'

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
        result = None
        if '####' in line:
            result = addtoo(f)
            # params are read until ####
            # line will be the name of the next parameter
            if result == '####':
                while result == '####':
                    result = addtoo(f)
        for line in f:
            if result == 'break':
                return
            if '####' in line:
                result = addtoo(f)
            # params are read until ####
            # line will be the name of the next parameter
            #if result == '####':
            #    while result == '####':
            #        result = addtoo(f, name=line)
            elif result is not None:
                result = addtoo(f, name=line.strip())
            else:
                return line

    def read_param(self, f, name=None):
        if name is None:
            name = next(f).strip()
        ndim = int(next(f).strip())
        dim_names = []
        for d in range(ndim):
            dim_names.append(next(f).strip())
        nvalues = int(next(f).strip())

        # skip reading this one if not in load_only
        if self.load_only is not None:
            if len(self.load_only) == 0:
                return 'break'
            elif name not in self.load_only:
                for val in f:
                    val = val.strip()
                    if '####' in val:
                        return val
            else:
                self.load_only.remove(name)

        dtype = int(next(f).strip())
        convert_dtype = dtypes[dtype]
        values = []
        for val in f:
            val = val.strip()
            if '*' in val:
                nval, val = val.split('*')
                values += [convert_dtype(val)] * int(nval)
            elif '####' in val:
                break
            else:
                values.append(convert_dtype(val))
        #values = [convert_dtype(next(f).strip()) for i in range(nvalues)]
        self.params[name] = param(name, values, ndim=ndim,
                                  dim_names=dim_names,
                                  dtype=dtype,
                                  nrow=self.nrow, ncol=self.ncol)
        self.param_order.append(name)
        if self.verbose:
            print(name)
        return val

    @staticmethod
    def load(filename, model=None, nrow=None, ncol=None, verbose=False,
             load_only=None):

        if load_only is not None and isinstance(load_only, str):
            load_only = [load_only]

        pf = paramFile(filename=filename, nrow=nrow, ncol=ncol, verbose=verbose)
        pf.load_only = load_only
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

        if load_only is not None and len(load_only) > 0:
            for param in load_only:
                print('{} not found!'.format(param))
        if model is not None:
            model.dimensions.update(pf.dimensions)
            model.params.update(pf.params)
            model.param_files[filename] = pf
            model.paramdf.append(pf.df)
        else:
            return pf

    def write(self, filename=None):

        if filename is None:
            filename = self.filename

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

