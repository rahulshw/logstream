#!/usr/bin/env bash

image=$1

docker run -d \
-p 8888:8888 \
-v ~/git/logstream:/git \
-v /var/log/:/host_logs:ro \
-e LOGDIR=/host_logs \
-e LOGBUFFER=10 \
-e PINGINTERVAL=5 \
-e PINGTIMEOUT = 10 \
-e PORT = 8888 \
--cpus 1 \
--memory 536870912 \
--name logstream \
$image