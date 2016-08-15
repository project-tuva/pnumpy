import pnumpy
from pnumpy import CubeDecomp
import sys
import numpy
from mpi4py import MPI

"""
Apply the finite difference Laplacian operator in 3d
"""

# local rank and number of procs
rk = MPI.COMM_WORLD.Get_rank()
sz = MPI.COMM_WORLD.Get_size()

# domain sizes
nx, ny, nz = 16, 16, 16

# domain sizes
xMin, xMax = 0.0, 1.0
yMin, yMax = 0.0, 1.0
zMin, zMax = 0.0, 1.0

dx = (xMax - xMin)/float(nx)
dy = (yMax - yMin)/float(ny)
dz = (zMax - zMin)/float(nz)

# domain dc.sition
dc = CubeDecomp(sz, (nx, ny, nz))

# the dc.must be regular
if not dc.getDecomp():
    if rk == 0: 
        print('no decomp could be found, adjust the number of procs')
        MPI.Finalize()
        sys.exit(1)

# number of procs in each direction
npx, npy, npz = dc.getDecomp()

# list of slices
slab = dc.getSlab(rk)

# starting/ending indices for local domain
iBeg, iEnd = slab[0].start, slab[0].stop
jBeg, jEnd = slab[1].start, slab[1].stop
kBeg, kEnd = slab[2].start, slab[2].stop

# set the input field
f = numpy.zeros( (nx, ny, nz), numpy.float64 )

for i in range(iEnd - iBeg):
    x = xMin + dx*(iBeg + i + 0.5)
    for j in range(jEnd - jBeg):
        y = yMin + dy*(jBeg + j + 0.5)
        for k in range(kEnd - kBeg):
            z = zMin + dz*(kBeg + k + 0.5)
            f = numpy.sin(numpy.pi*x) * numpy.cos(2*numpy.pi*y)

# compute the Laplacian
lapl = pnumpy.Laplacian(dc, periodic=(True, True, True))
fout = lapl.apply(f)


