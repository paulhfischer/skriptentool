#!/bin/bash

ORDERS_DIR="media/skriptenaufträge"

ean="$1"


die() {
	echo "$*" >&2
	exit 1
}

pushd "$ORDERS_DIR" >/dev/null \
	|| die "Could not change directory"

pdftk "vorlage/skriptenauftrag.pdf" fill_form "$ean.xfdf" output "$ean.pdf" >/dev/null \
	|| die "pdftk failed"

