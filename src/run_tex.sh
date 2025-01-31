#!/bin/sh
# Created: Jan, 31, 2025 09:38:57 by Wataru Fukuda
set -eu

BASE=$(pwd)

name_set="height1 height4 height10 square"
data_set="disa nxx nyy nxy"

for data in $data_set; do
  for name in $name_set; do
    lualatex -jobname=${data}_${name} "\def\name{$name} \def\data{$data} \input{src/base.tex}"
  done
done
mkdir -p figs/pdf
mv *.pdf figs/pdf/
rm *.log *.aux
