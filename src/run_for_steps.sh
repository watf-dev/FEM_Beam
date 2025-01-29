#!/bin/sh
# Created: Oct, 27, 2024 21:07:23 by Wataru Fukuda
set -eu

ELE_X=$1
ELE_Y=$2
RANGE_X=10
RANGE_Y=1

BASE=$(pwd)
MESH=MESH_x$1_y$2
MESH_GEN_REPO=https://github.com/watf-dev/MeshGeneration.git
MESH_GEN_DIR=MeshGeneration/FEM
OUTPUT=output

### Ensure MeshGeneration repository exists
if [ ! -d $MESH_GEN_DIR ]; then
    echo "Cloning MeshGeneration repository..."
    git clone "$MESH_GEN_REPO"
else
    echo "MeshGeneration repository already exists."
fi

### Generate mesh
./$MESH_GEN_DIR/src/gen_mesh_FEM.py -o $MESH -e $ELE_X -e $ELE_Y -s 0 $RANGE_X -s 0 $RANGE_Y -p 1 -p 1 -n 2
gen_xdmf_wataf.py $MESH/mesh.cfg -o mesh_x$1_y$2.xmf2

### Run FEM solver
$BASE/FEM_solver.py $MESH/mesh.cfg --output_dir $OUTPUT --output_dis dis_x$1_y$2 --output_disx dis_x_x$1_y$2 --output_disy dis_y_x$1_y$2 --output_nxx nxx_x$1_y$2 --output_nyy nyy_x$1_y$2 --output_nxy nxy_x$1_y$2

### Generate XDMF files
gen_xdmf_wataf.py $MESH/mesh.cfg -i $OUTPUT --fs dis_x$1_y$2 n2f dis --fs dis_x_x$1_y$2 n1f dis_x --fs dis_y_x$1_y$2 n1f dis_y -o dis_x$1_y$2.xmf2 
gen_xdmf_wataf.py $MESH/mesh.cfg -i $OUTPUT --fs nxx_x$1_y$2 n1f nxx --fs nyy_x$1_y$2 n1f nyy --fs nxy_x$1_y$2 n1f nxy -o stress_x$1_y$2.xmf2 
 
