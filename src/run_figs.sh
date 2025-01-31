#!/bin/sh
# Created: Jan, 30, 2025 22:28:48 by Wataru Fukuda
set -eu

BASE=$(pwd)

### Generate figs
PVSM_DIR=figs/pvsm
FIGS_DIR=figs/figs
mkdir -p $PVSM_DIR
mkdir -p $FIGS_DIR

for NAME in height1 height4 height10 square; do
  for id in {1..6}; do 
    pvsm_tofiles.py ${PVSM_DIR}/base_mesh.pvsm -r mesh_square_6.xmf2 mesh_${NAME}_$id.xmf2 -o ${PVSM_DIR}/mesh_${NAME}_$id.pvsm
    pvsm_tofiles.py ${PVSM_DIR}/base_disa.pvsm -r dis_square_6.xmf2 dis_${NAME}_$id.xmf2 -o ${PVSM_DIR}/disa_${NAME}_$id.pvsm
    pvsm_tofiles.py ${PVSM_DIR}/base_nxx.pvsm -r stress_square_6.xmf2 stress_${NAME}_$id.xmf2 -o ${PVSM_DIR}/nxx_${NAME}_$id.pvsm
    pvsm_tofiles.py ${PVSM_DIR}/base_nyy.pvsm -r stress_square_6.xmf2 stress_${NAME}_$id.xmf2 -o ${PVSM_DIR}/nyy_${NAME}_$id.pvsm
    pvsm_tofiles.py ${PVSM_DIR}/base_nxy.pvsm -r stress_square_6.xmf2 stress_${NAME}_$id.xmf2 -o ${PVSM_DIR}/nxy_${NAME}_$id.pvsm
    set +e
    pvpython $(which pv_rendering.py) -d :0.0 $PVSM_DIR/mesh_${NAME}_$id.pvsm -o $FIGS_DIR -f mesh_${NAME}_$id.png -s 1920x1080 --force --transparent
    pvpython $(which pv_rendering.py) -d :0.0 $PVSM_DIR/disa_${NAME}_$id.pvsm -o $FIGS_DIR -f disa_${NAME}_$id.png -s 1920x1080 --force --transparent
    pvpython $(which pv_rendering.py) -d :0.0 $PVSM_DIR/nxx_${NAME}_$id.pvsm -o $FIGS_DIR -f nxx_${NAME}_$id.png -s 1920x1080 --force --transparent
    pvpython $(which pv_rendering.py) -d :0.0 $PVSM_DIR/nyy_${NAME}_$id.pvsm -o $FIGS_DIR -f nyy_${NAME}_$id.png -s 1920x1080 --force --transparent
    pvpython $(which pv_rendering.py) -d :0.0 $PVSM_DIR/nxy_${NAME}_$id.pvsm -o $FIGS_DIR -f nxy_${NAME}_$id.png -s 1920x1080 --force --transparent
    set -e
  done
done

