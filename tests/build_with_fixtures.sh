#!/bin/sh
# Build a copy of the site with tests/fixtures/ overlaid, then run the suite against it.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d "${TMPDIR:-/tmp}/portfolio-fixtures.XXXX")
rsync -a --exclude vendor --exclude _site --exclude .git --exclude .superpowers --exclude tests "$ROOT/" "$TMP/src/"
rsync -a "$ROOT/tests/fixtures/" "$TMP/src/"
cd "$TMP/src"
BUNDLE_GEMFILE="$ROOT/Gemfile" BUNDLE_PATH="$ROOT/vendor/bundle" bundle exec jekyll build -q -d "$TMP/site"
cd "$ROOT"
SITE_DIR="$TMP/site" FIXTURES=1 python3 -I -m unittest discover -s "$ROOT/tests" "$@"
rm -rf "$TMP"
