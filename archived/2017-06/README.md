**Note: I never "published" these results and don't consider them accurate.**
The overlay/overlay2 regression seemed strange to me, and I suspect it's due to
something weird with the kernel I compiled. I re-did these tests in October 2017 while being careful with the kernel versions and settings, and the regression disappeared.

Below is the original text from the PR:

----------------


This was run on a `c3.8xlarge` (32 cores, 60GB RAM, on instance storage in
RAID0) with Docker 17.03.1-ce and kernel 4.9.33 (custom-built with the AUFS
patches).

## results

overlay and overlay2 have a *huge* regression in file appending. i want to try
this out on a stock kernel (just in case my custom-built one was built
strangely), but if it happens there, this is definitely bug-worthy:

![append-to-small-files](https://i.fluffy.cc/Jr1KxbpXgVWWKvNJRC3P48Lg4knzwN6S.png)
([compare to last time](https://i.fluffy.cc/GjjxQmVTtCH31ZR7PVpR9xMwhzQ8LBqK.png))
![append-to-file-tree](https://i.fluffy.cc/qL5swgqVD3FWNx7JJbGSh4sm25KdQsmZ.png)
([compare to last time](https://i.fluffy.cc/gWtX0x4kFc2K6C5tvJfBkwJCpRMscHv1.png))

aufs continues to significantly decrease performance even when reading a _mounted_ filesystem:

![read-file-tree-mounted](https://i.fluffy.cc/4tLLGwzRrsVhs2bD8CgtbqHwJJGvZhTf.png)

aufs is still slow at large file trees:

![read-file-tree](https://i.fluffy.cc/xNn8RwPVZsHGpGT9TG4dgR8PkbdPpqQr.png)

devicemapper (not tested last time) is good at most of these graphs, but has super slow reads?

![read-big-files](https://i.fluffy.cc/zhHBJc6njhqn2QhPd585Vtd0H3VBS7V7.png)

other graphs (not as interesting):
* [append-to-big-files](https://i.fluffy.cc/f8dBH7F98NDcg1xXx46hZxcqMxLjHvQw.png)
* [read-small-files](https://i.fluffy.cc/sZGvZSGqTBZm2Tnpz1c76P4GmTnDNjDX.png)
