#!/bin/sh
# Created: Jan, 29, 2025 14:43:07 by Wataru Fukuda
set -eu

BASE=$(pwd)

### arg1: element num in x, arg2: element num in y
step=(
  "10 1"
  "20 2"
  "30 3"
  "50 5"
  "70 7"
  "100 10"
)

for step_ in "${step[@]}"; do
  set -- $step_
  $BASE/src/run_for_steps.sh $1 $2
done

cd src/pgfplots
cp ../../max_dis_y.txt .
pdflatex -shell-escape pgfplots.tex
pdfcrop --margins 10 pgfplots.pdf output.pdf
open output.pdf
