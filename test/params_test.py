from prms import paramFile


p = paramFile.load('data/gis.params', load_only='covden_sum')
assert 'covden_sum' in p.params
assert p.params['covden_sum'].array.shape[0] == 128


p = paramFile.load('D:/ATLData/BR/badriver/gsflow/data/prms/br_1sta_edited_new_segs.param', load_only='covden_sum')
j=2