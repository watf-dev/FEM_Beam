#!/bin/sh
# Created: Jan, 29, 2025 14:43:07 by Wataru Fukuda
set -eu

BASE=$(pwd)

for NAME in height1 height4 height10 square; do
  case $NAME in
    height1)  steps="10 1 20 1 30 1 50 1 70 1 100 1";;
    height4)  steps="10 4 20 4 30 4 50 4 70 4 100 4";;
    height10) steps="10 10 20 10 30 10 50 10 70 10 100 10";;
    square)   steps="10 1 20 2 30 3 50 5 70 7 100 10";;
  esac
  set -- $steps
  while [ $# -gt 0 ]; do
    $BASE/src/run_for_steps.sh $1 $2 $NAME
    shift 2
  done
  cp max_dis_y_${NAME}.txt src/pgfplots/
done
cd src/pgfplots
pdflatex -shell-escape pgfplots.tex
pdfcrop --margins 10 pgfplots.pdf output.pdf
open output.pdf

