#!/bin/sh
# Created: Oct, 27, 2024 21:07:23 by Wataru Fukuda
set -eu

ELE_X=$1
ELE_Y=$2
NAME=$3
RANGE_X=10
RANGE_Y=1

BASE=$(pwd)
MESH=MESH_x$1_y$2
MESH_GEN_REPO=https://github.com/watf-dev/MeshGeneration.git
MESH_GEN_DIR=MeshGeneration/FEM
OUTPUT=output_$NAME

### Ensure MeshGeneration repository exists
if [ ! -d $MESH_GEN_DIR ]; then
  echo "Cloning MeshGeneration repository..."
  git clone "$MESH_GEN_REPO"
else
  echo "MeshGeneration repository already exists."
fi

### Generate mesh
if [ ! -d $MESH ]; then
  echo "Generating mesh..."
  ./$MESH_GEN_DIR/src/gen_mesh_FEM.py -o $MESH -e $ELE_X -e $ELE_Y -s 0 $RANGE_X -s 0 $RANGE_Y -p 1 -p 1 -n 2
  gen_xdmf_wataf.py $MESH/mesh.cfg -o mesh_x$1_y$2.xmf2
else
  echo "Mesh already exists."
fi

### Run FEM solver
$BASE/src/FEM_solver.py $MESH/mesh.cfg --output_dir $OUTPUT --output_dis dis_x$1_y$2 --output_disx dis_x_x$1_y$2 --output_disy dis_y_x$1_y$2 --output_nxx nxx_x$1_y$2 --output_nyy nyy_x$1_y$2 --output_nxy nxy_x$1_y$2 --y_positive_flag

### Generate XDMF files
gen_xdmf_wataf.py $MESH/mesh.cfg -i $OUTPUT --fs dis_x$1_y$2 n2f dis --fs dis_x_x$1_y$2 n1f dis_x --fs dis_y_x$1_y$2 n1f dis_y_abs -o dis_${NAME}_x$1_y$2.xmf2 
gen_xdmf_wataf.py $MESH/mesh.cfg -i $OUTPUT --fs nxx_x$1_y$2 n1f nxx --fs nyy_x$1_y$2 n1f nyy --fs nxy_x$1_y$2 n1f nxy -o stress_${NAME}_x$1_y$2.xmf2 
 
### Convergence
fname=dis_y
[ ! -f max_${fname}_${NAME}.txt ] && touch max_${fname}_${NAME}.txt
printf "$1 $2 $(($1 * $2)) " >> max_${fname}_${NAME}.txt
$BASE/src/find_max.py $OUTPUT/${fname}_x$1_y$2 >> max_${fname}_${NAME}.txt

