from control import controlFile

p = controlFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/br_test_fullycoupled.control_bak')
assert 'subbasin_flag' in p.control_params
j=2