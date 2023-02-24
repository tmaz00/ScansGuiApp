from numpy import empty, shape, fromfile, reshape
from os import listdir
from os.path import isfile, join

def loadBin(fname: str, sampling_step=1):
    N = fromfile(fname, count=2, dtype='>u4')   # > stands for big endian, u4 - unsigned int, 4-bytes number

    n_Ascans = N[0]
    n_pts = N[1]

    A = fromfile(fname, count=n_Ascans*n_pts, dtype='>f8')
    B = reshape(A, (n_Ascans, n_pts))

    if (sampling_step != 1):
        B = B[::sampling_step, :]
        n_Ascans = shape(B)[0]

    return (B, n_Ascans, n_pts)

def bin2array(dir_path: str, sampling_step=1):
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    files.sort(key=lambda f: len(f))

    (Bscan1, n_Ascans, n_pts) = loadBin(join(dir_path, files[0]), sampling_step)

    D = empty(shape=(len(files), n_Ascans, n_pts))
    D[0, :, :] = Bscan1

    for i in range(1, len(files)):
        (B, _, _) = loadBin(join(dir_path, files[i]), sampling_step)
        D[i, :, :] = B

    return D
