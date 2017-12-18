from prms import paramFile

p = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/cal_full.param')
j=2

p = paramFile.load('data/gis.params', load_only='covden_sum')
assert len(p.params) == 1
assert 'covden_sum' in p.params
assert p.params['covden_sum'].array.shape[0] == 128

#p = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/br_1sta_edited_new_segs.param', load_only='covden_sum')

p = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/br_1sta_edited_new_segs.param')
assert len(p.params) == 79
