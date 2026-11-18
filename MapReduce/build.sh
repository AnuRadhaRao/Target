#!/usr/bin/env bash
# Compile TermIndex.java into term-index.jar with plain javac + jar.
#
# On a machine with Hadoop installed, the Hadoop classes come from
# `hadoop classpath`. Without Hadoop, the few client jars needed to compile
# and to run in local mode are downloaded once into lib/.
set -euo pipefail
cd "$(dirname "$0")"

HADOOP_VERSION=3.4.1
MAVEN_CENTRAL=https://repo1.maven.org/maven2
JARS=(
  "org/apache/hadoop/hadoop-client-api/$HADOOP_VERSION/hadoop-client-api-$HADOOP_VERSION.jar"
  "org/apache/hadoop/hadoop-client-runtime/$HADOOP_VERSION/hadoop-client-runtime-$HADOOP_VERSION.jar"
  "org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar"
  "commons-logging/commons-logging/1.2/commons-logging-1.2.jar"
)

if command -v hadoop >/dev/null 2>&1; then
  CLASSPATH="$(hadoop classpath)"
else
  mkdir -p lib
  for path in "${JARS[@]}"; do
    jar="lib/$(basename "$path")"
    [ -f "$jar" ] || curl -sSfL --retry 3 -o "$jar" "$MAVEN_CENTRAL/$path"
  done
  CLASSPATH="lib/*"
fi

rm -rf build
javac -cp "$CLASSPATH" -d build TermIndex.java
jar cf term-index.jar -C build .
echo "Built $(pwd)/term-index.jar"
