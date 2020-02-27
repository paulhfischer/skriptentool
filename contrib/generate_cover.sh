#!/bin/bash

COVERS_DIR="media/deckblätter"
LECTURE_NOTES_DIR="media/skripten"
OUTPUT_DIR="media/druck"

ean="$1"
file="${ean}.tex"


die() {
	echo "$*" >&2
	exit 1
}

pushd "$COVERS_DIR" >/dev/null \
	|| die "Could not change directory"

latexmk -pdf "$file" >/dev/null \
	|| die "latexmk failed"

latexmk -c "$file" >/dev/null \
	|| die "latexmk cleanup failed"

popd >/dev/null \
	|| die "Could not change directory"

pdftk "${COVERS_DIR}/$ean.pdf" "${LECTURE_NOTES_DIR}/$ean.pdf" cat output "${OUTPUT_DIR}/$ean.pdf" >/dev/null \
	|| die "pdftk failed"
