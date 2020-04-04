#!/bin/bash

ean="$1"
orders_dir="$2"
order_template_form_file="$3"

die() {
    echo "$*" >&2
    exit 1
}

# fill in pdf form
pdftk "$order_template_form_file" fill_form "${orders_dir}/${ean}.xfdf" output "${orders_dir}/${ean}.pdf" &>/dev/null ||
die "pdftk failed"
