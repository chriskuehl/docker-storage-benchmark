# A convenient Docker image for benchmarking. It has a bunch of files in the
# "/test" directory that can be used by tests.
FROM debian:jessie
MAINTAINER Chris Kuehl <ckuehl@ocf.berkeley.edu>

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gfortran \
        libblas-dev \
        liblapack-dev \
        python \
        python-dev \
        python-pip \
        virtualenv \
    && apt-get clean

RUN curl -L -o /tmp/dumb-init.deb \
        https://github.com/Yelp/dumb-init/releases/download/v1.1.1/dumb-init_1.1.1_amd64.deb \
    && dpkg -i /tmp/dumb-init.deb \
    && rm /tmp/dumb-init.deb

WORKDIR /test
RUN mkdir -p /test/big-files /test/small-files

# Make a bunch of big files.
RUN for i in $(seq 0 9); do \
        for size in 1M 8M 32M 128M; do \
            dd if=/dev/urandom of=/test/big-files/${size}-${i}.bin bs=${size} count=1 2>/dev/null; \
        done; \
    done

# And a lot more small files.
RUN for i in $(seq 0 10000); do \
        dd if=/dev/urandom of=/test/small-files/$i bs=512 count=1 2>/dev/null; \
    done

# And a binary tree of files.
RUN bash -c 'make_tree() { \
    local cur="$1"; local remaining_depth="$2"; \
    mkdir "$cur"; \
    if [ "$remaining_depth" -gt 0 ]; then \
        make_tree "${cur}/0" "$((remaining_depth - 1))"; \
        make_tree "${cur}/1" "$((remaining_depth - 1))"; \
    else \
        echo "oh, hi!" > "${cur}/oh-hi"; \
    fi; \
}; \
make_tree /test/tree-of-files 14 \
'

ENTRYPOINT ["dumb-init", "--"]
