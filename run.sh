#!/bin/sh
# Created: Oct, 27, 2024 21:07:23 by Wataru Fukuda
set -eu

# ELE_X=$1
# ELE_Y=$2
MESH_DIR=TEST

# cd MeshGeneration/FEM
# ./gen_mesh_FEM.py -o $MESH_DIR -e $ELE_X -e $ELE_Y -s 0 $ELE_X -s 0 $ELE_Y -p 1 -p 1 -n 2
# cd ../../
./FEM_implement.py $MESH_DIR/mesh.cfg --output_x dis_x --output_y dis_y

