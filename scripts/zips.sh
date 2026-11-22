#!/usr/bin/env bash
# Builds the downloads a release carries: one zip per language, and one of everything.
#
#   scripts/zips.sh <version> [<out-dir>]
#
# Each zip holds the files git tracks at HEAD under a top folder named coho-samples, laid
# out as the repository is. The tutorials reach two levels up for sample-assets and
# INSTALLING.md, and copy a starter from beside them, so a reader who unzips one runs the
# same commands as a reader who cloned: cd coho-samples/dotnet/cli-razor-blog.
#
# A language's zip leaves out the README at the top, which links to every language; the
# zip of everything keeps it.

set -euo pipefail

version="${1:?usage: scripts/zips.sh <version> [<out-dir>]}"
out="${2:-dist}"

cd "$(git rev-parse --show-toplevel)"
mkdir -p "$out"

shared=(sample-assets INSTALLING.md LICENSE NOTICE)
languages=(dotnet java kotlin node python)

for language in "${languages[@]}"; do
  git archive --format=zip --prefix=coho-samples/ \
    -o "$out/coho-samples-$language-$version.zip" HEAD "$language" "${shared[@]}"
done

git archive --format=zip --prefix=coho-samples/ -o "$out/coho-samples-$version.zip" HEAD

ls -l "$out"
