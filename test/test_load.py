import sys
import glob
sys.path += glob.glob('D:/github/*')
from pyrms import model
from pyrms import paramFile

m = model.load('data/gsflow_examples/sagehen/windows/gsflow.control')
df = m.summary
p = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/arrays/covden_sum.param')

p2 = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/arrays/covden_win.param')
assert 'covden_sum' not in p2.params

m = model.load('D:/ATLData/BR/badriver/gsflow/data/prms/br_test_fullycoupled.control',
               skip='all_cascadesgw')