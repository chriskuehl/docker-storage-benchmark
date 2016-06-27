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

I ran some early tests against `aufs`, `overlay`, and `overlay2`.

For all of these graphs, smaller bars are better. Some of these are pretty open
to interpretation, so mostly just providing the raw graphs. In rough order of
most-to-least-interesting:


### Appending to files

Appending to files is interesting because it typically requires copying the
entire file from a lower layer to the top before appending. Appending even one
byte to large files can be very expensive.

With aufs, appending to files in parallel quickly becomes extremely expensive
with lots of files:

![](https://i.fluffy.cc/bsb85DCjKGr9Lrkrz2gfS5Ww1cWSdDFV.png)

A similar test which involves appending to files in a binary tree (described
better below) was much more drastic:

![](https://i.fluffy.cc/qcf9GCwhGvlkGcTlZ1V97mltCvsSwXrP.png)

This might suggest that aufs suffers with some kinds of large directory
structures?


### Reading files

The graph below was the only test that reads files in a directory tree on
`ext4` mounted with `-v`. Strangely, the storage driver still makes a large
difference in performance.

The test works by doing a DFS on a deep binary tree (directory structure) until
hitting a leaf node, then reading the file. It does `readlink` on the
intermediate directories.

![](https://i.fluffy.cc/Tqvb767CGGn9vrFMpM5FcP6Nw1MQDt6Q.png)

Here is the exact same test but with the binary tree in the Docker filesystem
(not mounted with `-v`):

![](https://i.fluffy.cc/LbBnQwmJ75VKgQG7xVCwkP1JnR77t5N0.png)

Reading lots of small files in parallel:

![](https://i.fluffy.cc/kFjMRncFlXsV9qh2TcrghF9P45QZq1CH.png)


### Some not very interesting results

Reading a small number of large files:

![](https://i.fluffy.cc/nL50t4qV7M03GR39hV3XZJQL3tldqPnB.png)

Appending a line to a small number of large files:

![](https://i.fluffy.cc/w8k0xjQ4CV8HR8fVQ6MSGmFctrBtjwQB.png)


### Test machine specs

All the tests were run on the same physical machine and each had the machine to
itself.

* Docker 1.12rc2
* Debian stretch (as of 2016-06-27)
* Kernel 4.6.0 for overlay, 3.16 for aufs (since `aufs` was taken out of
  Debian's kernel builds in stretch)
* 32-core Intel Sandy Bridge, 256 GB RAM
* SSDs in RAID 10

I didn't have a lot of time to run these tests (the aufs ones take *forever*),
so the sample sizes are currently about 5 each. I'm running more as you read
this and will eventually update the graphs.
