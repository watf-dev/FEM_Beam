#!/bin/sh
# Created: Jan, 30, 2025 13:03:56 by Wataru Fukuda
set -eu

OUTPUT=croped
list1="dis dis_with_arrow nxx nyy nxy"
list2="height1 height4 height10 square"

mkdir -p $OUTPUT
for item1 in $list1; do
  for item2 in $list2; do
    target=${item1}_${item2}.tex
    pdflatex $target
  done
done

