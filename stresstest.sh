#!/bin/sh

ip="127.0.0.1"
SECONDS=0
t1=$(date +%s%3N)
for u in {1..1000}
do
    user='user'${u}
    url="${ip}/getfeed/${user}"
    curl $url >/dev/null 2>/dev/null
done
t2=$(date +%s%3N)
time_diff=$((t2-t1))
echo "Elapsed time ${time_diff} ms"