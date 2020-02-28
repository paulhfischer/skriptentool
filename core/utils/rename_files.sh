#!/bin/bash

old="$1"
new="$2"
covers_dir="$3"
output_dir="$4"
lecture_notes_dir="$5"
orders_dir="$6"

die() {
  echo "$*" >&2
  exit 1
}

mv "${covers_dir}/${old}.pdf" "${covers_dir}/${new}.pdf" &>/dev/null ||
  die "mv failed"

mv "${covers_dir}/${old}.tex" "${covers_dir}/${new}.tex" &>/dev/null ||
  die "mv failed"

mv "${output_dir}/${old}.pdf" "${output_dir}/${new}.pdf" &>/dev/null ||
  die "mv failed"

mv "${lecture_notes_dir}/${old}.pdf" "${lecture_notes_dir}/${new}.pdf" &>/dev/null ||
  die "mv failed"

mv "${orders_dir}/${old}.pdf" "${orders_dir}/${new}.pdf" &>/dev/null ||
  die "mv failed"

mv "${orders_dir}/${old}.xfdf" "${orders_dir}/${new}.xfdf" &>/dev/null ||
  die "mv failed"
