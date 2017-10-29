docker-storage-benchmark
========

These are some simple benchmarks intended to discover performance differences
between Docker storage drivers.

Tests are in the `tests` directory. Each test is spawned inside one container
several times (depending on the parallelization being tested). There are other
potential tests (like running lots of containers), but I didn't find many
differences between the storage drivers doing this, and I was more interested
in parallel IO inside individual containers.


## Results (as of 2017-10-28)

I ran some early tests against `aufs`, `overlay`, `overlay2`, and
`devicemapper`. I also ran the tests against tmpfs without Docker. The raw data
is in `results`. The full details (Docker version, machine specs, etc. are at
the bottom of this README).

For all of these graphs, smaller bars are better. Some of these are pretty open
to interpretation, so mostly just providing the raw graphs. In rough order of
most-to-least-interesting:


### Appending to files

Appending to files is interesting because it typically requires copying the
entire file from a lower layer to the top before appending. Appending even one
byte to large files can be very expensive.

With aufs, appending to files in parallel quickly becomes extremely expensive
with lots of files:

![](https://i.fluffy.cc/hVJ4JG1Zg26Dk8mfZLmRKGs2JK2mk0dD.png)

A similar test which involves appending to files in a binary tree (described
better below) was much more drastic:

![](https://i.fluffy.cc/xtcTCLbDpGs5JCcBBL02Mfh24P23BLGV.png)

This might suggest that aufs suffers with some kinds of large directory
structures?


### Reading files

The graph below was the only test that reads files in a directory tree on
`ext4` mounted with `-v`. Strangely, the storage driver still makes a large
difference in performance.

The test works by doing a DFS on a deep binary tree (directory structure) until
hitting a leaf node, then reading the file. It does `readlink` on the
intermediate directories.

![](https://i.fluffy.cc/nPmHCP8PFgQ9dPzcVTkLfNP6fT5WX9nD.png)

Here is the exact same test but with the binary tree in the Docker filesystem
(not mounted with `-v`):

![](https://i.fluffy.cc/34gMq4ZBtRqfvjbctgMHBTs196gH4vn7.png)

Reading lots of small files in parallel:

![](https://i.fluffy.cc/6fQq11mwkzzkBJVpMSDmBMP76LQt5084.png)


### Some not very interesting results

Reading a small number of large files:

![](https://i.fluffy.cc/hQQbXPG80s0kgMbhJMVd2j6H8CMrqm5m.png)

Appending a line to a small number of large files:

![](https://i.fluffy.cc/GMz4qVBzl2FVDHnskCtPkrTFZ4PMmBb7.png)


### All test graphs by name:

* [`append-to-big-files`](https://i.fluffy.cc/GMz4qVBzl2FVDHnskCtPkrTFZ4PMmBb7.png)
* [`append-to-file-tree`](https://i.fluffy.cc/xtcTCLbDpGs5JCcBBL02Mfh24P23BLGV.png)
* [`append-to-small-files`](https://i.fluffy.cc/hVJ4JG1Zg26Dk8mfZLmRKGs2JK2mk0dD.png)
* [`read-big-files`](https://i.fluffy.cc/hQQbXPG80s0kgMbhJMVd2j6H8CMrqm5m.png)
* [`read-file-tree-mounted`](https://i.fluffy.cc/nPmHCP8PFgQ9dPzcVTkLfNP6fT5WX9nD.png)
* [`read-file-tree`](https://i.fluffy.cc/34gMq4ZBtRqfvjbctgMHBTs196gH4vn7.png)
* [`read-small-files`](https://i.fluffy.cc/6fQq11mwkzzkBJVpMSDmBMP76LQt5084.png)


### Test machine specs

All the tests were run on a [`c4.8xlarge`][c4.8xlarge] EC2 instance.

* Docker 17.09.0-ce
* Debian stretch
* Kernel 4.9.51 (stock Debian except for `aufs` tests, which used a
  custom-built 4.9.51 kernel with the aufs patches applied)
* 36 "vCPUs", 60 GiB RAM
* `tmpfs` as backing filesystem for all tests except `devicemapper`. For
  `devicemapper`, LVM was configured as recommended by [the
  docs][devicemapper-config], using a ramdisk as the backing physical volume.
  Doing all writes against a tmpfs/ramdisk was an attempt to avoid variances in
  the underlying IO speed of EBS or instance storage.


[c4.8xlarge]: http://www.ec2instances.info/?selected=c4.8xlarge
[devicemapper-config]: https://docs.docker.com/engine/userguide/storagedriver/device-mapper-driver/
