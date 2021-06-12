import h5py
import numpy as np

class readingCMOS():

super(Opening, self).__init__()

  @staticmethod
   def h5printR(item, leading=''):
        for key in item:
            if isinstance(item[key], h5py.Dataset):
                print(leading + key + ' : ' + str(item[key].shape))
            else:
                print(leading + key)
                h5printR(item[key], leading + ' ')

    @staticmethod
    @lru_cache
    def h5print(filename):
        with h5py.File(filename, 'r') as h:
            print(filename)
            h5printR(h, '  ')


readingCMOS.h5print('filename.bxr')  # read the structure of .bxr fil
