#!/usr/bin/env bash
# Compile TermIndex.java into term-index.jar with plain javac + jar.
#
# On a machine with Hadoop installed, the Hadoop classes come from
# `hadoop classpath`. Without Hadoop, the client jars listed in jars.txt
# are downloaded once into lib/.
set -euo pipefail
cd "$(dirname "$0")"

MAVEN_CENTRAL=https://repo1.maven.org/maven2

if command -v hadoop >/dev/null 2>&1; then
  CLASSPATH="$(hadoop classpath)"
else
  mkdir -p lib
  # one jar path per line in jars.txt; blank lines and # comments skipped
  grep -v -e '^#' -e '^$' jars.txt | while read -r path; do
    jar="lib/$(basename "$path")"
    [ -f "$jar" ] || curl -sSfL --retry 5 --retry-all-errors -o "$jar" "$MAVEN_CENTRAL/$path"
  done
  CLASSPATH="lib/*"
fi

rm -rf build
javac -cp "$CLASSPATH" -d build TermIndex.java
jar cf term-index.jar -C build .
echo "Built $(pwd)/term-index.jar"
