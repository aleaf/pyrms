import numpy as np
import pandas as pd
from pyrms.dtypes import dtypes


class param:

    def __init__(self, name, values, dim_names=['one'],
                 filename=None,
                 dtype=None, nrow=None, ncol=None, model=None,
                 verbose=False):

        if not isinstance(values, list) and not isinstance(values, np.ndarray):
            values = [values]
        if dtype is None:
            self.dtype = 1 # default to int
            if isinstance(values[0], float):
                self.dtype = 2
            elif isinstance(values[0], str):
                self.dtype = 4
        else:
            self.dtype = dtype
            pydtype = dtypes[dtype]
            # enforce submitted dtypes
            values = list(map(pydtype, values))

        self.name = name
        self.filename = filename
        self.model = model
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
    def active(self):
        if self.model is not None and self.dim_names[0] == 'nhru':
            return self.model.hru_type > 0
        else:
            return np.ones(self.nvalues, dtype=bool)

    @property
    def ndim(self):
        return len(self.dim_names)

    @property
    def nvalues(self):
        return self.array.size

    @property
    def nactive_values(self):
        return self.active.sum()

    @property
    def min(self):
        try:
            arr = self.array.ravel()
            active = self.active.ravel()
            val = arr[active].min()
        except:
            val = self.array[0]
        return val

    @property
    def mean(self):
        val = np.nan
        try:
            arr = self.array.ravel()
            active = self.active.ravel()
            val = arr[active].mean()
        except:
            if self.nvalues > 1:
                val = self.array[1]
        return val

    @property
    def max(self):
        val = np.nan
        try:
            arr = self.array.ravel()
            active = self.active.ravel()
            val = arr[active].max()
        except:
            if self.nvalues > 2:
                val = self.array[2]
        return val

    def plot(self):
        if len(self.array.shape) == 2:
            import matplotlib.pyplot as plt
            plt.imshow(self.array)
            plt.colorbar()

    def write(self, f=None, **kwargs):
        """Write information for a parameter
        
        Parameters
        ----------
        f : filename (string) or open file handle
        kwargs : keyword arguments to pandas.DataFrame.to_csv()
        """
        if f is None:
            f = self.filename
        close = False
        if isinstance(f, str):
            filename = f
            f = open(f, 'w')
            close=True
        # update the array length in case it has been changed
        a = self.array.ravel()
        f.write('####\n')
        f.write('{}\n{:d}\n'.format(self.name, self.ndim))
        for n in self.dim_names:
            f.write('{}\n'.format(n))
        f.write('{:d}\n{:d}\n'.format(self.nvalues, self.dtype))
        df = pd.DataFrame(a)
        df.to_csv(f, index=False, header=False, lineterminator='\n', **kwargs)
        if self.verbose:
            print(self.name)
        if close:
            f.close()
            print('wrote {}'.format(filename))

class paramFile(object):

    def __init__(self, filename='stuff.param', dimensions={}, params={},
                 nrow=None, ncol=None, model=None, comments=None,
                 verbose=False):

        if comments is None:
            self.comments = 'paramfile created by pyrms\n'
        else:
            self.comments = comments.strip() + '\n'

        self.model = model
        self.filename = filename
        self.dimensions = dimensions.copy()
        self.params = params.copy()
        self.nrow = nrow
        self.ncol = ncol
        self.verbose = verbose
        self.param_order = []
        return

    @property
    def summary(self):
        return self.get_summary_dataframe()

    def get_summary_dataframe(self):
        plist = []
        for k, v in self.params.items():
            plist.append([v.name, ' '.join(v.dim_names),
                          v.nvalues,
                          v.nactive_values,
                          v.min,
                          v.mean,
                          v.max,
                          self.filename])
        return pd.DataFrame(plist, columns=['name',
                                            'dimensions',
                                            'nvalues',
                                            'nactive_values',
                                            'min',
                                            'mean',
                                            'max',
                                            'file'])

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
        if dtype != 4:
            def convert_dtype(val):
                return dtypes[dtype](float(val))
        else:
            convert_dtype = dtypes[dtype]

        values = []
        for val in f:
            val = val.strip()
            if '*' in val:
                nval, val = val.split('*')
                values += [convert_dtype(val)] * int(nval)
            elif '####' in val:
                break
            elif val.strip() == '':
                continue
            else:
                values.append(convert_dtype(val))
        #values = [convert_dtype(next(f).strip()) for i in range(nvalues)]
        self.params[name] = param(name, values,
                                  dim_names=dim_names,
                                  filename=self.filename,
                                  dtype=dtype,
                                  nrow=self.nrow, ncol=self.ncol,
                                  model=self.model)
        self.param_order.append(name)
        if self.verbose:
            print(name)
        return val

    @staticmethod
    def load(filename, model=None, nrow=None, ncol=None, verbose=False,
             load_only=None):

        if load_only is not None and isinstance(load_only, str):
            load_only = [load_only]

        pf = paramFile(filename=filename, nrow=nrow, ncol=ncol,
                       model=model,
                       verbose=verbose)
        pf.load_only = load_only
        with open(filename) as input:

            line = pf.read_comments(input)
            if 'Dimensions' in line:
                if verbose:
                    print('reading dimensions...')
                line = paramFile._read_stuff(input, line, pf.read_dimension)
            if line is not None:
                if 'Parameters' in line or '####' in line:
                    if verbose:
                        print('reading parameters...')
                    line = paramFile._read_stuff(input, line, pf.read_param)
            else:
                pass

        if load_only is not None and len(load_only) > 0:
            for param in load_only:
                print('{} not found!'.format(param))
        if model is not None:
            #model.dimensions.update(pf.dimensions)
            #model.params.update(pf.params)
            model.files[filename] = pf
            #model.paramdf.append(pf.df)
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
            print('wrote {}'.format(filename))

