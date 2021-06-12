class readingCMOS():
    import h5py
    import numpy as np

    @staticmethod
    def h5printR(item, leading=''):
        for key in item:
            if isinstance(item[key], h5py.Dataset):
                print(leading + key + ' : ' + str(item[key].shape))
            else:
                print(leading + key)
                h5printR(item[key], leading + ' ')

    @staticmethod
    def h5print(filename):
        with h5py.File(filename, 'r') as h:
            print(filename)
            h5printR('h', '  ')


readingCMOS.h5print('filename.bxr')  # read the structure of .bxr file
