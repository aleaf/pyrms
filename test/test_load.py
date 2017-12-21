import sys
import glob
sys.path += glob.glob('D:/github/*')
from pyrms import model
from pyrms import paramFile

m = model.load('D:/ATLData/BR/gsflow/data/br_fc.control', nrow=817, ncol=1228)

m = model.load('data/gsflow_examples/sagehen/windows/gsflow.control', nrow=73, ncol=81)
df = m.summary
assert len(m.params) == len(df)

p = paramFile.load('D:/ATLData/BR/gsflow/data/params/dimensions.param')

p = paramFile.load('D:/ATLData/BR/gsflow/data/arrays/covden_sum.param')

p2 = paramFile.load('D:/ATLData/BR/gsflow/data/arrays/covden_win.param')
assert 'covden_sum' not in p2.params
