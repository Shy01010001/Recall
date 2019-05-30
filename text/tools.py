#encoding: utf8
'''
Created on 2018/07/25

@author: HOLLY
'''

import glob
import os
import errors

def get_all_dirname_at(a_pathname, a_recurrence_count = 0):
    '''
    get all directory name under 'a_pathname'
    'a_pathname' should end with os.sep
    '''
    if not a_pathname.endswith(os.sep):
        raise errors.PathFormatError('a_pathname "{path}" don\'t ends with os.sep(\'{sep}\')'.format(path = a_pathname, sep = os.sep))
    return ['{0}{1}'.format(i, os.sep) for i in sorted(glob.glob(a_pathname + '*')) if os.path.isdir(i)]

def get_all_filename_at(a_pathname, a_extension = '', a_recurrence_count = 0):
    '''
    get all filename under 'a_pathname'
    'a_pathname' should end with os.sep
    '''
    if not a_pathname.endswith(os.sep):
        raise errors.PathFormatError('a_pathname "{path}" don\'t ends with os.sep(\'{sep}\')'.format(path = a_pathname, sep = os.sep))
    if len(a_extension) != 0 and a_extension[0] != '.': a_extension = '.' + a_extension
    name_list = []
    if a_recurrence_count > 0:
        for dirname in get_all_dirname_at(a_pathname):
            name_list +=  get_all_filename_at(dirname+os.sep, a_extension, a_recurrence_count-1)
#     return glob.glob(a_pathname + '*' + a_extension)
    return name_list + [i for i in sorted(glob.glob(a_pathname + '*' + a_extension)) if os.path.isfile(i)]


if __name__ == '__main__':
    pass