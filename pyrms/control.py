import numpy as np
import pandas as pd
from .dtypes import dtypes


class controlParam:

    def __init__(self, name, values, dtype=None, verbose=False):

        self.name = name
        self.verbose = verbose
        if not isinstance(values, list) and not isinstance(values, np.ndarray):
            values = [values]
        if dtype is None:
            for prmsdtype, pydtype in dtypes.items():
                if isinstance(values[0], pydtype):
                    self.dtype = prmsdtype
            self.values = values
        else:
            self.dtype = dtype
            pydtype = dtypes[dtype]
            # enforce submitted dtypes
            self.values = list(map(pydtype, values))

    @property
    def nvalues(self):
        return len(self.values)

    def write(self, f):

        f.write('####\n')
        f.write('{}\n'.format(self.name))
        f.write('{:d}\n{:d}\n'.format(self.nvalues, self.dtype))
        for v in self.values:
            f.write('{}\n'.format(v))
        if self.verbose:
            print(self.name)


class controlFile:


    def __init__(self, datafile=None, param_file=[],
                 start_time='2000-01-01', end_time='2000-12-31',
                 model_mode='PRMS',
                 capillary_module='soilzone_prms',
                 et_module='potet_jh',
                 gravity_module='soilzone_prms',
                 precip_module='precip_1sta',
                 solrad_module='ddsolrad',
                 srunoff_module='srunoff_smidx',
                 strmflow_module='muskingum',
                 temp_module='temp_1sta',
                 transp_module='transp_tindex',
                 statsON_OFF=1, statVar_names=[],
                 statVar_element=[], stat_var_file='1sta.statvar',
                 mapOutON_OFF=0, mapOutVar_names=[], map_output_file='output.map',
                 aniOutON_OFF=0, aniOutVar_names=[], ani_output_file='prms.ani',
                 csvON_OFF=0, csv_output_file='prms_summary.csv',
                 executable_model='gsflow.exe', model_output_file='prms.out',
                 dprst_flag=0, comments='Control file created by pyrms',
                 verbose=False):

        self.executable_model = controlParam('executable_model', executable_model, 4)
        self.model_mode = controlParam('model_mode', model_mode, 4)
        self.comments = comments.strip() + '\n'
        self.param_order = [] # order of parameters in control file
        self.verbose = verbose

        # modules
        self.capillary_module = controlParam('capillary_module', capillary_module, 4)
        self.dprst_flag = controlParam('capillary_module', dprst_flag, 4)
        self.et_module = controlParam('et_module', et_module, 4)
        self.gravity_module = controlParam('gravity_module', gravity_module, 4)
        self.solrad_module = controlParam('solrad_module', solrad_module, 4)
        self.srunoff_module = controlParam('srunoff_module', srunoff_module, 4)
        self.strmflow_module = controlParam('strmflow_module', strmflow_module, 4)
        self.precip_module = controlParam('precip_module', precip_module, 4)
        self.temp_module = controlParam('temp_module', temp_module, 4)
        self.transp_module = controlParam('transp_module', transp_module, 4)

        # input
        self.start_time = pd.Timestamp(start_time)
        self.end_time = pd.Timestamp(end_time)
        self.data_file = controlParam('datafile', datafile, 4)
        self.param_file = controlParam('param_file', param_file, 4)

        # output
        self.model_output_file = controlParam('model_output_file', model_output_file, 4)

        # statvar output
        self.statsON_OFF = controlParam('statsON_OFF', statsON_OFF, 1)
        self.statVar_names = controlParam('statVar_names', statVar_names, 4)
        self.statVar_element = controlParam('statVar_element', statVar_element, 1)
        self.stat_var_file = controlParam('stat_var_file', stat_var_file, 4)

        # csv output
        self.csvON_OFF = controlParam('csvON_OFF', csvON_OFF, 1)
        self.csv_output_file = controlParam('csv_output_file', csv_output_file, 4)

        # map results output
        self.mapOutON_OFF = controlParam('mapOutON_OFF', mapOutON_OFF, 1)
        self.mapOutVar_names = controlParam('mapOutVar_names', mapOutVar_names, 4)
        self.map_output_file = controlParam('map_output_file', map_output_file, 4)

        # animation output
        self.aniOutON_OFF = controlParam('aniOutON_OFF', aniOutON_OFF, 1)
        self.aniOutVar_names = controlParam('aniOutVar_names', aniOutVar_names, 4)
        self.ani_output_file = controlParam('ani_output_file', ani_output_file, 4)

        # other stuff
        self.dispGraphsBuffSize = controlParam('dispGraphsBuffSize', 10)
        self.ndispGraphs = controlParam('ndispGraphs', 0)
        self.dispVar_plot = controlParam('dispVar_plot', 4)
        self.dispVar_element = controlParam('dispVar_element', 4)
        self.print_debug = controlParam('print_debug', -1)
        self.parameter_check_flag = controlParam('parameter_check_flag', 1)
        self.cascade_flag = controlParam('cascade_flag', 1)
        self.cascadegw_flag = controlParam('cascadegw_flag', 1)
        self.subbasin_flag = controlParam('subbasin_flag', 1)
        self.save_vars_to_file = controlParam('save_vars_to_file', 0)
        self.var_save_file = controlParam('var_save_file', 'var.init')
        self.initial_deltat = controlParam('initial_deltat', 24.0)
        self.stats_output_file = controlParam('stats_output_file', 'prms.stats')
        self.init_vars_from_file = controlParam('init_vars_from_file', 0)

    @property
    def nmapOutVars(self):
        return len(self.mapOutVar_names)

    @property
    def naniOutVars(self):
        return len(self.aniOutVar_names)

    @property
    def nstatVars(self):
        return len(self.aniOutVar_names)

    @property
    def control_params(self):
        return [k for k, v in self.__dict__.items() if isinstance(v, controlParam)]

    @staticmethod
    def read_comments(f):
        comments = ''
        while True:
            line = next(f)
            if '####' in line:
                break
            else:
                comments += line.strip() + '\n'
        return comments + 'rewritten by pyrms\n'

    @staticmethod
    def read_param(f, name):
        nvalues = int(next(f).strip())
        dtype = int(next(f).strip())
        convert_dtype = dtypes[dtype]
        values = [convert_dtype(next(f).strip()) for i in range(nvalues)]
        return controlParam(name, values, dtype=dtype)

    def reset(self):
        # need to expand this to give option to reset with defaults or not
        # and maybe to reset by parameter
        pass

    @staticmethod
    def load(filename, verbose=False):

        with open(filename) as input:

            # instantiate a new control file object
            ctrl = controlFile()
            # discard the default settings
            ctrl.__dict__ = {}

            ctrl.param_order = []
            ctrl.verbose = verbose
            ctrl.comments = controlFile.read_comments(input)
            for line in input:
                if '####' in line:
                    name = next(input).strip()
                    ctrl.__dict__[name] = controlFile.read_param(input, name)
                    ctrl.param_order.append(name)
        return ctrl

    def write(self, filename=None):

        if filename is None:
            filename = self.filename

        # determine an order for writing parameters
        # (alphabetically if none specified)
        if len(self.param_order) != len(self.control_params):
            self.param_order = sorted(self.control_params)

        with open(filename, 'w') as output:
            output.write(self.comments)

            if len(self.control_params) > 0:
                if self.verbose:
                    print('\nwriting control parameters...')
            for k in self.param_order:
                self.__dict__[k].write(output)




