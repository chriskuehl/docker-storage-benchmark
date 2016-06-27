docker-storage-benchmark
========

These are some simple benchmarks intended to discover performance differences
between Docker storage drivers.

Tests are in the `tests` directory. Each test is spawned inside one container
several times (depending on the parallelization being tested). There are other
potential tests (like running lots of containers), but I didn't find many
differences between the storage drivers doing this, and I was more interested
in parallel IO inside individual containers (I *did* find that it is easy to
break both aufs and overlay with many containers, sometimes requiring manual
recovery of `/var/lib/docker`. I have yet to be able to break overlay2 at all.)


## Results (as of 2016-06-27)

I ran some early tests against `aufs`, `overlay`, and `overlay2`. I also ran
the tests against ext4 without Docker. The raw data is in `results`.

For all of these graphs, smaller bars are better. Some of these are pretty open
to interpretation, so mostly just providing the raw graphs. In rough order of
most-to-least-interesting:


### Appending to files

Appending to files is interesting because it typically requires copying the
entire file from a lower layer to the top before appending. Appending even one
byte to large files can be very expensive.

With aufs, appending to files in parallel quickly becomes extremely expensive
with lots of files:

![](https://i.fluffy.cc/GjjxQmVTtCH31ZR7PVpR9xMwhzQ8LBqK.png)

A similar test which involves appending to files in a binary tree (described
better below) was much more drastic:

![](https://i.fluffy.cc/gWtX0x4kFc2K6C5tvJfBkwJCpRMscHv1.png)

This might suggest that aufs suffers with some kinds of large directory
structures?


### Reading files

The graph below was the only test that reads files in a directory tree on
`ext4` mounted with `-v`. Strangely, the storage driver still makes a large
difference in performance.

The test works by doing a DFS on a deep binary tree (directory structure) until
hitting a leaf node, then reading the file. It does `readlink` on the
intermediate directories.

![](https://i.fluffy.cc/mJpw5R00wk7fdG2stFd3NTcpW6WW70Qp.png)

Here is the exact same test but with the binary tree in the Docker filesystem
(not mounted with `-v`):

![](https://i.fluffy.cc/p82fnZ5bdMNM3LZnml7pMkWDSznpzZBC.png)

Reading lots of small files in parallel:

![](https://i.fluffy.cc/Rrrs8xnbVzx8hh4Xbk7TXxHGZqgS5bMj.png)


### Some not very interesting results

Reading a small number of large files:

![](https://i.fluffy.cc/S7vfD6ZQ2rqz95pFVFlxgzWbkfc9kzLJ.png)

Appending a line to a small number of large files:

![](https://i.fluffy.cc/Bgzs12VvCmv18C3VSvRP4FFrLJ2tVjHC.png)


### Test machine specs

All the tests were run on the same physical machine and each had the machine to
itself.

* Docker 1.12rc2
* Debian stretch (as of 2016-06-27)
* Kernel 4.6.0 for overlay, 3.16 for aufs (since `aufs` was taken out of
  Debian's kernel builds in stretch)
* 32-core Intel Sandy Bridge, 256 GB RAM
* SSDs in RAID 10
