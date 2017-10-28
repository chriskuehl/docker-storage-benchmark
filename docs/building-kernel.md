### Building a kernel with aufs support

Debian kernels don't come with aufs support anymore (aufs was never in the
mainline kernel). Rather than use an old kernel like Debian's 3.16 which still
had aufs, I prefer to add aufs to a new kernel. I originally tried adding the
aufs patches to the Debian kernel source, but the patches don't even remotely
apply cleanly, and I don't want to try to resolve the conflicts...

Adjust these instructions as needed to your linux version:

1. `apt-get build-dep linux`
2. `wget https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.9.51.tar.gz`
3. `git clone git@github.com:sfjro/aufs4-linux.git`
4. Grab the aufs patchset for your kernel version, e.g.
   `cd aufs4-linux && git diff v4.9..origin/aufs4.9 > aufs.patch`
5. Untar the linux you downloaded, apply the patches: `patch -p1 < ../aufs.patch`
6. Get the Debian config: `cp /boot/config-4.9.0-4-amd64 .config`
7. `make oldconfig`, choose these answers (based on Debian 3.16's aufs config):
   * `Aufs (Advanced multi layered unification filesystem) support (AUFS_FS) [N/y/?] (NEW)`: y
   * `Maximum number of branches`: 127
   * `Detect direct branch access (bypassing aufs) (AUFS_HNOTIFY) [N/y/?] (NEW)`: n
   * `NFS-exportable aufs (AUFS_EXPORT) [N/y/?] (NEW)`: y
   * `support for XATTR/EA (including Security Labels) (AUFS_XATTR) [N/y/?] (NEW)` not specified in 3.16 config, I took the default
   * `File-based Hierarchical Storage Management (AUFS_FHSM) [N/y/?] (NEW)`: n
   * `Readdir in userspace (AUFS_RDU) [N/y/?] (NEW)`: n
   * `Workaround for rename(2)-ing a directory (AUFS_DIRREN) [N/y/?] (NEW)`: not specified in 3.16 config, I took the default
   * `Show whiteouts (AUFS_SHWH) [N/y/?] (NEW)`: n
   * `Ramfs (initramfs/rootfs) as an aufs branch (AUFS_BR_RAMFS) [N/y/?] (NEW)`: n
   * `Fuse fs as an aufs branch (AUFS_BR_FUSE) [N/y/?] (NEW)`: n
   * `Hfsplus as an aufs branch (AUFS_BR_HFSPLUS) [Y/n/?] (NEW)`: y
   * `Debug aufs (AUFS_DEBUG) [N/y/?] (NEW)`: n

   Take the defaults for anything else (it won't be aufs-related), there's only
   like 5 of these.
8. `make clean`: https://i.fluffy.cc/0pzncxxj4N4KgMCWXfznPsZ709GvTp5h.png
9. `make -j36 deb-pkg`
10. `sudo dpkg -i ../linux-image-4.9.51_4.9.51-1_amd64.deb ../linux-headers-4.9.51_4.9.51-1_amd64.deb` (need headers for DKMS)
11. Reboot and test for aufs support with `grep aufs /proc/filesystems`


Also useful:

* https://github.com/sfjro/aufs4-linux
* http://aufs.sourceforge.net/
* https://kernel-handbook.alioth.debian.org/ch-common-tasks.html#s-common-official
