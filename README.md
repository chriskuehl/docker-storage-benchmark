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

![](https://i.fluffy.cc/s4Xpwdx0pzhjSMJNZ4b4CTbc5r2mTMT9.png)

A similar test which involves appending to files in a binary tree (described
better below) was much more drastic:

![](https://i.fluffy.cc/4qDkn7mkHM2q1W61Gp4fBprVqtx2xL8D.png)

This might suggest that aufs suffers with some kinds of large directory
structures?


### Reading files

The graph below was the only test that reads files in a directory tree on
`ext4` mounted with `-v`. Strangely, the storage driver still makes a large
difference in performance.

The test works by doing a DFS on a deep binary tree (directory structure) until
hitting a leaf node, then reading the file. It does `readlink` on the
intermediate directories.

![](https://i.fluffy.cc/tNPpHsgnRllqS4JdQNnLr3m3fWvz02J4.png)

Here is the exact same test but with the binary tree in the Docker filesystem
(not mounted with `-v`):

![](https://i.fluffy.cc/9bqzdL70VxL8zKt0x5Ht7HpT9qvxp9Nc.png)

Reading lots of small files in parallel:

![](https://i.fluffy.cc/rthcV26tGZgF1Q9k8dJD5CrzlzdMlDgL.png)


### Some not very interesting results

Reading a small number of large files:

![](https://i.fluffy.cc/bdrvbkNh7K82J8h0l5PZ6hq3426TnLKF.png)

Appending a line to a small number of large files:

![](https://i.fluffy.cc/nJL9SBMBLdcvhJ2v8GwzLK4RQKsXGBKt.png)


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
