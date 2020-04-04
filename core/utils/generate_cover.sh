#!/bin/bash

ean="$1"
covers_dir="$2"
lecture_notes_dir="$3"
output_dir="$4"

die() {
    echo "$*" >&2
    exit 1
}

pushd "$covers_dir" &>/dev/null ||
die "pushd failed"

# generate pdf from tex
latexmk --no-shell-escape -pdf "${ean}.tex" &>/dev/null ||
die "latexmk pdf-generation failed"

# clean up latex-buildfiles
latexmk --no-shell-escape -c -pdf -c "${ean}.tex" &>/dev/null ||
die "latexmk cleanup failed"

popd &>/dev/null ||
die "popd failed"

# merge cover to lecturenote
pdftk "${covers_dir}/${ean}.pdf" "${lecture_notes_dir}/${ean}.pdf" cat output "${output_dir}/${ean}.pdf" &>/dev/null ||
die "pdftk failed"
