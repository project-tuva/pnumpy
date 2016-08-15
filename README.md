# pnumpy
Parallel computing in N dimensions made easy in Python

## Overview

pnumpy is a very lightweight implementation of distributed arrays,
which runs on architectures ranging from multi-core laptops to large
MPI clusters.  pnumpy is based on numpy and mpi4py and supports arrays in
any number of dimensions. Processes can access remote data using a "getData" 
method. This can be used to access neighbor ghost data but is more 
flexible as it allows to access data from any process--not necessarily
a neighboring one. pnumpy is designed to work seamlessly with numpy's 
slicing operators ufunc, etc., making it easy to transition your code
to a parallel computing environment.

## How to get pnumpy

```bash
git clone https://github.com/pletzer/pnumpy.git
```

## How to build pnumpy

pnumpy requires:

 * python 2.7 or 3.5
 * numpy, e.g. 1.10
 * MPI library (e.g. MPICH2 1.4.1p1 that comes with Anaconda)
 * mpi4py, e.g. 2.0.0


```bash
python setup.py install
```

or, if you need root access,

```bash
sudo python setup.py install
```

Alternatively you can use 
```python 
pip install pnumpy
```

or

```python 
pip install pnumpy --user
```

## How to test pnumpy

Run any file under tests/, e.g.

```bash
cd tests
mpiexec -n 4 python testDistArray.py
```

## How to use pnumpy

To run script myScript.py in parallel use

```python
mpiexec -n numProcs python <myScript.py>
```

where numProcs is the number of processes.

### A lightweight extension to numpy arrays

Think of pnumpy arrays as standard numpy arrays with additional data members and methods to access neighboring data. 

To create a ghosted distributed array (gda) use:

```python
from pnumpy import gdaZeros
da = gdaZeros((4, 5), numpy.float32, numGhosts=1)
```

The above creates a 4 x 5 float32 array filled with zeros -- the syntax should be familiar to anyone using 
numpy arrays. 

All numpy operations apply to pnumpy distributed arrays with no change and this includes slicing. 
Note that slicing operations are with respect to local array indices.

In the above, _numGhosts_ describes the thickness of the halo region, i.e. the slice of 
data inside the array that can be accessed by other processes. A value of numGhosts = 1 means 
the halo has depth of one. The thicker the halo the more costly communication will be because 
more data will need to be copied 
from one process to another.

For a 2D array, the halo can be broken into four regions: 

 * da[:numGhosts, :] => west
 * da[-numGhosts:, :] => east
 * da[:, :numGhosts] => south
 * da[:, -numGhosts:] => north

(In n-dimensions there are 2n regions.) pnumpy identifies each halo region
 with a tuple: 

  * (-1, 0) => west
  * (1, 0) => east
  * (0, -1) => south
  * (0, 1) => north

To access data on the south region of remote process otherRk, use
```python
southData = da.getData(otherRk, winID=(0, -1))
```

### Using a regular domain decomposition

The above will work for any domain decomposition, not necessarily a regular one. In the case where a global array is split into
uniform chunks of data, otherRk can be inferred from the local rank and an offset vector:

```python
from pnumpy import CubeDecomp
decomp = CubeDecomp(numProcs, dims)
...
otherRk = decomp.getNeighborProc(self, da.getMPIRank(), offset=(0, 1), periodic=(True, False))
```

where numProcs is the number of processes, dims are the global array dimensions and periodic is a tuple of 
True/False values indicating whether the domain is periodic or not. In the case where there is no neighbour rank (because the
local da.getMPIRank() rank lies at the boundary of the domain), then getNeighborProc may return None. In this case getData will also return None. 

### A very high level

For the Laplacian stencil, one may consider using 

```python
from pnumpy import Laplacian
lapl = Laplacian(decomp, periodic=(True, False))
```

Applying the Laplacian stencil to any numpy-like array _inp_ then simply involves:
```python
out = lapl.apply(inp)
```
