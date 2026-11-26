#!/usr/bin/env bash
# run.sh DIST_ARCHIVE AUTHORS_JAR [Example.java [derby-10.14.2.0.jar]]
set -euo pipefail
archive=$(realpath "${1:?Укажите архив Flink 1.7.1 для Scala 2.12}")
examples=$(realpath "${2:?Укажите examples-scala.jar из книги}")
code_dir=$(cd "$(dirname "$0")" && pwd)
image='maven:3.9.9-eclipse-temurin-8@sha256:e20e4fc05fb5480c884a1f750c362ed0e91aca15cec5736e12796713710ec9b3'
mounts=(-v "$code_dir:/examples:ro")
if [[ -n ${4:-} ]]; then
    derby=$(realpath "$4")
    mounts+=(-v "$derby:/input/derby.jar:ro")
fi
docker run --rm --network none --hostname flink-book --add-host flink-book:127.0.0.1 --cpus 2 --memory 2304m \
    -v "$archive:/input/flink.tgz:ro" -v "$examples:/input/examples-scala.jar:ro" \
    "${mounts[@]}" "$image" bash /examples/in-container.sh "${3:-}"
